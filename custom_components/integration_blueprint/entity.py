"""BlueprintEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION
from .coordinator import CleanPayDataUpdateCoordinator


class CleanPayLaundryRoomEntity(CoordinatorEntity[CleanPayDataUpdateCoordinator]):
    """BlueprintEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: CleanPayDataUpdateCoordinator, label_id: str, entity_type: str) -> None:
        """Initialize."""
        super().__init__(coordinator)
        unique_id = coordinator.config_entry.unique_id
        self._attr_device_info = DeviceInfo(
            identifiers={
                (coordinator.config_entry.domain, f"{unique_id}_laundryroom_{label_id}"),
            },
            manufacturer="CleanPay App",
            name=f"CleanPay Laundry Room {entity_type} {label_id}"
        )
