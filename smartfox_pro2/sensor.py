"""Sensor platform for Smartfox Pro 2."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CC_STATUS_MAP, CONF_HOST, DOMAIN
from .coordinator import SmartfoxCoordinator, extract_number, strip_html

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class SmartfoxSensorDescription(SensorEntityDescription):
    """Extended description with a value function."""
    value_fn: Callable[[dict[str, str]], float | str | None] = None


# ---------------------------------------------------------------------------
# Grid / Netzanschlusspunkt sensors
# ---------------------------------------------------------------------------

GRID_SENSORS: tuple[SmartfoxSensorDescription, ...] = (
    SmartfoxSensorDescription(
        key="grid_power",
        translation_key="grid_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: extract_number(d.get("detailsPowerValue")),
    ),
    SmartfoxSensorDescription(
        key="grid_power_l1",
        translation_key="grid_power_l1",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: extract_number(d.get("powerL1Value")),
    ),
    SmartfoxSensorDescription(
        key="grid_power_l2",
        translation_key="grid_power_l2",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: extract_number(d.get("powerL2Value")),
    ),
    SmartfoxSensorDescription(
        key="grid_power_l3",
        translation_key="grid_power_l3",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: extract_number(d.get("powerL3Value")),
    ),
    SmartfoxSensorDescription(
        key="grid_voltage_l1",
        translation_key="grid_voltage_l1",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: extract_number(d.get("voltageL1Value")),
    ),
    SmartfoxSensorDescription(
        key="grid_voltage_l2",
        translation_key="grid_voltage_l2",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: extract_number(d.get("voltageL2Value")),
    ),
    SmartfoxSensorDescription(
        key="grid_voltage_l3",
        translation_key="grid_voltage_l3",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: extract_number(d.get("voltageL3Value")),
    ),
    SmartfoxSensorDescription(
        key="grid_current_l1",
        translation_key="grid_current_l1",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: extract_number(d.get("ampereL1Value")),
    ),
    SmartfoxSensorDescription(
        key="grid_current_l2",
        translation_key="grid_current_l2",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: extract_number(d.get("ampereL2Value")),
    ),
    SmartfoxSensorDescription(
        key="grid_current_l3",
        translation_key="grid_current_l3",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: extract_number(d.get("ampereL3Value")),
    ),
    SmartfoxSensorDescription(
        key="energy_from_grid",
        translation_key="energy_from_grid",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: extract_number(d.get("energyValue")),
    ),
    SmartfoxSensorDescription(
        key="energy_to_grid",
        translation_key="energy_to_grid",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: extract_number(d.get("eToGridValue")),
    ),
    SmartfoxSensorDescription(
        key="energy_from_grid_today",
        translation_key="energy_from_grid_today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: (v / 1000 if (v := extract_number(d.get("eDayValue"))) is not None else None),
    ),
    SmartfoxSensorDescription(
        key="energy_to_grid_today",
        translation_key="energy_to_grid_today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: (v / 1000 if (v := extract_number(d.get("eDayToGridValue"))) is not None else None),
    ),
    SmartfoxSensorDescription(
        key="grid_frequency",
        translation_key="grid_frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: extract_number(d.get("hidFrequency")),
    ),
)


# ---------------------------------------------------------------------------
# Wallbox CC1 sensors
# ---------------------------------------------------------------------------

def _cc1_power(d: dict) -> float | None:
    val = extract_number(d.get("cc1Power"))  # kW → W
    return round(val * 1000, 1) if val is not None else None


def _cc1_status(d: dict) -> str | None:
    raw = d.get("hidCcSt1", "255")
    return CC_STATUS_MAP.get(raw.strip(), raw)


WALLBOX_SENSORS: tuple[SmartfoxSensorDescription, ...] = (
    SmartfoxSensorDescription(
        key="wallbox_power",
        translation_key="charger_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_cc1_power,
    ),
    SmartfoxSensorDescription(
        key="wallbox_energy_today",
        translation_key="charger_energy_today",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: extract_number(d.get("hidCc1EnergyDay")),
    ),
    SmartfoxSensorDescription(
        key="wallbox_last_session",
        translation_key="charger_last_session",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda d: extract_number(d.get("cc1LastChargeValue")),
    ),
    SmartfoxSensorDescription(
        key="wallbox_cycle_count",
        translation_key="charger_cycle_count",
        native_unit_of_measurement=None,
        device_class=None,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda d: int(d["hidCc1CycleCounter"]) if d.get("hidCc1CycleCounter", "").isdigit() else None,
    ),
    SmartfoxSensorDescription(
        key="wallbox_status",
        translation_key="charger_status",
        native_unit_of_measurement=None,
        device_class=SensorDeviceClass.ENUM,
        state_class=None,
        options=list(CC_STATUS_MAP.values()),
        value_fn=_cc1_status,
    ),
    SmartfoxSensorDescription(
        key="wallbox_control_current",
        translation_key="charger_control_current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: extract_number(d.get("cc1_control_current")),
    ),
    SmartfoxSensorDescription(
        key="wallbox_phase_l1",
        translation_key="charger_phase_l1",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: extract_number(d.get("cc1_phase_l1")),
    ),
    SmartfoxSensorDescription(
        key="wallbox_phase_l2",
        translation_key="charger_phase_l2",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: extract_number(d.get("cc1_phase_l2")),
    ),
    SmartfoxSensorDescription(
        key="wallbox_phase_l3",
        translation_key="charger_phase_l3",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: extract_number(d.get("cc1_phase_l3")),
    ),
    SmartfoxSensorDescription(
        key="wallbox_temperature",
        translation_key="charger_temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: extract_number(d.get("hidCc1Temperature")),
    ),
    SmartfoxSensorDescription(
        key="wallbox_current_limit",
        translation_key="charger_current_limit",
        native_unit_of_measurement=PERCENTAGE,
        device_class=None,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: float(d["hidCc1Percent"].replace("%", "").strip())
            if d.get("hidCc1Percent") else None,
    ),
)


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smartfox Pro 2 sensor entities."""
    coordinator: SmartfoxCoordinator = hass.data[DOMAIN][entry.entry_id]
    host: str = entry.data[CONF_HOST]
    data = coordinator.data or {}
    wallbox_name: str = strip_html(data.get("hidCc1Name", "Wallbox"))

    entities: list = [
        *[SmartfoxSensor(coordinator, desc, host, is_wallbox=False) for desc in GRID_SENSORS],
        *[SmartfoxSensor(coordinator, desc, host, is_wallbox=True, wallbox_name=wallbox_name)
          for desc in WALLBOX_SENSORS],
        WallboxTotalEnergySensor(coordinator, host, wallbox_name),
    ]
    async_add_entities(entities)


