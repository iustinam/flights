import logging
import random
import re
import time
import traceback
from datetime import datetime, timedelta

import joblib
import requests
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

from flights.config import DATETIME_NOW, EUR_RON_RATE, PUSHGATEWAY_URL

from .config import (
    API_URL_REX,
    DATA_FPATH,
    DATA_FPATH_HISTORY,
    FLIGHTS_URL_TPL,
    HEADERS,
    OPERATOR,
    REQ_DATA,
    RETURN_DAYS_DIFF,
    WAIR_DOMAIN,
)

logger = logging.getLogger(__name__)


def _parse_flight(it: dict) -> dict | None:
    if it["departureStation"] and it["arrivalStation"] and it["price"]["amount"]:
        return {
            "src_dst": f"{it['departureStation']}_{it['arrivalStation']}",
            "date": datetime.fromisoformat(it["date"]).strftime("%Y-%m-%d %H:%M"),
            "price_ron": it["price"]["amount"],
            "price_eur": round(it["price"]["amount"] / float(EUR_RON_RATE), 2),
            "currency": "ron",
            "crawl_date": DATETIME_NOW,
        }
    return None


def get_api_version() -> str:
    resp = requests.get(f"https://{WAIR_DOMAIN}/", headers=HEADERS)
    m = re.search(API_URL_REX, resp.text)
    if not m:
        raise RuntimeError("API version not found")
    api_version = m.group(1)
    logger.debug("api_version: %s", api_version)
    return api_version


def run(config: dict) -> None:
    api_version = get_api_version()
    dates: list[dict] = []
    errors = 0
    t_start = time.time()

    for src, dst in config["src_dst_pairs"]:
        logger.info(f"{src}/{dst}")
        for day in config["days_to_query"]:
            out_date = (DATETIME_NOW + timedelta(days=day)).strftime("%Y-%m-%d")
            ret_date = (DATETIME_NOW + timedelta(days=day + RETURN_DAYS_DIFF)).strftime(
                "%Y-%m-%d"
            )
            logger.debug(f"{src}/{dst}: querying {out_date} > {ret_date}")

            req_data = {
                **REQ_DATA,
                "flightList": [
                    {
                        "departureStation": src,
                        "arrivalStation": dst,
                        "date": out_date,
                    },
                    {
                        "departureStation": dst,
                        "arrivalStation": src,
                        "date": ret_date,
                    },
                ],
            }
            url = FLIGHTS_URL_TPL.format(api_version)

            resp = None
            try:
                resp = requests.post(url, json=req_data, headers=HEADERS)
                resp.raise_for_status()
                resp_json = resp.json()
                flights = resp_json["outboundFlights"] + resp_json["returnFlights"]
                dates.extend(f for it in flights if (f := _parse_flight(it)))

                time.sleep(1.5 + random.uniform(0, 0.5))

            except Exception:
                errors += 1
                logger.error(traceback.format_exc())
                logger.error(
                    f"{src} -> {dst} ({out_date} > {ret_date}) |"
                    f" resp={resp.text if resp else 'no response'}"
                )

    joblib.dump(dates, DATA_FPATH)
    joblib.dump(dates, DATA_FPATH_HISTORY)

    if PUSHGATEWAY_URL:
        _push_metrics(
            operator=OPERATOR,
            duration=time.time() - t_start,
            flights_total=len(dates),
            errors_total=errors,
            pushgateway_url=PUSHGATEWAY_URL,
        )


def _push_metrics(
    operator: str,
    duration: float,
    flights_total: int,
    errors_total: int,
    pushgateway_url: str,
) -> None:
    registry = CollectorRegistry()
    labels = ["operator"]

    Gauge(
        "flights_crawl_duration_seconds",
        "Crawl duration in seconds",
        labels,
        registry=registry,
    ).labels(operator=operator).set(duration)

    Gauge(
        "flights_crawl_flights_total",
        "Number of flights found",
        labels,
        registry=registry,
    ).labels(operator=operator).set(flights_total)

    Gauge(
        "flights_crawl_errors_total",
        "Number of failed requests",
        labels,
        registry=registry,
    ).labels(operator=operator).set(errors_total)

    Gauge(
        "flights_crawl_last_success_timestamp",
        "Unix timestamp of last successful crawl",
        labels,
        registry=registry,
    ).labels(operator=operator).set(time.time())

    try:
        push_to_gateway(pushgateway_url, job="flights", registry=registry)
        logger.info("metrics pushed to %s", pushgateway_url)
    except Exception:
        logger.error("failed to push metrics: %s", traceback.format_exc())
