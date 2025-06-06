"""Custom types for integration_blueprint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .coordinator import CleanPayDataUpdateCoordinator


type CleanPayConfigEntry = ConfigEntry[CleanPayConfigData]


@dataclass
class CleanPayConfigData:
    """Data for the Blueprint integration."""

    userid: str
    api_key: str
    srcode: str
    coordinator: CleanPayDataUpdateCoordinator
    integration: Integration
