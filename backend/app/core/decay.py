import math
import time


DEFAULT_DECAY_RATE_PER_HOUR = 0.001


def get_decay_factor(
    elapsed_hours: float,
    decay_rate_per_hour: float = DEFAULT_DECAY_RATE_PER_HOUR
) -> float:
    """
    Calculate exponential memory decay.

    decay_factor = exp(-lambda * elapsed_hours)

    Returns a value between 0 and 1.
    """

    if not isinstance(elapsed_hours, (int, float)):
        raise TypeError(
            "elapsed_hours must be numeric."
        )

    if not isinstance(decay_rate_per_hour, (int, float)):
        raise TypeError(
            "decay_rate_per_hour must be numeric."
        )

    if elapsed_hours < 0:
        raise ValueError(
            "elapsed_hours cannot be negative."
        )

    if decay_rate_per_hour < 0:
        raise ValueError(
            "decay_rate_per_hour cannot be negative."
        )

    return math.exp(
        -decay_rate_per_hour * elapsed_hours
    )


def get_effective_mastery(
    stored_mastery: float,
    last_practiced_at: float | None,
    current_time: float | None = None,
    decay_rate_per_hour: float = DEFAULT_DECAY_RATE_PER_HOUR
) -> float:
    """
    Return time-adjusted mastery without modifying
    the stored mastery value.

    Parameters
    ----------
    stored_mastery : float
        Mastery immediately after the student's
        last relevant attempt.

    last_practiced_at : float | None
        Unix timestamp in seconds.

        If None, no decay is applied because there
        is no practice timestamp to decay from.

    current_time : float | None
        Unix timestamp used as 'now'.

        Defaults to time.time().

        Supplying this explicitly makes tests
        deterministic.

    decay_rate_per_hour : float
        Exponential decay rate lambda per hour.

    Returns
    -------
    float
        Effective mastery at current_time.
    """

    if not isinstance(stored_mastery, (int, float)):
        raise TypeError(
            "stored_mastery must be numeric."
        )

    if not 0 <= stored_mastery <= 1:
        raise ValueError(
            "stored_mastery must be between 0 and 1."
        )

    if last_practiced_at is None:
        return float(stored_mastery)

    if not isinstance(last_practiced_at, (int, float)):
        raise TypeError(
            "last_practiced_at must be numeric or None."
        )

    if current_time is None:
        current_time = time.time()

    if not isinstance(current_time, (int, float)):
        raise TypeError(
            "current_time must be numeric."
        )

    if current_time < last_practiced_at:
        raise ValueError(
            "current_time cannot be earlier than "
            "last_practiced_at."
        )

    elapsed_seconds = (
        current_time - last_practiced_at
    )

    elapsed_hours = (
        elapsed_seconds / 3600
    )

    decay_factor = get_decay_factor(
        elapsed_hours=elapsed_hours,
        decay_rate_per_hour=decay_rate_per_hour
    )

    effective_mastery = (
        stored_mastery * decay_factor
    )

    return max(
        0.0,
        min(1.0, effective_mastery)
    )