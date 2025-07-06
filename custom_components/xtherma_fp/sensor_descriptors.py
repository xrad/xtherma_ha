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
    PERCENTAGE,
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
    low_active: bool = False


def _electric_switch_icon(state: bool | None) -> str:  # noqa: FBT001
    if state:
        return "mdi:electric-switch"
    return "mdi:electric-switch-closed"


def _pump_on_off_icon(state: bool | None) -> str:  # noqa: FBT001
    if state:
        return "mdi:pump"
    return "mdi:pump-off"

def _error_icon(state: bool | None) -> str:  # noqa: FBT001
    if state:
        return "mdi:alert"
    return "mdi:check"


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
_icon_pump = "mdi:pump"
_icon_hot_water = "mdi:water-boiler"
_icon_heating = "mdi:heating-coil"
_icon_cooling = "mdi:snowflake"

_sensor_tvl = XtSensorEntityDescription(
    key="tvl",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_heating_in,
)
_sensor_trl = XtSensorEntityDescription(
    key="trl",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_heating_out,
)
_sensor_tw = XtSensorEntityDescription(
    key="tw",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature_water,
)
_sensor_tk = XtSensorEntityDescription(
    key="tk",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature,
)
_sensor_tk1 = XtSensorEntityDescription(
    key="tk1",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature,
)
_sensor_tk2 = XtSensorEntityDescription(
    key="tk2",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature,
)
_sensor_vf = XtSensorEntityDescription(
    key="vf",
    native_unit_of_measurement=UnitOfFrequency.HERTZ,
    device_class=SensorDeviceClass.FREQUENCY,
    state_class=SensorStateClass.MEASUREMENT,
    suggested_display_precision=0,
    icon=_icon_frequency,
)
_sensor_ta = XtSensorEntityDescription(
    key="ta",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature,
)
_sensor_ta1 = XtSensorEntityDescription(
    key="ta1",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature_average,
)
_sensor_ta4 = XtSensorEntityDescription(
    key="ta4",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature_average,
)
_sensor_ta24 = XtSensorEntityDescription(
    key="ta24",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature_average,
)
_sensor_ld1 = XtSensorEntityDescription(
    key="ld1",
    native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
    state_class=SensorStateClass.MEASUREMENT,
    suggested_display_precision=0,
    icon=_icon_fan,
)
_sensor_ld2 = XtSensorEntityDescription(
    key="ld2",
    native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
    state_class=SensorStateClass.MEASUREMENT,
    suggested_display_precision=0,
    icon=_icon_fan,
)
_sensor_tr = XtSensorEntityDescription(
    key="tr",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature,
)
_sensor_evu = XtBinarySensorEntityDescription(
    key="evu",
    icon_provider=_electric_switch_icon,
)
_sensor_pk = XtBinarySensorEntityDescription(
    key="pk",
    device_class=BinarySensorDeviceClass.RUNNING,
    icon_provider=_pump_on_off_icon,
)
_sensor_pk_amount = XtSensorEntityDescription(
    key="pk_amount",
    factor="/10",
    native_unit_of_measurement=PERCENTAGE,
    device_class=None,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_pump,
)
_sensor_pk1 = XtBinarySensorEntityDescription(
    key="pk1",
    device_class=BinarySensorDeviceClass.RUNNING,
    icon_provider=_pump_on_off_icon,
)
_sensor_pk2 = XtBinarySensorEntityDescription(
    key="pk2",
    device_class=BinarySensorDeviceClass.RUNNING,
    icon_provider=_pump_on_off_icon,
)
_sensor_pww = XtBinarySensorEntityDescription(
    key="pww",
    device_class=BinarySensorDeviceClass.RUNNING,
    icon_provider=_pump_on_off_icon,
)
_sensor_hw_target = XtSensorEntityDescription(
    key="hw_target",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_temperature_target_water,
)
_sensor_hw_keep_target = XtSensorEntityDescription(
    key="hw_keep_target",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_temperature_target_water,
)
_sensor_h_target = XtSensorEntityDescription(
    key="h_target",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature_target_heating,
)
_sensor_h1_target = XtSensorEntityDescription(
    key="h1_target",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature_target_heating,
)
_sensor_h2_target = XtSensorEntityDescription(
    key="h2_target",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature_target_heating,
)
_sensor_c_target = XtSensorEntityDescription(
    key="c_target",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature_target_cooling,
)
_sensor_c1_target = XtSensorEntityDescription(
    key="c1_target",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature_target_cooling,
)
_sensor_c2_target = XtSensorEntityDescription(
    key="c2_target",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature_target_cooling,
)
_sensor_in_hp = XtSensorEntityDescription(
    key="in_hp",
    native_unit_of_measurement=UnitOfPower.WATT,
    device_class=SensorDeviceClass.POWER,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_electric_power,
)
_sensor_v = XtSensorEntityDescription(
    key="v",
    native_unit_of_measurement=UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
    device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_volume_rate,
)
_sensor_out_hp = XtSensorEntityDescription(
    key="out_hp",
    native_unit_of_measurement=UnitOfPower.WATT,
    device_class=SensorDeviceClass.POWER,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_thermal_power,
)
_sensor_efficiency_hp = XtSensorEntityDescription(
    key="efficiency_hp",
    state_class=SensorStateClass.MEASUREMENT,
    factor="/100",
    icon=_icon_performance,
)
_sensor_efficiency_total = XtSensorEntityDescription(
    key="efficiency_total",
    state_class=SensorStateClass.MEASUREMENT,
    factor="/100",
    icon=_icon_performance,
)
_sensor_in_backup = XtSensorEntityDescription(
    key="in_backup",
    native_unit_of_measurement=UnitOfPower.WATT,
    device_class=SensorDeviceClass.POWER,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_electric_power,
)
_sensor_out_backup = XtSensorEntityDescription(
    key="out_backup",
    native_unit_of_measurement=UnitOfPower.WATT,
    device_class=SensorDeviceClass.POWER,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_thermal_power,
)
_sensor_mode_3 = XtSensorEntityDescription(
    key="mode_3",
    device_class=SensorDeviceClass.ENUM,
    options=_opmode_options,
    icon_provider=_operation_mode_icon,
)
_sensor_ta8 = XtSensorEntityDescription(
    key="ta8",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    factor="/10",
    icon=_icon_temperature_average,
)
_sensor_sg = XtSensorEntityDescription(
    key="sg",
    device_class=SensorDeviceClass.ENUM,
    options=_sgready_options,
    icon_provider=_sgready_icon,
)
_sensor_day_hp_out_h = XtSensorEntityDescription(
    key="day_hp_out_h",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_thermal_power,
)
_sensor_day_hp_out_c = XtSensorEntityDescription(
    key="day_hp_out_c",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_thermal_power,
)
_sensor_day_hp_out_hw = XtSensorEntityDescription(
    key="day_hp_out_hw",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_thermal_power,
)
_sensor_day_backup3_out_h = XtSensorEntityDescription(
    key="day_backup3_out_h",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_thermal_power,
)
_sensor_day_backup6_out_h = XtSensorEntityDescription(
    key="day_backup6_out_h",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_thermal_power,
)
_sensor_day_backup6_out_hw = XtSensorEntityDescription(
    key="day_backup6_out_hw",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_thermal_power,
)
_sensor_day_backup3_out_hw = XtSensorEntityDescription(
    key="day_backup3_out_hw",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_thermal_power,
)
_sensor_day_hp_in_h = XtSensorEntityDescription(
    key="day_hp_in_h",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_electric_power,
)
_sensor_day_hp_in_c = XtSensorEntityDescription(
    key="day_hp_in_c",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_electric_power,
)
_sensor_day_hp_in_hw = XtSensorEntityDescription(
    key="day_hp_in_hw",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_electric_power,
)
_sensor_day_backup3_in_hw = XtSensorEntityDescription(
    key="day_backup3_in_hw",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_electric_power,
)
_sensor_day_backup6_in_hw = XtSensorEntityDescription(
    key="day_backup6_in_hw",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_electric_power,
)
_sensor_day_backup3_in_h = XtSensorEntityDescription(
    key="day_backup3_in_h",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_electric_power,
)
_sensor_day_backup6_in_h = XtSensorEntityDescription(
    key="day_backup6_in_h",
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    icon=_icon_electric_power,
)
_sensor_system_active = XtBinarySensorEntityDescription(
    key="system_active",
    device_class=BinarySensorDeviceClass.POWER,
)
_sensor_sw_version = XtSensorEntityDescription(
    key="sw_version",
    icon="mdi:information-outline",
)
_sensor_hotwater_now = XtBinarySensorEntityDescription(
    key="hotwater_now",
    device_class=BinarySensorDeviceClass.RUNNING,
    icon=_icon_hot_water,
)
_sensor_hk1_enabled = XtBinarySensorEntityDescription(
    key="hk1_enabled",
    device_class=BinarySensorDeviceClass.RUNNING,
    icon=_icon_heating,
)
_sensor_hk1_ta_p1 = XtSensorEntityDescription(
    key="hk1_ta_p1",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_temperature,
)
_sensor_hk1_ta_p2 = XtSensorEntityDescription(
    key="hk1_ta_p2",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_temperature,
)
_sensor_hk1_target_p1 = XtSensorEntityDescription(
    key="hk1_target_p1",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_temperature,
)
_sensor_hk1_target_p2 = XtSensorEntityDescription(
    key="hk1_target_p2",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_temperature,
)
_sensor_hk1_h_target_const = XtSensorEntityDescription(
    key="hk1_h_target_const",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_temperature,
)
_sensor_hk2_enabled = XtBinarySensorEntityDescription(
    key="hk2_enabled",
    device_class=BinarySensorDeviceClass.RUNNING,
    icon=_icon_heating,
)
_sensor_hk2_ta_p1 = XtSensorEntityDescription(
    key="hk2_ta_p1",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_temperature,
)
_sensor_hk2_ta_p2 = XtSensorEntityDescription(
    key="hk2_ta_p2",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_temperature,
)
_sensor_hk2_target_p1 = XtSensorEntityDescription(
    key="hk2_target_p1",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_temperature,
)
_sensor_hk2_target_p2 = XtSensorEntityDescription(
    key="hk2_target_p2",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_temperature,
)
_sensor_hk2_h_target_const = XtSensorEntityDescription(
    key="hk2_h_target_const",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_temperature,
)
_sensor_kk1_enabled = XtBinarySensorEntityDescription(
    key="kk1_enabled",
    device_class=BinarySensorDeviceClass.RUNNING,
    icon=_icon_cooling,
)
_sensor_kk1_ta_p1 = XtSensorEntityDescription(
    key="kk1_ta_p1",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_temperature,
)
_sensor_kk1_ta_p2 = XtSensorEntityDescription(
    key="kk1_ta_p2",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_temperature,
)
_sensor_kk1_target_p1 = XtSensorEntityDescription(
    key="kk1_target_p1",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_temperature,
)
_sensor_kk1_target_p2 = XtSensorEntityDescription(
    key="kk1_target_p2",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_temperature,
)
_sensor_kk1_c_target_const = XtSensorEntityDescription(
    key="kk1_c_target_const",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_temperature,
)
_sensor_kk2_enabled = XtBinarySensorEntityDescription(
    key="kk2_enabled",
    device_class=BinarySensorDeviceClass.RUNNING,
    icon=_icon_cooling,
)
_sensor_kk2_ta_p1 = XtSensorEntityDescription(
    key="kk2_ta_p1",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_temperature,
)
_sensor_kk2_ta_p2 = XtSensorEntityDescription(
    key="kk2_ta_p2",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_temperature,
)
_sensor_kk2_target_p1 = XtSensorEntityDescription(
    key="kk2_target_p1",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_temperature,
)
_sensor_kk2_target_p2 = XtSensorEntityDescription(
    key="kk2_target_p2",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_temperature,
)
_sensor_kk2_c_target_const = XtSensorEntityDescription(
    key="kk2_c_target_const",
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    icon=_icon_temperature,
)
_sensor_error = XtBinarySensorEntityDescription(
    key="error",
    device_class=BinarySensorDeviceClass.RUNNING,
    icon_provider=_error_icon,
    low_active=True,
)


