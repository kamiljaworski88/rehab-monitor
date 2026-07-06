from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from custom_components.rehab_monitor.notification_policy import (
    filter_by_min_interval,
    select_slots_to_notify,
)


def _slot(slot_id: str) -> dict[str, str]:
    return {
        "slot_id": slot_id,
        "data": "2026-06-24",
        "godzina": "10:00",
        "rehabilitant": "Test",
        "miejsce": "Terapia",
    }


def test_new_slot_is_notified_once_and_count_is_recorded() -> None:
    to_notify, counts = select_slots_to_notify([_slot("1")], {}, max_notifications_per_slot=2)

    assert [slot["slot_id"] for slot in to_notify] == ["1"]
    assert counts == {"1": 1}


def test_slot_is_notified_up_to_two_times_and_then_stops() -> None:
    to_notify_1, counts_1 = select_slots_to_notify([_slot("1")], {}, max_notifications_per_slot=2)
    to_notify_2, counts_2 = select_slots_to_notify([_slot("1")], counts_1, max_notifications_per_slot=2)
    to_notify_3, counts_3 = select_slots_to_notify([_slot("1")], counts_2, max_notifications_per_slot=2)

    assert [slot["slot_id"] for slot in to_notify_1] == ["1"]
    assert [slot["slot_id"] for slot in to_notify_2] == ["1"]
    assert to_notify_3 == []
    assert counts_3 == {"1": 2}


def test_slot_that_disappears_and_reappears_can_be_notified_again() -> None:
    _, counts_after_removal = select_slots_to_notify([], {"1": 2}, max_notifications_per_slot=2)
    to_notify, counts = select_slots_to_notify([_slot("1")], counts_after_removal, max_notifications_per_slot=2)

    assert to_notify == [_slot("1")]
    assert counts == {"1": 1}


def test_min_interval_zero_disables_throttle() -> None:
    kept = filter_by_min_interval([_slot("1")], {"1": 1000.0}, min_interval_seconds=0, now=1000.1)

    assert kept == [_slot("1")]


def test_min_interval_blocks_slot_notified_too_recently() -> None:
    kept = filter_by_min_interval(
        [_slot("1")], {"1": 1000.0}, min_interval_seconds=600, now=1000.0 + 300
    )

    assert kept == []


def test_min_interval_allows_slot_once_enough_time_has_passed() -> None:
    kept = filter_by_min_interval(
        [_slot("1")], {"1": 1000.0}, min_interval_seconds=600, now=1000.0 + 600
    )

    assert kept == [_slot("1")]


def test_min_interval_always_allows_a_never_notified_slot() -> None:
    kept = filter_by_min_interval([_slot("1")], {}, min_interval_seconds=600, now=1000.0)

    assert kept == [_slot("1")]
