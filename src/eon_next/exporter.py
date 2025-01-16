from aiohttp import web

from prometheus_client import (
    CollectorRegistry,
    PlatformCollector,
    ProcessCollector,
    generate_latest,
)

from .collector import Collector


class Exporter:
    def __init__(self) -> None:
        self.registry = CollectorRegistry()
        PlatformCollector(registry=self.registry)
        ProcessCollector(registry=self.registry)
        self.collector: Collector

    async def collect(self, request: web.Request) -> web.Response:  # noqa: ARG002
        username = request.query.get("username")
        password = request.query.get("password")

        if not username or not password:
            return web.Response(
                body="'target', 'username' and 'password' parameters must be specified",
                status=400,
            )

        collector = Collector(username, password)
        await collector.preload_metrics()
        self.registry.register(collector)

        return web.Response(
            body=generate_latest(self.registry),
            headers={"Content-Type": "text/plain"},
        )
