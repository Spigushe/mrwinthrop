"""Discord Bot"""
import logging
import os
import io
import random
import unidecode
import datetime
from dotenv import load_dotenv

import discord

from krcg import vtes
from krcg import twda
from krcg import analyzer
from krcg_cli.subcommands import _utils

logger = logging.getLogger()
logging.basicConfig(format="[%(levelname)7s] %(message)s")
client = discord.Client()


def unpack(str):
    return str.split("|") if "|" in str else [str]


def normalize(s):
    """Normalize a string for indexing: unidecode and lowercase"""
    if not isinstance(s, str):
        return s
    return unidecode.unidecode(s).lower().strip()


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


#: Functions to deal with commands
def fn_build(message: str, args: list) -> dict:
    """Build command

    Args:
        message containing list of cards

    Returns:
        Keyword args for the discord channel.send() function
    """
    # Getting all cards in args
    try:
        cards = unpack(message)
        cards = [vtes.VTES[name] for name in cards]
    except KeyError as e:
        return {"content": f"Card not found: {e.args[0]}"}

    # Generating output file
    try:
        deck_list = analyzer.Analyzer(list(twda.TWDA.values())).build_deck(*cards)
        deck_name = message + ".txt"
        deck_file = io.StringIO(deck_list.to_txt())
    except analyzer.AnalysisError:
        return {"content": "No example in TWDA"}

    # Returning file to dicord
    return {
        "content": deck_list.to_vdb(),
        "file": discord.File(fp=deck_file, filename=deck_name),
    }


def fn_affinity(message: str, args: list) -> dict:
    """Affinity command

    Args:
        message containing list of cards

    Returns:
        Keyword args for the discord channel.send() function
    """
    # Getting all cards in args
    try:
        cards = unpack(message)
        cards = [vtes.VTES[name] for name in cards]
    except KeyError as e:
        return {"content": f"Card not found: {e.args[0]}"}

    # Getting candidates from TWDA
    try:
        A = analyzer.Analyzer(list(twda.TWDA.values()))
        A.refresh(*cards, similarity=1)
        candidates = A.candidates(*cards, spoiler_multiplier=1.5)
    except analyzer.AnalysisError:
        return {"content": "No example in TWDA"}

    # Too few example
    if len(A.examples) < 4:
        str = "Too few example in TWDA\n"
        if len(A.examples) > 0:
            str = (
                str
                + "To see them:\n\tkrcg deck "
                + " ".join('"' + card.name + '"' for card in cards)
            )
        return {"content": str}

    # Full answer
    str = ""
    i = 0
    for card, score in candidates:
        i = i + 1
        if i > 5:
            break
        score = round(score * 100 / len(cards))
        if score < 25:
            break
        str = str + (
            f"{card.name:<30} (in {score:.0f}% of decks, typically "
            f"{_utils.typical_copies(A, card)})\n"
        )
    card_names = ""
    for card in cards:
        card_names = card_names + card.name + ", "
    return {"content": "Affinity for " + card_names[:-2] + "```" + str + "```"}


def fn_top(message: str, args: list) -> dict:
    """Top command

    Args:
        message containing list of cards

    Returns:
        Keyword args for the discord channel.send() function
    """
    return {
        "content": "List of arguments: "
        + ",".join([(str(a["arg"]) + " " + str(a["content"])) for a in args])
    }


def fn_deck(message: str, args: list) -> dict:
    """Deck command

    Args:
        message containing list of cards

    Returns:
        Keyword args for the discord channel.send() function
    """
    decks = list(twda.TWDA.values())
    # Filtering
    if args["date_from"]:
        decks = [d for d in decks if d.date >= args["date_from"]]
    if args["date_to"]:
        decks = [d for d in decks if d.date < args["date_to"]]
    if args["players"]:
        decks = [d for d in decks if d.players_count >= args["players"]]
    # deck_ids
    deck_ids = [i for i in unpack(args["deck"]) if i in twda.TWDA]
    if deck_ids:
        decks = [d for d in decks if d.id in deck_ids]
    # cards
    cards = [vtes.VTES[c] for c in unpack(args["card"]) if c in vtes.VTES]
    if cards:
        decks = [d for d in decks if (cards and all(c in d for c in cards))]
    # authors
    authors = [
        normalize(a)
        for a in unpack(args["author"])
        if normalize(a) in twda.TWDA.by_author
    ]
    if authors:
        decks = [
            d
            for d in decks
            if normalize(d.player) in authors or normalize(d.author) in authors
        ]
    # Preparing output
    if len(decks) == 1:
        full = True
    else:
        full = False
        output = f"-- {len(decks)} decks --\n"

    for d in sorted(decks, key=lambda a: a.date):
        if full:
            output = (
                f"[{d.id:<15}]===================================================\n"
            )
            output = output + d.to_vdb()
            deck_file = io.StringIO(d.to_txt())
            # Returning file to dicord
            return {
                "content": output,
                "file": discord.File(fp=deck_file, filename=d.id),
            }
        else:
            output = output + f"[{d.id}] {d.name}\n"
            if len(output) > 500:
                output = output + "..."
                break

    if not full:
        return {"content": "```" + output + "```"}


