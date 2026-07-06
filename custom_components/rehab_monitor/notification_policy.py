"""Pure notification-throttling policy for rehab_monitor.

No dependency on Home Assistant or the network stack — safe to import and
unit test in isolation (see tests/test_notification_policy.py).
"""
from __future__ import annotations

from typing import Any


def select_slots_to_notify(
    slots: list[dict[str, Any]],
    counts: dict[str, int],
    max_notifications_per_slot: int,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Decide which slots are still within their per-slot notification budget.

    Slots absent from `slots` are evicted from `counts`, so a slot that
    disappears (booked/cancelled) and later reappears is treated as new and
    gets a fresh budget.
    """
    current_ids = {slot["slot_id"] for slot in slots}
    counts = {slot_id: n for slot_id, n in counts.items() if slot_id in current_ids}

    to_notify = [
        slot for slot in slots
        if counts.get(slot["slot_id"], 0) < max_notifications_per_slot
    ]

    new_counts = dict(counts)
    for slot in to_notify:
        slot_id = slot["slot_id"]
        new_counts[slot_id] = new_counts.get(slot_id, 0) + 1

    return to_notify, new_counts


def filter_by_min_interval(
    slots: list[dict[str, Any]],
    last_notified_at: dict[str, float],
    min_interval_seconds: float,
    now: float,
) -> list[dict[str, Any]]:
    """Keep only slots whose last notification is at least min_interval_seconds old.

    A slot never notified before always passes. `min_interval_seconds <= 0`
    disables the throttle (every slot passes).
    """
    if min_interval_seconds <= 0:
        return list(slots)

    return [
        slot for slot in slots
        if now - last_notified_at.get(slot["slot_id"], float("-inf")) >= min_interval_seconds
    ]