# ---------------------------------------------------------------------------
# Standard sensor entity
# ---------------------------------------------------------------------------

class SmartfoxSensor(CoordinatorEntity[SmartfoxCoordinator], SensorEntity):
    """A single Smartfox Pro 2 sensor."""

    entity_description: SmartfoxSensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SmartfoxCoordinator,
        description: SmartfoxSensorDescription,
        host: str,
        is_wallbox: bool = False,
        wallbox_name: str = "Wallbox",
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"smartfox_{host}_{description.key}"

        if not is_wallbox:
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, f"{host}_grid")},
                name="Smartfox Pro 2",
                manufacturer="Smartfox",
                model="Pro 2",
                configuration_url=f"http://{host}",
            )
        else:
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, f"{host}_wallbox")},
                name=wallbox_name,
                manufacturer="Smartfox",
                model="Pro Charger",
                via_device=(DOMAIN, f"{host}_grid"),
            )

    @property
    def native_value(self) -> float | str | None:
        if self.coordinator.data is None:
            return None
        try:
            return self.entity_description.value_fn(self.coordinator.data)
        except Exception:  # noqa: BLE001
            return None


# ---------------------------------------------------------------------------
# Cumulative total energy sensor (RestoreSensor)
# ---------------------------------------------------------------------------

class WallboxTotalEnergySensor(
    CoordinatorEntity[SmartfoxCoordinator], RestoreSensor
):
    """Cumulative lifetime energy counter for the wallbox.

    Strategy:
    - Tracks hidCc1EnergyDay (today's kWh from the Smartfox).
    - When today's value is >= previous today's value → add the delta to total.
    - When today's value drops (midnight reset) → the previous today's value
      is already fully included; just start accumulating from the new value.
    - State is persisted across HA restarts via RestoreSensor.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "charger_energy_total"
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_icon = "mdi:ev-station"

    def __init__(
        self,
        coordinator: SmartfoxCoordinator,
        host: str,
        wallbox_name: str,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"smartfox_{host}_wallbox_energy_total"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{host}_wallbox")},
            name=wallbox_name,
            manufacturer="Smartfox",
            model="Pro Charger",
            via_device=(DOMAIN, f"{host}_grid"),
        )
        self._total: float = 0.0          # lifetime kWh accumulated
        self._last_day_value: float | None = None  # last seen hidCc1EnergyDay

    async def async_added_to_hass(self) -> None:
        """Restore state from last HA run."""
        await super().async_added_to_hass()
        if (last := await self.async_get_last_sensor_data()) is not None:
            try:
                self._total = float(last.native_value)
                _LOGGER.debug(
                    "Wallbox total energy restored: %.3f kWh", self._total
                )
            except (TypeError, ValueError):
                self._total = 0.0

    def _handle_coordinator_update(self) -> None:
        """Called on every coordinator poll — update the running total."""
        data = self.coordinator.data
        if data is None:
            return

        today_raw = extract_number(data.get("hidCc1EnergyDay"))
        if today_raw is None:
            return

        if self._last_day_value is None:
            # First update after startup — just record the baseline, don't add
            self._last_day_value = today_raw
            self.async_write_ha_state()
            return

        if today_raw >= self._last_day_value:
            # Normal case: counter is still running up during the day
            delta = today_raw - self._last_day_value
            self._total = round(self._total + delta, 3)
        else:
            # today_raw < last: midnight reset detected.
            # The full value up to midnight was already accumulated in previous
            # updates, so nothing extra to add — just start fresh from today_raw.
            _LOGGER.debug(
                "Wallbox daily reset detected (%.3f → %.3f kWh). Total: %.3f kWh",
                self._last_day_value,
                today_raw,
                self._total,
            )

        self._last_day_value = today_raw
        self.async_write_ha_state()

    @property
    def native_value(self) -> float:
        return round(self._total, 3)