def fn_seats(message: str, args: list) -> dict:
    """Seats command

    Args:
        message containing list of players

    Returns:
        Keyword args for the discord channel.send() function
    """
    players = unpack(message)
    seats = []
    while len(players) > 0:
        seat = random.randint(0, len(players) - 1)
        player = players.pop(seat)
        if " " in player[len(player) - 1]:
            player = player[:-1]
        seats.append(player)
    return {"content": " > ".join(seats)}


def fn_help(message: str, args: list) -> dict:
    """Help command

    Args:
        message containing list of players

    Returns:
        Keyword args for the discord channel.send() function
    """
    # message = (message or " ").lower()
    message = message.lower()
    # General helper
    if message.replace(" ", "") == "":
        # Getting max_size of command names
        max_size = max(len(c["name"]) for c in COMMANDS)
        # Building str
        str = "List of commands:\n"
        # List
        for c in COMMANDS:
            if "display" in c.keys() and c["display"] == "no":
                continue

            str = str + shorten(f"  {c['name']:<{max_size}} {c['brief']}") + "\n"
        # Footer
        str = str + "\nType mrw help command for more info on a command."
        return {"content": "```" + str + "```"}

    # Command helper
    if message in [c["name"] for c in COMMANDS]:
        for c in COMMANDS:
            if message != c["name"]:
                continue
            # Building str
            str = "mrw {0} {1}\n\n".format(c["name"], c["usage"])
            # Adding detailed explanation
            str = str + f"{c['help']}\n\n"
            # Adding args
            if "arguments" in c.keys():
                str = str + "List of arguments:\n"
                max_size = max(len(a["name"]) for a in c["arguments"])
                for a in c["arguments"]:
                    str = str + shorten(f"  {a['name']:<{max_size}} {a['doc']}") + "\n"

            return {"content": "```" + str + "```"}


#: Arguments for detailed commands
VTES_ARGS = [
    {
        "name": "discipline",
        "type": str,
        "doc": "Filter by discipline ({})".format(
            ",".join(vtes.VTES.search_dimensions["discipline"])
        ),
    },
    {
        "name": "clan",
        "type": str,
        "doc": "Filter by clan ({})".format(
            ",".join(vtes.VTES.search_dimensions["clan"])
        ),
    },
    {
        "name": "type",
        "type": str,
        "doc": "Filter by card type ({})".format(
            ",".join(vtes.VTES.search_dimensions["type"])
        ),
    },
    {
        "name": "group",
        "type": int,
        "doc": "Filter by grouping ({})".format(
            ",".join(map(str, vtes.VTES.search_dimensions["group"]))
        ),
    },
    {
        "name": "bonus",
        "type": str,
        "doc": "Filter by bonus ({})".format(
            ",".join(vtes.VTES.search_dimensions["bonus"])
        ),
    },
    {
        "name": "text",
        "type": str,
        "doc": "Filter by text (including name and flavor text)",
    },
    {
        "name": "trait",
        "type": str,
        "doc": "Filter by trait ({})".format(
            ",".join(vtes.VTES.search_dimensions["trait"])
        ),
    },
    {
        "name": "capacity",
        "type": str,
        "doc": "Filter by capacity ({})".format(
            ",".join(map(str, vtes.VTES.search_dimensions["capacity"]))
        ),
    },
    {"name": "set", "type": str, "doc": "Filter by set"},
    {
        "name": "sect",
        "type": str,
        "doc": "Filter by sect ({})".format(
            ",".join(vtes.VTES.search_dimensions["sect"])
        ),
    },
    {
        "name": "title",
        "type": str,
        "doc": "Filter by title ({})".format(
            ",".join(vtes.VTES.search_dimensions["title"])
        ),
    },
    {
        "name": "city",
        "type": str,
        "doc": "Filter by city",
    },
    {
        "name": "rarity",
        "type": str,
        "doc": "Filter by rarity ({})".format(
            ",".join(vtes.VTES.search_dimensions["rarity"])
        ),
    },
    {
        "name": "precon",
        "type": str,
        "doc": "Filter by preconstructed starter",
    },
    {
        "name": "artist",
        "type": str,
        "doc": "Filter by artist",
    },
    {
        "name": "exclude",
        "type": str,
        "doc": "Exclude given types ({})".format(
            ",".join(vtes.VTES.search_dimensions["type"])
        ),
    },
]
TWDA_ARGS = [
    {
        "name": "card",
        "type": str,
        "doc": "Filter by card names: 'Fame|Carrion Crows'",
    },
    {
        "name": "deck",
        "type": str,
        "doc": "TWDA ID of a deck: 2016gncbg",
    },
    {
        "name": "players",
        "type": int,
        "doc": "Minimum number of players",
        "default": 0,
    },
    {
        "name": "date_from",
        "type": "date",
        "doc": "Year (included) for deck searching",
        "default": datetime.date(1994, 1, 1),
    },
    {
        "name": "date_to",
        "type": "date",
        "doc": "Year (excluded) for deck searching",
        "default": datetime.date.today(),
    },
    {
        "name": "author",
        "type": str,
        "doc": "Looking for TWDA by player name: 'Ben peal'",
    },
]

