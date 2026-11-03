"""Meetup.

The public "find events" page already lists each event with its organising
group in schema.org JSON-LD, so one request per city is enough.
"""
from __future__ import annotations

from ..fetch import get, json_ld
from ..models import Sighting
from ..states import normalise_state

FIND_URL = "https://www.meetup.com/find/?location=au--{city}&source=EVENTS"

STATE_BY_CITY = {
    "sydney": "NSW", "melbourne": "VIC", "brisbane": "QLD", "perth": "WA",
    "adelaide": "SA", "hobart": "TAS", "canberra": "ACT", "darwin": "NT",
    "gold coast": "QLD", "newcastle": "NSW",
}


def scrape(city: str, limit: int = 40) -> list[Sighting]:
    html = get(FIND_URL.format(city=city.title().replace(" ", "%20")))
    sightings = []
    for ev in json_ld(html):
        if ev.get("@type") != "Event" or not isinstance(ev.get("organizer"), dict):
            continue
        org = ev["organizer"]
        loc = ev.get("location") or {}
        addr = loc.get("address") or {}
        online = loc.get("@type") == "VirtualLocation"
        raw_region = (addr.get("addressRegion") if isinstance(addr, dict) else "") or ""
        sightings.append(
            Sighting(
                source="meetup",
                organiser_name=org.get("name", ""),
                organiser_url=org.get("url", ""),
                event_name=(ev.get("name") or "").strip(),
                event_url=ev.get("url", ""),
                event_date=(ev.get("startDate") or "")[:10],
                city=(addr.get("addressLocality") if isinstance(addr, dict) else "") or city.title(),
                region=normalise_state(raw_region) or STATE_BY_CITY.get(city.lower(), ""),
                online=online,
            )
        )
    return sightings[:limit]
