import glob
import itertools
import logging
from pathlib import Path
from pprint import pformat as pf

import joblib
import pandas as pd
from jinja2 import Environment, FileSystemLoader

from flights.config import DATA_DIR

from .config import (
    AIRPORTS,
    CONFIG,
    MKDOCS_REPORT_FILE_TPL,
    MKDOCS_TEMPLATE_FILE,
    REPORT_FILE_TPL,
    TEMPLATE_DIR,
    TEMPLATE_FILE,
    TRIP_URL,
    parse_config,
)

__all__ = ["run", "CONFIG"]

logger = logging.getLogger(__name__)


def load_data() -> pd.DataFrame:
    dfs = []
    for file in glob.glob(f"{DATA_DIR}/*.joblib"):
        data = joblib.load(file)
        df = pd.DataFrame(data)
        df["operator"] = Path(file).stem
        dfs.append(df)

    df_all = pd.concat(dfs, ignore_index=True)

    # some operators don't provide the departure hour:minute in the list api response
    df_all["has_departure_time"] = ~df_all["date"].str.endswith("00:00")

    df_all["date"] = pd.to_datetime(df_all["date"], errors="coerce")

    return df_all


def filter_flights(df: pd.DataFrame, conf: dict) -> pd.DataFrame:
    """Apply filters to the flights data"""

    df = df.copy()

    # Select only flights within the specified date range
    df = df.loc[(df["date"].between(*conf["dates_range"]))]

    # Filter out departures that are too early (eg. before 08:00)
    mask = False
    for src, min_hour in conf["min_hour_depart"].items():
        if src == "*":
            mask |= (df["has_departure_time"]) & (df["date"].dt.time < min_hour)
        else:
            mask |= (
                df["src_dst"].str.startswith(src, na=False)
                & (df["has_departure_time"])
                & (df["date"].dt.time < min_hour)
            )
    df = df.loc[~mask]

    return df


def build_roundtrips_for_trip(
    df: pd.DataFrame, conf: dict, trip_from: list[str], trip_to: list[str]
) -> pd.DataFrame:
    """
    Build a dataframe with all possible round trips for a given trip configuration
    (eg. from ["GHV", "OTP"] to ["DTM", "CGN"]) and calculate the total price for each
    round trip option, then sort by price and return the dataframe with the round
    trips options for the given trip configuration
    """

    logger.debug("%s → %s", trip_from, trip_to)

    # Get all possible outbound and inbound routes for a trip
    # by doing a Cartesian product between the departure and arrival airports:
    # Eg for: trip_from = ["GHV", "OTP"], trip_to = ["DTM", "CGN"]:
    #   * outbound_routes: ["GHV_DTM", "GHV_CGN", "OTP_DTM", "OTP_CGN"]
    #   * inbound_routes: ["DTM_GHV", "CGN_GHV", "DTM_OTP", "CGN_OTP"]
    outbound_routes = [
        f"{src}_{dst}" for src, dst in itertools.product(trip_from, trip_to)
    ]
    inbound_routes = [
        f"{src}_{dst}" for src, dst in itertools.product(trip_to, trip_from)
    ]

    outb = df.loc[df["src_dst"].isin(outbound_routes)]
    inb = df.loc[df["src_dst"].isin(inbound_routes)]

    if outb.empty or inb.empty:
        return pd.DataFrame()

    # Create a dataframe with all possible nights of stay (eg. 1 to 7) and merge it with
    # the outbound flights to calculate the corresponding return dates, then merge with
    # the inbound flights on the return date to find matching round trips

    nights_df = pd.DataFrame({"nights": range(*conf["nights_stay"])})

    outb_ext = outb.merge(nights_df, how="cross")
    outb_ext["join_date"] = (
        # drop the time part to keep only the date for the merge
        outb_ext["date"].dt.normalize()
        + pd.to_timedelta(outb_ext["nights"], unit="D")
    )
    outb_inb = outb_ext.merge(
        inb.assign(join_date=inb["date"].dt.normalize()),
        on="join_date",
        suffixes=("_outb", "_inb"),
    )
    if outb_inb.empty:
        return pd.DataFrame()

    # Filter out round trips that do not meet the minimum hours of stay requirement
    outb_inb["hours_stay"] = (
        outb_inb["date_inb"] - outb_inb["date_outb"]
    ).dt.total_seconds() / 3600

    outb_inb = outb_inb.loc[outb_inb["hours_stay"] >= conf["min_hours_stay"]]

    if outb_inb.empty:
        return pd.DataFrame()

    # Calculate total price for round trips
    outb_inb["price"] = outb_inb["price_outb"] + outb_inb["price_inb"]

    # Sort
    outb_inb = outb_inb.sort_values(
        conf["order_by"], ascending=[True] * len(conf["order_by"])
    )

    return outb_inb