#: Variables needed for interaction with the bot
PREFIXES = ("mr.winthrop ", "winthrop ", "mr.w ", "mrw ")
COMMANDS = (
    {
        "name": "build",
        "help": (
            "Build a deck from any given card(s) based on TWDA, "
            + "takes any number of card names to build a deck sample"
        ),
        "brief": "Build a deck from any given card(s) based on TWDA",
        "usage": "Fame|Carrion Crows",
    },
    {
        "name": "affinity",
        "help": (
            "Display cards affinity (most played together) based on TWDA, "
            + "takes any number of card names to build a deck sample"
        ),
        "brief": "Display cards affinity (most played together)",
        "usage": "Fame|Carrion Crows",
    },
    {
        "name": "top",
        "help": (
            "Display top cards (most played together) based on TWDA, "
            + "take any number of arguments"
        ),
        "brief": "Display top cards (most played together)",
        "usage": "clan=!Toreador discipline=aus",
        "arguments": VTES_ARGS,
    },
    {
        "name": "deck",
        "help": (
            "Display a list of TWDA decks from IDs, author names or card names, "
            + "take any number of arguments"
        ),
        "brief": "Display a list of TWDA decks from IDs, author names or card names",
        "usage": "author='Ben Peal'",
        "arguments": TWDA_ARGS,
    },
    {
        "name": "seats",
        "help": "Randomise seating from 1 to 5 players",
        "brief": "Randomise seating",
        "usage": "Player 1 | Player 2 | Player 3 | Player 4 | Player 5",
    },
    {
        "name": "help",
        "display": "no",
    },
)
CALLS = {
    "build": fn_build,
    "affinity": fn_affinity,
    "top": fn_top,
    "deck": fn_deck,
    "seats": fn_seats,
    "help": fn_help,
}

load_dotenv()


@client.event
async def on_ready():
    """Login success informative log"""
    logger.info("Logged in as %s", client.user)


@client.event
async def on_message(message: discord.Message):
    """Main message loop"""
    if message.author == client.user:
        return

    if message.content.lower().startswith(PREFIXES):
        command, content, args = handle_message(message.content, PREFIXES, COMMANDS)

        # Execute command
        if command:
            logger.info(
                "Received command %s with instructions %s",
                command["name"] or "none",
                content,
            )
            await message.channel.send(**CALLS[command["name"]](content, args))
        # Default behaviour
        else:
            logger.info(
                "Received no command with instructions %s",
                content,
            )
            await message.reply("Here's a cup of fresh blood, sir/madam")


def handle_message(message: str, prefixes: tuple, commands: tuple):
    """Function that removes start of message

    Args:
        message: The message received, with prefix

    Returns:
        Two strings: command and instructions
    """
    # Check for prefix
    for p in prefixes:
        if message.lower().startswith(p):
            message = message[len(p) :]
            break
    # Check for command
    command = None
    for c in commands:
        if message.lower().startswith(c["name"]):
            command = c
            message = message[len(c["name"]) + 1 :]
            break
    # Check for arguments
    args = {}
    if command and "arguments" in command.keys():
        look_args = message
        arg_presence = True
        while arg_presence:
            arg_presence = False
            look_args = look_args.strip()
            for a in command["arguments"]:
                test = look_args.split("=", 1)[0]
                if test.lower() == a["name"]:
                    # Get value of arg
                    arg = look_args[len(test) + 1 :].split("=", 1)[0]
                    if "=" in look_args[len(test) + 1 :]:
                        # There is a need to remove the next argument key
                        arg = arg[: (len(last_word(arg)) + 1) * -1]
                    # Check type
                    if a["type"] == "date":
                        arg = datetime.date(int(arg), 1, 1)
                    elif not isinstance(arg, a["type"]):
                        arg = a["type"](arg)  # Convert to chosen type
                    # Add to list of args
                    args[test] = arg
                    # Updating string
                    look_args = look_args[len(test) + len(str(arg)) + 1 :]
                    arg_presence = True
        # Defaulting missing arguments
        for a in command["arguments"]:
            if a["name"] not in args.keys():
                if "default" in a.keys():
                    args[a["name"]] = a["default"]
                else:
                    args[a["name"]] = a["type"]("")

    return command, message, args


def main():
    """Entrypoint for the Discord Bot."""
    logger.setLevel(logging.INFO)
    # use latest card texts
    vtes.VTES.load()
    # use latest TWDA entries
    twda.TWDA.load()
    client.run(os.getenv("DISCORD_TOKEN"))
    # reset log level so as to not mess up tests
    logger.setLevel(logging.NOTSET)
