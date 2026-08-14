import math

import pytest

from backend.app.core.decay import (
    get_decay_factor,
    get_effective_mastery
)


HOUR = 3600


def test_zero_elapsed_time_has_no_decay():

    result = get_decay_factor(
        elapsed_hours=0,
        decay_rate_per_hour=0.001
    )

    assert result == pytest.approx(
        1.0
    )


def test_decay_factor_matches_formula():

    result = get_decay_factor(
        elapsed_hours=24,
        decay_rate_per_hour=0.001
    )

    expected = math.exp(
        -0.001 * 24
    )

    assert result == pytest.approx(
        expected,
        abs=1e-9
    )


def test_effective_mastery_same_when_just_practiced():

    now = 1_800_000_000

    result = get_effective_mastery(
        stored_mastery=0.81,
        last_practiced_at=now,
        current_time=now
    )

    assert result == pytest.approx(
        0.81
    )


def test_effective_mastery_decreases_with_time():

    now = 1_800_000_000

    result = get_effective_mastery(
        stored_mastery=0.81,
        last_practiced_at=now - 7 * 24 * HOUR,
        current_time=now
    )

    assert result < 0.81


def test_longer_gap_causes_more_decay():

    now = 1_800_000_000

    two_days = get_effective_mastery(
        stored_mastery=0.81,
        last_practiced_at=now - 2 * 24 * HOUR,
        current_time=now
    )

    twenty_one_days = get_effective_mastery(
        stored_mastery=0.81,
        last_practiced_at=now - 21 * 24 * HOUR,
        current_time=now
    )

    assert (
        twenty_one_days
        < two_days
        < 0.81
    )


def test_missing_timestamp_does_not_decay():

    result = get_effective_mastery(
        stored_mastery=0.65,
        last_practiced_at=None
    )

    assert result == pytest.approx(
        0.65
    )


def test_stored_mastery_is_not_mutated():

    mastery = 0.81

    now = 1_800_000_000

    get_effective_mastery(
        stored_mastery=mastery,
        last_practiced_at=now - 7 * 24 * HOUR,
        current_time=now
    )

    assert mastery == 0.81


def test_invalid_mastery_rejected():

    with pytest.raises(ValueError):

        get_effective_mastery(
            stored_mastery=1.2,
            last_practiced_at=100
        )


def test_future_last_practiced_timestamp_rejected():

    with pytest.raises(ValueError):

        get_effective_mastery(
            stored_mastery=0.80,
            last_practiced_at=200,
            current_time=100
        )