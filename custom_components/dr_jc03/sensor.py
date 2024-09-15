"""Support for sensors exposed by the DR-JC03 BMS through RS485."""

from __future__ import annotations

from .const import (
    DOMAIN,

    SENSOR_KEY_SOH,
    SENSOR_KEY_SOC,
    SENSOR_KEY_ENERGY,
    SENSOR_KEY_CURRENT,
    SENSOR_KEY_VOLTAGE,
    SENSOR_KEY_CELL_VOLTAGE,
    SENSOR_KEY_ENV_TEMP,
    SENSOR_KEY_CELL_TEMP,
    SENSOR_KEY_MOS_TEMP,
    SENSOR_KEY_TEMP,
)

from .coordinator import Coordinator

from typing import Any

from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfEnergy,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

def create_entity_percentage(
    coordinator: Coordinator,
    entry: ConfigEntry,
    key: str,
    name: str,
    icon: str,
) -> Sensor:
    desc = SensorEntityDescription(
        key=key,
        name=name,
        icon=icon,
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    )

    return Sensor(coordinator, entry, desc)

def create_entity_kilowatt_hour(
    coordinator: Coordinator,
    entry: ConfigEntry,
    key: str,
    name: str,
) -> Sensor:
    desc = SensorEntityDescription(
        key=key,
        name=name,
        icon="mdi:lightning-bolt-circle",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        state_class=SensorStateClass.MEASUREMENT,
    )

    return Sensor(coordinator, entry, desc)

def create_entity_ampere(
    coordinator: Coordinator,
    entry: ConfigEntry,
    key: str,
    name: str,
) -> Sensor:
    desc = SensorEntityDescription(
        key=key,
        name=name,
        icon="mdi:current-dc",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    )

    return Sensor(coordinator, entry, desc)

def create_entity_volt(
    coordinator: Coordinator,
    entry: ConfigEntry,
    key: str,
    name: str,
) -> Sensor:
    desc = SensorEntityDescription(
        key=key,
        name=name,
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    )

    return Sensor(coordinator, entry, desc)

def create_entity_celsius(
    coordinator: Coordinator,
    entry: ConfigEntry,
    key: str,
    name: str,
) -> Sensor:
    desc = SensorEntityDescription(
        key=key,
        name=name,
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    )

    return Sensor(coordinator, entry, desc)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    entities.append(create_entity_percentage(
        coordinator, entry, SENSOR_KEY_SOH, "State of health", "mdi:battery-heart"))
    entities.append(create_entity_percentage(
        coordinator, entry, SENSOR_KEY_SOC, "State of charge", "mdi:battery"))
    entities.append(create_entity_kilowatt_hour(
        coordinator, entry, SENSOR_KEY_ENERGY, "Energy"))
    entities.append(create_entity_ampere(
        coordinator, entry, SENSOR_KEY_CURRENT, "Current"))
    entities.append(create_entity_volt(
        coordinator, entry, SENSOR_KEY_VOLTAGE, "Voltage"))
    for i in range(1, 17):
        entities.append(create_entity_volt(
            coordinator, entry, SENSOR_KEY_CELL_VOLTAGE.format(i), f"Cell {i} voltage"))
    entities.append(create_entity_celsius(
        coordinator, entry, SENSOR_KEY_ENV_TEMP, "Environment temperature"))
    entities.append(create_entity_celsius(
        coordinator, entry, SENSOR_KEY_CELL_TEMP, "Cell temperature"))
    entities.append(create_entity_celsius(
        coordinator, entry, SENSOR_KEY_MOS_TEMP, "MOS temperature"))
    for i in range(1, 5):
        entities.append(create_entity_celsius(
            coordinator, entry, SENSOR_KEY_TEMP.format(i), f"Temperature {i}"))

    async_add_entities(entities)


class Sensor(CoordinatorEntity[Coordinator], SensorEntity):
    def __init__(
        self,
        coordinator: Coordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ):
        super().__init__(coordinator=coordinator)

        self.entity_description = description

        self.entity_id = (
            f"{SENSOR_DOMAIN}.{entry.title}_{self.entity_description.key}"
        )
        self._attr_unique_id = (
            f"{entry.entry_id}_{self.entity_description.key}"
        )
        self._attr_name = self.entity_description.name
    
    @property
    def native_value(self) -> Any | None:
        return self.coordinator.battery_info.get(self.entity_description.key, None)
