"""DataUpdateCoordinator for integration_blueprint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from cleanpay_api import CleanPay, get_room_status, RoomStatus


if TYPE_CHECKING:
    from .data import CleanPayConfigEntry


@dataclass
class CleanPayCoordinatorData:
    room_status: RoomStatus


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class CleanPayDataUpdateCoordinator(DataUpdateCoordinator[CleanPayCoordinatorData]):
    """Class to manage fetching data from the API."""

    config_entry: CleanPayConfigEntry

    async def _async_update_data(self) -> CleanPayCoordinatorData:
        """Update data via library."""

        client_session = async_get_clientsession(self.hass)
        api = CleanPay(
            api_key=self.config_entry.runtime_data.api_key,
            userid=self.config_entry.runtime_data.userid,
            client_session=client_session,
        )

        try:
            room_status = await get_room_status(
                api, self.config_entry.runtime_data.srcode
            )
            await room_status.refesh()

            return CleanPayCoordinatorData(room_status=room_status)
        # except IntegrationBlueprintApiClientAuthenticationError as exception:
        #     raise ConfigEntryAuthFailed(exception) from exception
        # except IntegrationBlueprintApiClientError as exception:
        #     raise UpdateFailed(exception) from exception
        except Exception as e:
            raise UpdateFailed(e) from e
