"""Each source module exposes `scrape(city: str, limit: int) -> list[Sighting]`.

Adding a new source (a club directory, a venue calendar, a school site) means
writing one more module with that function and registering it below.
"""
from . import eventbrite, meetup

SOURCES = {
    "eventbrite": eventbrite.scrape,
    "meetup": meetup.scrape,
}
