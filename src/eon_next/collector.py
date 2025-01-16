import datetime
import typing
import threading

from prometheus_client import Metric
from.eon_next import EonNext



class Collector:

    def __init__(
        self,
        username: str,
        password: str,
    ) -> None:

        self.username = username
        self.password = password
        self.api: typing.Optional[EonNext] = None
        self.lock = threading.Lock()

        # Storage for preloaded metrics
        self.preloaded_metrics = []

    async def _setup(self):
        self.api = EonNext()
        await self.api.login_with_username_and_password(self.username, self.password)

    async def preload_metrics(self) -> typing.AsyncGenerator:
        """Asynchronously preload metrics."""
        with self.lock:
            self.preloaded_metrics = []  # Clear the previous metrics
            await self._setup()

            for account in self.api.accounts:
                for meter in account.meters:
                    labels = {
                        "account_number": account.account_number,
                        "serial": meter.get_serial(),
                        "meter_id": meter.meter_id,
                        "type": meter.get_type()
                    }

                    latest_reading_date = await meter.get_latest_reading_date()
                    latest_reading_time = datetime.datetime.combine(
                        latest_reading_date, datetime.time(12, 0)
                    )
                    unix_time = latest_reading_time.timestamp()

                    latest_reading = await meter.get_latest_reading()

                    metric = Metric(
                        "eonnext_meter_reading",
                        "Latest meter reading taken my EonNext (kWh)",
                        "gauge",
                    )

                    metric.add_sample(
                        "eonnext_meter_reading",
                        value=latest_reading,
                        labels=labels,
                        timestamp=unix_time,
                    )

                    self.preloaded_metrics.append(metric)

    def collect(self):
        """Synchronous collection of preloaded metrics."""
        with self.lock:
            for metric in self.preloaded_metrics:
                print(metric)
                yield metric