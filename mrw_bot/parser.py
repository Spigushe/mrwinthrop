import collections
import json
from discord.ext import commands
from discord_argparse import *
from krcg import vtes

class MyHelpCommand(commands.DefaultHelpCommand):
	async def send_command_help(self, command):
		self.add_command_formatting(command)
		for name, param in command.clean_params.items():
			if isinstance(param.annotation, ArgumentConverter):
				arguments = param.annotation.arguments
				if not arguments:
					continue
				self.paginator.add_line("Arguments:")
				max_size = max(len(name) for name in arguments)

				for name, argument in arguments.items():
					entry = "{0}{1:<{width}} {2}".format(self.indent * " ", name, argument.doc, width=max_size)
					self.paginator.add_line(self.shorten_text(entry))
		self.paginator.close_page()
		await self.send_pages()

class ArgumentConverter(ArgumentConverter):
	def sort(self):
		self.arguments = collections.OrderedDict(sorted(self.arguments.items()))

	def get_args(self):
		return self.arguments.keys()


parser = ArgumentConverter(
	discipline = OptionalArgument(
		str,
		doc="Filter by discipline ({})".format(",".join(vtes.VTES.search_dimensions["discipline"]))
	),
	clan = OptionalArgument(
		str,
		doc="Filter by clan ({})".format(",".join(vtes.VTES.search_dimensions["clan"]))
	),
	type = OptionalArgument(
		str,
		doc="Filter by card type ({})".format(",".join(vtes.VTES.search_dimensions["type"]))
	),
	group = OptionalArgument(
		str,
		doc="Filter by grouping ({})".format(
			",".join(map(str, vtes.VTES.search_dimensions["group"]))
		)
	),
	bonus = OptionalArgument(
		str,
		doc="Filter by bonus ({})".format(",".join(vtes.VTES.search_dimensions["bonus"])),
		default=None
	),
	text = OptionalArgument(
		str,
		doc="Filter by text (including name and flavor text)"
	),
	trait = OptionalArgument(
		str,
		doc="Filter by trait ({})".format(",".join(vtes.VTES.search_dimensions["trait"])),
		default=None
	),
	capacity = OptionalArgument(
		str,
		doc="Filter by capacity ({})".format(
			",".join(map(str, vtes.VTES.search_dimensions["capacity"])),
			default=None
		)
	),
	set = OptionalArgument(
		str,
		doc="Filter by set",
		default=None
	),
	sect = OptionalArgument(
		str,
		doc="Filter by sect ({})".format(",".join(vtes.VTES.search_dimensions["sect"])),
		default=None
	),
	title = OptionalArgument(
		str,
		doc="Filter by title ({})".format(",".join(vtes.VTES.search_dimensions["title"])),
		default=None
	),
	city = OptionalArgument(
		str,
		doc="Filter by city",
		default=None
	),
	rarity = OptionalArgument(
		str,
		doc="Filter by rarity ({})".format(",".join(vtes.VTES.search_dimensions["rarity"])),
		default=None
	),
	precon = OptionalArgument(
		str,
		doc="Filter by preconstructed starter",
		default=None
	),
	artist = OptionalArgument(
		str,
		doc="Filter by artist",
		default=None
	),
	exclude = OptionalArgument(
		str,
		doc="Exclude given types ({})".format(",".join(vtes.VTES.search_dimensions["type"])),
		default=None
	)
)
parser.sort()
