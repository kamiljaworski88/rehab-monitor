"""Stub out `homeassistant` and `aiohttp` so custom_components.rehab_monitor
can be imported without installing full Home Assistant core.

Only the names actually touched at *import time* by __init__.py / coordinator.py
are provided — nothing here needs to be functional since tests only exercise
the pure logic in notification_policy.py, never a running coordinator.
"""
from __future__ import annotations

import sys
import types


def _install_stub_module(name: str) -> types.ModuleType:
    if name in sys.modules:
        return sys.modules[name]
    module = types.ModuleType(name)
    sys.modules[name] = module
    return module


def _install_homeassistant_stubs() -> None:
    if "homeassistant" in sys.modules:
        return

    _install_stub_module("homeassistant")

    config_entries = _install_stub_module("homeassistant.config_entries")
    config_entries.ConfigEntry = type("ConfigEntry", (), {})

    const = _install_stub_module("homeassistant.const")
    const.EVENT_HOMEASSISTANT_STARTED = "homeassistant_started"

    core = _install_stub_module("homeassistant.core")
    core.HomeAssistant = type("HomeAssistant", (), {})

    _install_stub_module("homeassistant.helpers")

    storage = _install_stub_module("homeassistant.helpers.storage")
    storage.Store = type("Store", (), {})

    update_coordinator = _install_stub_module("homeassistant.helpers.update_coordinator")

    class _DataUpdateCoordinator:
        def __class_getitem__(cls, item):
            return cls

    update_coordinator.DataUpdateCoordinator = _DataUpdateCoordinator


def _install_aiohttp_stub() -> None:
    if "aiohttp" in sys.modules:
        return
    _install_stub_module("aiohttp")


_install_homeassistant_stubs()
_install_aiohttp_stub()
