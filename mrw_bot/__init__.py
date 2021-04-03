"""Discord Bot"""
import asyncio
import collections
import datetime
import os
import re
import io
import urllib.parse

from dotenv import load_dotenv
load_dotenv()

import discord
from discord.ext import commands
"""
if intents become necessary at some point:
	intents = discord.Intents.all()
	bot = commands.Bot(command_prefix=commands.when_mentioned_or('mrw '), intents=intents)
"""
bot = commands.Bot(command_prefix=commands.when_mentioned_or('mrw '))

from krcg import logging
logger = logging.logger

from krcg import analyzer
from krcg import vtes
from krcg import twda
# Initialize VTES and TWDA
vtes.VTES.load()
twda.TWDA.load()


@bot.listen()
async def on_ready():
	"""Login success informative log"""
	logger.info("Logged in as {}", bot.user)


"""Config by commands"""
@bot.command(
	name="build",
	#aliases=["builds"],
	help="Build a deck from any given card(s) based on TWDA, takes any number of card names to build a deck sample",
	brief="Build a deck from any given card(s) based on TWDA",
	usage="Fame|Carrion Crows",
)
async def msg_build(ctx, *args):
	logger.info("Received instructions {}", ctx.message.content)

	card_list = ctx.message.content[10:]
	cards = card_list.split("|") if "|" in card_list else card_list.split()
	logger.info("Cards: {}", cards)

	decks = list(twda.TWDA.values())
	try:
		cards = [vtes.VTES[name] for name in cards]
	except KeyError as e:
		sys.stderr.write(f"Card not found: {e.args[0]}\n")
		return 1

	# Generating output file
	deck_list = io.StringIO(analyzer.Analyzer(decks).build_deck(*cards).to_txt())
	deck_name = card_list + ".txt"
	# Still needs to generate VDB deck link to replace content="info"
	# Sending file
	await ctx.channel.send(content="info", file=discord.File(fp=deck_list, filename=deck_name))
	# Close object and discard memory buffer
	deck_list.close()


def main():
	"""Entrypoint for the Discord Bot"""
	logger.setLevel(logging.INFO)
	# use latest card texts
	vtes.VTES.load()
	bot.run(os.getenv("DISCORD_TOKEN"))
	# reset log level so as to not mess up tests
	logger.setLevel(logging.NOTSET)