@dataclass(kw_only=True, frozen=True)
class ModbusRegisterSet:
    """Register set."""

    base: int
    descriptors: list[XtSensorEntityDescription|XtBinarySensorEntityDescription|None]


MODBUS_SENSORS_GENERAL_STATE = ModbusRegisterSet(
    base=0,
    descriptors=[
        _sensor_system_active,
        _sensor_mode_3,
        _sensor_hotwater_now,
    ],
)

MODBUS_SENSORS_HEATING_CURVE_1 = ModbusRegisterSet(
    base=10,
    descriptors=[
        _sensor_hk1_enabled,
        _sensor_hk1_ta_p1,
        _sensor_hk1_ta_p2,
        _sensor_hk1_target_p1,
        _sensor_hk1_target_p2,
        _sensor_hk1_h_target_const,
    ],
)

MODBUS_SENSORS_COOLING_CURVE_1 = ModbusRegisterSet(
    base=20,
    descriptors=[
        _sensor_kk1_enabled,
        _sensor_kk1_ta_p1,
        _sensor_kk1_ta_p2,
        _sensor_kk1_target_p1,
        _sensor_kk1_target_p2,
        _sensor_kk1_c_target_const,
    ],
)

MODBUS_SENSORS_HEATING_CURVE_2 = ModbusRegisterSet(
    base=30,
    descriptors=[
        _sensor_hk2_enabled,
        _sensor_hk2_ta_p1,
        _sensor_hk2_ta_p2,
        _sensor_hk2_target_p1,
        _sensor_hk2_target_p2,
        _sensor_hk2_h_target_const,
        _sensor_kk2_enabled,
    ],
)

