from pathlib import Path
import os
import json
import yaml
import copy

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(os.environ.get("FLIGHTS_DATA_DIR", PROJECT_ROOT / "data"))


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
