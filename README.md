# Event organiser scraper (example)

A small scraper written from scratch, with no Apify and no paid data tools. It finds **event organisers** in an Australian city from more than one source and **merges duplicates**, so each organiser shows up once with every event it runs.

It is the base of phase 1 (lead sourcing): the web page where your team picks the region, organiser type and source would call this same code.

## What it does

1. **Pulls events from each source.** Right now that's Eventbrite AU and Meetup. Both publish schema.org event data, so the scraper reads that data and doesn't depend on page layout.
2. **Reads the organiser behind each event.** It saves the organiser's name, profile link, city, state and event date.
3. **Dedupes across sources.** Two records count as the same organiser when they share the organiser's own website domain, have the same name once filler words are removed (`Pty Ltd`, `Inc`, `The`, `Events`...), or have nearly the same name *in the same state*.
4. **Ranks the results.** Organisers found on more sources and running more events come first. For each one it saves its next and last event date, which shows how active it is.
5. **Saves a CSV and a JSON file** to `output/`.

It is polite to the sites: requests are spaced out, it retries with back-off and it keeps a 12 h on-disk cache, so a re-run doesn't hit the sites again.

## Run it

Python 3.10+, no dependencies.

```bash
python -m organisers --city sydney --limit 30
python -m organisers --city melbourne --sources meetup
python -m unittest discover -s tests -t .
```

Live run, 3 Nov 2026:

```
eventbrite: 25 events with an organiser
meetup: 12 events with an organiser

37 sightings -> 28 unique organisers
```

## Layout

```
organisers/
  sources/       one file per source, each exposes scrape(city, limit)
  fetch.py       shared HTTP: user agent, delay, retry, cache, JSON-LD reader
  dedupe.py      name normalising + website/name/fuzzy matching
  states.py      "NS" / "nsw" / "New South Wales" -> NSW
  __main__.py    command line + CSV/JSON export
tests/           dedupe and state tests
```

## Adding a source

To add a club directory, venue calendar or school site, write one more module in `organisers/sources/` that returns a list of `Sighting` objects, then add it to `SOURCES`. Dedupe, ranking and export work for it with no other changes.
