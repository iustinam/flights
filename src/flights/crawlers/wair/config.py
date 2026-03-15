import itertools
import os
from pathlib import Path

from flights.config import DATA_DIR, DATETIME_NOW_STR

SITE = "wair"
if "WAIR_DOMAIN" not in os.environ:
    raise RuntimeError("WAIR_DOMAIN environment variable is not set")
WAIR_DOMAIN = os.environ["WAIR_DOMAIN"]

DATA_FPATH = Path(DATA_DIR / f"{SITE}.joblib")
DATA_FPATH_HISTORY = Path(DATA_DIR / "history" / f"{SITE}_{DATETIME_NOW_STR}.joblib")

# fmt: off
src_dsts = [
    {
        "srcs": ["GHV"],  # ,"BCM","CND","TGM"]
        "dsts": ["BUD", "DTM", "NAP"],  # "CAM"-nonExistent ...was before?
    },
    {
        "srcs": ["SBZ"],  # ,"BCM","CND","TGM"]
        "dsts": ["DTM"],  # "CAM"-nonExistent ...was before?
    },
    {
        "srcs": ["OTP"],  # ,"BCM","CND","TGM"]
        "dsts": [
            # Spain:
            "CDT","ALC","AGP","PMI",# "SDR","BCN","SVQ","MAD","VLC", # "IBZ"-nonExistent
            "LIS","OPO","TFS", #"LPA"-nonExistent,  # Portugal
            # "LCA", # Cyprus
            # "MLA", # Malta
            # Greece:
            "ZTH","JMK","JTR","HER","PVK","JSI","CFU","ATH",
            # Italy:
            "PSA","FCO","CIA","NAP", #"QSR" -nonE, #"TRN","MXP","BGY",
            "TRS","TSF","VCE","PSR","BRI","BDS",#"CTA", #"CAM"-nonExistent,
            "NCE", # France
            "AHO", # Sardinia
            # "BLL","CPH", # "AAR"-nonExistent, # Denmark
            "DTM","CGN","HHN",#"HAM","STR","FMM", # Germany
            "BUD", # Hungary
            # "GDN", # Poland
            # "CRL", # Belgium
            "BSL", # Switzerland
            # "TRF", # Norway
            # "AYT", # Turkey
        ],
    },
]
# fmt: on

src_dst_pairs = list(
    itertools.chain.from_iterable(
        [list(itertools.product(comb["srcs"], comb["dsts"])) for comb in src_dsts]
    )
)
# # the request already includes return flights
# src_dst_pairs += [(dst, src) for src, dst in src_dst_pairs]

# number of days between departure and return query dates (will return [-7,+7] days)
RETURN_DAYS_DIFF = 7

DBG = 0

CONFIG = {
    "days_to_query": range(7, 3 * 30, 15),  # 3 months
    "src_dst_pairs": src_dst_pairs,
    "src_dsts": src_dsts,
}

API_URL_REX = r'"apiUrl":".+?(\d+\.\d+\.\d+).+"'
FLIGHTS_URL_TPL = f"https://be.{WAIR_DOMAIN}/{{}}/Api/asset/farechart"

REQ_DATA = {
    "isRescueFare": False,
    "adultCount": 1,
    "childCount": 0,
    "dayInterval": 7,
    "wdc": False,
    "isFlightChange": False,
}

HEADERS = {
    "authority": f"be.{WAIR_DOMAIN}",
    "origin": f"https://{WAIR_DOMAIN}",
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9,ro;q=0.8",
    "content-type": "application/json;charset=UTF-8",
    "sec-ch-ua": '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "Referer": f"https://{WAIR_DOMAIN}/ro-ro/",
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    ),
}
