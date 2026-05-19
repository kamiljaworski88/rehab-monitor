"""Rehab Monitor — monitors free rehabilitation slots on the Intermedicus portal."""
from __future__ import annotations

import logging
import os
import shutil
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
CARD_VERSION = "3"
CARD_URL = f"/local/{CARD_FILENAME}?v={CARD_VERSION}"
LOVELACE_RESOURCES_STORAGE_KEY = "lovelace_resources"


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Copy card JS to www/ and register it as a Lovelace resource."""
    await hass.async_add_executor_job(_copy_card_to_www, hass)

    async def _register(_event: object = None) -> None:
        await _async_ensure_lovelace_resource(hass)

    if hass.is_running:
        await _register()
    else:
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _register)

    return True


def _copy_card_to_www(hass: HomeAssistant) -> None:
    src = os.path.join(os.path.dirname(__file__), CARD_FILENAME)
    www_dir = hass.config.path("www")
    os.makedirs(www_dir, exist_ok=True)
    shutil.copy2(src, os.path.join(www_dir, CARD_FILENAME))
    _LOGGER.debug("RehabMonitor: skopiowano %s → www/", CARD_FILENAME)


async def _async_ensure_lovelace_resource(hass: HomeAssistant) -> None:
    store = Store(hass, 1, LOVELACE_RESOURCES_STORAGE_KEY)
    data: dict[str, Any] = await store.async_load() or {"items": []}
    items: list[dict[str, Any]] = data.get("items", [])

    if any(item.get("url") == CARD_URL for item in items):
        return

    # Remove stale entries for this card (old URL without version or old version number)
    items = [item for item in items if CARD_FILENAME not in item.get("url", "")]

    items.append({"id": str(uuid.uuid4()), "type": "module", "url": CARD_URL})
    data["items"] = items
    await store.async_save(data)
    _LOGGER.info(
        "RehabMonitor: zaktualizowano zasób Lovelace %s — zrób Ctrl+Shift+R.",
        CARD_URL,
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Rehab Monitor from a config entry."""
    # Copy card JS and register Lovelace resource here too, so the card
    # is always refreshed when the integration is loaded via config entry
    # (async_setup may not be called if the domain isn't in configuration.yaml).
    await hass.async_add_executor_job(_copy_card_to_www, hass)
    await _async_ensure_lovelace_resource(hass)

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
