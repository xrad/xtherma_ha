"""Sensor descriptions."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    REVOLUTIONS_PER_MINUTE,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfVolumeFlowRate,
)
from homeassistant.helpers.typing import StateType

type SensorIconProvider = Callable[[StateType | date | datetime | Decimal], str]


@dataclass(kw_only=True, frozen=True)
class XtModbusEntityDescription:
    """Manage properties related to Modbus."""

    modbus_index: int = -1

@dataclass(kw_only=True, frozen=True)
class XtSensorEntityDescription(XtModbusEntityDescription, SensorEntityDescription):
    """A numeric value sensor."""

    factor: str | None = None
    icon_provider: SensorIconProvider | None = None


type BinaryIconProvider = Callable[[bool | None], str]


@dataclass(kw_only=True, frozen=True)
class XtBinarySensorEntityDescription(
    XtModbusEntityDescription, BinarySensorEntityDescription):
    """A binary sensor."""

    icon_provider: BinaryIconProvider | None = None


def _electric_switch_icon(state: bool | None) -> str:
    if state:
        return "mdi:electric-switch"
    return "mdi:electric-switch-closed"


def _pump_icon(state: bool | None) -> str:
    if state:
        return "mdi:pump"
    return "mdi:pump-off"


_opmode_options = ["standby", "heating", "cooling", "water", "auto"]

_opmode_icon_map = {
    0: "mdi:power-standby",
    1: "mdi:heating-coil",
    2: "mdi:snowflake",
    3: "mdi:thermometer-water",
    4: "mdi:brightness-auto",
}


def _operation_mode_icon(state: StateType | date | datetime | Decimal) -> str:
    if isinstance(state, str):
        try:
            index = _opmode_options.index(state)
            return _opmode_icon_map.get(index, "mdi:cogs")
        except ValueError:
            pass
    return "mdi:cogs"


"""
see also https://www.waermepumpe.de/normen-technik/sg-ready/
0: Nicht aktiviert

1: Betriebszustand 2: Normalbetrieb
   Klemme 0/0
   Anteilige Wärmespeicher-Füllung für die maximal zweistündige EVU-Sperre

2: Betriebszustand 1: Sperre
   Klemme 1/0
   Maximal zwei Stunden „harte“ Sperrzeit

3: Betriebszustand 3: Temperaturen anheben
   Klemme 0/1
   Verstärkter Betrieb für Raumheizung und Warmwasserbereitung

4: Betriebszustand 4: Anlaufbefehl
   Klemme 1/1
   Variante 1: Die Wärmepumpe (Verdichter) wird aktiv eingeschaltet.
   Variante 2: Die Wärmepumpe (Verdichter und elektrische Zusatzheizungen) wird aktiv
               eingeschaltet, optional: höhere Temperatur in den Wärmespeichern
