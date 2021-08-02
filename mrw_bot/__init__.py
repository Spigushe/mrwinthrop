"""Discord Bot"""
import asyncio
import collections
import datetime
import os
import re
import io
import urllib.parse
import random

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
	command_prefix=commands.when_mentioned_or('mr.winthrop ','winthrop ','mr.w ','mrw '),
	case_insensitive=True
)

from krcg import analyzer
from krcg import vtes
from krcg import twda
from krcg_cli.subcommands import _utils

import logging
logger = logging.getLogger()
logging.basicConfig(format="[%(levelname)7s] %(message)s")

import discord_argparse
from . import parser
bot.help_command = parser.MyHelpCommand()

from . import utils as _u

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
		cards = _u.unpack(card_list)
		cards = [vtes.VTES[name] for name in cards]
	except KeyError as e:
		await ctx.message.reply(f"Card not found: {e.args[0]}\n")
		return False

	# Generating output file
	try:
		deck_list = analyzer.Analyzer(list(twda.TWDA.values())).build_deck(*cards)
		deck_name = card_list + ".txt"
		deck_file = io.StringIO(deck_list.to_txt())
	except analyzer.AnalysisError as e:
		await ctx.message.reply(f"No example in TWDA")
		return False

	await ctx.channel.send(content=deck_list.to_vdb(), file=discord.File(fp=deck_file, filename=deck_name))
	deck_file.close()


@bot.command(
	name="affinity",
	#aliases=["affi"],
	help="Display cards affinity (most played together) based on TWDA, takes any number of card names to build a deck sample",
	brief="Display cards affinity (most played together)",
	usage="Fame|Carrion Crows",
)
async def msg_affinity(ctx, *args):
	logger.info("Received instructions %s", ctx.message.content)

	try:
		card_list = ctx.message.content.split("affinity ",1)[1]
		cards = _u.unpack(card_list)
		cards = [vtes.VTES[name] for name in cards]
	except KeyError as e:
		await ctx.message.reply(f"Card not found: {e.args[0]}")
		return False

	try:
		A = analyzer.Analyzer(list(twda.TWDA.values()))
		A.refresh(*cards, similarity=1)
		candidates = A.candidates(*cards, spoiler_multiplier=1.5)
	except analyzer.AnalysisError as e:
		await ctx.message.reply(f"No example in TWDA")
		return False

	if len(A.examples) < 4:
		str = "Too few example in TWDA\n"
		if len(A.examples) > 0:
			str = str + "To see them:\n\tkrcg deck " + " ".join('"' + card.name + '"' for card in cards)
		await ctx.send(str)
		return True

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
	await ctx.send("Affinity for " + card_names[:-2] + "```" + str + "```")


@bot.command(
	name="top",
	#aliases=["best"],
	help="Display top cards (most played together) based on TWDA, take any number of arguments",
	brief="Display top cards (most played together)",
	usage="clan=!Toreador discipline=aus",
)
async def msg_top(ctx, *, args: parser.vtes=parser.vtes.defaults()):
	logger.info("Received instructions {}", ctx.message.content)
	await ctx.send("I'm sorry dear Metuselah, I'm still working on it, it should be available soon")


@bot.command(
	name="seats",
	#aliases=["random"],
	help="Randomise seating",
	brief="Display top cards (most played together)",
	usage="Player 1 | Player 2 | Player 3 | Player 4 | Player 5",
)
async def msg_top(ctx, args):
	logger.info("Received instructions {}", ctx.message.content)
	players = _u.unpack(ctx.message.content.split("seats ",1)[1])
	seats = []
	while len(players) > 0:
		seat = random.randint(0,len(players)-1)
		player = players.pop(seat)
		if " " in player[len(player)-1]:
			player = player[:-1]
		seats.append(player)
	await ctx.send(" > ".join(seats))


@bot.command(
	name="deck",
	#aliases=["twda"],
	help="Display a list of TWDA decks from IDs, author names or card names, take any number of arguments",
	brief="Display a list of TWDA decks from IDs, author names or card names",
	usage="author='Ben Peal'",
)
async def msg_deck(ctx, *, args: parser.twda=parser.twda.defaults()):
	logger.info("Received instructions {}", ctx.message.content)

	# deck_ids
	deck_ids = _u.unpack(args["deck"])
	deck_ids = [i for i in deck_ids if i in twda.TWDA]

	# cards
	cards = _u.unpack(args["card"])
	cards = [vtes.VTES[c] for c in cards if c in vtes.VTES]

	# authors
	authors = _u.unpack(args["author"])
	authors = [_u.normalize(a) for a in authors if _u.normalize(a) in twda.TWDA.by_author]

	decks = _u.filter_twda(args)
	if deck_ids or cards or authors:
		decks = [
			d
			for d in decks
			if d.id in deck_ids
			or (cards and all(c in d for c in cards))
			or _u.normalize(d.player) in authors
			or _u.normalize(d.author) in authors
		]

	if len(decks) == 1:
		full = True
	else:
		full = False
		output = f"-- {len(decks)} decks --\n"


	for d in sorted(decks, key=lambda a: a.date):
		if full:
			output = f"[{d.id:<15}]===================================================\n"
			output = output +_u.to_vdb(d,d.id)
			deck_file = io.StringIO(d.to_txt())
			await ctx.channel.send(content=output, file=discord.File(fp=deck_file, filename=d.id))
			deck_file.close()
		else:
			output = output + f"[{d.id}] {d.name}\n"
			if len(output) > 500:
				output = output + "..."
				break

	if not full:
		await ctx.send("```"+output+"```")



def main():
	"""Entrypoint for the Discord Bot"""
	logger.setLevel(logging.INFO)
	# use latest card texts
	vtes.VTES.load()
	twda.TWDA.load()
	bot.run(os.getenv("DISCORD_TOKEN"))
	# reset log level so as to not mess up tests
	logger.setLevel(logging.NOTSET)
