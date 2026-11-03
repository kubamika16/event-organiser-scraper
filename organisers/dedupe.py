"""Merge sightings of the same organiser across sources.

Two sightings are the same organiser when any of these is true:
1. they share the organiser's own website domain, or
2. their normalised names are equal, or
3. their normalised names are very close (typos, "Sydney" suffixes, "Inc." etc.)
   AND they were seen in the same state (stops "Yoga Club" in NSW merging with VIC).
"""
from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher
from urllib.parse import urlparse

from .models import Organiser, Sighting

# Words that say nothing about WHO the organiser is.
NOISE = {
    "pty", "ltd", "limited", "inc", "incorporated", "co", "company", "the",
    "group", "events", "event", "presents", "official", "au", "australia",
    "and", "&",
}
# Big ticketing/social domains are not the organiser's own site.
PLATFORM_DOMAINS = {
    "eventbrite.com", "eventbrite.com.au", "meetup.com", "facebook.com",
    "instagram.com", "humanitix.com", "trybooking.com", "linktr.ee",
}
FUZZY_THRESHOLD = 0.9


def normalise(name: str) -> str:
    text = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-z0-9 ]+", " ", text.lower())
    return " ".join(w for w in text.split() if w not in NOISE)


def domain(url: str) -> str:
    if not url:
        return ""
    host = urlparse(url if "//" in url else "//" + url).netloc.lower()
    host = host.removeprefix("www.")
    return "" if host in PLATFORM_DOMAINS else host


def _close(a: str, b: str) -> bool:
    if not a or not b:
        return False
    return SequenceMatcher(None, a, b).ratio() >= FUZZY_THRESHOLD


def merge(sightings: list[Sighting]) -> list[Organiser]:
    organisers: list[Organiser] = []
    by_domain: dict[str, Organiser] = {}
    by_name: dict[str, Organiser] = {}

    for s in sightings:
        key = normalise(s.organiser_name)
        if not key:
            continue
        dom = domain(s.website)

        match = by_domain.get(dom) if dom else None
        match = match or by_name.get(key)
        if match is None:
            for org in organisers:
                same_state = not s.region or not org.regions or s.region in org.regions
                if same_state and _close(key, org.key):
                    match = org
                    break

        if match is None:
            match = Organiser(name=s.organiser_name.strip(), key=key)
            organisers.append(match)

        match.sources.add(s.source)
        if s.organiser_url:
            match.profile_urls.add(s.organiser_url)
        if dom:
            match.websites.add(dom)
            by_domain[dom] = match
        if s.city:
            match.cities.add(s.city)
        if s.region:
            match.regions.add(s.region)
        if s.event_url not in match.events:
            match.events[s.event_url] = s.event_date
            match.online_events += int(s.online)
        by_name[key] = match

    return organisers
