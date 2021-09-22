"""Discord Bot"""
import logging
import os
import io
import random
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


#: Functions to deal with commands
def fn_build(message: str) -> dict:
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


def fn_affinity(message: str) -> dict:
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


def fn_top(message: str) -> dict:
    """Top command

    Args:
        message containing list of cards

    Returns:
        Keyword args for the discord channel.send() function
    """
    return {"content": "I'm working on being better, sir/madam"}


def fn_deck(message: str) -> dict:
    """Deck command

    Args:
        message containing list of cards

    Returns:
        Keyword args for the discord channel.send() function
    """
    return {"content": "I'm working on being better, sir/madam"}


def fn_seats(message: str) -> dict:
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
    },
    {
        "name": "deck",
        "help": (
            "Display a list of TWDA decks from IDs, author names or card names, "
            + "take any number of arguments"
        ),
        "brief": "Display a list of TWDA decks from IDs, author names or card names",
        "usage": "author='Ben Peal'",
    },
    {
        "name": "seats",
        "help": "Randomise seating from 1 to 5 players",
        "brief": "Randomise seating",
        "usage": "Player 1 | Player 2 | Player 3 | Player 4 | Player 5",
    },
)
CALLS = {
    "build": fn_build,
    "affinity": fn_affinity,
    "top": fn_top,
    "deck": fn_deck,
    "seats": fn_seats,
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
        command, content = trim_message(message.content, PREFIXES, COMMANDS)

        # Execute command
        if command:
            logger.info(
                "Received command %s with instructions %s",
                command["name"] or "none",
                content,
            )
            await message.reply(**CALLS[command["name"]](content))
        # Default behaviour
        else:
            logger.info(
                "Received no command with instructions %s",
                content,
            )
            await message.reply("Here's a cup of fresh blood, sir/madam")


def trim_message(message: str, prefixes: tuple, commands: tuple) -> str:
    """Function that removes start of message

    Args:
        message: The message received, with prefix

    Returns:
        Two strings: command and instructions
    """
    message = message.lower()
    # Check for prefix
    for p in prefixes:
        if message.startswith(p):
            message = message[len(p) :]
            break
    # Check for command
    command = None
    for c in commands:
        if message.startswith(c["name"]):
            command = c
            message = message[len(c["name"]) + 1 :]
            break
    return command, message


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
