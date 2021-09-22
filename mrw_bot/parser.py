import collections
import json

from discord.ext import commands
from discord_argparse import *

from krcg import vtes
import arrow


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
                    entry = "{0}{1:<{width}} {2}".format(
                        self.indent * " ", name, argument.doc, width=max_size
                    )
                    self.paginator.add_line(self.shorten_text(entry))
        self.paginator.close_page()
        await self.send_pages()


class ArgumentConverter(ArgumentConverter):
    def sort(self):
        self.arguments = collections.OrderedDict(sorted(self.arguments.items()))

    def get_args(self):
        return self.arguments.keys()

    def __add__(self, other):
        args = {}
        for k, v in self.arguments.items():
            args[k] = v
        for k, v in other.arguments.items():
            if k in args.keys():
                pass
            args[k] = v
        return ArgumentConverter(**args)


vtes = ArgumentConverter(
    discipline=OptionalArgument(
        str,
        doc="Filter by discipline ({})".format(
            ",".join(vtes.VTES.search_dimensions["discipline"])
        ),
    ),
    clan=OptionalArgument(
        str,
        doc="Filter by clan ({})".format(",".join(vtes.VTES.search_dimensions["clan"])),
    ),
    type=OptionalArgument(
        str,
        doc="Filter by card type ({})".format(
            ",".join(vtes.VTES.search_dimensions["type"])
        ),
    ),
    group=OptionalArgument(
        str,
        doc="Filter by grouping ({})".format(
            ",".join(map(str, vtes.VTES.search_dimensions["group"]))
        ),
    ),
    bonus=OptionalArgument(
        str,
        doc="Filter by bonus ({})".format(
            ",".join(vtes.VTES.search_dimensions["bonus"])
        ),
    ),
    text=OptionalArgument(str, doc="Filter by text (including name and flavor text)"),
    trait=OptionalArgument(
        str,
        doc="Filter by trait ({})".format(
            ",".join(vtes.VTES.search_dimensions["trait"])
        ),
    ),
    capacity=OptionalArgument(
        str,
        doc="Filter by capacity ({})".format(
            ",".join(map(str, vtes.VTES.search_dimensions["capacity"]))
        ),
    ),
    set=OptionalArgument(str, doc="Filter by set"),
    sect=OptionalArgument(
        str,
        doc="Filter by sect ({})".format(",".join(vtes.VTES.search_dimensions["sect"])),
    ),
    title=OptionalArgument(
        str,
        doc="Filter by title ({})".format(
            ",".join(vtes.VTES.search_dimensions["title"])
        ),
    ),
    city=OptionalArgument(str, doc="Filter by city"),
    rarity=OptionalArgument(
        str,
        doc="Filter by rarity ({})".format(
            ",".join(vtes.VTES.search_dimensions["rarity"])
        ),
    ),
    precon=OptionalArgument(str, doc="Filter by preconstructed starter"),
    artist=OptionalArgument(str, doc="Filter by artist"),
    exclude=OptionalArgument(
        str,
        doc="Exclude given types ({})".format(
            ",".join(vtes.VTES.search_dimensions["type"])
        ),
    ),
)

twda = ArgumentConverter(
    card=OptionalArgument(str, doc="Filter by card names: 'Fame|Carrion Crows'"),
    deck=OptionalArgument(str, doc="TWDA ID of a deck: 2016gncbg"),
    players=OptionalArgument(int, doc="Minimum number of players", default=0),
    date_from=OptionalArgument(
        lambda s: arrow.get(s).date(),
        doc="Year (included) for deck searching",
        default=arrow.get(1994).date(),
    ),
    date_to=OptionalArgument(
        lambda s: arrow.get(s).date(),
        doc="Year (excluded) for deck searching",
        default=arrow.now().date(),
    ),
    author=OptionalArgument(str, doc="Looking for TWDA by player name: 'Ben peal'"),
)

# Building full parser
full = vtes + twda
