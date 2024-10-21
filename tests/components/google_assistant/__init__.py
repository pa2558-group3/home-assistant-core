"""Tests for the Google Assistant integration."""

from unittest.mock import MagicMock

from homeassistant.components.google_assistant import http
from homeassistant.core import HomeAssistant

from .const import TRAITS, TYPES


def mock_google_config_store(agent_user_ids=None):
    """Fake a storage for google assistant."""
    store = MagicMock(spec=http.GoogleConfigStore)
    if agent_user_ids is not None:
        store.agent_user_ids = agent_user_ids
    else:
        store.agent_user_ids = {}
    return store


class MockConfig(http.GoogleConfig):
    """Fake config that always exposes everything."""

    def __init__(
        self,
        *,
        agent_user_ids=None,
        enabled=True,
        entity_config=None,
        hass: HomeAssistant | None = None,
        secure_devices_pin=None,
        should_2fa=None,
        should_expose=None,
        should_report_state=False,
    ) -> None:
        """Initialize config."""
        super().__init__(hass, None)
        self._enabled = enabled
        self._entity_config = entity_config or {}
        self._secure_devices_pin = secure_devices_pin
        self._should_2fa = should_2fa
        self._should_expose = should_expose
        self._should_report_state = should_report_state
        self._store = mock_google_config_store(agent_user_ids)

    @property
    def enabled(self):
        """Return if Google is enabled."""
        return self._enabled

    @property
    def secure_devices_pin(self):
        """Return secure devices pin."""
        return self._secure_devices_pin

    @property
    def entity_config(self):
        """Return secure devices pin."""
        return self._entity_config

    def get_agent_user_id_from_context(self, context):
        """Get agent user ID making request."""
        return context.user_id

    def should_expose(self, state):
        """Expose it all."""
        return self._should_expose is None or self._should_expose(state)

    @property
    def should_report_state(self):
        """Return if states should be proactively reported."""
        return self._should_report_state

    def should_2fa(self, state):
        """Expose it all."""
        return self._should_2fa is None or self._should_2fa(state)


BASIC_CONFIG = MockConfig()

DEMO_DEVICES = [
    {
        "id": "light.kitchen_lights",
        "name": {"name": "Kitchen Lights"},
        "traits": [
            TRAITS["on_off"],
            TRAITS["brightness"],
            TRAITS["color_setting"],
        ],
        "type": TYPES["light"],
        "willReportState": False,
    },
    {
        "id": "switch.ac",
        "name": {"name": "AC"},
        "traits": [TRAITS["on_off"]],
        "type": TYPES["outlet"],
        "willReportState": False,
    },
    {
        "id": "switch.decorative_lights",
        "name": {"name": "Decorative Lights"},
        "traits": [TRAITS["on_off"]],
        "type": TYPES["switch"],
        "willReportState": False,
    },
    {
        "id": "light.ceiling_lights",
        "name": {
            "name": "Roof Lights",
            "nicknames": ["Roof Lights", "top lights", "ceiling lights"],
        },
        "traits": [
            TRAITS["on_off"],
            TRAITS["brightness"],
            TRAITS["color_setting"],
        ],
        "type": TYPES["light"],
        "willReportState": False,
    },
    {
        "id": "light.bed_light",
        "name": {"name": "Bed Light"},
        "traits": [
            TRAITS["on_off"],
            TRAITS["brightness"],
            TRAITS["color_setting"],
            TRAITS["modes"],
        ],
        "type": TYPES["light"],
        "willReportState": False,
    },
    {
        "id": "cover.living_room_window",
        "name": {"name": "Living Room Window"},
        "traits": [
            TRAITS["start_stop"],
            TRAITS["open_close"],
        ],
        "type": TYPES["blinds"],
        "willReportState": False,
    },
    {
        "id": "cover.pergola_roof",
        "name": {"name": "Pergola Roof"},
        "traits": [
            TRAITS["open_close"],
        ],
        "type": TYPES["blinds"],
        "willReportState": False,
    },
    {
        "id": "cover.hall_window",
        "name": {"name": "Hall Window"},
        "traits": [
            TRAITS["start_stop"],
            TRAITS["open_close"],
        ],
        "type": TYPES["blinds"],
        "willReportState": False,
    },
    {
        "id": "cover.garage_door",
        "name": {"name": "Garage Door"},
        "traits": [TRAITS["open_close"]],
        "type": TYPES["garage"],
        "willReportState": False,
    },
    {
        "id": "cover.kitchen_window",
        "name": {"name": "Kitchen Window"},
        "traits": [
            TRAITS["start_stop"],
            TRAITS["open_close"],
        ],
        "type": TYPES["blinds"],
        "willReportState": False,
    },
    {
        "id": "media_player.bedroom",
        "name": {"name": "Bedroom"},
        "traits": [
            TRAITS["on_off"],
            TRAITS["volume"],
            TRAITS["modes"],
            TRAITS["transport_control"],
            TRAITS["media_state"],
        ],
        "type": TYPES["set_top"],
        "willReportState": False,
    },
    {
        "id": "media_player.kitchen",
        "name": {"name": "Kitchen"},
        "traits": [
            TRAITS["on_off"],
            TRAITS["volume"],
            TRAITS["modes"],
            TRAITS["transport_control"],
            TRAITS["media_state"],
        ],
        "type": TYPES["set_top"],
        "willReportState": False,
    },
    {
        "id": "media_player.living_room",
        "name": {"name": "Living Room"},
        "traits": [
            TRAITS["on_off"],
            TRAITS["volume"],
            TRAITS["modes"],
            TRAITS["transport_control"],
            TRAITS["media_state"],
        ],
        "type": TYPES["set_top"],
        "willReportState": False,
    },
    {
        "id": "media_player.lounge_room",
        "name": {"name": "Lounge room"},
        "traits": [
            TRAITS["input_selector"],
            TRAITS["on_off"],
            TRAITS["modes"],
            TRAITS["transport_control"],
            TRAITS["media_state"],
        ],
        "type": TYPES["tv"],
        "willReportState": False,
    },
    {
        "id": "media_player.walkman",
        "name": {"name": "Walkman"},
        "traits": [
            TRAITS["on_off"],
            TRAITS["volume"],
            TRAITS["modes"],
            TRAITS["transport_control"],
            TRAITS["media_state"],
        ],
        "type": TYPES["set_top"],
        "willReportState": False,
    },
    {
        "id": "media_player.browse",
        "name": {"name": "Browse"},
        "traits": [TRAITS["media_state"], TRAITS["on_off"]],
        "type": TYPES["set_top"],
        "willReportState": False,
    },
    {
        "id": "media_player.group",
        "name": {"name": "Group"},
        "traits": [
            TRAITS["on_off"],
            TRAITS["volume"],
            TRAITS["modes"],
            TRAITS["transport_control"],
            TRAITS["media_state"],
        ],
        "type": TYPES["set_top"],
        "willReportState": False,
    },
    {
        "id": "fan.living_room_fan",
        "name": {"name": "Living Room Fan"},
        "traits": [
            TRAITS["fan_speed"],
            TRAITS["on_off"],
        ],
        "type": TYPES["fan"],
        "willReportState": False,
    },
    {
        "id": "fan.ceiling_fan",
        "name": {"name": "Ceiling Fan"},
        "traits": [
            TRAITS["fan_speed"],
            TRAITS["on_off"],
        ],
        "type": TYPES["fan"],
        "willReportState": False,
    },
    {
        "id": "fan.percentage_full_fan",
        "name": {"name": "Percentage Full Fan"},
        "traits": [TRAITS["fan_speed"], TRAITS["on_off"]],
        "type": TYPES["fan"],
        "willReportState": False,
    },
    {
        "id": "fan.percentage_limited_fan",
        "name": {"name": "Percentage Limited Fan"},
        "traits": [TRAITS["fan_speed"], TRAITS["on_off"]],
        "type": TYPES["fan"],
        "willReportState": False,
    },
    {
        "id": "fan.preset_only_limited_fan",
        "name": {"name": "Preset Only Limited Fan"},
        "traits": [
            TRAITS["on_off"],
            TRAITS["modes"],
        ],
        "type": TYPES["fan"],
        "willReportState": False,
    },
    {
        "id": "climate.hvac",
        "name": {"name": "Hvac"},
        "traits": [
            TRAITS["on_off"],
            TRAITS["temperature_setting"],
            TRAITS["fan_speed"],
        ],
        "type": TYPES["thermostat"],
        "willReportState": False,
        "attributes": {
            "availableThermostatModes": [
                "off",
                "heat",
                "cool",
                "heatcool",
                "auto",
                "dry",
                "fan-only",
            ],
            "thermostatTemperatureUnit": "C",
        },
    },
    {
        "id": "climate.heatpump",
        "name": {"name": "HeatPump"},
        "traits": [
            TRAITS["on_off"],
            TRAITS["temperature_setting"],
        ],
        "type": TYPES["thermostat"],
        "willReportState": False,
    },
    {
        "id": "climate.ecobee",
        "name": {"name": "Ecobee"},
        "traits": [
            TRAITS["on_off"],
            TRAITS["temperature_setting"],
            TRAITS["fan_speed"],
        ],
        "type": TYPES["thermostat"],
        "willReportState": False,
    },
    {
        "id": "humidifier.humidifier",
        "name": {"name": "Humidifier"},
        "traits": [
            TRAITS["humidity_setting"],
            TRAITS["on_off"],
        ],
        "type": TYPES["humidifier"],
        "willReportState": False,
        "attributes": {"humiditySetpointRange": {"minPercent": 0, "maxPercent": 100}},
    },
    {
        "id": "humidifier.dehumidifier",
        "name": {"name": "Dehumidifier"},
        "traits": [
            TRAITS["humidity_setting"],
            TRAITS["on_off"],
        ],
        "type": TYPES["dehumidifier"],
        "willReportState": False,
        "attributes": {"humiditySetpointRange": {"minPercent": 0, "maxPercent": 100}},
    },
    {
        "id": "humidifier.hygrostat",
        "name": {"name": "Hygrostat"},
        "traits": [
            TRAITS["humidity_setting"],
            TRAITS["modes"],
            TRAITS["on_off"],
        ],
        "type": TYPES["humidifier"],
        "willReportState": False,
        "attributes": {"humiditySetpointRange": {"minPercent": 0, "maxPercent": 100}},
    },
    {
        "id": "lock.front_door",
        "name": {"name": "Front Door"},
        "traits": [TRAITS["lock_unlock"]],
        "type": TYPES["lock"],
        "willReportState": False,
    },
    {
        "id": "lock.kitchen_door",
        "name": {"name": "Kitchen Door"},
        "traits": [TRAITS["lock_unlock"]],
        "type": TYPES["lock"],
        "willReportState": False,
    },
    {
        "id": "lock.openable_lock",
        "name": {"name": "Openable Lock"},
        "traits": [TRAITS["lock_unlock"]],
        "type": TYPES["lock"],
        "willReportState": False,
    },
    {
        "id": "lock.poorly_installed_door",
        "name": {"name": "Poorly Installed Door"},
        "traits": [TRAITS["lock_unlock"]],
        "type": TYPES["lock"],
        "willReportState": False,
    },
    {
        "id": "alarm_control_panel.security",
        "name": {"name": "Security"},
        "traits": [TRAITS["arm_disarm"]],
        "type": TYPES["securitysystem"],
        "willReportState": False,
    },
    {
        "id": "light.living_room_rgbww_lights",
        "name": {"name": "Living Room RGBWW Lights"},
        "traits": [
            TRAITS["on_off"],
            TRAITS["brightness"],
            TRAITS["color_setting"],
        ],
        "type": TYPES["light"],
        "willReportState": False,
    },
    {
        "id": "light.office_rgbw_lights",
        "name": {"name": "Office RGBW Lights"},
        "traits": [
            TRAITS["on_off"],
            TRAITS["brightness"],
            TRAITS["color_setting"],
        ],
        "type": TYPES["light"],
        "willReportState": False,
    },
    {
        "id": "light.entrance_color_white_lights",
        "name": {"name": "Entrance Color + White Lights"},
        "traits": [
            TRAITS["on_off"],
            TRAITS["brightness"],
            TRAITS["color_setting"],
        ],
        "type": TYPES["light"],
        "willReportState": False,
    },
]
