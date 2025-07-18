"""
Custom integration to integrate integration_blueprint with Home Assistant.

For more details about this integration, please refer to
https://github.com/ludeeus/integration_blueprint
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING


from homeassistant.const import CONF_ID, CONF_API_KEY, Platform
from homeassistant.loader import async_get_loaded_integration

from .const import CONF_SRCODE, DOMAIN, LOGGER
from .coordinator import CleanPayDataUpdateCoordinator
from .data import CleanPayConfigData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import CleanPayConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: CleanPayConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    coordinator = CleanPayDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        update_interval=timedelta(minutes=5),
    )
    entry.runtime_data = CleanPayConfigData(
        userid=entry.data[CONF_ID],
        api_key=entry.data[CONF_API_KEY],
        srcode=entry.data[CONF_SRCODE],
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: CleanPayConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: CleanPayConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
