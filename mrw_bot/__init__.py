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
bot = commands.Bot(
	# Starting with longest strings
	# Doc: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Bot.command_prefix
	command_prefix=commands.when_mentioned_or('mr.winthrop ','winthrop ','mr.w ','mrw '),
	case_insensitive=True
)

from krcg import logging
from krcg import analyzer
from krcg import vtes
from krcg import twda
logger = logging.logger


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

	try:
		card_list = ctx.message.content.split("build ",1)[1]
		cards = card_list.split("|") if "|" in card_list else [card_list]
		cards = [vtes.VTES[name] for name in cards]
	except KeyError as e:
		await ctx.message.reply(f"Card not found: {e.args[0]}\n")
		return False

	# Generating output file
	deck_list = analyzer.Analyzer(list(twda.TWDA.values())).build_deck(*cards)
	deck_name = card_list + ".txt"
	deck_file = io.StringIO(deck_list.to_txt())

	# Generating VDB link
	link = "https://vdb.smeea.casa/decks?name=" + re.sub(" ","_",card_list) + "&author=Mr.Winthrop#"
	for card, count in deck_list.cards(lambda c: c.crypt):
		link = link + str(card.id) + "=" + str(count) + ";"
	for card, count in deck_list.cards(lambda c: c.library):
		link = link + str(card.id) + "=" + str(count) + ";"
	link = link[:-1]

	await ctx.channel.send(content=link, file=discord.File(fp=deck_file, filename=deck_name))
	deck_file.close()


def main():
	"""Entrypoint for the Discord Bot"""
	logger.setLevel(logging.INFO)
	# use latest card texts
	vtes.VTES.load()
	twda.TWDA.load()
	bot.run(os.getenv("DISCORD_TOKEN"))
	# reset log level so as to not mess up tests
	logger.setLevel(logging.NOTSET)
