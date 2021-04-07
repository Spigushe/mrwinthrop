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
		doc="Filter by discipline ({})".format(",".join(vtes.VTES.search_dimensions["discipline"])),
		default=""
	),
	clan = OptionalArgument(
		str,
		doc="Filter by clan ({})".format(",".join(vtes.VTES.search_dimensions["clan"])),
		default=""
	),
	type = OptionalArgument(
		str,
		doc="Filter by card type ({})".format(",".join(vtes.VTES.search_dimensions["type"])),
		default=""
	),
	group = OptionalArgument(
		str,
		doc="Filter by grouping ({})".format(
			",".join(map(str, vtes.VTES.search_dimensions["group"])),
			default=""
		)
	),
	bonus = OptionalArgument(
		str,
		doc="Filter by bonus ({})".format(",".join(vtes.VTES.search_dimensions["bonus"])),
		default=""
	),
	text = OptionalArgument(
		str,
		doc="Filter by text (including name and flavor text)",
		default=""
	),
	trait = OptionalArgument(
		str,
		doc="Filter by trait ({})".format(",".join(vtes.VTES.search_dimensions["trait"])),
		default=""
	),
	capacity = OptionalArgument(
		str,
		doc="Filter by capacity ({})".format(
			",".join(map(str, vtes.VTES.search_dimensions["capacity"])),
			default=""
		)
	),
	set = OptionalArgument(
		str,
		doc="Filter by set",
		default=""
	),
	sect = OptionalArgument(
		str,
		doc="Filter by sect ({})".format(",".join(vtes.VTES.search_dimensions["sect"])),
		default=""
	),
	title = OptionalArgument(
		str,
		doc="Filter by title ({})".format(",".join(vtes.VTES.search_dimensions["title"])),
		default=""
	),
	city = OptionalArgument(
		str,
		doc="Filter by city",
		default=""
	),
	rarity = OptionalArgument(
		str,
		doc="Filter by rarity ({})".format(",".join(vtes.VTES.search_dimensions["rarity"])),
		default=""
	),
	precon = OptionalArgument(
		str,
		doc="Filter by preconstructed starter",
		default=""
	),
	artist = OptionalArgument(
		str,
		doc="Filter by artist",
		default=""
	),
	exclude = OptionalArgument(
		str,
		doc="Exclude given types ({})".format(",".join(vtes.VTES.search_dimensions["type"])),
		default=""
	)
)
parser.sort()
