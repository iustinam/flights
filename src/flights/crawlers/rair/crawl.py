import logging
import random
import time
import traceback
from datetime import datetime, timedelta

import joblib
import requests

from flights.config import DATETIME_NOW, EUR_RON_RATE

from .config import (
    DATA_FPATH,
    DATA_FPATH_HISTORY,
    FLIGHTS_URL_TPL,
    HEADERS,
)

logger = logging.getLogger(__name__)


def run(config: dict) -> None:
    dates = []

    for src, dst in config["src_dst_pairs"]:
        for days_diff in config["days_to_query"]:
            logger.debug(f"{src}/{dst}")

            qdate = (DATETIME_NOW + timedelta(days=days_diff)).strftime("%Y-%m-%d")
            url = FLIGHTS_URL_TPL.format(f"{src}/{dst}", qdate)

            resp = None
            try:
                resp = requests.get(url, headers=HEADERS)
                resp.raise_for_status()
                # if DBG:
                #     print(resp.text)
                flights = resp.json()["outbound"]["fares"]
                for it in flights:
                    if it["departureDate"] and it["arrivalDate"]:
                        dates.append(
                            {
                                "src_dst": f"{src}_{dst}",
                                "date": datetime.fromisoformat(
                                    it["departureDate"]
                                ).strftime("%Y-%m-%d %H:%M"),
                                "price_ron": it["price"]["value"] * EUR_RON_RATE,
                                "price_eur": it["price"]["value"],
                                "currency_orig": "eur",
                                "crawl_date": DATETIME_NOW,
                            }
                        )

                time.sleep(1 + random.uniform(0, 1))

            except Exception:
                logger.error(traceback.format_exc())
                logger.error(
                    f"{src} -> {dst} ({qdate}) |"
                    f" resp={resp.text if resp else 'no response'}"
                )

            print(".", end="", flush=True)

    joblib.dump(dates, DATA_FPATH)
    joblib.dump(dates, DATA_FPATH_HISTORY)
