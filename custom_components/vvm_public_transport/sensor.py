"""VVM Stop departure monitor as a sensor."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .coordinator_base import VVMStopCoordinatorEntityBase
from .vvm_access import VVMStopMonitorHA


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up VVM Stop entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            VVMStopDepartureNearest(coordinator),
            VVMStopDepartureNearestLeft(coordinator),
            VVMStopDepartureNearestDelay(coordinator),
            VVMStopDepartureNearestVehicleType(coordinator),
            VVMStopDepartureNearestVehicleNum(coordinator),
        ]
    )


class VVMStopSensorEntityBase(VVMStopCoordinatorEntityBase, SensorEntity):
    """Base functionality for all VVM sensors."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, sensor_id) -> None:
        """Construct the base sensor class."""
        super().__init__(coordinator, "sensor", sensor_id)


class VVMStopDepartureNearest(VVMStopSensorEntityBase):
    """Entity representing a public transport stop to monitor for departures."""

    def __init__(self, coordinator: DataUpdateCoordinator[VVMStopMonitorHA]) -> None:
        """Construct the nearest sensor."""
        super().__init__(coordinator, "Summary")
        self.extra = {
            "departures": self.coordinator.data.departures,
            "last_updated": self.coordinator.data.last_updated,
        }

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the device."""
        self.extra["departures"] = self.coordinator.data.departures
        self.extra["last_updated"] = self.coordinator.data.last_updated
        self.extra["stop_name"] = self.coordinator.data.stop_name
        return self.extra

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.nearest_summary


class VVMStopDepartureNearestLeft(VVMStopSensorEntityBase):
    """Entity representing a public transport stop to monitor for departures."""

    def __init__(self, coordinator: DataUpdateCoordinator[VVMStopMonitorHA]) -> None:
        """Construct the Nearest Left sensor."""
        super().__init__(coordinator, "Time Left")

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.nearest_left_minutes


class VVMStopDepartureNearestDelay(VVMStopSensorEntityBase):
    """Entity representing a public transport stop to monitor for departures."""

    def __init__(self, coordinator: DataUpdateCoordinator[VVMStopMonitorHA]) -> None:
        """Construct the Nearest Delay sensor."""
        super().__init__(coordinator, "Delay")

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.nearest_delay_minutes


class VVMStopDepartureNearestVehicleType(VVMStopSensorEntityBase):
    """Sensor for a vehicle type for the soonest one."""

    def __init__(self, coordinator: DataUpdateCoordinator[VVMStopMonitorHA]) -> None:
        """Construct the Nearest Vehicle Type sensor."""
        super().__init__(coordinator, "Vehicle Type")

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.nearest_vehicle_type


class VVMStopDepartureNearestVehicleNum(VVMStopSensorEntityBase):
    """Sensor for a vehicle number for the soonest one."""

    def __init__(self, coordinator: DataUpdateCoordinator[VVMStopMonitorHA]) -> None:
        """Construct the Nearest Vehicle Number sensor."""
        super().__init__(coordinator, "Vehicle Number")

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.nearest_vehicle_num
