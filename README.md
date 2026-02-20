# ✈️ Flights guru

Features:
- given a list of source airports and a list of destination airports, find flights using any combination of them (eg. if you have multiple airports near home or near your destination)
- combines flights from multiple operators (outbound and inbound flights from different operators)
- helps decide on the next vacation destination by providing a report with filtered + sorted flights based on multiple criteria (see [configuration example](examples/report-config-explained.yaml))

Generate custom report based on latest data:
```sh
curl -X POST \
  -H "Authorization: Bearer $GITHUB_FLIGHT_REPORTS" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/iustinam/flights/actions/workflows/on-demand.yml/dispatches \
  -d '{"ref":"main","inputs":{"config_json":"{\"srcs\":[\"OTP\"],\"dsts\":[\"BCN\"],\"dates_range\": [\"2026-02-01\", \"2026-03-04\"],\"nights_stay\":[1,7],\"order_by\":[\"price\"]}"}'

json=`python tools/actions_curl_config.py examples/test.json`
curl -X POST \
  -H "Authorization: Bearer $GITHUB_FLIGHT_REPORTS" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/iustinam/flights/actions/workflows/on-demand.yml/dispatches \
  -d "$json"
```

Usage:
```sh
pip install -e .

flights crawl rair
flights crawl wizz
flights report --config examples/test.json
```
or:
```sh
cd src/
python -m flights.cli crawl rair
python -m flights.cli crawl wair
python -m flights.cli report --config ../examples/test.json
```
