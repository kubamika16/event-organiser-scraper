"""Run:  python -m organisers --city sydney --sources eventbrite,meetup --limit 30"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .dedupe import merge
from .sources import SOURCES


def main() -> None:
    p = argparse.ArgumentParser(description="Find event organisers in an Australian city.")
    p.add_argument("--city", default="sydney")
    p.add_argument("--sources", default=",".join(SOURCES), help="comma list: " + ",".join(SOURCES))
    p.add_argument("--limit", type=int, default=30, help="max events per source")
    p.add_argument("--out", default="output")
    p.add_argument("--include-online", action="store_true", help="keep organisers who only run online events")
    args = p.parse_args()

    sightings = []
    for name in args.sources.split(","):
        found = SOURCES[name.strip()](args.city, args.limit)
        print(f"{name}: {len(found)} events with an organiser")
        sightings += found

    organisers = merge(sightings)
    if not args.include_online:
        organisers = [o for o in organisers if o.online_events < o.event_count]
    organisers.sort(key=lambda o: (-len(o.sources), -o.event_count, o.name.lower()))

    out = Path(args.out)
    out.mkdir(exist_ok=True)
    rows = [
        {
            "organiser": o.name,
            "sources": ", ".join(sorted(o.sources)),
            "events_found": o.event_count,
            "next_event": o.next_event,
            "last_event": o.last_event,
            "cities": ", ".join(sorted(o.cities)),
            "state": ", ".join(sorted(o.regions)),
            "website": ", ".join(sorted(o.websites)),
            "profile_urls": " | ".join(sorted(o.profile_urls)),
        }
        for o in organisers
    ]
    stem = f"organisers-{args.city.lower().replace(' ', '-')}"
    with open(out / f"{stem}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["organiser"])
        w.writeheader()
        w.writerows(rows)
    (out / f"{stem}.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n{len(sightings)} sightings -> {len(organisers)} unique organisers")
    print(f"saved {out / stem}.csv and .json")


if __name__ == "__main__":
    main()
