# ✈️ Flights guru

Features:
- given a list of source airports and a list of destination airports, find flights using any combination of them (eg. if you have multiple airports near home or near your destination)
- combines flights from multiple operators (outbound and inbound flights from different operators)
- helps decide on the next vacation destination by providing a report with filtered + sorted flights based on multiple criteria (see [configuration example](examples/report-config-explained.yaml))

Reports examples:
- https://iustinam.github.io/flights/reports/flights-test/ ([source](reports/flights-test.md))
- https://iustinam.github.io/flights/reports/flights-test-no-srcs-dsts/ ([source](reports/flights-test-no-srcs-dsts.md))

Generate custom report based on latest data:
```sh
curl -X POST \
  -H "Authorization: Bearer $GITHUB_FLIGHT_REPORTS" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/iustinam/flights/actions/workflows/reports.yml/dispatches \
  -d '{"ref":"main","inputs":{"config_json":"{\"srcs\":[\"OTP\"],\"dsts\":[\"BCN\"],\"dates_range\": [\"2026-02-01\", \"2026-03-04\"],\"nights_stay\":[1,7],\"order_by\":[\"price\"]}"}'

json=`python tools/actions_curl_config.py examples/test.json`
curl -X POST \
  -H "Authorization: Bearer $GITHUB_FLIGHT_REPORTS" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/iustinam/flights/actions/workflows/reports.yml/dispatches \
  -d "$json"
```

Usage:
```sh
pip install -e .
flights report --config examples/test.json
```

Workflows:
- on demand report generation: install, report configured, build site, deploy to pages
- on push to main + `data/` changes: install, report default, build site, deploy to pages
- on push to main: install+lint, build site
- on PR: install+lint

Development:
- first time / on dependencies change: `make install`
- iterate
```sh
make format
make check
make lint-fix
make type
make local-run
```
