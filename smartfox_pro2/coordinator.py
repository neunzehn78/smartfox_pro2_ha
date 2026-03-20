"""DataUpdateCoordinator for Smartfox Pro 2."""
from __future__ import annotations

import json
import logging
import re
import xml.etree.ElementTree as ET
from datetime import timedelta

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_HOST, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


def strip_html(text: str) -> str:
    """Remove HTML tags from a string."""
    if not text:
        return ""
    return re.sub(r"<[^>]+>", "", text).strip()


def extract_number(text: str | None) -> float | None:
    """Extract the first numeric value from a string like '-18 W' or '5.31 kW'."""
    if text is None:
        return None
    clean = strip_html(text)
    match = re.search(r"[-+]?\d+\.?\d*", clean)
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None
    return None


class SmartfoxCoordinator(DataUpdateCoordinator[dict[str, str]]):
    """Coordinator that fetches data from the Smartfox Pro 2 /values.xml endpoint."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.host: str = entry.data[CONF_HOST]
        interval: int = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=interval),
        )

    async def _async_update_data(self) -> dict[str, str]:
        url = f"http://{self.host}/values.xml"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    resp.raise_for_status()
                    text = await resp.text()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Connection error to Smartfox at {url}: {err}") from err
        except TimeoutError as err:
            raise UpdateFailed(f"Timeout connecting to Smartfox at {url}") from err

        try:
            root = ET.fromstring(text)
        except ET.ParseError as err:
            raise UpdateFailed(f"Failed to parse XML from Smartfox: {err}") from err

        data: dict[str, str] = {}
        for elem in root.findall("value"):
            vid = elem.get("id")
            val = (elem.text or "").strip()
            if vid:
                data[vid] = val

        # Expand JSON arrays: hidCcPhaseCurrent and hidCcControlCurrent
        # hidCcPhaseCurrent = [[L1,L2,L3], ...] per charger slot
        # hidCcControlCurrent = [A, ...] per charger slot
        try:
            cc_phases_raw = data.get("hidCcPhaseCurrent", "[[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]")
            cc_phases: list[list[float]] = json.loads(cc_phases_raw)
            for i in range(5):
                n = i + 1
                phases = cc_phases[i] if i < len(cc_phases) else [0.0, 0.0, 0.0]
                data[f"cc{n}_phase_l1"] = str(phases[0] if len(phases) > 0 else 0.0)
                data[f"cc{n}_phase_l2"] = str(phases[1] if len(phases) > 1 else 0.0)
                data[f"cc{n}_phase_l3"] = str(phases[2] if len(phases) > 2 else 0.0)
        except (json.JSONDecodeError, TypeError, IndexError) as err:
            _LOGGER.debug("Could not parse hidCcPhaseCurrent: %s", err)

        try:
            cc_ctrl_raw = data.get("hidCcControlCurrent", "[0,0,0,0,0]")
            cc_ctrl: list[float] = json.loads(cc_ctrl_raw)
            for i in range(5):
                n = i + 1
                data[f"cc{n}_control_current"] = str(cc_ctrl[i] if i < len(cc_ctrl) else 0.0)
        except (json.JSONDecodeError, TypeError, IndexError) as err:
            _LOGGER.debug("Could not parse hidCcControlCurrent: %s", err)

        return data
