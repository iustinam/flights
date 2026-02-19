import itertools
from pathlib import Path

from flights.config import DATA_DIR, DATETIME_NOW_STR

SITE = "wair"

DATA_FPATH = Path(DATA_DIR / f"{SITE}.joblib")
DATA_FPATH_HISTORY = Path(DATA_DIR / "history" / f"{SITE}_{DATETIME_NOW_STR}.joblib")

src_dsts = [
    {
        "srcs": ["GHV"],  # ,'BCM','CND','TGM']
        "dsts": ["BUD", "DTM", "NAP"],  # 'CAM'-nonExistent ...was before?
    },
    {
        "srcs": ["OTP"],  # ,'BCM','CND','TGM']
        "dsts": [
            "CDT",
            "VLC",
            "ALC",
            "AGP",
            "PMI",
            "MAD",
            "SDR",
            "BCN",
            "SVQ",  # 'IBZ'-nonExistent
            "LIS",
            "TFS",  # 'LPA'-nonExistent,
            "LCA",
            "MLA",
            "AHO",
            "ZTH",
            "JMK",
            "JTR",
            "HER",
            "PVK",
            "JSI",
            "CFU",
            "ATH",
            "PSA",
            "FCO",
            "CIA",
            "NAP",
            "QSR",  # 'TRN','MXP','BGY',
            "TRS",
            "TSF",
            "VCE",
            "PSR",
            "BRI",
            "BDS",
            "CTA",  # 'CAM'-nonExistent,
            "NCE",
            "BLL",
            "CPH",  # 'AAR'-nonExistent, # DK
            "DTM",
            "STR",
            "FMM",
            "CGN",
            "HHN",
            "HAM",
            "BUD",
            "GDN",
            "CRL",
            "BSL",
            "OPO",
            "TRF",
            "AYT",
        ],
    },
]

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
    "days_to_query": range(7, 1 * 30, 15),  # 1 month
    "src_dst_pairs": src_dst_pairs,
    "src_dsts": src_dsts,
}
