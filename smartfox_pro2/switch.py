"""Switch platform for Smartfox Pro 2 — Wallbox Lademodus via Modbus TCP."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_HOST, DOMAIN
from .coordinator import SmartfoxCoordinator, strip_html

_LOGGER = logging.getLogger(__name__)

REG_CC1_MODE     = 41607   # 41608 - 1  → 0=Überschuss, 1=Manuell
REG_CC1_MAN_VAL  = 41608   # 41609 - 1  → 0–100 %
MODBUS_PORT      = 502


async def _modbus_write(host: str, register: int, value: int) -> bool:
    """Write a single holding register via Modbus TCP."""
    try:
        from pymodbus.client import AsyncModbusTcpClient
    except ImportError as err:
        _LOGGER.error("pymodbus Import-Fehler: %s", err)
        return False

    client = AsyncModbusTcpClient(host, port=MODBUS_PORT, timeout=5)
    try:
        connected = await client.connect()
        if not connected:
            _LOGGER.warning("Modbus: Verbindung zu %s fehlgeschlagen", host)
            return False
        result = await client.write_registers(register, [value])
        if result.isError():
            _LOGGER.warning("Modbus: Register %s = %s fehlgeschlagen: %s", register, value, result)
            return False
        _LOGGER.debug("Modbus: Register %s = %s OK", register, value)
        return True
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("Modbus: Fehler: %s", err)
        return False
    finally:
        client.close()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SmartfoxCoordinator = hass.data[DOMAIN][entry.entry_id]
    host: str = entry.data[CONF_HOST]
    data = coordinator.data or {}
    wallbox_name: str = strip_html(data.get("hidCc1Name", "Wallbox"))
    async_add_entities([WallboxModeSwitch(coordinator, host, wallbox_name)])


class WallboxModeSwitch(CoordinatorEntity[SmartfoxCoordinator], SwitchEntity):
    """Switch: Überschussladen (OFF) ↔ Manuell (ON).

    Zustand wird live aus hidCcMode1 gelesen → spiegelt auch manuelle
    Änderungen an der Wallbox korrekt wider.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "wallbox_mode_switch"
    _attr_icon = "mdi:ev-station"

    def __init__(
        self,
        coordinator: SmartfoxCoordinator,
        host: str,
        wallbox_name: str,
    ) -> None:
        super().__init__(coordinator)
        self._host = host
        self._attr_unique_id = f"smartfox_{host}_wallbox_mode_switch"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{host}_wallbox")},
            name=wallbox_name,
            manufacturer="Smartfox",
            model="Pro Charger",
        )

    @property
    def is_on(self) -> bool:
        """Return True wenn Modus = Manuell (1), False wenn Überschuss (0)."""
        if self.coordinator.data is None:
            return False
        raw = self.coordinator.data.get("hidCcMode1", "0").strip()
        # hidCcMode1: 0=Überschuss(A), 1=Manuell(M), 2=A+, 3=AUS
        return raw == "1"

    async def async_turn_on(self, **kwargs) -> None:
        """Manuellen Modus aktivieren + Ladewert auf 100%."""
        ok1 = await _modbus_write(self._host, REG_CC1_MAN_VAL, 100)
        if ok1:
            ok2 = await _modbus_write(self._host, REG_CC1_MODE, 1)
            if ok2:
                await self.coordinator.async_request_refresh()
                return
        _LOGGER.warning("Wallbox: Manueller Modus konnte nicht gesetzt werden")

    async def async_turn_off(self, **kwargs) -> None:
        """Überschussladen aktivieren."""
        if await _modbus_write(self._host, REG_CC1_MODE, 0):
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.warning("Wallbox: Überschuss-Modus konnte nicht gesetzt werden")
