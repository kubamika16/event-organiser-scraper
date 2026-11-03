"""Sources spell Australian states differently ("NS", "New South Wales", "nsw")."""

STATES = {
    "NSW": ["nsw", "ns", "new south wales"],
    "VIC": ["vic", "victoria"],
    "QLD": ["qld", "queensland"],
    "WA": ["wa", "western australia"],
    "SA": ["sa", "south australia"],
    "TAS": ["tas", "tasmania"],
    "ACT": ["act", "australian capital territory"],
    "NT": ["nt", "northern territory"],
}
_LOOKUP = {alias: code for code, aliases in STATES.items() for alias in aliases}


def normalise_state(value: str) -> str:
    v = (value or "").strip().lower().rstrip(".")
    return _LOOKUP.get(v, value.strip().upper() if v else "")
