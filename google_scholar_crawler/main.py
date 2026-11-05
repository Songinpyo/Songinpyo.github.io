"""Collect a complete Scholar snapshot; publish nothing on a failed request."""
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
import re
import tempfile
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, build_opener

from bs4 import BeautifulSoup
import httpx
from scholarly.author_parser import AuthorParser

LOG = logging.getLogger("citation_crawler")
SECTIONS = ["basics", "indices", "counts", "publications"]


class CollectionError(RuntimeError):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class ProfileHTTPClient:
    """Use the ordinary urllib request path, without redirects or retries."""

    def __init__(self, timeout=20):
        self.timeout = timeout
        self.opener = build_opener(NoRedirect())

    def get(self, url):
        try:
            reply = self.opener.open(url, timeout=self.timeout)
        except HTTPError as exc:
            reply = exc
        except (TimeoutError, URLError) as exc:
            if isinstance(exc, TimeoutError) or isinstance(exc.reason, TimeoutError):
                raise httpx.TimeoutException("Scholar request timed out") from exc
            raise httpx.RequestError("Scholar connection failed") from exc
        with reply:
            try:
                return httpx.Response(reply.status, content=reply.read(), headers=dict(reply.headers))
            except TimeoutError as exc:
                raise httpx.TimeoutException("Scholar response timed out") from exc


class ProfileFetcher:
    """The small navigator interface used by scholarly 1.7.11's author parser.

    Retain its data format, but avoid its opaque retries, session rotation and
    interactive CAPTCHA handling. Never log URLs, response bodies or cookies.
    """

    def __init__(self, client, scholar_id):
        self.client = client
        self.scholar_id = scholar_id
        self.logger = LOG
        self.requests = 0

    def _get_soup(self, path):
        parts = urlsplit(path)
        if (parts.scheme or parts.netloc or parts.path != "/citations"
                or parse_qs(parts.query).get("user") != [self.scholar_id]):
            raise CollectionError("Unexpected profile request")
        self.requests += 1
        if self.requests > 10:
            raise CollectionError("Publication pagination exceeded 10 pages")
        query = parse_qs(parts.query)
        query = {"user": query.pop("user"), **query}
        url = "https://scholar.google.com/citations?" + urlencode(query, doseq=True)
        try:
            response = self.client.get(url)
        except httpx.TimeoutException as exc:
            raise CollectionError("Scholar request timed out; no retry attempted") from exc
        except httpx.RequestError as exc:
            raise CollectionError("Scholar transport failure: " + type(exc).__name__) from exc
        LOG.info("Scholar response: page=%d HTTP=%d bytes=%d", self.requests,
                 response.status_code, len(response.content))
        if response.status_code in (403, 429):
            raise CollectionError("Scholar access denied/rate limited (HTTP %d); stopped without bypass"
                                  % response.status_code)
        if response.status_code != 200:
            raise CollectionError("Unexpected Scholar HTTP %d; no retry attempted" % response.status_code)
        if "text/html" not in response.headers.get("content-type", "").lower():
            raise CollectionError("Scholar response is not HTML")
        soup = BeautifulSoup(response.text.replace("\xa0", " "), "html.parser")
        if (soup.select_one("#gs_captcha_ccl, #recaptcha, #captcha-form, .g-recaptcha, .rc-doscaptcha-body")
                or "unusual traffic" in soup.get_text(" ").lower()):
            raise CollectionError("Scholar CAPTCHA detected; stopped without bypass")
        canonical = soup.select_one('link[rel="canonical"]')
        canonical_id = parse_qs(urlsplit(canonical.get("href", "")).query).get("user") if canonical else None
        if canonical_id != [self.scholar_id]:
            raise CollectionError("Scholar profile identity is missing or does not match")
        metrics = soup.select("#gsc_rsb_st td.gsc_rsb_std")
        if len(metrics) != 6 or any(not re.fullmatch(r"[0-9]+", cell.get_text(strip=True)) for cell in metrics):
            raise CollectionError("Scholar metrics are missing or invalid")
        if not soup.select_one("#gsc_prf_in") or not soup.select_one("#gsc_bpf_more"):
            raise CollectionError("Incomplete Scholar profile/publication page")
        # A missing citation cell must not be interpreted as zero by the parser.
        for row in soup.select("tr.gsc_a_tr"):
            citation = row.select_one(".gsc_a_ac")
            if citation is None or not re.fullmatch(r"[0-9]*", citation.get_text(strip=True)):
                raise CollectionError("Invalid publication citation count")
        return soup


def validate(author, scholar_id):
    if author.get("scholar_id") != scholar_id or not author.get("name"):
        raise CollectionError("Invalid author identity")
    for field in ("citedby", "citedby5y", "hindex", "hindex5y", "i10index", "i10index5y"):
        if type(author.get(field)) is not int or author[field] < 0:
            raise CollectionError("Invalid author metric: " + field)
    publications = author.get("publications")
    if not isinstance(publications, list) or (author["citedby"] and not publications):
        raise CollectionError("Missing publication data")
    ids = set()
    for publication in publications:
        pub_id = publication.get("author_pub_id", "")
        count = publication.get("num_citations")
        if (not pub_id.startswith(scholar_id + ":") or pub_id in ids
                or type(count) is not int or count < 0):
            raise CollectionError("Invalid or duplicate publication data")
        ids.add(pub_id)


def collect(scholar_id, client):
    if not isinstance(scholar_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{12}", scholar_id):
        raise CollectionError("GOOGLE_SCHOLAR_ID must be a 12-character profile ID")
    parser = AuthorParser(ProfileFetcher(client, scholar_id))
    author = parser.get_author(scholar_id)
    try:
        parser.fill(author, sections=SECTIONS.copy())
    except CollectionError:
        raise
    except Exception as exc:
        raise CollectionError("Scholar profile parsing failed: " + type(exc).__name__) from exc
    validate(author, scholar_id)
    author["publications"] = {p["author_pub_id"]: p for p in author["publications"]}
    # A timestamp is assigned only after every page has been fetched and validated.
    author["updated"] = datetime.now(timezone.utc).isoformat()
    return author


def write_json(path, data):
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     delete=False) as handle:
        temporary = Path(handle.name)
        try:
            json.dump(data, handle, ensure_ascii=False)
            handle.write("\n")
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def run(scholar_id, output, client):
    author = collect(scholar_id, client)
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "gs_data_shieldsio.json", {
        "schemaVersion": 1, "label": "citations", "message": str(author["citedby"]),
    })
    write_json(output / "gs_data.json", author)
    LOG.info("Validated snapshot: citations=%d h-index=%d publications=%d updated=%s",
             author["citedby"], author["hindex"], len(author["publications"]), author["updated"])


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    # httpx's INFO messages include full URLs. Keep only our safe diagnostics.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    try:
        run(os.environ.get("GOOGLE_SCHOLAR_ID"), Path("results"), ProfileHTTPClient())
    except Exception as exc:
        message = str(exc) if isinstance(exc, CollectionError) else type(exc).__name__
        LOG.error("Citation refresh failed; last published snapshot is unchanged: %s", message)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