MODBUS_SENSORS_COOLING_CURVE_2 = ModbusRegisterSet(
    base=40,
    descriptors=[
        _sensor_kk2_ta_p1,
        _sensor_kk2_ta_p2,
        _sensor_kk2_target_p1,
        _sensor_kk2_target_p2,
        _sensor_kk2_c_target_const,
    ],
)

MODBUS_SENSORS_HOT_WATER = ModbusRegisterSet(
    base=50,
    descriptors=[
        _sensor_hw_target,
        _sensor_hw_keep_target,
    ],
)

MODBUS_SENSORS_NETWORK = ModbusRegisterSet(
    base=100,
    descriptors=[
        _sensor_sw_version,
        None,
        _sensor_error,
        None,
        None,
        _sensor_evu,
    ],
)

MODBUS_SENSORS_HEATING_STATE = ModbusRegisterSet(
    base=110,
    descriptors=[
        _sensor_h_target,
        _sensor_h1_target,
        _sensor_h2_target,
        _sensor_c_target,
        _sensor_c1_target,
        _sensor_c2_target,
        _sensor_hw_target,
    ],
)

MODBUS_SENSORS_HEATING_CONTROL = ModbusRegisterSet(
    base=120,
    descriptors=[
        _sensor_tk,
        _sensor_tk1,
        _sensor_tk2,
        _sensor_tw,
    ],
)

