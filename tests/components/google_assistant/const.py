"""Constants for the Google Assistant integration."""

TRAITS = {
    "on_off": "action.devices.traits.OnOff",
    "brightness": "action.devices.traits.Brightness",
    "color_setting": "action.devices.traits.ColorSetting",
    "modes": "action.devices.traits.Modes",
    "transport_control": "action.devices.traits.TransportControl",
    "media_state": "action.devices.traits.MediaState",
    "volume": "action.devices.traits.Volume",
    "input_selector": "action.devices.traits.InputSelector",
    "fan_speed": "action.devices.traits.FanSpeed",
    "temperature_setting": "action.devices.traits.TemperatureSetting",
    "humidity_setting": "action.devices.traits.HumiditySetting",
    "lock_unlock": "action.devices.traits.LockUnlock",
    "arm_disarm": "action.devices.traits.ArmDisarm",
    "start_stop": "action.devices.traits.StartStop",
    "open_close": "action.devices.traits.OpenClose",
}


TYPES = {
    "light": "action.devices.types.LIGHT",
    "outlet": "action.devices.types.OUTLET",
    "switch": "action.devices.types.SWITCH",
    "blinds": "action.devices.types.BLINDS",
    "garage": "action.devices.types.GARAGE",
    "set_top": "action.devices.types.SETTOP",
    "tv": "action.devices.types.TV",
    "fan": "action.devices.types.FAN",
    "thermostat": "action.devices.types.THERMOSTAT",
    "humidifier": "action.devices.types.HUMIDIFIER",
    "dehumidifier": "action.devices.types.DEHUMIDIFIER",
    "lock": "action.devices.types.LOCK",
    "securitysystem": "action.devices.types.SECURITYSYSTEM",
}
