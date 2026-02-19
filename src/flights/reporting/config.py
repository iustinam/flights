from copy import deepcopy
from pathlib import Path
import os
import pandas as pd

from flights.config import PROJECT_ROOT

CONFIG = {
    "max_price": 1000,
    "min_hours_stay": 20,
    "nights_stay": [1, 1],
    "dates_range": ["2025-11-07", "2025-12-31"],
    "min_hour_depart": {"OTP": "10:00", "GHV": "10:00"},
}
TEMPLATE_DIR = Path(__file__).parent / "templates"

REPORTS_DIR = Path(os.environ.get("FLIGHTS_REPORT_DIR", PROJECT_ROOT / "reports"))
# REPORT_FILE_TPL = f"{REPORTS_DIR}/flights__{{dates}}__{{max_price}}__{{nights}}.md"
REPORT_FILE_TPL = f"{REPORTS_DIR}/flights-{{name}}.md"
TEMPLATE_FILE = "report.md.j2"

MKDOCS_REPORTS_DIR = Path(
    os.environ.get("FLIGHTS_REPORT_DIR", PROJECT_ROOT / "docs" / "reports")
)
MKDOCS_REPORT_FILE_TPL = f"{MKDOCS_REPORTS_DIR}/flights-{{name}}.md"
MKDOCS_TEMPLATE_FILE = "report-mkdocs.md.j2"


AIRPORTS = {
    "AAR": "Aarhus.DK",
    "AGP": "Malaga.ESP",
    "AHO": "Alghero.Sardinia",
    "ALC": "Alicante",
    "AMM": "Amman Jordan.JOR",
    "ATH": "Athens",
    "AYT": "Antalya",
    "BCN": "Barcelona",
    "BDS": "Brindisi.IT-SE",
    "BER": "Berlin Brandenburg.DEU",
    "BGY": "Milano Bergamo.ITA",
    "BHX": "Birmingham.GBR",
    "BLL": "Billund.DK",
    "BLQ": "Bologna.ITA",
    "BRI": "Bari",
    "BRS": "Bristol.GBR",
    "BSL": "Basel.Switz",
    "BTS": "Bratislava",
    "BVA": "Paris Beauvais.FRA",
    "CDT": "Castellon",
    "CFU": "Corfu.GRC",
    "CGN": "Cologne",
    "CHQ": "Chania.GRC",
    "CIA": "Rome",
    "CRL": "Bruxelles Charleroi.BEL",
    "CTA": "Catania.ITA",
    "DTM": "Dortmund.DE",
    "DUB": "Dublin.IRL",
    "EDI": "Edinburgh.GBR",
    "FCO": "Fiumicino",
    "FMM": "Munich",
    "GDN": "Gdansk.PL",
    "GOA": "Genoa.ITA",
    "GVA": "Geneva.Switz",
    "HAM": "Hamburg",
    "HER": "Crete",
    "HHN": "Frankfurt",
    "JMK": "Mykonos",
    "JSI": "Skiathos.Gr",
    "JTR": "Santorini",
    "LBA": "Leeds Bradford.GBR",
    "LCA": "Larnaca.Cyprus",
    "LIS": "Lisbon",
    "LPA": "Gran Canaria",
    "MAD": "Madrid.ESP",
    "MAN": "Manchester.GBR",
    "MLA": "Malta.MLT",
    "MRS": "Marseille.FRA",
    "MXP": "Milan Malpensa.ITA",
    "NAP": "Napoli.ITA",
    "NCE": "Nisa.FR",
    "OPO": "Porto",
    "PEG": "Perugia.ITA",
    "PFO": "Paphos.CYP",
    "PMI": "Palma de Mallorca.ESP",
    "PMO": "Palermo.ITA",
    "PSA": "Pisa.ITA",
    "PSR": "Pescara.ITA",
    "PVK": "Preveza",
    "QSR": "Salerno.IT-SW",
    "SDR": "Santander.Spain-N",
    "SKG": "Thessaloniki.GRC",
    "STN": "Londra Stansted.GBR",
    "STR": "Stuttgart",
    "SUF": "Lamezia.ITA",
    "SVQ": "Seville",
    "TFS": "Tenerife",
    "TIA": "Tirana.ALB",
    "TLV": "Tel-Aviv",
    "TRF": "Oslo",
    "TRS": "Trieste.IT-NE",
    "TSF": "Venice",
    "VCE": "Venice",
    "VIE": "Vienna.AUT",
    "VLC": "Valencia",
    "ZAD": "Zadar.HRV",
    "ZTH": "Zakinthos",
}

TRIP_URL = {
    "rair": {
        "one_way": "https://www.rair.com/ro/ro/trip/flights/select?adults=2&teens=0&children=0&infants=0&dateOut={date_short}&dateIn=&isConnectedFlight=false&discount=0&isReturn=false&promoCode=&originIata={src}&destinationIata={dst}&tpAdults=2&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate={date_short}&tpEndDate=&tpDiscount=0&tpPromoCode=&tpOriginIata={src}&tpDestinationIata={dst}",
        "return": "https://www.rair.com/ro/ro/trip/flights/select?adults=2&teens=0&children=0&infants=0&dateOut={date_outb_short}&dateIn={date_inb_short}&isConnectedFlight=false&discount=0&promoCode=&isReturn=true&originIata={src}&destinationIata={dst}&tpAdults=2&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate={date_outb_short}&tpEndDate={date_inb_short}&tpDiscount=0&tpPromoCode=&tpOriginIata={src}&tpDestinationIata={dst}",
    },
    "wair": {
        "one_way": "https://www.wair.com/ro-ro/booking/select-flight/{src}/{dst}/{date_short}/null/1/0/0/null",
        "return": "https://www.wair.com/ro-ro/booking/select-flight/{src}/{dst}/{date_outb_short}/{date_inb_short}/1/0/0/null",
    },
}


def as_list(x: str | list) -> list:
    return x if isinstance(x, list) else [x]


def as_list_of_lists(x: list) -> list[list]:
    return [as_list(i) for i in x]


def parse_config(config: dict) -> dict:
    conf = deepcopy(config)

    if not config.get("name"):
        config["name"] = (
            f"{'-'.join(config['dates_range'])}--{config['max_price']}--{'-'.join(map(str, config['nights_stay']))}"
        )
    conf["srcs"] = as_list_of_lists(config["srcs"])
    conf["dsts"] = as_list_of_lists(config["dsts"])
    # conf['nights_stay'] = range(*conf['nights_stay'])
    conf["dates_range"] = [
        pd.to_datetime(config["dates_range"][0]),
        pd.to_datetime(config["dates_range"][1]) + pd.Timedelta(days=1),
    ]
    for src in conf["min_hour_depart"].keys():
        conf["min_hour_depart"][src] = pd.to_datetime(
            conf["min_hour_depart"][src], format="%H:%M"
        ).time()

    return conf
