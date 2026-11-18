"""Explicit CLI subcommands; no network access or credentials are needed."""

import argparse
import json
from pathlib import Path

from solar_grid.config import load_config
from solar_grid.pipeline import publish_snapshot, run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build", help="Generate synthetic scenario and audit outputs")
    build.add_argument("--config", type=Path, default=Path("config/default.json"))
    build.add_argument("--output", type=Path, default=Path("artifacts"))
    build.add_argument("--publish-snapshot", action="store_true")
    args = parser.parse_args()
    report = run(load_config(args.config), args.output)
    if args.publish_snapshot:
        publish_snapshot(args.output)
    print(
        json.dumps(
            {
                "rows": report["input_rows"],
                "test": report["forecast"]["test_metrics"],
                "annual_net_savings_eur": report["economics"]["annual_net_savings_eur"],
                "npv_eur": report["economics"]["npv_eur"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