MODBUS_SENSORS_HYDRAULIC_CIRCUIT = ModbusRegisterSet(
    base=130,
    descriptors=[
        _sensor_v,
        _sensor_pk,
        _sensor_pk_amount,
        _sensor_pk1,
        _sensor_pk2,
        _sensor_pww,
        _sensor_vf,
        _sensor_ld1,
        _sensor_ld2,
    ],
)

MODBUS_SENSORS_TEMPERATURES = ModbusRegisterSet(
    base=140,
    descriptors=[
        _sensor_ta,
        _sensor_ta1,
        _sensor_ta4,
        _sensor_ta8,
        _sensor_ta24,
    ],
)

MODBUS_SENSORS_PERFORMANCE = ModbusRegisterSet(
    base=170,
    descriptors=[
        _sensor_out_hp,
        _sensor_in_hp,
        _sensor_efficiency_hp,
        _sensor_efficiency_total,
        _sensor_in_backup,
        _sensor_out_backup,
    ],
)

MODBUS_SENSORS_POWER = ModbusRegisterSet(
    base=180,
    descriptors=[
        _sensor_day_hp_out_h,
        _sensor_day_hp_in_h,
        _sensor_day_hp_out_c,
        _sensor_day_hp_in_c,
        _sensor_day_hp_out_hw,
        _sensor_day_hp_in_hw,
        _sensor_day_backup3_out_h,
        _sensor_day_backup3_in_h,
        _sensor_day_backup3_out_hw,
        _sensor_day_backup3_in_hw,
        _sensor_day_backup6_out_h,
        _sensor_day_backup6_in_h,
        _sensor_day_backup6_out_hw,
        _sensor_day_backup6_in_hw,
    ],
)

