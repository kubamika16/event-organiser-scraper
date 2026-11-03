import unittest

from organisers.dedupe import domain, merge, normalise
from organisers.models import Sighting
from organisers.states import normalise_state


def s(source, name, url, region="NSW", website="", date="2026-11-10"):
    return Sighting(source=source, organiser_name=name, organiser_url="", event_name="x",
                    event_url=url, event_date=date, region=region, website=website)


class DedupeTests(unittest.TestCase):
    def test_normalise_drops_company_noise(self):
        self.assertEqual(normalise("The Sydney Wine Club Pty Ltd."), "sydney wine club")

    def test_platform_domains_are_not_websites(self):
        self.assertEqual(domain("https://www.eventbrite.com.au/o/abc"), "")
        self.assertEqual(domain("https://www.winefest.com.au/about"), "winefest.com.au")

    def test_same_name_across_sources_merges(self):
        orgs = merge([s("eventbrite", "Sydney Wine Club", "e1"), s("meetup", "sydney wine club inc", "m1")])
        self.assertEqual(len(orgs), 1)
        self.assertEqual(orgs[0].sources, {"eventbrite", "meetup"})
        self.assertEqual(orgs[0].event_count, 2)

    def test_same_website_merges_even_with_different_names(self):
        orgs = merge([s("eventbrite", "WineFest", "e1", website="https://winefest.com.au"),
                      s("meetup", "Sydney Wine Festival Crew", "m1", website="winefest.com.au")])
        self.assertEqual(len(orgs), 1)

    def test_close_typo_merges_in_same_state(self):
        orgs = merge([s("eventbrite", "Bondi Run Club", "e1"), s("meetup", "Bondi Runs Club", "m1")])
        self.assertEqual(len(orgs), 1)

    def test_close_name_in_other_state_stays_separate(self):
        orgs = merge([s("eventbrite", "Bondi Run Club", "e1", region="NSW"),
                      s("meetup", "Bondi Runs Club", "m1", region="VIC")])
        self.assertEqual(len(orgs), 2)

    def test_same_event_twice_counts_once(self):
        orgs = merge([s("meetup", "Bondi Run Club", "m1"), s("meetup", "Bondi Run Club", "m1")])
        self.assertEqual(orgs[0].event_count, 1)

    def test_next_and_last_event(self):
        orgs = merge([s("meetup", "A Club", "m1", date="2026-12-01"), s("meetup", "A Club", "m2", date="2026-11-05")])
        self.assertEqual((orgs[0].next_event, orgs[0].last_event), ("2026-11-05", "2026-12-01"))


class StateTests(unittest.TestCase):
    def test_state_spellings(self):
        for raw in ["NS", "nsw", "New South Wales"]:
            self.assertEqual(normalise_state(raw), "NSW")
        self.assertEqual(normalise_state(""), "")


if __name__ == "__main__":
    unittest.main()
