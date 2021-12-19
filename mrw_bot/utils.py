import unidecode
from krcg import twda


def unpack(str):
    return str.split("|") if "|" in str else [str]


def normalize(s):
    """Normalize a string for indexing: unidecode and lowercase."""
    if not isinstance(s, str):
        return s
    return unidecode.unidecode(s).lower().strip()


def filter_twda(args):
    decks = list(twda.TWDA.values())
    date_from = args.pop("date_from", None)
    if date_from:
        decks = [d for d in decks if d.date >= date_from]
    date_to = args.pop("date_to", None)
    if date_to:
        decks = [d for d in decks if d.date < date_to]
    players = args.pop("players", None)
    if players:
        decks = [d for d in decks if (d.players_count or 0) >= players]
    return decks
