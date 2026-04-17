import argparse
from pathlib import Path

import yaml


def _slo_rules(service: str, slo: dict) -> dict:
    name = slo["name"]
    objective = float(slo["objective"])
    good = slo["sli"]["good"]
    total = slo["sli"]["total"]
    threshold = 1.0 - objective

    error_ratio_expr = f"(1 - (({good}) / ({total})))"
    page_expr = f"{error_ratio_expr} > ({threshold} * 4)"
    ticket_expr = f"{error_ratio_expr} > ({threshold} * 2)"

    labels = {"service": service, "slo": name}
    labels.update(slo.get("labels", {}))

    return {
        "name": f"slo_{service}_{name}",
        "rules": [
            {
                "alert": "SLOBurnRatePage",
                "expr": page_expr,
                "for": "5m",
                "labels": {"severity": "page", **labels},
                "annotations": {
                    "summary": f"SLO burn rate (page): {service} {name}",
                    "description": f"Error ratio is burning the SLO budget too fast for {service}/{name}.",
                },
            },
            {
                "alert": "SLOBurnRateTicket",
                "expr": ticket_expr,
                "for": "30m",
                "labels": {"severity": "ticket", **labels},
                "annotations": {
                    "summary": f"SLO burn rate (ticket): {service} {name}",
                    "description": f"Error ratio indicates elevated error budget burn for {service}/{name}.",
                },
            },
        ],
    }


def generate(in_path: Path, out_path: Path) -> None:
    data = yaml.safe_load(in_path.read_text(encoding="utf-8"))
    service = data.get("service", "service")
    slos = data.get("slos", [])

    groups = []
    for slo in slos:
        groups.append(_slo_rules(service, slo))

    out = {"groups": groups}
    out_path.write_text(yaml.safe_dump(out, sort_keys=False), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(prog="sloctl")
    sub = parser.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate")
    g.add_argument("--in", dest="in_path", required=True)
    g.add_argument("--out", dest="out_path", required=True)

    args = parser.parse_args()

    if args.cmd == "generate":
        generate(Path(args.in_path), Path(args.out_path))


if __name__ == "__main__":
    main()
