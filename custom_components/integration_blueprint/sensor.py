"""Sensor platform for integration_blueprint."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING, Callable

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import StateType

from .entity import CleanPayLaundryRoomEntity

from cleanpay_api import Washer

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import CleanPayDataUpdateCoordinator
    from .data import CleanPayConfigEntry

ICON_WASHING_MACHINE = "mdi:washing-machine"
ICON_DRYING_MACHINE = "mdi:tumble-dryer"

_LOGGER = logging.getLogger(__name__)

ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key="cleanpay_app",
        name="CleanPay Laundry Room Sensor",
    ),
)

@dataclass(kw_only=True, frozen=True)
class WashingMachineSensorEntityDescription(SensorEntityDescription):
    label_id: str
    value_fn: Callable[[Washer], StateType]


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: CleanPayConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""

    washers_entities = []
    for entity in entry.runtime_data.coordinator.data.room_status.washers:
        washers_entities.extend(
            [
                CleanPayWashingMachineSensor(
                    coordinator=entry.runtime_data.coordinator,
                    entity_description=WashingMachineSensorEntityDescription(
                        key=f"cleanpay_washer_{entity.label_id}",
                        name=f"CleanPay Washer {entity.label_id}",
                        label_id=entity.label_id,
                        value_fn=lambda washer: washer.status_text,
                        device_class=SensorDeviceClass.ENUM,
                    ),
                ),
                CleanPayWashingMachineSensor(
                    coordinator=entry.runtime_data.coordinator,
                    entity_description=WashingMachineSensorEntityDescription(
                        key=f"cleanpay_washer_{entity.label_id}_timeleft",
                        name=f"CleanPay Washer {entity.label_id} Time Left",
                        label_id=entity.label_id,
                        value_fn=lambda washer: int(washer.left_time or 0),
                        device_class=SensorDeviceClass.DURATION,
                        native_unit_of_measurement="min",
                    ),
                ),
            ]
        )

    async_add_entities(washers_entities)


class CleanPayWashingMachineSensor(CleanPayLaundryRoomEntity, SensorEntity):
    """integration_blueprint Sensor class."""

    _attr_icon = ICON_WASHING_MACHINE
    entity_description: WashingMachineSensorEntityDescription

    def __init__(
        self,
        coordinator: CleanPayDataUpdateCoordinator,
        entity_description: WashingMachineSensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, entity_description.label_id)
        self._attr_unique_id = (
            f"{coordinator.config_entry.unique_id}-cleanpay-{entity_description.key}"
        )
        self.entity_description = entity_description

    @property
    def native_value(self) -> StateType:
        """Return the native value of the sensor."""
        return self.entity_description.value_fn(self._appliance)

    @property
    def _appliance(self) -> Washer:
        return [
            w
            for w in self.coordinator.data.room_status.washers
            if w.label_id == self.entity_description.label_id
        ][0]
