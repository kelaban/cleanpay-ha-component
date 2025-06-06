"""Constants for clean_pay."""

from logging import Logger, getLogger
from typing import Final

LOGGER: Logger = getLogger(__package__)

DOMAIN = "cleanpay_ha"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"

CONF_SRCODE: Final = "srcode"
