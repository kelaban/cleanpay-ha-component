"""Sensor platform for integration_blueprint."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING, Any, Callable, Literal

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorDeviceClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import StateType

from .entity import CleanPayLaundryRoomEntity

from cleanpay_api import Washer, Dryer

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
class MachineSensorEntityDescription(SensorEntityDescription):
    label_id: str
    type: Literal["washer"] | Literal["dryer"]
    value_fn: Callable[[Washer | Dryer], StateType]

def status_to_text(status: str) -> str:
    status_map = {
        "7": "Available",
        "4": "Running",
        "5": "Finished",
    }
    return status_map.get(status, status)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: CleanPayConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""

    entities = []
    for entity in entry.runtime_data.coordinator.data.room_status.washers:
        entities.extend(
            [
                CleanPayWashingMachineSensor(
                    coordinator=entry.runtime_data.coordinator,
                    entity_description=MachineSensorEntityDescription(
                        key=f"cleanpay_washer_{entity.label_id}",
                        name=f"CleanPay Washer {entity.label_id}",
                        type="washer",
                        label_id=entity.label_id,
                        value_fn=lambda a: status_to_text(a.satus),
                        device_class=SensorDeviceClass.ENUM,
                    ),
                ),
                CleanPayWashingMachineSensor(
                    coordinator=entry.runtime_data.coordinator,
                    entity_description=MachineSensorEntityDescription(
                        key=f"cleanpay_washer_{entity.label_id}_timeleft",
                        name=f"CleanPay Washer {entity.label_id} Time Left",
                        type="washer",
                        label_id=entity.label_id,
                        value_fn=lambda a: int(a.left_time or 0) / 60,
                        device_class=SensorDeviceClass.DURATION,
                        native_unit_of_measurement="m",
                    ),
                ),
            ]
        )

    for entity in entry.runtime_data.coordinator.data.room_status.dryers:
        entities.extend(
            [
                CleanPayWashingMachineSensor(
                    coordinator=entry.runtime_data.coordinator,
                    entity_description=MachineSensorEntityDescription(
                        key=f"cleanpay_dryer_{entity.label_id}",
                        name=f"CleanPay Dryer {entity.label_id}",
                        type="dryer",
                        label_id=entity.label_id,
                        value_fn=lambda a: status_to_text(a.satus),
                        device_class=SensorDeviceClass.ENUM,
                    ),
                ),
                CleanPayWashingMachineSensor(
                    coordinator=entry.runtime_data.coordinator,
                    entity_description=MachineSensorEntityDescription(
                        key=f"cleanpay_dryer_{entity.label_id}_timeleft",
                        name=f"CleanPay Dryer {entity.label_id} Time Left",
                        type="dryer",
                        label_id=entity.label_id,
                        value_fn=lambda a: int(a.left_time or 0) / 60,
                        device_class=SensorDeviceClass.DURATION,
                        native_unit_of_measurement="m",
                    ),
                ),
            ]
        )

    async_add_entities(entities)

class CleanPayWashingMachineSensor(CleanPayLaundryRoomEntity, SensorEntity):
    """integration_blueprint Sensor class."""

    entity_description: MachineSensorEntityDescription

    def __init__(
        self,
        coordinator: CleanPayDataUpdateCoordinator,
        entity_description: MachineSensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, entity_description.label_id, entity_description.type.title())
        self._attr_unique_id = (
            f"{coordinator.config_entry.unique_id}-cleanpay-{entity_description.key}"
        )
        self.entity_description = entity_description
        self._attr_icon = ICON_WASHING_MACHINE if entity_description.type == "washer" else ICON_DRYING_MACHINE

    @property
    def native_value(self) -> StateType:
        """Return the native value of the sensor."""
        return self.entity_description.value_fn(self._appliance)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes for the sensor."""
        appliance = self._appliance
        return {
            "label_id": appliance.label_id,
            "status": appliance.status_text,
        }

    @property
    def _appliance(self) -> Washer | Dryer:
        if self.entity_description.type == "washer":
            entities = self.coordinator.data.room_status.washers
        else:
            entities = self.coordinator.data.room_status.dryers
        return [
            w
            for w in entities
            if w.label_id == self.entity_description.label_id
        ][0]
