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
	command_prefix=commands.when_mentioned_or('mr.winthrop ','winthrop ','mr.w ','mrw '),
	case_insensitive=True
)

from krcg import logging
from krcg import analyzer
from krcg import vtes
from krcg import twda
from krcg_cli.subcommands import _utils
logger = logging.logger

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

	await ctx.channel.send(content=_u.to_vdb(deck_list,re.sub(" ","_",card_list)), file=discord.File(fp=deck_file, filename=deck_name))
	deck_file.close()


@bot.command(
	name="affinity",
	#aliases=["affi"],
	help="Display cards affinity (most played together) based on TWDA, takes any number of card names to build a deck sample",
	brief="Display cards affinity (most played together)",
	usage="Fame|Carrion Crows",
)
async def msg_affinity(ctx, *args):
	logger.info("Received instructions {}", ctx.message.content)

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
async def msg_top(ctx, *, params: parser.parser=parser.parser.defaults()):
	logger.info("Received instructions {}", ctx.message.content)
	await ctx.send("I'm sorry dear Metuselah, I'm still working on it, it should be available soon")
	return True

	"""Here is legacy code that I used to check errors but nothing went well"""

	"""
	await ctx.send("Looking for {a} ?".format(a=", ".join(params.keys())))

	args = {
		k: v
		for k, v in params.items()
		if k
		in {
			"discipline",
			"clan",
			"type",
			"group",
			"exclude",
			"bonus",
			"text",
			"trait",
			"capacity",
			"set",
			"sect",
			"title",
			"city",
			"rarity",
			"precon",
			"artist",
		}
	}

	exclude_type = args.pop("exclude", None)
	if exclude_type:
		args["type"] = list(
			args.get("type", set())
			| (set(TypeChoice.get_choices()) - set(exclude_type))
		)
	args["text"] = " ".join(args.pop("text") or [])
	args = {k: v for k, v in args.items() if v}
	print(vtes.VTES.search(**args))
	"""

	"""
	params = {}

	for arg in args:
		(k,v) = arg.split("=")
		print(f"I think you are looking for {v} in the {k} dimension")
		if k == "clan" and v[0] == "!":
			v = v[1:] + " antitribu"
			print(f"I've changed the value of the {k} dimension to: **{v}**")
		if k not in ['text','city','artist'] and v not in vtes.VTES.search_dimensions[k]:
			print(f"{v} is not a correct parameter of {k}")
		else:
			params[k] = v

	print(params)
	print(vtes.VTES.search(**params))
	"""
	"""
	# case of antitribu marked as "!Clan"
	if "clan" in params.keys():
		if params["clan"][0] == "!":
			params["clan"] = params["clan"][1:] + " antitribu"

	exclude_type = params.pop("exclude", None)
	if exclude_type:
		params["type"] = list(
			params.get("type", set())
			| (set(vtes.VTES.search_dimensions["type"]) - set(exclude_type))
		)
	#if "text" in params.keys():
		#params["text"] = " ".join(params.pop("text") or [])

	print(params)

	candidates = vtes.VTES.search(**params)
	if not candidates:
		await ctx.send("No result in TWDA")
		return 1
	"""



def main():
	"""Entrypoint for the Discord Bot"""
	logger.setLevel(logging.INFO)
	# use latest card texts
	vtes.VTES.load()
	twda.TWDA.load()
	bot.run(os.getenv("DISCORD_TOKEN"))
	# reset log level so as to not mess up tests
	logger.setLevel(logging.NOTSET)