def build_trips(df: pd.DataFrame, conf: dict) -> list[dict]:
    """
    Create all possible trips combinations by doing a Cartesian product between all
    source (lists) and destination (lists of proximity) airports.
    """
    # eg. [(["GHV", "OTP"], ["DTM", "CGN", "HHN"]),...]
    trips_conf = list(itertools.product(conf["srcs"], conf["dsts"]))

    trips = []

    for trip_from, trip_to in trips_conf:
        outb_inb = build_roundtrips_for_trip(df, conf, trip_from, trip_to)

        if not outb_inb.empty:
            trips.append(
                {
                    "from": trip_from,
                    "to": trip_to,
                    "df": outb_inb,
                    "min_price": outb_inb["price"].min(),
                }
            )

    return trips


def get_flights_links_md(row: pd.Series) -> str:
    """
    Generate markdown links to the flights pages for each round trip option.
    If the outbound and inbound flights are with the same operator and between the same
    airports, generate a single link to the return trip, otherwise generate separate
    links for outbound and inbound flights
    """

    date_outb_str = row["date_outb"].strftime("%Y-%m-%d_%H:%M")
    date_inb_str = row["date_inb"].strftime("%Y-%m-%d_%H:%M")
    src_outb, dst_outb = row["src_dst_outb"].split("_")
    src_inb, dst_inb = row["src_dst_inb"].split("_")

    # single link when we have the same operator+airports for outbound and inbound
    if (
        row["operator_outb"] == row["operator_inb"]
        and src_outb == dst_inb
        and dst_outb == src_inb
    ):
        url = TRIP_URL[row["operator_outb"]]["return"].format(
            src=src_outb,
            dst=dst_outb,
            date_outb_short=date_outb_str[:10],
            date_inb_short=date_inb_str[:10],
        )
        links_str = f"[{date_outb_str[5:]} - {date_inb_str[5:]}]({url})"
    else:
        # separate links for outbound and inbound if different operators/airports
        links = []
        routes = [
            (src_outb, dst_outb, date_outb_str, row["operator_outb"]),
            (src_inb, dst_inb, date_inb_str, row["operator_inb"]),
        ]
        for src, dst, date_str, operator in routes:
            url = TRIP_URL[operator]["one_way"].format(
                src=src,
                dst=dst,
                date_short=date_str[:10],
            )
            links.append(f"[{date_str[5:]}]({url}) ")
        links_str = " - ".join(links)

    return links_str


def format_trips_data(trips: list[dict]) -> list[dict]:
    """Format the trips data for rendering in the report"""
    formatted_trips = []

    for trip in trips:
        # make the route more readable by replacing airport codes with names
        # (eg. "GHV (Ghimbav) --> DTM (Dortmund)")
        trip_from = [
            f"{code} ({AIRPORTS[code]})" if code in AIRPORTS.keys() else code
            for code in trip["from"]
        ]
        trip_to = [
            f"{code} ({AIRPORTS[code]})" if code in AIRPORTS.keys() else code
            for code in trip["to"]
        ]

        df = trip["df"].copy()

        # Add markdown links to the flights pages for each round trip option
        df["links"] = df.apply(lambda row: get_flights_links_md(row), axis=1)

        # Format dates and highlight in bold the ones that are on weekend (Sat, Sun)
        df["date_outb_fmt"] = df["date_outb"].dt.strftime("%Y-%m-%d %H:%M")
        df["date_inb_fmt"] = df["date_inb"].dt.strftime("%Y-%m-%d %H:%M")

        df.loc[df["date_outb"].dt.weekday >= 5, "date_outb_fmt"] = (
            "**" + df["date_outb_fmt"] + "**"
        )

        df.loc[df["date_inb"].dt.weekday >= 5, "date_inb_fmt"] = (
            "**" + df["date_inb_fmt"] + "**"
        )

        formatted_trips.append(
            {
                "route": f'{" / ".join(trip_from)} --> {" / ".join(trip_to)}',
                "df": df,
                "min_price": trip["min_price"],
            }
        )

    return formatted_trips


def generate_md(trips: list[dict], config: dict) -> None:
    """Generate a markdown report using a jinja template and save it to a file"""

    config_str = pf(config, compact=True).replace("'", '"')

    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    template = env.get_template(TEMPLATE_FILE)
    md = template.render(
        name=config["name"], config_str=config_str, trips=trips, airports=AIRPORTS
    )

    REPORT_FILE = REPORT_FILE_TPL.format(name=config["name"])
    with open(REPORT_FILE, "w") as f:
        f.write(md)

    logging.info(REPORT_FILE)

    # Generate a separate markdown report for mkdocs
    template = env.get_template(MKDOCS_TEMPLATE_FILE)
    md = template.render(
        name=config["name"], config_str=config_str, trips=trips, airports=AIRPORTS
    )

    REPORT_FILE = MKDOCS_REPORT_FILE_TPL.format(name=config["name"])
    with open(REPORT_FILE, "w") as f:
        f.write(md)

    logging.info(REPORT_FILE)


def run(config: dict) -> None:
    conf = parse_config(config)
    df = load_data()
    df = filter_flights(df, conf)
    trips = build_trips(df, conf)
    trips = sorted(trips, key=lambda x: x["min_price"])
    formatted_trips = format_trips_data(trips)
    generate_md(formatted_trips, config)
