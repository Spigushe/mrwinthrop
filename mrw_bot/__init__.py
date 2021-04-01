"""Discord Bot"""
import asyncio
import collections
import datetime
import os
import re
import urllib.parse

from dotenv import load_dotenv
load_dotenv()

import discord
from discord.ext import commands
"""
if intents become necessary at some point:
	intents = discord.Intents.all()
	bot = commands.Bot(command_prefix='mrw', intents=intents)
"""
bot = commands.Bot(command_prefix='mrw ')

from krcg import logging
from krcg import analyzer
from krcg import vtes
from krcg_cli.subcommands import *

logger = logging.logger
client = discord.Client()


@bot.listen()
async def on_ready():
	"""Login success informative log"""
	logger.info("Logged in as {}", bot.user)

"""Config by commands"""
@bot.command(
	name="build",
	aliases=["builds"],
	help="Build a deck from any given cards based on TWDA, takes any number of card names to build a deck sample",
	brief="Build a deck from any given cards based on TWDA",
	usage="mrw build \"Fame\" \"Carrion Crows\"",
)
async def msg_build(ctx, *args):
	logger.info("Received instructions {}", ctx.message.content)
	build.build(args)

def main():
	"""Entrypoint for the Discord Bot"""
	logger.setLevel(logging.INFO)
	# use latest card texts
	vtes.VTES.load()
	bot.run(os.getenv("DISCORD_TOKEN"))
	# reset log level so as to not mess up tests
	logger.setLevel(logging.NOTSET)
