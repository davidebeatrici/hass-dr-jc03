"""Support for sensors exposed by the DR-JC03 BMS through RS485."""

from .const import (
    DOMAIN,

    CONF_VERSION,

    CONF_KEY_ENTRY_NAME,
    CONF_KEY_SERIAL_PATH,
    CONF_KEY_SERIAL_BAUDRATE,
    CONF_KEY_UPDATE_INTERVAL,

    CONF_DEF_ENTRY_NAME,
    CONF_DEF_SERIAL_BAUDRATE,
    CONF_DEF_UPDATE_INTERVAL,
)

from typing import Any

from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

import voluptuous as vol

DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_KEY_ENTRY_NAME, default=CONF_DEF_ENTRY_NAME): cv.string,
        vol.Required(CONF_KEY_SERIAL_PATH): cv.string,
        vol.Optional(CONF_KEY_SERIAL_BAUDRATE, default=CONF_DEF_SERIAL_BAUDRATE): cv.positive_int,
        vol.Optional(CONF_KEY_UPDATE_INTERVAL, default=CONF_DEF_UPDATE_INTERVAL): cv.positive_int,
    }
)

class ConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = CONF_VERSION

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)

        title = user_input[CONF_KEY_ENTRY_NAME]
        if title is not None:
            del user_input[CONF_KEY_ENTRY_NAME]
        else:
            title = CONF_DEF_ENTRY_NAME

        return self.async_create_entry(title=title, data=user_input)