"""

_sgready_options = ["off", "normal", "block", "raise", "start"]

_sgready_icon_map = {
    0: "mdi:cancel",  # "Kein Eingriff
    1: "mdi:circle",  # Normalbetrieb
    2: "mdi:circle-double",  # Sperre
    3: "mdi:thermometer-plus",  # Temperaturen anheben
    4: "mdi:home-thermometer",  # Anlaufbefehl
}


def _sgready_icon(state: StateType | date | datetime | Decimal) -> str:
    if isinstance(state, str):
        try:
            index = _sgready_options.index(state)
            return _sgready_icon_map.get(index, "mdi:cogs")
        except ValueError:
            pass
    return "mdi:cogs"


_icon_electric_power = "mdi:lightning-bolt"
_icon_thermal_power = "mdi:heat-wave"
_icon_temperature = "mdi:thermometer"
_icon_temperature_water = "mdi:thermometer-water"
_icon_temperature_average = "mdi:thermometer-auto"
_icon_frequency = "mdi:sine-wave"
_icon_heating_in = "mdi:thermometer-chevron-up"
_icon_heating_out = "mdi:thermometer-chevron-down"
_icon_fan = "mdi:fan"
_icon_temperature_target_water = "mdi:thermometer-water"
_icon_temperature_target_heating = "mdi:home-thermometer-outline"
_icon_temperature_target_cooling = "mdi:snowflake-thermometer"
_icon_volume_rate = "mdi:waves-arrow-right"
_icon_performance = "mdi:poll"

SENSOR_DESCRIPTIONS = [
    XtSensorEntityDescription(
        modbus_index=2,
        key="tvl",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor="/10",
        icon=_icon_heating_in,
    ),
    XtSensorEntityDescription(
        modbus_index=3,
        key="trl",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor="/10",
        icon=_icon_heating_out,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="tw",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor="/10",
        icon=_icon_temperature_water,
    ),
    XtSensorEntityDescription(
        modbus_index=4,
        key="tk",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor="/10",
        icon=_icon_temperature,
    ),
    XtSensorEntityDescription(
        modbus_index=5,
        key="tk1",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor="/10",
        icon=_icon_temperature,
    ),
    XtSensorEntityDescription(
        modbus_index=6,
        key="tk2",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor="/10",
        icon=_icon_temperature,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="vf",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        icon=_icon_frequency,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="ta",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor="/10",
        icon=_icon_temperature,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="ta1",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor="/10",
        icon=_icon_temperature_average,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="ta4",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor="/10",
        icon=_icon_temperature_average,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="ta24",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor="/10",
        icon=_icon_temperature_average,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="ld1",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        icon=_icon_fan,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="ld2",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        icon=_icon_fan,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="tr",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor="/10",
        icon=_icon_temperature,
    ),
    XtBinarySensorEntityDescription(
        modbus_index=0,
        key="evu",
        icon_provider=_electric_switch_icon,
    ),
    XtBinarySensorEntityDescription(
        modbus_index=0,
        key="pk",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon_provider=_pump_icon,
    ),
    XtBinarySensorEntityDescription(
        modbus_index=0,
        key="pk1",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon_provider=_pump_icon,
    ),
    XtBinarySensorEntityDescription(
        modbus_index=0,
        key="pk2",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon_provider=_pump_icon,
    ),
    XtBinarySensorEntityDescription(
        modbus_index=0,
        key="pww",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon_provider=_pump_icon,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="hw_target",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor="/10",
        icon=_icon_temperature_target_water,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="h_target",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor="/10",
        icon=_icon_temperature_target_heating,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="c_target",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor="/10",
        icon=_icon_temperature_target_cooling,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="in_hp",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon=_icon_electric_power,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="v",
        native_unit_of_measurement=UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        factor="/10",
        icon=_icon_volume_rate,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="out_hp",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon=_icon_thermal_power,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="efficiency_hp",
        state_class=SensorStateClass.MEASUREMENT,
        factor="/100",
        icon=_icon_performance,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="efficiency_total",
        state_class=SensorStateClass.MEASUREMENT,
        factor="/100",
        icon=_icon_performance,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="in_backup",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon=_icon_electric_power,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="out_backup",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon=_icon_thermal_power,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="mode_3",
        device_class=SensorDeviceClass.ENUM,
        options=_opmode_options,
        icon_provider=_operation_mode_icon,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="ta8",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor="/10",
        icon=_icon_temperature_average,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="sg",
        device_class=SensorDeviceClass.ENUM,
        options=_sgready_options,
        icon_provider=_sgready_icon,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="day_hp_out_h",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_thermal_power,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="day_hp_out_c",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_thermal_power,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="day_hp_out_hw",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_thermal_power,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="day_backup3_out_h",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_thermal_power,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="day_backup6_out_h",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_thermal_power,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="day_backup6_out_hw",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_thermal_power,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="day_backup3_out_hw",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_thermal_power,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="day_hp_in_h",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_electric_power,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="day_hp_in_c",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_electric_power,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="day_hp_in_hw",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_electric_power,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="day_backup3_in_hw",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_electric_power,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="day_backup6_in_hw",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_electric_power,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="day_backup3_in_h",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_electric_power,
    ),
    XtSensorEntityDescription(
        modbus_index=0,
        key="day_backup6_in_h",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_electric_power,
    ),
]
