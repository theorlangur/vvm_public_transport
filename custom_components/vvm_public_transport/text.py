"""VVM Stop departure monitor: text entities for filtering."""

from homeassistant.components.text import TextEntity

from .const import DOMAIN
from .coordinator_base import VVMStopCoordinatorEntityBase


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up VVM Stop switch entries."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            VVMStopTextFilterNums(coordinator),
            VVMStopTextFilterDirections(coordinator),
        ]
    )


class VVMStopTextFilterNums(VVMStopCoordinatorEntityBase, TextEntity):
    """Filter TextEntity for vehicle numbers."""

    _attr_has_entity_name = True

    def __init__(self, coordinator) -> None:
        """Construct the base sensor class."""
        super().__init__(coordinator, "text", "Filter By Numbers")

    async def async_set_value(self, value: str) -> None:
        """Set the text value."""
        self.coordinator.data.filter_nums = value
        await self.coordinator.async_request_refresh()

    @property
    def native_value(self):
        """Return the state of the text filter."""
        return ",".join(self.coordinator.data.filter_nums)


class VVMStopTextFilterDirections(VVMStopCoordinatorEntityBase, TextEntity):
    """Filter TextEntity for vehicle directions."""

    _attr_has_entity_name = True

    def __init__(self, coordinator) -> None:
        """Construct the base sensor class."""
        super().__init__(coordinator, "text", "Filter By Directions")

    async def async_set_value(self, value: str) -> None:
        """Set the text value."""
        self.coordinator.data.filter_direction = value
        await self.coordinator.async_request_refresh()

    @property
    def native_value(self):
        """Return the state of the text filter."""
        return ",".join(self.coordinator.data.filter_direction)
