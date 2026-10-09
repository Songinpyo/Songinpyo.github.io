# Citation refresh

`Get Citation Data` runs daily or via `workflow_dispatch`. It fetches the public
profile identified by the existing `GOOGLE_SCHOLAR_ID` secret. A normal push runs
regression tests and the site's Pages build; it does not fetch new citations.

The pinned scholarly 1.7.11 author parser retains the existing JSON schema. Its
navigator is replaced by a small bounded HTTP client: 20-second network timeouts,
at most 10 profile pages, no automatic retries, no redirect following, no proxy
rotation and no CAPTCHA handling. The workflow also limits collection to two
minutes and the whole job to five. Changes to the pinned parser must pass the
fixture tests, including pagination. HTTP status and exception type are logged;
URLs, IDs, cookies and response bodies are not.

All profile pages, metrics and publication IDs must validate before output is
written. Only a fully successful collection receives a new UTC `updated` value.
A failed fetch fails the workflow and skips publication, leaving both files on
`google-scholar-stats` unchanged. The `updated` timestamp remains in the JSON
for collection diagnostics.

Run checks from the repository root:

```sh
python -m unittest discover -s google_scholar_crawler -p 'test_*.py'
node --test google_scholar_crawler/tests/display.test.cjs
```

For a live refresh use the workflow's **Run workflow** action. Inspect the
`Fetch citation data` log. HTTP 403/429 or CAPTCHA means collection stopped;
do not rotate addresses, solve challenges or substitute invented counts.
A timeout/5xx is a failed attempt, not evidence by itself of access blocking.
The failed October 8, 2026 run only recorded scholarly's generic
`MaxTriesExceededException`; its original underlying response is unknown.
