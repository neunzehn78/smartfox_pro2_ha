"""Config flow for Smartfox Pro 2."""
from __future__ import annotations

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import CONF_HOST, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            int, vol.Range(min=5, max=300)
        ),
    }
)


async def _validate_connection(host: str) -> None:
    """Try to reach the Smartfox device and validate the response."""
    url = f"http://{host}/values.xml"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status != 200:
                raise ConnectionError(f"HTTP {resp.status}")
            content = await resp.text()
            if "<values>" not in content:
                raise ValueError("Response does not look like a Smartfox values.xml")


class SmartfoxConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smartfox Pro 2."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> config_entries.FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            try:
                await _validate_connection(host)
            except (aiohttp.ClientError, TimeoutError):
                errors["base"] = "cannot_connect"
            except ValueError:
                errors["base"] = "invalid_response"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Smartfox Pro 2 ({host})",
                    data={CONF_HOST: host, CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL]},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )
