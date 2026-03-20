import itertools
import os
from pathlib import Path

from flights.config import DATA_DIR, DATETIME_NOW_STR

OPERATOR = "rair"
if "RAIR_DOMAIN" not in os.environ:
    raise RuntimeError("RAIR_DOMAIN environment variable is not set")
RAIR_DOMAIN = os.environ["RAIR_DOMAIN"]

DATA_FPATH = Path(DATA_DIR / f"{OPERATOR}.joblib")
DATA_FPATH_HISTORY = Path(
    DATA_DIR / "history" / f"{OPERATOR}_{DATETIME_NOW_STR}.joblib"
)

# fmt: off
src_dsts = [
    {
        "srcs": ["OTP"],  # ,"BCM","CND","TGM"]
        "dsts": [
            "VIE", # "SZG", # Austria 
            # "CRL", # "BRU", # Belgium
            "VAR", # Bulgaria
            "BSL", # Switzerland
            "PFO", "LCA", # Cyprus
            "PRG", # Czech Republic
            "BER", "CGN", "HHN", "NRN", # Germany
            # "AAR", "CPH", # Denmark
            # Spain:
            "AGP", "ALC", "PMI", "TFS", # "ACE", "BCN", "MAD", "RMU", "VLC","LPA",  #wwi
            "ZAD", # Croatia
            "MRS", # France
            # Greece:
            "CHQ","CFU","JSI","JTR","SKG", # "ZTH","JMK","HER","PVK","ATH",
            # "DUB", # Ireland
            # Italy:
            "GOA", "SUF", "PSR", "TSF", "PSA","NAP","FCO","CIA", 
            # "PMO","PEG","CTA","BGY",
            # "LIS",# Portugal
            "MLA", # "LCA"-nonExistent,"AHO"-nonExistent,
            # "BRS","EDI", # UK
            # "BLL","CPH", "AAR", # DK -nonExistent
            # "BUD", 
            # "DTM","CAM", -nonExistent
        ],
    },
]
src_dsts = [
    {
        "srcs": ["OTP"],  
        "dsts": ["BER","PMO","BRS"] 
        #,"MLA","DUB","JMK","PEG","CTA","BGY"],  
    }
]
# fmt: on

src_dst_pairs = list(
    itertools.chain.from_iterable(
        [list(itertools.product(comb["srcs"], comb["dsts"])) for comb in src_dsts]
    )
)
src_dst_pairs += [(dst, src) for src, dst in src_dst_pairs]

DBG = 0

CONFIG = {
    "days_to_query": range(7, 1 * 30, 30),  # 1 month
    "src_dst_pairs": src_dst_pairs,
    "src_dsts": src_dsts,
}

FLIGHTS_URL_TPL = f"https://www.{RAIR_DOMAIN}/api/farfnd/v4/oneWayFares/{{}}/cheapestPerDay?outboundMonthOfDate={{}}&currency=EUR&promoCode="

HEADERS = {
    "user-agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9,ro;q=0.8",
    "client": "desktop",
    "client-version": "3.130.1",
    "priority": "u=1, i",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "Referrer-Policy": "same-origin",
}
