import copy
import importlib
import json
import os
from datetime import datetime
from pathlib import Path

import yaml

DATETIME_NOW = datetime.now()
DATETIME_NOW_STR = DATETIME_NOW.strftime("%Y.%m.%d_%H.%M.%S")
EUR_RON_RATE = 5.1

FLIGHTS_BASE_DIR = Path(
    os.environ.get("FLIGHTS_BASE_DIR", Path(__file__).resolve().parents[2])
)
DATA_DIR = FLIGHTS_BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
(DATA_DIR / "history").mkdir(exist_ok=True)
OPERATORS = ["rair", "wair"]
PUSHGATEWAY_URL = os.environ.get("PUSHGATEWAY_URL", "")


def merge_config(
    *,
    default_config: dict,
    file_path: str | None = None,
    inline_json: str | None = None,
) -> dict:
    config = copy.deepcopy(default_config)

    if file_path:
        path = Path(file_path)
        if path.suffix in (".yaml", ".yml"):
            with open(path) as f:
                config.update(yaml.safe_load(f))
        elif path.suffix == ".json":
            with open(path) as f:
                config.update(json.load(f))

    if inline_json:
        config.update(json.loads(inline_json))

    return config


def get_srcs_dsts_from_crawlers_configs(operators: list) -> dict:
    new_config = {"srcs": set[str](), "dsts": set[str]()}
    crawler_configs = []
    for operator in operators:
        crawler_configs.append(
            importlib.import_module(f"flights.crawlers.{operator}").CONFIG
        )

    for config in crawler_configs:
        for comb in config["src_dsts"]:
            new_config["srcs"].update(comb["srcs"])
            new_config["dsts"].update(comb["dsts"])

    return {"srcs": list(new_config["srcs"]), "dsts": list(new_config["dsts"])}
