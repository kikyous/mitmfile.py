import typing
import re
import os

from collections import defaultdict
from collections.abc import Sequence
from mitmproxy import command
from mitmproxy import ctx
from subprocess import call

EDITOR = os.environ.get('EDITOR','vim')
REGEX  = re.compile(r'^\s*(\w+)\s+(.+)', re.MULTILINE)
FALSELY = ("False", "false", "f", "F", "0", "no", "n", "NO", "N")

MITMFILE_PATH = '.mitmproxy'
MITMFILE = f"{MITMFILE_PATH}/Mitmfile"
DEFAULT_MITMFILE_CONTENT = '''
view_filter !~u /static/

### login api
#map_local |/api/login|.mitmproxy/login.json
'''

def parse_primitive_option(value, option_spec):
    if option_spec in (str, typing.Optional[str]):
        return value
    elif option_spec in (int, typing.Optional[int]):
        return int(value)
    elif option_spec in (float, typing.Optional[float]):
        return float(value)
    elif option_spec in (bool, typing.Optional[bool]):
        return value not in FALSELY

def get_option_spec(option: str):
    return ctx.options._options[option].typespec

class MitmFile:
    def __init__(self):
        self.file = MITMFILE
        self.touched_options : typing.Dict[str, typing.Any] = {}

    def load(self, loader):
        loader.add_option(
            name = "f",
            typespec = typing.Optional[str],
            default = None,
            help = "Load a mitmfile",
        )

    def running(self):
        self.load_file()

    def parse(self, content: str):
        option_maps = REGEX.findall(content)
        parsed_option_maps = defaultdict(list)

        for k, v in option_maps:
            if k in ctx.options:
                value = v.strip()
                option_spec = get_option_spec(k)
                if typing.get_origin(option_spec) is Sequence:
                    option_spec = typing.get_args(option_spec)[0]
                    parsed_option_maps[k].append(parse_primitive_option(value, option_spec))
                else:
                    parsed_option_maps[k] = parse_primitive_option(value, option_spec)
        return parsed_option_maps

    def apply(self, options: typing.Dict[str, typing.Any]):
        for k in options.keys():
            if not k in self.touched_options:
                self.touched_options[k] = getattr(ctx.options, k)

        for k, origin_value in self.touched_options.items():
            value = options.get(k)
            if isinstance(value, list):
                value.extend(origin_value)
            value = value or origin_value
            try:
                ctx.options.update(**{k: value})
            except:
                pass

    def load_file(self):
        if not os.path.exists(self.file):
            return
        with open(self.file, 'r') as f:
            content = f.read()
        self.apply(self.parse(content))

    @command.command("mitmfile.edit")
    def edit(self) -> None:
        if not os.path.exists(MITMFILE_PATH):
            os.makedirs(MITMFILE_PATH)
        if not os.path.exists(self.file):
            with open(self.file, 'w+') as f:
                f.write(DEFAULT_MITMFILE_CONTENT)

        console_master = ctx.master.addons.get('consoleaddon').master
        with console_master.uistopped():
            call([EDITOR, self.file])
        self.load_file()

addons = [
    MitmFile()
]
