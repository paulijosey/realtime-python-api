import enum
import logging
import types
import typing as T

import aiohttp

from pupil_labs.realtime_api.models import DiscoveredDevice, Status

logger = logging.getLogger(__name__)


class APIPath(enum.Enum):
    PREFIX = "/api"
    STATUS = "/status"
    RECORDING_START = "/recording:start"
    RECORDING_STOP_AND_SAVE = "/recording:stop_and_save"
    RECORDING_CANCEL = "/recording:cancel"


class Control:
    class Error(Exception):
        pass

    @classmethod
    def for_discovered_device(cls, device: DiscoveredDevice) -> "Control":
        return cls(device.addresses[0], device.port)

    def __init__(self, address: str, port: int) -> None:
        self.address = address
        self.port = port
        self.session = aiohttp.ClientSession()

    async def get_status(self):
        url = (
            f"http://{self.address}:{self.port}"
            + APIPath.PREFIX.value
            + APIPath.STATUS.value
        )
        async with self.session.get(url) as response:
            result = (await response.json())["result"]
            logger.debug(f"[{self}.get_status] Received status: {result}")
            return Status.from_dict(result)

    async def start_recording(self):
        url = (
            f"http://{self.address}:{self.port}"
            + APIPath.PREFIX.value
            + APIPath.RECORDING_START.value
        )
        async with self.session.post(url) as response:
            confirmation = await response.json()
            logger.debug(f"[{self}.start_recording] Received response: {confirmation}")
            if response.status != 200:
                raise Control.Error(response.status, confirmation["message"])

    async def stop_and_save_recording(self):
        url = (
            f"http://{self.address}:{self.port}"
            + APIPath.PREFIX.value
            + APIPath.RECORDING_STOP_AND_SAVE.value
        )
        async with self.session.post(url) as response:
            confirmation = await response.json()
            logger.debug(f"[{self}.stop_recording] Received response: {confirmation}")
            if response.status != 200:
                raise Control.Error(response.status, confirmation["message"])

    async def cancel_recording(self):
        url = (
            f"http://{self.address}:{self.port}"
            + APIPath.PREFIX.value
            + APIPath.RECORDING_CANCEL.value
        )
        async with self.session.post(url) as response:
            confirmation = await response.json()
            logger.debug(f"[{self}.stop_recording] Received response: {confirmation}")
            if response.status != 200:
                raise Control.Error(response.status, confirmation["message"])

    async def close(self):
        await self.session.close()

    async def __aenter__(self) -> "Control":
        return self

    async def __aexit__(
        self,
        exc_type: T.Optional[T.Type[BaseException]],
        exc_val: T.Optional[BaseException],
        exc_tb: T.Optional[types.TracebackType],
    ) -> None:
        await self.close()

    def __repr__(self) -> str:
        return f"Control({self.address}, {self.port})"