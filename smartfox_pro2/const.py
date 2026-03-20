"""Constants for the Smartfox Pro 2 integration."""

DOMAIN = "smartfox_pro2"
DEFAULT_SCAN_INTERVAL = 30

CONF_HOST = "host"
CONF_SCAN_INTERVAL = "scan_interval"

# Car Charger status codes
CC_STATUS_MAP = {
    "0": "not_configured",
    "1": "available",
    "2": "occupied",
    "3": "charging",
    "255": "offline",
}

# Car Charger charging mode
CC_MODE_MAP = {
    "0": "surplus",
    "1": "manual",
    "2": "surplus_plus",
    "3": "off",
}
