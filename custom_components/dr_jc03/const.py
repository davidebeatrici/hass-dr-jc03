"""Support for sensors exposed by the DR-JC03 BMS through RS485."""

from typing import Final

DOMAIN: Final = "dr_jc03"

CONF_VERSION: Final = 1

CONF_KEY_ENTRY_NAME: Final = "entry_name"
CONF_KEY_SERIAL_PATH: Final = "serial_path"
CONF_KEY_SERIAL_BAUDRATE: Final = "serial_baudrate"
CONF_KEY_UPDATE_INTERVAL: Final = "update_interval"

CONF_DEF_ENTRY_NAME: Final = "BMS"
CONF_DEF_SERIAL_BAUDRATE: Final = "9600"
CONF_DEF_UPDATE_INTERVAL: Final = 5

SENSOR_KEY_SOH: Final = "soh"
SENSOR_KEY_SOC: Final = "soc"
SENSOR_KEY_ENERGY: Final = "energy"
SENSOR_KEY_CURRENT: Final = "current"
SENSOR_KEY_VOLTAGE: Final = "voltage"
SENSOR_KEY_CELL_VOLTAGE: Final = "cell{}_voltage"
SENSOR_KEY_ENV_TEMP: Final = "env_temp"
SENSOR_KEY_CELL_TEMP: Final = "cell_temp"
SENSOR_KEY_MOS_TEMP: Final = "mos_temp"
SENSOR_KEY_TEMP: Final = "temp{}"

WAIT_TIME: Final = 3
