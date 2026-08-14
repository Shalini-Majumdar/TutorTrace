import pytest

from backend.app.core.bkt_engine import update_mastery
import json
from pathlib import Path
from backend.app.core.bkt_engine import (
    update_mastery,
    calculate_posterior,
    apply_learning_transition,
    derive_effective_parameters,
    update_mastery_response_aware,
    update_mastery_dont_know,
    process_attempt
)

# ==========================================================
# TEST 1
# Hand-calculated correct-answer example
# ==========================================================
def test_correct_posterior():

    posterior = calculate_posterior(
        current_mastery=0.30,
        correct=True,
        p_g=0.25,
        p_s=0.10
    )

    expected = 0.6067415730337079

    assert posterior == pytest.approx(
        expected,
        abs=1e-6
    )


def test_learning_transition():

    result = apply_learning_transition(
        posterior_mastery=0.6067415730337079,
        p_t=0.15
    )

    expected = 0.6657303370786517

    assert result == pytest.approx(
        expected,
        abs=1e-6
    )
def test_correct_answer_update():

    result = update_mastery(
        current_mastery=0.30,
        correct=True,
        p_t=0.15,
        p_g=0.25,
        p_s=0.10
    )

    expected = 0.6657303370786517

    assert result == pytest.approx(
        expected,
        abs=1e-6
    )


# ==========================================================
# TEST 2
# Incorrect answer should lower evidence of mastery
# ==========================================================

def test_incorrect_answer_update():

    result = update_mastery(
        current_mastery=0.30,
        correct=False,
        p_t=0.15,
        p_g=0.25,
        p_s=0.10
    )

    # Hand calculation:
    #
    # posterior =
    # (0.30 * 0.10)
    # /
    # ((0.30 * 0.10)
    # + (0.70 * 0.75))
    #
    # = 0.054054054...
    #
    # then transition:
    #
    # 0.054054054
    # + (1 - 0.054054054) * 0.15
    #
    # = 0.195945945...

    expected = 0.19594594594594594

    assert result == pytest.approx(
        expected,
        abs=1e-6
    )


# ==========================================================
# TEST 3
# Output should always remain a probability
# ==========================================================

def test_output_between_zero_and_one():

    result = update_mastery(
        current_mastery=0.80,
        correct=True,
        p_t=0.20,
        p_g=0.25,
        p_s=0.10
    )

    assert 0 <= result <= 1


# ==========================================================
# TEST 4
# Invalid current mastery
# ==========================================================

def test_invalid_mastery_above_one():

    with pytest.raises(ValueError):

        update_mastery(
            current_mastery=1.2,
            correct=True,
            p_t=0.15,
            p_g=0.25,
            p_s=0.10
        )


# ==========================================================
# TEST 5
# Invalid BKT parameter
# ==========================================================

def test_invalid_guess_probability():

    with pytest.raises(ValueError):

        update_mastery(
            current_mastery=0.30,
            correct=True,
            p_t=0.15,
            p_g=-0.25,
            p_s=0.10
        )


def test_real_tutortrace_parameters():

    params_path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "bkt_params.json"
    )

    with open(
        params_path,
        "r",
        encoding="utf-8"
    ) as file:

        all_params = json.load(file)


    params = all_params[
        "integer_operations"
    ]


    result = update_mastery(
        current_mastery=params["p_l0"],
        correct=True,
        p_t=params["p_t"],
        p_g=params["p_g"],
        p_s=params["p_s"]
    )


    assert 0 <= result <= 1

    # A correct observation should provide
    # positive evidence of mastery for our
    # fitted parameter configuration.
    assert result > params["p_l0"]

def test_normal_correct_keeps_base_parameters():

    (
        effective_guess,
        effective_slip,
        signal
    ) = derive_effective_parameters(
        base_guess=0.25,
        base_slip=0.10,
        correct=True,
        time_taken_seconds=12
    )

    assert effective_guess == pytest.approx(
        0.25
    )

    assert effective_slip == pytest.approx(
        0.10
    )

    assert signal == "normal"


def test_slow_correct_increases_effective_slip():

    (
        effective_guess,
        effective_slip,
        signal
    ) = derive_effective_parameters(
        base_guess=0.25,
        base_slip=0.10,
        correct=True,
        time_taken_seconds=45
    )

    assert effective_guess == pytest.approx(
        0.25
    )

    assert effective_slip == pytest.approx(
        0.20
    )

    assert signal == "slow_correct"


