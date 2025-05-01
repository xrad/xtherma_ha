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
class XtSensorEntityDescription(SensorEntityDescription):
    """Abstract base class."""

    factor: float | None = None
    icon_provider: SensorIconProvider | None = None


type BinaryIconProvider = Callable[[bool | None], str]


@dataclass(kw_only=True, frozen=True)
class XtBinarySensorEntityDescription(BinarySensorEntityDescription):
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
        key="tvl",
        name="[TVL] Vorlauftemperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor=0.1,
        icon=_icon_heating_in,
    ),
    XtSensorEntityDescription(
        key="trl",
        name="[TRL] Rücklauftemperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor=0.1,
        icon=_icon_heating_out,
    ),
    XtSensorEntityDescription(
        key="tw",
        name="[TW] Warmwassertemperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor=0.1,
        icon=_icon_temperature_water,
    ),
    XtSensorEntityDescription(
        key="tk",
        name="[TK] Heiz-/ Kühltemperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor=0.1,
        icon=_icon_temperature,
    ),
    XtSensorEntityDescription(
        key="tk1",
        name="[TK1] Kreis 1 Temperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor=0.1,
        icon=_icon_temperature,
    ),
    XtSensorEntityDescription(
        key="tk2",
        name="[TK2] Kreis 2 Temperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor=0.1,
        icon=_icon_temperature,
    ),
    XtSensorEntityDescription(
        key="vf",
        name="Verdichter Frequenz",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        icon=_icon_frequency,
    ),
    XtSensorEntityDescription(
        key="ta",
        name="[TA] Außentemperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor=0.1,
        icon=_icon_temperature,
    ),
    XtSensorEntityDescription(
        key="ta1",
        name="[TA1] Außentemperatur Mittelwert 1h",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor=0.1,
        icon=_icon_temperature_average,
    ),
    XtSensorEntityDescription(
        key="ta4",
        name="[TA4] Außentemperatur Mittelwert 4h",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor=0.1,
        icon=_icon_temperature_average,
    ),
    XtSensorEntityDescription(
        key="ta24",
        name="[TA24] Außentemperatur Mittelwert 24h",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor=0.1,
        icon=_icon_temperature_average,
    ),
    XtSensorEntityDescription(
        key="ld1",
        name="[LD1] Lüfter 1 Drehzahl",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        icon=_icon_fan,
    ),
    XtSensorEntityDescription(
        key="ld2",
        name="[LD2] Lüfter 2 Drehzahl",
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        icon=_icon_fan,
    ),
    XtSensorEntityDescription(
        key="tr",
        name="[TR] Raumtemperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor=0.1,
        icon=_icon_temperature,
    ),
    XtBinarySensorEntityDescription(
        key="evu",
        name="EVU Status",
        icon_provider=_electric_switch_icon,
    ),
    XtBinarySensorEntityDescription(
        key="pk",
        name="[PK] Umwälzpumpe eingeschaltet",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon_provider=_pump_icon,
    ),
    XtBinarySensorEntityDescription(
        key="pk1",
        name="[PK1] Umwälzpumpe Kreis 1 eingeschaltet",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon_provider=_pump_icon,
    ),
    XtBinarySensorEntityDescription(
        key="pk2",
        name="[PK2] Umwälzpumpe Kreis 2 eingeschaltet",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon_provider=_pump_icon,
    ),
    XtBinarySensorEntityDescription(
        key="pww",
        name="[PWW] Zirkulationspumpe Warmwasser eingeschaltet",
        device_class=BinarySensorDeviceClass.RUNNING,
        icon_provider=_pump_icon,
    ),
    XtSensorEntityDescription(
        key="hw_target",
        name="Sollwert Warmwasserbereitung",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor=0.1,
        icon=_icon_temperature_target_water,
    ),
    XtSensorEntityDescription(
        key="h_target",
        name="Sollwert Heizbetrieb",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor=0.1,
        icon=_icon_temperature_target_heating,
    ),
    XtSensorEntityDescription(
        key="c_target",
        name="Sollwert Kühlbetrieb",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor=0.1,
        icon=_icon_temperature_target_cooling,
    ),
    XtSensorEntityDescription(
        key="in_hp",
        name="Leistungsaufnahme Wärmepumpe (elektrisch)",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon=_icon_electric_power,
    ),
    XtSensorEntityDescription(
        key="v",
        name="[V] Volumenstrom",
        native_unit_of_measurement=UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        factor=0.1,
        icon=_icon_volume_rate,
    ),
    XtSensorEntityDescription(
        key="out_hp",
        name="Leistungsabgabe Wärmepumpe (thermisch)",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon=_icon_thermal_power,
    ),
    XtSensorEntityDescription(
        key="efficiency_hp",
        name="Leistungszahl Wärmepumpe",
        state_class=SensorStateClass.MEASUREMENT,
        factor=0.01,
        icon=_icon_performance,
    ),
    XtSensorEntityDescription(
        key="efficiency_total",
        name="Leistungszahl Gesamtsystem (inkl. Zusatzheizing)",
        state_class=SensorStateClass.MEASUREMENT,
        factor=0.01,
        icon=_icon_performance,
    ),
    XtSensorEntityDescription(
        key="in_backup",
        name="Leistungsaufnahme Zusatz-/Notheizung (elektrisch)",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon=_icon_electric_power,
    ),
    XtSensorEntityDescription(
        key="out_backup",
        name="Leistungsabgabe Zusatz-/Notheizung (thermisch)",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon=_icon_thermal_power,
    ),
    XtSensorEntityDescription(
        key="mode_3",
        name="Betriebsmodus",
        device_class=SensorDeviceClass.ENUM,
        options=_opmode_options,
        icon_provider=_operation_mode_icon,
        translation_key="mode_3",
    ),
    XtSensorEntityDescription(
        key="ta8",
        name="[TA8] Außentemperatur Mittelwert 8h",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        factor=0.1,
        icon=_icon_temperature_average,
    ),
    XtSensorEntityDescription(
        key="sg",
        name="SG-Ready Status",
        device_class=SensorDeviceClass.ENUM,
        options=_sgready_options,
        icon_provider=_sgready_icon,
        translation_key="sgready",
    ),
    XtSensorEntityDescription(
        key="day_hp_out_h",
        name="Tag Heizbetrieb thermische Leistungsabgabe",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_thermal_power,
    ),
    XtSensorEntityDescription(
        key="day_hp_out_c",
        name="Tag Kühlbetrieb thermische Leistungsabgabe",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_thermal_power,
    ),
    XtSensorEntityDescription(
        key="day_hp_out_hw",
        name="Tag Warmwasserbetrieb thermische Leistungsabgabe",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_thermal_power,
    ),
    XtSensorEntityDescription(
        key="day_backup3_out_h",
        name="Tag Heizbetrieb Zusatzheizung Stufe 1 (3 kW) thermische Leistungsabgabe",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_thermal_power,
    ),
    XtSensorEntityDescription(
        key="day_backup6_out_h",
        name="Tag Heizbetrieb Zusatzheizung Stufe 2 (6 kW) thermische Leistungsabgabe",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_thermal_power,
    ),
    XtSensorEntityDescription(
        key="day_backup6_out_hw",
        name="Tag Warmwasserbetrieb Zusatzheizung Stufe 2 (6 kW) thermische Leistungsabgabe",  # noqa: E501
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_thermal_power,
    ),
    XtSensorEntityDescription(
        key="day_backup3_out_hw",
        name="Tag Warmwasserbetrieb Zusatzheizung Stufe 1 (3 kW) thermische Leistungsabgabe",  # noqa: E501
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_thermal_power,
    ),
    XtSensorEntityDescription(
        key="day_hp_in_h",
        name="Tag Heizbetrieb elektrische Leistungsaufnahme",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_electric_power,
    ),
    XtSensorEntityDescription(
        key="day_hp_in_c",
        name="Tag Kühlbetrieb elektrische Leistungsaufnahme",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_electric_power,
    ),
    XtSensorEntityDescription(
        key="day_hp_in_hw",
        name="Tag Warmwasserbetrieb elektrische Leistungsaufnahme",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_electric_power,
    ),
    XtSensorEntityDescription(
        key="day_backup3_in_hw",
        name="Tag Warmwasserbetrieb Zusatzheizung Stufe 1 (3 kW) elektrische Leistungsaufnahme",  # noqa: E501
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_electric_power,
    ),
    XtSensorEntityDescription(
        key="day_backup6_in_hw",
        name="Tag Warmwasserbetrieb Zusatzheizung Stufe 2 (6 kW) elektrische Leistungsaufnahme",  # noqa: E501
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_electric_power,
    ),
    XtSensorEntityDescription(
        key="day_backup3_in_h",
        name="Tag Heizbetrieb Zusatzheizung Stufe 1 (3 kW) elektrische Leistungsaufnahme",  # noqa: E501
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_electric_power,
    ),
    XtSensorEntityDescription(
        key="day_backup6_in_h",
        name="Tag Heizbetrieb Zusatzheizung Stufe 2 (6 kW) elektrische Leistungsaufnahme",  # noqa: E501
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon=_icon_electric_power,
    ),
]
