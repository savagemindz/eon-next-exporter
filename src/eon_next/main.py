import asyncio
import sys
import os

from aiohttp import web

from .exporter import Exporter


async def main() -> None:

    exporter = Exporter()

    app = web.Application()
    app.router.add_get("/metrics", exporter.collect)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 9101)  # noqa: S104
    await site.start()

    if os.environ.get("EON_NEXT_STARTUP_TEST"):
        sys.exit()

    done = asyncio.Event()
    await done.wait()   # Sleep forever
