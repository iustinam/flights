import argparse
import importlib
import logging

from flights.config import merge_config


def main() -> None:
    global_parser = argparse.ArgumentParser(add_help=False)

    global_parser.add_argument(
        "--log-level",
        default="INFO",
        choices=list(logging.getLevelNamesMapping().keys()),
    )
    global_args, remaining = global_parser.parse_known_args()
    logging.basicConfig(
        level=getattr(logging, global_args.log_level.upper()),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(prog="flights", parents=[global_parser])
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---- crawl command ----
    crawl_parser = subparsers.add_parser("crawl")
    crawl_parser.add_argument(
        "provider",
        choices=["rair", "wair"],
        help="Which crawler to run"
    )
    crawl_parser.add_argument("--config", help="Path to config file")
    crawl_parser.add_argument("--config-json", help="Inline JSON config")

    # ---- report command ----
    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("--config", help="Path to config file")
    report_parser.add_argument("--config-json", help="Inline JSON config")

    # ---- parse args and load config ----
    args = parser.parse_args(remaining)

    if args.command == "crawl":
        module = importlib.import_module(
            f"flights.crawlers.{args.provider}.crawl")
    elif args.command == "report":
        module = importlib.import_module(f"flights.reporting.report")

    config = merge_config(
        default_config=module.CONFIG,
        file_path=getattr(args, "config", None),
        inline_json=getattr(args, "config_json", None),
    )
    module.run(config)


if __name__ == "__main__":
    main()
