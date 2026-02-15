from pathlib import Path
import os
import json
import yaml
import copy
import importlib

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.environ.get("FLIGHTS_DATA_DIR", PROJECT_ROOT / "data"))
OPERATORS = ["rair", "wair"]


def merge_config(*, default_config: dict, file_path: str | None = None, inline_json: str | None = None) -> dict:
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
    new_config = {"srcs": set(), "dsts": set()}
    crawler_configs = []
    for operator in operators:
        crawler_configs.append(importlib.import_module(
            f"flights.crawlers.{operator}.crawl").CONFIG)

    for config in crawler_configs:
        for comb in config["src_dsts"]:
            new_config["srcs"].update(comb["srcs"])
            new_config["dsts"].update(comb["dsts"])

    return {"srcs": list(new_config["srcs"]), "dsts": list(new_config["dsts"])}
