"""Sensor for Steam account status."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, cast

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import SteamConfigEntry
from .const import CONF_ACCOUNTS, STEAM_STATUSES
from .coordinator import SteamDataUpdateCoordinator
from .entity import SteamEntity

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class SteamSensorEntityDescription(SensorEntityDescription):
    """Describes GitHub issue sensor entity."""

    value_fn: Callable[[dict[str, Any]], StateType]

    attr_fn: Callable[[dict[str, Any]], Mapping[str, Any] | None] = lambda data: None
    avabl_fn: Callable[[dict[str, Any]], bool] = lambda data: True


def value_fn(data):
    print("DATAAAA", data)
    return STEAM_STATUSES[cast(int, data["personastate"])]


def avabl_fn(data):
    print("AVABLL", data)
    return True


def attr_fn(data):
    print("ATTR", data)
    return {"some_attr": "foo"}


# def native_value(data):
#     """Return the state of the sensor."""
#     if self.entity_description.key in data:
#         player = self.coordinator.data[self.entity_description.key]
#         return STEAM_STATUSES[cast(int, player["personastate"])]
#     return None


SENSOR_DESCRIPTIONS: tuple[SteamSensorEntityDescription, ...] = (
    SteamSensorEntityDescription(
        key="player_status",
        entity_category=EntityCategory.DIAGNOSTIC,
        # state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: value_fn(data),
        avabl_fn=lambda data: avabl_fn(data),
        attr_fn=lambda data: attr_fn(data),
    ),
    SteamSensorEntityDescription(
        key="player_status_int",
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_unit_of_measurement="Status",
        value_fn=lambda data,: data["personastate"],
        avabl_fn=lambda data: avabl_fn(data),
        attr_fn=lambda data: attr_fn(data),
    ),
)


# {
#     "76561198205352739": {
#         "steamid": "76561198205352739",
#         "communityvisibilitystate": 3,
#         "profilestate": 1,
#         "personaname": "kamekona aka Minuten",
#         "commentpermission": 1,
#         "profileurl": "https://steamcommunity.com/profiles/76561198205352739/",
#         "avatar": "https://avatars.steamstatic.com/893a616823e6ecccb5b6b59005dc32347b772cb3.jpg",
#         "avatarmedium": "https://avatars.steamstatic.com/893a616823e6ecccb5b6b59005dc32347b772cb3_medium.jpg",
#         "avatarfull": "https://avatars.steamstatic.com/893a616823e6ecccb5b6b59005dc32347b772cb3_full.jpg",
#         "avatarhash": "893a616823e6ecccb5b6b59005dc32347b772cb3",
#         "lastlogoff": 1728469345,
#         "personastate": 1,
#         "primaryclanid": "103582791460967173",
#         "timecreated": 1436027260,
#         "personastateflags": 0,
#         "loccountrycode": "SE",
#         "level": 6,
#     },
#     "76561198065467037": {
#         "steamid": "76561198065467037",
#         "communityvisibilitystate": 3,
#         "profilestate": 1,
#         "personaname": "Salmonth",
#         "commentpermission": 1,
#         "profileurl": "https://steamcommunity.com/profiles/76561198065467037/",
#         "avatar": "https://avatars.steamstatic.com/30abfab2155494619dff134b295f2a50b9a15f96.jpg",
#         "avatarmedium": "https://avatars.steamstatic.com/30abfab2155494619dff134b295f2a50b9a15f96_medium.jpg",
#         "avatarfull": "https://avatars.steamstatic.com/30abfab2155494619dff134b295f2a50b9a15f96_full.jpg",
#         "avatarhash": "30abfab2155494619dff134b295f2a50b9a15f96",
#         "lastlogoff": 1728479790,
#         "personastate": 4,
#         "primaryclanid": "103582791463574238",
#         "timecreated": 1339941712,
#         "personastateflags": 0,
#         "level": 21,
#     },
#     "76561198410267685": {
#         "steamid": "76561198410267685",
#         "communityvisibilitystate": 3,
#         "profilestate": 1,
#         "personaname": "Viggan",
#         "profileurl": "https://steamcommunity.com/profiles/76561198410267685/",
#         "avatar": "https://avatars.steamstatic.com/2d0fc1011488211785f5a3133264a51eef6c97a3.jpg",
#         "avatarmedium": "https://avatars.steamstatic.com/2d0fc1011488211785f5a3133264a51eef6c97a3_medium.jpg",
#         "avatarfull": "https://avatars.steamstatic.com/2d0fc1011488211785f5a3133264a51eef6c97a3_full.jpg",
#         "avatarhash": "2d0fc1011488211785f5a3133264a51eef6c97a3",
#         "lastlogoff": 1546651644,
#         "personastate": 0,
#         "primaryclanid": "103582791462575813",
#         "timecreated": 1502041850,
#         "personastateflags": 0,
#         "level": 4,
#     },
# }


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SteamConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Steam platform."""
    async_add_entities(
        (
            SteamSensor(entry.runtime_data, description, account)
            for description in SENSOR_DESCRIPTIONS
            for account in entry.options[CONF_ACCOUNTS]
        ),
    )


