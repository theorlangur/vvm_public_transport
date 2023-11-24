"""VVM Stop departure monitor as a binary_switch."""

from homeassistant.components.switch import SwitchEntity

from .const import (
    DOMAIN,
    V_TYPE_BUS,
    V_TYPE_LIST,
    V_TYPE_NIGHT_BUS,
    V_TYPE_REGIONAL_BUS,
    V_TYPE_TRAM,
)
from .coordinator_base import VVMStopCoordinatorEntityBase


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up VVM Stop switch entries."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            VVMStopDepartureFilterTram(coordinator, entry),
            VVMStopDepartureFilterBus(coordinator, entry),
            VVMStopDepartureFilterRegionalBus(coordinator, entry),
            VVMStopDepartureFilterNightBus(coordinator, entry),
        ]
    )


class VVMStopSwitchFilterEntityBase(VVMStopCoordinatorEntityBase, SwitchEntity):
    """Base functionality for all VVM switches."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator, switch_id, vehicle_type_filter, config_entry
    ) -> None:
        """Construct the base sensor class."""
        super().__init__(coordinator, "switch", switch_id)
        self._vehicle_type = vehicle_type_filter
        self._config_entry = config_entry

    @property
    def is_on(self):
        """Return state of the switch."""
        if len(self.coordinator.data.filter_types) == 0:
            return True
        for t in self.coordinator.data.filter_types:
            if t.lower() == self._vehicle_type.lower():
                return True
        return False

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        if not self.is_on:
            self.coordinator.data.filter_types.append(self._vehicle_type)
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        if len(self.coordinator.data.filter_types) == 0:
            self.coordinator.data.filter_types = V_TYPE_LIST.copy()

        if self.is_on:
            self.coordinator.data.filter_types.remove(self._vehicle_type)
            await self.coordinator.async_request_refresh()


class VVMStopDepartureFilterTram(VVMStopSwitchFilterEntityBase):
    """Switch to control tram filter."""

    def __init__(self, coordinator, config_entry) -> None:
        """Construct the tram filter class."""
        super().__init__(coordinator, "Tram Filter", V_TYPE_TRAM, config_entry)


class VVMStopDepartureFilterBus(VVMStopSwitchFilterEntityBase):
    """Switch to control bus filter."""

    def __init__(self, coordinator, config_entry) -> None:
        """Construct the bus filter class."""
        super().__init__(coordinator, "Bus Filter", V_TYPE_BUS, config_entry)


class VVMStopDepartureFilterRegionalBus(VVMStopSwitchFilterEntityBase):
    """Switch to control regional bus filter."""

    def __init__(self, coordinator, config_entry) -> None:
        """Construct the regional bus filter class."""
        super().__init__(
            coordinator, "Regional Bus Filter", V_TYPE_REGIONAL_BUS, config_entry
        )


class VVMStopDepartureFilterNightBus(VVMStopSwitchFilterEntityBase):
    """Switch to control night bus filter."""

    def __init__(self, coordinator, config_entry) -> None:
        """Construct the night bus filter class."""
        super().__init__(
            coordinator, "Night Bus Filter", V_TYPE_NIGHT_BUS, config_entry
        )
