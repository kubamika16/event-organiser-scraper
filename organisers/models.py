from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Sighting:
    """One organiser seen on one event, exactly as a source reported it."""

    source: str              # "eventbrite", "meetup", ...
    organiser_name: str
    organiser_url: str       # the organiser's profile page on that source
    event_name: str
    event_url: str
    event_date: str          # ISO date (YYYY-MM-DD)
    city: str = ""
    region: str = ""         # state, e.g. NSW
    website: str = ""        # organiser's own site, when the source gives it
    online: bool = False


@dataclass
class Organiser:
    """One real-world organiser after merging sightings across sources."""

    name: str
    key: str
    sources: set[str] = field(default_factory=set)
    profile_urls: set[str] = field(default_factory=set)
    websites: set[str] = field(default_factory=set)
    cities: set[str] = field(default_factory=set)
    regions: set[str] = field(default_factory=set)
    events: dict[str, str] = field(default_factory=dict)  # event_url -> date
    online_events: int = 0

    @property
    def event_count(self) -> int:
        return len(self.events)

    @property
    def next_event(self) -> str:
        return min(self.events.values()) if self.events else ""

    @property
    def last_event(self) -> str:
        return max(self.events.values()) if self.events else ""
