"""VVM Stop departure monitor base coordinator class for entities."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN
from .vvm_access import VVMStopMonitorHA


class VVMStopCoordinatorEntityBase(
    CoordinatorEntity[DataUpdateCoordinator[VVMStopMonitorHA]]
):
    """Base functionality for all VVM entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entity_type, entity_id) -> None:
        """Construct the base class."""
        super().__init__(coordinator)
        self._attr_unique_id = (
            f"{DOMAIN}_{coordinator.data.stop_id}_{entity_type}_{entity_id}"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.data.stop_id)},
            name="VVM Stop",
            manufacturer="VVM",
        )
        self._name = f"{coordinator.data.stop_name} {entity_id}"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name
