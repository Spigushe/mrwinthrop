import unidecode
from krcg import twda


def unpack(s):
    if not isinstance(s, str):
        return s
    return s.split("|") if "|" in s else [s]


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


def shorten(str):
    if len(str) > 80:
        return str[:77] + "..."
    return str


def last_word(str) -> str:
    # taking empty string
    new = ""
    # calculating length of string
    length = len(str)
    # traversing from last
    for i in range(length - 1, 0, -1):
        # if space is occured then return
        if str[i] == " ":
            # return reverse of newstring
            return new[::-1]
        else:
            new = new + str[i]
    return new
