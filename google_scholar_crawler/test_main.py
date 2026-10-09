import json
from pathlib import Path
import tempfile
import unittest

import httpx
from main import CollectionError, collect, run

ID = "test1234ABCD"


def profile(*, count="2", pub="paper", more=False):
    return f'''<link rel="canonical" href="https://scholar.google.com/citations?user={ID}">
    <div id="gsc_prf_in">Example Author</div><div class="gsc_prf_il">Example University</div>
    <div id="gsc_prf_ivh" class="gsc_prf_il">No verified email</div>
    <table id="gsc_rsb_st"><tr>{''.join('<td class="gsc_rsb_std">'+v+'</td>' for v in [count,count,'1','1','0','0'])}</tr></table>
    <table><tr class="gsc_a_tr"><td><a class="gsc_a_at" href="/citations?citation_for_view={ID}:{pub}">Example paper</a></td>
    <td><a class="gsc_a_ac" href="https://scholar.google.com/scholar?cites=123">{count}</a></td></tr></table>
    <button id="gsc_bpf_more" {'' if more else 'disabled'}>More</button>'''


def client_for(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))


def response(body, status=200, content_type="text/html"):
    return httpx.Response(status, text=body, headers={"content-type": content_type})


class CollectorTests(unittest.TestCase):
    def test_success_preserves_schema_and_uses_utc(self):
        with client_for(lambda _: response(profile())) as client, tempfile.TemporaryDirectory() as tmp:
            run(ID, Path(tmp), client)
            data = json.loads((Path(tmp) / "gs_data.json").read_text())
            self.assertEqual((data["citedby"], data["hindex"]), (2, 1))
            self.assertEqual(data["publications"][ID + ":paper"]["num_citations"], 2)
            self.assertTrue(data["updated"].endswith("+00:00"))
            self.assertEqual(json.loads((Path(tmp) / "gs_data_shieldsio.json").read_text())["message"], "2")

    def assert_preserved(self, handler, pattern):
        calls = []
        def observed(request):
            calls.append(request)
            return handler(request)
        with client_for(observed) as client, tempfile.TemporaryDirectory() as tmp:
            paths = [Path(tmp) / name for name in ["gs_data.json", "gs_data_shieldsio.json"]]
            for path in paths:
                path.write_bytes(b'{"updated":"2026-09-30","citedby":86}')
            before = [path.read_bytes() for path in paths]
            with self.assertRaisesRegex(CollectionError, pattern):
                run(ID, Path(tmp), client)
            self.assertEqual([path.read_bytes() for path in paths], before)
        return calls

    def test_http_errors_stop_after_one_request_and_preserve_files(self):
        for status in [302, 403, 404, 429, 500]:
            with self.subTest(status=status):
                calls = self.assert_preserved(lambda _: response("error", status), "HTTP")
                self.assertEqual(len(calls), 1)

    def test_captcha_stops_without_retry(self):
        for body in ['<form id="captcha-form"></form>', '<div class="rc-doscaptcha-body"></div>', 'Unusual traffic']:
            self.assertEqual(len(self.assert_preserved(lambda _: response(body), "CAPTCHA")), 1)

    def test_transport_errors_do_not_leak_details(self):
        for error in [httpx.ReadTimeout("sensitive URL"), httpx.ConnectError("sensitive URL")]:
            def fail(_):
                raise error
            calls = self.assert_preserved(fail, "timed out|transport failure: ConnectError")
            self.assertEqual(len(calls), 1)

    def test_invalid_profile_preserves_last_good_snapshot(self):
        bodies = ["<html>maintenance</html>", profile().replace(ID, "wrong123ABCD"),
                  profile(count="-1"), profile().replace('class="gsc_a_ac"', 'class="missing"'),
                  profile().replace('id="gsc_bpf_more"', 'id="missing"')]
        for body in bodies:
            with self.subTest(body=body[:30]):
                self.assert_preserved(lambda _: response(body), "identity|metrics|publication")
        self.assert_preserved(lambda _: response('{}', content_type="application/json"), "not HTML")

    def test_invalid_input_makes_no_request(self):
        for invalid in [None, "", "https://scholar.google.com", " test1234ABCD", "../citations"]:
            with client_for(lambda _: self.fail("unexpected request")) as client:
                with self.assertRaisesRegex(CollectionError, "12-character"):
                    collect(invalid, client)

    def test_all_publication_pages_are_required(self):
        calls = []
        def fetch(request):
            calls.append(request)
            return response(profile(pub="first", more=True) if len(calls) == 1 else profile(pub="second"))
        with client_for(fetch) as client:
            data = collect(ID, client)
        self.assertEqual(len(data["publications"]), 2)
        self.assertEqual(calls[1].url.params["cstart"], "100")

    def test_second_page_failure_preserves_files(self):
        self.assert_preserved(lambda request: response("blocked", 403) if "cstart" in request.url.params
                              else response(profile(more=True)), "access denied")

    def test_duplicate_and_unbounded_pages_fail(self):
        self.assert_preserved(lambda _: response(profile(more=True)), "exceeded 10 pages")
        self.assert_preserved(lambda r: response(profile(more="cstart" not in r.url.params)), "duplicate")

    def test_zero_citations_are_valid(self):
        with client_for(lambda _: response(profile(count="0"))) as client:
            self.assertEqual(collect(ID, client)["citedby"], 0)


if __name__ == "__main__":
    unittest.main()
