import typing
import re
import os

from mitmproxy import command
from mitmproxy import ctx
from subprocess import call

EDITOR = os.environ.get('EDITOR','vim')
REGEX  = re.compile("^\s*(\w+)\s+(.+)", re.MULTILINE)

class MitmFile:
    def __init__(self):
        self.file = os.path.expanduser('~/.mitmproxy/mitmfile')
        self.touched_options : typing.Dict[str, typing.Any] = {}

    def load(self, loader):
        loader.add_option(
            name = "f",
            typespec = typing.Optional[str],
            default = None,
            help = "Load a mitmfile",
        )
        self.load_file()
    
    def get_option_specs(self, option: str):
        return ctx.options._options[option].typespec

    def parse(self, content: str):
        maps = REGEX.findall(content)
        option_maps = {}

        def set_list(key, value):
            if key not in option_maps:
                option_maps[key] = []
            option_maps[key].append(value)

        for k,v in maps:
            if k in ctx.options:
                value = v.strip()
                if self.get_option_specs(k) in (typing.Sequence[str],):
                    set_list(k, value)
                elif self.get_option_specs(k) in (str, typing.Optional[str]):
                    option_maps[k] = value
                elif self.get_option_specs(k) in (int, typing.Optional[str]):
                    option_maps[k] = int(value)
                elif self.get_option_specs(k) in (bool, typing.Optional[bool]):
                    option_maps[k] = False if value in ("False", "false", "f", "F", "0", "no", "n", "NO", "N") else True
        return option_maps
    
    def apply(self, options: typing.Dict[str, typing.Any]):
        for k, v in options.items():
            if not k in self.touched_options:
                self.touched_options[k] = getattr(ctx.options, k)

        for k, v in self.touched_options.items():
            value = options.get(k) or self.touched_options[k]
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
        console_master = ctx.master.addons.get('consoleaddon').master
        with console_master.uistopped():
            call([EDITOR, self.file])
        self.load_file()

addons = [
    MitmFile()
]
