import re

import asyncio
from collections.abc import Sequence
from typing import NamedTuple

from mitmproxy import ctx, exceptions, flowfilter, http
from mitmproxy.utils.spec import parse_spec


class SleepSpec(NamedTuple):
    matches: flowfilter.TFilter
    subject: str
    sleep_time: str


def parse_sleep_spec(option: str) -> SleepSpec:
    spec = SleepSpec(*parse_spec(option))

    try:
        re.compile(spec.subject)
    except re.error as e:
        raise ValueError(f"Invalid regular expression {spec.subject!r} ({e})")

    return spec


class SleepRequest:
    def __init__(self):
        self.sleep_specs: list[SleepSpec] = []

    def load(self, loader):
        loader.add_option(
            "sleep",
            Sequence[str],
            [],
            """
            Sleep a request of URL using a pattern of the form
            "[/flow-filter]/url-regex/time", where the separator can
            be any character.
            """,
        )

    def configure(self, updated):
        if "sleep" in updated:
            self.sleep_specs = []
            for option in ctx.options.sleep:
                try:
                    spec = parse_sleep_spec(option)
                except ValueError as e:
                    raise exceptions.OptionsError(f"Cannot parse sleep option {option}: {e}") from e

                self.sleep_specs.append(spec)

    async def request(self, flow: http.HTTPFlow):
        url = flow.request.pretty_url
        for spec in self.sleep_specs:
            if spec.matches(flow) and re.search(spec.subject, url):
                await asyncio.sleep(int(spec.sleep_time))


addons = [SleepRequest()]