class SteamSensor(SteamEntity, SensorEntity):
    """A class for the Steam account."""

    def __init__(
        self,
        coordinator: SteamDataUpdateCoordinator,
        entity_description: SteamSensorEntityDescription,
        account: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self.account_id = account
        # self.entity_description = SensorEntityDescription(
        #     key=account,
        #     name=f"steam_{account}",
        #     icon="mdi:steam",
        # )
        self._attr_unique_id = f"sensor.steam_{account}_{entity_description.key}"

        # self._attr_device_info = DeviceInfo(
        #     identifiers={(DOMAIN, account)},
        #     name=coordinator.data[account]["personaname"],
        #     manufacturer="Steam",
        #     configuration_url=f"https://steamcommunity.com/profiles/{account}",
        #     entry_type=DeviceEntryType.SERVICE,
        # )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            super().available
            and self.coordinator.data is not None
            and self.entity_description.avabl_fn(self.coordinator.data[self.account_id])
        )

    # @property
    # def native_value(self) -> StateType:
    #     """Return the state of the sensor."""
    #     if self.entity_description.key in self.coordinator.data:
    #         player = self.coordinator.data[self.entity_description.key]
    #         return STEAM_STATUSES[cast(int, player["personastate"])]
    #     return None

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data[self.account_id])

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return the extra state attributes."""
        return self.entity_description.attr_fn(self.coordinator.data[self.account_id])

    # @property
    # def extra_state_attributes(self) -> dict[str, str | int | datetime]:
    #     """Return the state attributes of the sensor."""
    #     if self.entity_description.key not in self.coordinator.data:
    #         return {}
    #     player = self.coordinator.data[self.entity_description.key]

    #     attrs: dict[str, str | int | datetime] = {}
    #     if game := player.get("gameextrainfo"):
    #         attrs["game"] = game
    #     if game_id := player.get("gameid"):
    #         attrs["game_id"] = game_id
    #         game_url = f"{STEAM_API_URL}{player['gameid']}/"
    #         attrs["game_image_header"] = f"{game_url}{STEAM_HEADER_IMAGE_FILE}"
    #         attrs["game_image_main"] = f"{game_url}{STEAM_MAIN_IMAGE_FILE}"
    #         if info := self._get_game_icon(player):
    #             attrs["game_icon"] = f"{STEAM_ICON_URL}{game_id}/{info}.jpg"
    #     self._attr_name = str(player["personaname"]) or None
    #     self._attr_entity_picture = str(player["avatarmedium"]) or None
    #     if last_online := cast(int | None, player.get("lastlogoff")):
    #         attrs["last_online"] = utc_from_timestamp(mktime(localtime(last_online)))
    #     if level := self.coordinator.data[self.entity_description.key]["level"]:
    #         attrs["level"] = level

    #     attrs["is_friend"] = (
    #         self.coordinator.config_entry.unique_id != self.entity_description.key
    #     )
    #     return attrs

    def _get_game_icon(self, player: dict) -> str | None:
        """Get game icon identifier."""
        if player.get("gameid") in self.coordinator.game_icons:
            return self.coordinator.game_icons[player["gameid"]]
        # Reset game icons to have coordinator get id for new game
        self.coordinator.game_icons = {}
        return None
