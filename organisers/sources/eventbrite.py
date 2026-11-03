"""Eventbrite Australia.

The city listing page carries a schema.org ItemList of events (no organiser),
so we open each event page once and read its `organizer` block.
"""
from __future__ import annotations

from ..fetch import get, json_ld
from ..models import Sighting
from ..states import normalise_state

LIST_URL = "https://www.eventbrite.com.au/d/australia--{city}/events/?page={page}"


def _event_urls(city: str, pages: int) -> list[tuple[str, dict]]:
    seen, out = set(), []
    for page in range(1, pages + 1):
        for block in json_ld(get(LIST_URL.format(city=city.lower().replace(" ", "-"), page=page))):
            if block.get("@type") != "ItemList":
                continue
            for el in block.get("itemListElement", []):
                ev = el.get("item", {})
                url = ev.get("url", "").split("?")[0]
                if url and url not in seen:
                    seen.add(url)
                    out.append((url, ev))
    return out


def scrape(city: str, limit: int = 40) -> list[Sighting]:
    sightings = []
    for url, listed in _event_urls(city, pages=max(1, limit // 20 + 1))[:limit]:
        try:
            blocks = json_ld(get(url))
        except Exception as exc:  # one dead page shouldn't stop the run
            print(f"  eventbrite: skipped {url} ({exc})")
            continue
        event = next((b for b in blocks if isinstance(b.get("organizer"), dict)), None)
        if not event:
            continue
        org = event["organizer"]
        loc = event.get("location") or listed.get("location") or {}
        addr = loc.get("address") or {}
        sightings.append(
            Sighting(
                source="eventbrite",
                organiser_name=org.get("name", ""),
                organiser_url=org.get("url", ""),
                event_name=event.get("name", ""),
                event_url=url,
                event_date=(event.get("startDate") or listed.get("startDate") or "")[:10],
                city=addr.get("addressLocality", "") if isinstance(addr, dict) else "",
                region=normalise_state(addr.get("addressRegion", "")) if isinstance(addr, dict) else "",
                website=org.get("sameAs", "") if isinstance(org.get("sameAs"), str) else "",
                online="Online" in str(event.get("eventAttendanceMode", "")),
            )
        )
    return sightings
