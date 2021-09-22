"""Discord Bot"""
import asyncio
import collections
import datetime
import logging
import os
import re
import urllib.parse
from dotenv import load_dotenv

import discord

from krcg import vtes
from krcg import twda

logger = logging.getLogger()
logging.basicConfig(format="[%(levelname)7s] %(message)s")
client = discord.Client()


load_dotenv()


@client.event
async def on_ready():
    """Login success informative log."""
    logger.info("Logged in as %s", client.user)


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
