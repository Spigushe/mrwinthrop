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
	if args["date_from"]:
		decks = [d for d in decks if d.date >= args["date_from"]]
	if args["date_to"]:
		decks = [d for d in decks if d.date < args["date_to"]]
	if args["players"]:
		decks = [d for d in decks if d.players_count >= args["players"]]
	return decks


def to_vdb(deck,name: str = "New KRCG deck"):
	link = f"https://vdb.smeea.casa/decks?name={name}&author=Mr.Winthrop#"
	for card, count in deck.cards(lambda c: c.crypt):
		link = link + str(card.id) + "=" + str(count) + ";"
	for card, count in deck.cards(lambda c: c.library):
		link = link + str(card.id) + "=" + str(count) + ";"
	return link[:-1]
