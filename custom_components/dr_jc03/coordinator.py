"""Support for sensors exposed by the DR-JC03 BMS through RS485."""

from .const import (
    DOMAIN,

    CONF_KEY_SERIAL_PATH,
    CONF_KEY_SERIAL_BAUDRATE,
    CONF_KEY_UPDATE_INTERVAL,

    CONF_DEF_SERIAL_BAUDRATE,
    CONF_DEF_UPDATE_INTERVAL,

    WAIT_TIME,
)

from .protocol import get_info

from asyncio import (
    create_task,
    sleep,
    wait_for,
)
from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from serial import SerialException
from serial_asyncio_fast import open_serial_connection

_LOGGER = logging.getLogger(__name__)

class Coordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=entry.options.get(CONF_KEY_UPDATE_INTERVAL, CONF_DEF_UPDATE_INTERVAL)
            ),
        )

        self.path = entry.data.get(CONF_KEY_SERIAL_PATH)
        self.baudrate = entry.data.get(CONF_KEY_SERIAL_BAUDRATE, CONF_DEF_SERIAL_BAUDRATE)
        self.battery_info = {}

    async def _async_update_data(self):
        try:
            self.in_stream, self.out_stream = await open_serial_connection(
                url=self.path,
                baudrate=self.baudrate,
            )
        except SerialException:
            raise UpdateFailed(f"Unable to connect to the serial device {self.path}")

        _LOGGER.debug(f"Serial device {self.path} connected")

        task = create_task(get_info(self.in_stream, self.out_stream))
        try:
            self.battery_info = await wait_for(task, WAIT_TIME)
        except TimeoutError as e:
            _LOGGER.error(e)

        if self.battery_info is None:
            raise UpdateFailed()
