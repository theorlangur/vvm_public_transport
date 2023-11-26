"""The vvm_transport integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_FILTER_DIRECTION,
    CONF_FILTER_NUM,
    CONF_FILTER_TYPE,
    CONF_STOP_ID,
    CONF_TIMEFRAME,
    DOMAIN,
)
from .vvm_access import VVMStopMonitorHA

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH, Platform.TEXT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up vvm_transport from a config entry."""
    api = VVMStopMonitorHA(
        entry.data[CONF_STOP_ID], entry.title, entry.data[CONF_TIMEFRAME]
    )

    if entry.options is not None:
        if CONF_FILTER_TYPE in entry.options:
            api.filter_types = entry.options[CONF_FILTER_TYPE]
        if CONF_FILTER_NUM in entry.options:
            api.filter_nums = entry.options[CONF_FILTER_NUM]
        if CONF_FILTER_DIRECTION in entry.options:
            api.filter_direction = entry.options[CONF_FILTER_DIRECTION]
        if CONF_TIMEFRAME in entry.options:
            api.timespan = entry.options[CONF_TIMEFRAME]

    async def async_update_data() -> VVMStopMonitorHA:
        """Fetch data from the API."""
        await api.async_update()
        return api

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="vvm_public_transport_stop",
        update_method=async_update_data,
        update_interval=timedelta(minutes=1),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