def test_fast_incorrect_becomes_speed_slip():

    (
        effective_guess,
        effective_slip,
        signal
    ) = derive_effective_parameters(
        base_guess=0.25,
        base_slip=0.10,
        correct=False,
        time_taken_seconds=2
    )

    assert effective_guess == pytest.approx(
        0.25
    )

    assert effective_slip == pytest.approx(
        0.25
    )

    assert signal == "speed_slip"


def test_slow_correct_gives_weaker_positive_update():

    standard = update_mastery(
        current_mastery=0.30,
        correct=True,
        p_t=0.15,
        p_g=0.25,
        p_s=0.10
    )

    response_aware = (
        update_mastery_response_aware(
            current_mastery=0.30,
            correct=True,
            time_taken_seconds=45,
            p_t=0.15,
            p_g=0.25,
            p_s=0.10
        )
    )

    assert (
        response_aware["mastery_after"]
        < standard
    )

    assert (
        response_aware["mastery_after"]
        > 0.30
    )


def test_fast_incorrect_is_less_punishing_than_normal_incorrect():

    normal_incorrect = (
        update_mastery_response_aware(
            current_mastery=0.60,
            correct=False,
            time_taken_seconds=10,
            p_t=0.15,
            p_g=0.25,
            p_s=0.10
        )
    )

    speed_slip = (
        update_mastery_response_aware(
            current_mastery=0.60,
            correct=False,
            time_taken_seconds=2,
            p_t=0.15,
            p_g=0.25,
            p_s=0.10
        )
    )

    assert (
        speed_slip["mastery_after"]
        > normal_incorrect["mastery_after"]
    )


def test_negative_response_time_rejected():

    with pytest.raises(ValueError):

        update_mastery_response_aware(
            current_mastery=0.50,
            correct=True,
            time_taken_seconds=-2,
            p_t=0.15,
            p_g=0.25,
            p_s=0.10
        )


def test_confidence_must_be_probability():

    with pytest.raises(ValueError):

        update_mastery_response_aware(
            current_mastery=0.50,
            correct=True,
            time_taken_seconds=10,
            p_t=0.15,
            p_g=0.25,
            p_s=0.10,
            confidence=1.5
        )
def test_dont_know_reduces_mastery_moderately():

    result = update_mastery_dont_know(
        current_mastery=0.60,
        p_t=0.15,
        uncertainty_penalty=0.20
    )

    assert result["mastery_after"] < 0.60

    assert result["mastery_after"] > 0.40

    assert (
        result["response_signal"]
        == "explicit_uncertainty"
    )

    assert (
        result["uncertainty_detected"]
        is True
    )


def test_dont_know_less_punishing_than_standard_incorrect():

    dont_know = update_mastery_dont_know(
        current_mastery=0.60,
        p_t=0.15
    )

    normal_incorrect = update_mastery_response_aware(
        current_mastery=0.60,
        correct=False,
        time_taken_seconds=10,
        p_t=0.15,
        p_g=0.25,
        p_s=0.10
    )

    assert (
        dont_know["mastery_after"]
        >
        normal_incorrect["mastery_after"]
    )


def test_process_attempt_routes_dont_know():

    result = process_attempt(
        current_mastery=0.60,
        answer_type="dont_know",
        p_t=0.15,
        p_g=0.25,
        p_s=0.10
    )

    assert (
        result["answer_type"]
        == "dont_know"
    )

    assert (
        result["uncertainty_detected"]
        is True
    )


def test_process_attempt_routes_selected_option():

    result = process_attempt(
        current_mastery=0.60,
        answer_type="selected_option",
        correct=True,
        time_taken_seconds=10,
        p_t=0.15,
        p_g=0.25,
        p_s=0.10
    )

    assert (
        result["answer_type"]
        == "selected_option"
    )

    assert (
        result["uncertainty_detected"]
        is False
    )

    assert result["mastery_after"] > 0.60


def test_selected_option_requires_correct():

    with pytest.raises(ValueError):

        process_attempt(
            current_mastery=0.60,
            answer_type="selected_option",
            time_taken_seconds=10,
            p_t=0.15,
            p_g=0.25,
            p_s=0.10
        )


def test_selected_option_requires_time():

    with pytest.raises(ValueError):

        process_attempt(
            current_mastery=0.60,
            answer_type="selected_option",
            correct=True,
            p_t=0.15,
            p_g=0.25,
            p_s=0.10
        )


def test_invalid_answer_type():

    with pytest.raises(ValueError):

        process_attempt(
            current_mastery=0.60,
            answer_type="random_guess",
            p_t=0.15,
            p_g=0.25,
            p_s=0.10
        )