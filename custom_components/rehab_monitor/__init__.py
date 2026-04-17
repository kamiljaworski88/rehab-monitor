"""Rehab Monitor — monitors free rehabilitation slots on the Intermedicus portal."""
from __future__ import annotations

import logging
import os
import uuid
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN, PLATFORMS
from .coordinator import RehabDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

CARD_FILENAME = "rehab-monitor-card.js"
CARD_URL = f"/rehab-monitor/{CARD_FILENAME}"
LOVELACE_RESOURCES_STORAGE_KEY = "lovelace_resources"


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Serve the card JS and register it as a Lovelace resource."""
    card_path = os.path.join(os.path.dirname(__file__), CARD_FILENAME)

    # Serve the JS file directly from the component directory (no www copy needed).
    hass.http.register_static_path(CARD_URL, card_path, cache_headers=False)

    # Register Lovelace resource after HA has fully started (storage is ready).
    async def _register(_event=None) -> None:
        await _async_ensure_lovelace_resource(hass)

    if hass.is_running:
        await _register()
    else:
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _register)

    return True


async def _async_ensure_lovelace_resource(hass: HomeAssistant) -> None:
    store = Store(hass, 1, LOVELACE_RESOURCES_STORAGE_KEY)
    data: dict[str, Any] = await store.async_load() or {"items": []}
    items: list[dict[str, Any]] = data.get("items", [])
    if any(item.get("url") == CARD_URL for item in items):
        return
    items.append({"id": str(uuid.uuid4()), "type": "module", "url": CARD_URL})
    data["items"] = items
    await store.async_save(data)
    _LOGGER.info(
        "RehabMonitor: registered Lovelace resource %s — zrób Ctrl+Shift+R w przeglądarce.",
        CARD_URL,
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Rehab Monitor from a config entry."""
    coordinator = RehabDataUpdateCoordinator(hass, entry)
    await coordinator.async_setup()
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry and release the aiohttp session."""
    coordinator: RehabDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await coordinator.async_shutdown()
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded
