import argparse
import csv
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


TEMPLATES_DIR = Path(__file__).parent / "templates"
INCIDENTS_DIR = Path(__file__).parent / "incidents"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def render_template(text: str, values: dict) -> str:
    out = text
    for k, v in values.items():
        out = out.replace(f"{{{{{k}}}}}", str(v))
    return out


def next_incident_id(now: datetime) -> str:
    year = now.year
    INCIDENTS_DIR.mkdir(parents=True, exist_ok=True)
    prefix = f"INC-{year}-"
    max_n = 0
    for p in INCIDENTS_DIR.iterdir():
        if not p.is_dir():
            continue
        name = p.name
        if not name.startswith(prefix):
            continue
        try:
            n = int(name.split("-")[-1])
        except ValueError:
            continue
        max_n = max(max_n, n)
    return f"{prefix}{max_n + 1:04d}"


@dataclass(frozen=True)
class IncidentMeta:
    incident_id: str
    title: str
    severity: str
    created_at: str
    owner: str


def create_incident(title: str, severity: str, owner: str) -> IncidentMeta:
    now = datetime.now(timezone.utc)
    incident_id = next_incident_id(now)
    created_at = now.isoformat().replace("+00:00", "Z")
    meta = IncidentMeta(
        incident_id=incident_id,
        title=title,
        severity=severity,
        created_at=created_at,
        owner=owner,
    )

    out_dir = INCIDENTS_DIR / incident_id
    out_dir.mkdir(parents=True, exist_ok=False)

    values = {
        "INCIDENT_ID": meta.incident_id,
        "TITLE": meta.title,
        "SEVERITY": meta.severity,
        "CREATED_AT": meta.created_at,
        "OWNER": meta.owner,
    }

    incident_md = render_template((TEMPLATES_DIR / "incident.md").read_text(encoding="utf-8"), values)
    postmortem_md = render_template((TEMPLATES_DIR / "postmortem.md").read_text(encoding="utf-8"), values)
    timeline_csv = (TEMPLATES_DIR / "timeline.csv").read_text(encoding="utf-8")

    (out_dir / "incident.md").write_text(incident_md, encoding="utf-8")
    (out_dir / "postmortem.md").write_text(postmortem_md, encoding="utf-8")
    (out_dir / "timeline.csv").write_text(timeline_csv, encoding="utf-8")
    (out_dir / "meta.env").write_text(
        "\n".join(
            [
                f"INCIDENT_ID={meta.incident_id}",
                f"TITLE={meta.title}",
                f"SEVERITY={meta.severity}",
                f"CREATED_AT={meta.created_at}",
                f"OWNER={meta.owner}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    return meta


def add_event(incident_id: str, time_s: str, who: str, what: str) -> None:
    out_dir = INCIDENTS_DIR / incident_id
    if not out_dir.exists():
        raise SystemExit(f"Incident not found: {incident_id}")

    timeline_path = out_dir / "timeline.csv"
    if not timeline_path.exists():
        timeline_path.write_text("time,who,what\n", encoding="utf-8")

    try:
        datetime.fromisoformat(time_s.replace("Z", "+00:00"))
    except ValueError:
        raise SystemExit("Invalid --time. Use ISO-8601, e.g. 2026-04-16T18:12:00Z")

    with timeline_path.open("a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([time_s, who, what])


def main() -> None:
    parser = argparse.ArgumentParser(prog="incidentctl")
    sub = parser.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create")
    c.add_argument("--title", required=True)
    c.add_argument("--sev", required=True, choices=["SEV1", "SEV2", "SEV3", "SEV4"])
    c.add_argument("--owner", default=os.getenv("USER", "on-call"))

    e = sub.add_parser("add-event")
    e.add_argument("--id", required=True, dest="incident_id")
    e.add_argument("--time", required=False, default=utc_now())
    e.add_argument("--who", required=True)
    e.add_argument("--what", required=True)

    args = parser.parse_args()

    if args.cmd == "create":
        meta = create_incident(args.title, args.sev, args.owner)
        print(meta.incident_id)
        return

    if args.cmd == "add-event":
        add_event(args.incident_id, args.time, args.who, args.what)
        return


if __name__ == "__main__":
    main()
