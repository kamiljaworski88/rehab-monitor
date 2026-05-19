"""Text platform — comma-separated list of rehabilitants to exclude from results."""
from __future__ import annotations

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN
from .coordinator import RehabDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: RehabDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RehabWykluczeniText(coordinator)])


class RehabWykluczeniText(RestoreEntity, TextEntity):
    """Comma-separated rehabilitant names to exclude from free-slot results."""

    _attr_has_entity_name = True
    _attr_name = "Wyklucz rehabilitantów"
    _attr_icon = "mdi:account-cancel"
    _attr_native_max = 255

    def __init__(self, coordinator: RehabDataUpdateCoordinator) -> None:
        self._coordinator = coordinator
        self._value: str = ""
        self._attr_unique_id = f"{DOMAIN}_wykluczeni"
        self.entity_id = "text.rehab_wykluczeni"

    async def async_added_to_hass(self) -> None:
        if (last := await self.async_get_last_state()) is not None:
            self._value = last.state or ""
            self._coordinator.set_excluded_rehabilitants(self._value)

    @property
    def native_value(self) -> str:
        return self._value

    async def async_set_value(self, value: str) -> None:
        self._value = value
        self._coordinator.set_excluded_rehabilitants(value)
        self.async_write_ha_state()