MODBUS_SENSOR_DESCRIPTIONS: list[ModbusRegisterSet] = [
    MODBUS_SENSORS_GENERAL_STATE,
    MODBUS_SENSORS_HEATING_CURVE_1,
    MODBUS_SENSORS_COOLING_CURVE_1,
    MODBUS_SENSORS_HEATING_CURVE_2,
    MODBUS_SENSORS_COOLING_CURVE_2,
    MODBUS_SENSORS_HOT_WATER,
    MODBUS_SENSORS_NETWORK,
    MODBUS_SENSORS_HEATING_STATE,
    MODBUS_SENSORS_HEATING_CONTROL,
    MODBUS_SENSORS_HYDRAULIC_CIRCUIT,
    MODBUS_SENSORS_TEMPERATURES,
    MODBUS_SENSORS_PERFORMANCE,
    MODBUS_SENSORS_POWER,
]

SENSOR_DESCRIPTIONS = [
    _sensor_tvl,
    _sensor_trl,
    _sensor_tw,
    _sensor_tk,
    _sensor_tk1,
    _sensor_tk2,
    _sensor_vf,
    _sensor_ta,
    _sensor_ta1,
    _sensor_ta4,
    _sensor_ta24,
    _sensor_ld1,
    _sensor_ld2,
    _sensor_tr,
    _sensor_evu,
    _sensor_pk,
    _sensor_pk_amount,
    _sensor_pk1,
    _sensor_pk2,
    _sensor_pww,
    _sensor_hw_target,
    _sensor_h_target,
    _sensor_h1_target,
    _sensor_h2_target,
    _sensor_c_target,
    _sensor_c1_target,
    _sensor_c2_target,
    _sensor_in_hp,
    _sensor_v,
    _sensor_out_hp,
    _sensor_efficiency_hp,
    _sensor_efficiency_total,
    _sensor_in_backup,
    _sensor_out_backup,
    _sensor_mode_3,
    _sensor_ta8,
    _sensor_sg,
    _sensor_day_hp_out_h,
    _sensor_day_hp_out_c,
    _sensor_day_hp_out_hw,
    _sensor_day_backup3_out_h,
    _sensor_day_backup6_out_h,
    _sensor_day_backup6_out_hw,
    _sensor_day_backup3_out_hw,
    _sensor_day_hp_in_h,
    _sensor_day_hp_in_c,
    _sensor_day_hp_in_hw,
    _sensor_day_backup3_in_hw,
    _sensor_day_backup6_in_hw,
    _sensor_day_backup3_in_h,
    _sensor_day_backup6_in_h,
]
