def _validate_probability(
    value: float,
    name: str
) -> None:
    """
    Validate that a value is numeric and lies
    between 0 and 1 inclusive.
    """

    if not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} must be numeric."
        )

    if not 0 <= value <= 1:
        raise ValueError(
            f"{name} must be between 0 and 1."
        )


def calculate_posterior(
    current_mastery: float,
    correct: bool,
    p_g: float,
    p_s: float
) -> float:
    """
    Calculate posterior mastery P(L | observation)
    before applying the learning transition.

    Parameters
    ----------
    current_mastery : float
        Current probability that the student
        knows the skill, P(L).

    correct : bool
        True if the student's response was correct,
        False otherwise.

    p_g : float
        Guess probability, P(G).

    p_s : float
        Slip probability, P(S).

    Returns
    -------
    float
        Posterior mastery probability after
        observing the response.
    """

    # --------------------------------------------------
    # VALIDATE INPUTS
    # --------------------------------------------------

    _validate_probability(
        current_mastery,
        "current_mastery"
    )

    _validate_probability(
        p_g,
        "p_g"
    )

    _validate_probability(
        p_s,
        "p_s"
    )


    # --------------------------------------------------
    # BAYESIAN POSTERIOR
    # --------------------------------------------------

    if correct:

        # P(L) * P(correct | learned)
        #
        # P(correct | learned) = 1 - P(S)
        numerator = (
            current_mastery
            * (1 - p_s)
        )

        denominator = (
            numerator
            + (1 - current_mastery) * p_g
        )

    else:

        # P(L) * P(incorrect | learned)
        #
        # P(incorrect | learned) = P(S)
        numerator = (
            current_mastery
            * p_s
        )

        denominator = (
            numerator
            + (1 - current_mastery)
            * (1 - p_g)
        )


    # --------------------------------------------------
    # NUMERICAL SAFETY
    # --------------------------------------------------

    if denominator == 0:
        raise ValueError(
            "BKT posterior denominator became zero."
        )


    posterior_mastery = (
        numerator / denominator
    )


    return posterior_mastery


def apply_learning_transition(
    posterior_mastery: float,
    p_t: float
) -> float:
    """
    Apply the BKT learning transition after
    the Bayesian posterior update.

    P(L_next) =
        P(L | observation)
        +
        (1 - P(L | observation)) * P(T)

    Parameters
    ----------
    posterior_mastery : float
        Mastery probability after the Bayesian
        evidence update.

    p_t : float
        Learning/transition probability, P(T).

    Returns
    -------
    float
        Mastery probability after the learning
        transition.
    """

    # --------------------------------------------------
    # VALIDATE INPUTS
    # --------------------------------------------------

    _validate_probability(
        posterior_mastery,
        "posterior_mastery"
    )

    _validate_probability(
        p_t,
        "p_t"
    )


    # --------------------------------------------------
    # LEARNING TRANSITION
    # --------------------------------------------------

    next_mastery = (
        posterior_mastery
        + (1 - posterior_mastery) * p_t
    )


    # --------------------------------------------------
    # NUMERICAL SAFETY
    # --------------------------------------------------

    next_mastery = max(
        0.0,
        min(1.0, next_mastery)
    )


    return next_mastery


def update_mastery(
    current_mastery: float,
    correct: bool,
    p_t: float,
    p_g: float,
    p_s: float
) -> float:
    """
    Perform one complete standard
    Bayesian Knowledge Tracing update.

    The update has two stages:

    1. Bayesian posterior update
       P(L | observation)

    2. Learning transition
       P(L_next)

    Parameters
    ----------
    current_mastery : float
        Current probability that the student
        knows the skill, P(L).

    correct : bool
        True if the answer was correct,
        False if incorrect.

    p_t : float
        Learning/transition probability, P(T).

    p_g : float
        Guess probability, P(G).

    p_s : float
        Slip probability, P(S).

    Returns
    -------
    float
        Updated mastery probability P(L_next).
    """

    # --------------------------------------------------
    # STEP 1: BAYESIAN EVIDENCE UPDATE
    # --------------------------------------------------

    posterior = calculate_posterior(
        current_mastery=current_mastery,
        correct=correct,
        p_g=p_g,
        p_s=p_s
    )


    # --------------------------------------------------
    # STEP 2: LEARNING TRANSITION
    # --------------------------------------------------

    return apply_learning_transition(
        posterior_mastery=posterior,
        p_t=p_t
    )
def derive_effective_parameters(
    base_guess: float,
    base_slip: float,
    correct: bool,
    time_taken_seconds: float,
    fast_threshold: float = 3.0,
    slow_threshold: float = 30.0
) -> tuple[float, float, str]:
    """
    Derive attempt-specific guess/slip values based on
    response latency.

    IMPORTANT:
    These are temporary effective parameters for this
    one observation only. The fitted base parameters
    are never mutated.

    Returns
    -------
    tuple
        (effective_guess, effective_slip, response_signal)
    """

    _validate_probability(
        base_guess,
        "base_guess"
    )

    _validate_probability(
        base_slip,
        "base_slip"
    )

    if not isinstance(
        time_taken_seconds,
        (int, float)
    ):
        raise TypeError(
            "time_taken_seconds must be numeric."
        )

    if time_taken_seconds < 0:
        raise ValueError(
            "time_taken_seconds cannot be negative."
        )

    if fast_threshold <= 0:
        raise ValueError(
            "fast_threshold must be greater than 0."
        )

    if slow_threshold <= fast_threshold:
        raise ValueError(
            "slow_threshold must be greater than fast_threshold."
        )

    effective_guess = base_guess
    effective_slip = base_slip

    response_signal = "normal"


    # --------------------------------------------------
    # CASE 1:
    # Correct but very slow
    #
    # Interpretation:
    # The answer is still positive evidence,
    # but slightly weaker because of hesitation.
    #
    # We temporarily increase slip probability.
    # --------------------------------------------------

    if (
        correct
        and time_taken_seconds > slow_threshold
    ):

        effective_slip = min(
            0.49,
            base_slip + 0.10
        )

        response_signal = "slow_correct"


    # --------------------------------------------------
    # CASE 2:
    # Incorrect but extremely fast
    #
    # Interpretation:
    # Could be impulsive / speed slip rather than
    # strong evidence of non-mastery.
    #
    # Increasing slip makes the incorrect response
    # less surprising under the "knows skill" state,
    # which weakens the negative evidence.
    # --------------------------------------------------

    elif (
        not correct
        and time_taken_seconds < fast_threshold
    ):

        effective_slip = min(
            0.49,
            base_slip + 0.15
        )

        response_signal = "speed_slip"


    return (
        effective_guess,
        effective_slip,
        response_signal
    )


def update_mastery_response_aware(
    current_mastery: float,
    correct: bool,
    time_taken_seconds: float,
    p_t: float,
    p_g: float,
    p_s: float,
    confidence: float | None = None
) -> dict:
    """
    Perform a response-aware BKT update.

    Response latency modulates the strength of the
    observation, while the underlying BKT equations
    remain unchanged.

    Confidence is accepted for forward compatibility,
    but is not used yet in Phase 4.

    Returns
    -------
    dict
        Contains mastery before/after and the effective
        parameters used for this attempt.
    """

    _validate_probability(
        current_mastery,
        "current_mastery"
    )

    _validate_probability(
        p_t,
        "p_t"
    )

    _validate_probability(
        p_g,
        "p_g"
    )

    _validate_probability(
        p_s,
        "p_s"
    )

    if confidence is not None:

        _validate_probability(
            confidence,
            "confidence"
        )


    (
        effective_guess,
        effective_slip,
        response_signal
    ) = derive_effective_parameters(
        base_guess=p_g,
        base_slip=p_s,
        correct=correct,
        time_taken_seconds=time_taken_seconds
    )


    posterior = calculate_posterior(
        current_mastery=current_mastery,
        correct=correct,
        p_g=effective_guess,
        p_s=effective_slip
    )


    next_mastery = apply_learning_transition(
        posterior_mastery=posterior,
        p_t=p_t
    )


    return {
        "mastery_before": current_mastery,
        "posterior_mastery": posterior,
        "mastery_after": next_mastery,

        "base_guess": p_g,
        "base_slip": p_s,

        "effective_guess": effective_guess,
        "effective_slip": effective_slip,

        "time_taken_seconds": time_taken_seconds,
        "response_signal": response_signal,

        "confidence": confidence
    }
def update_mastery_dont_know(
    current_mastery: float,
    p_t: float,
    uncertainty_penalty: float = 0.20
) -> dict:
    """
    Handle an explicit "I Don't Know" response.

    This is intentionally NOT treated as a standard
    incorrect multiple-choice response.

    Rationale:
    - There is no guessing contamination.
    - The response explicitly signals uncertainty.
    - We apply a moderate reduction in mastery evidence,
      rather than the full standard incorrect BKT update.

    Parameters
    ----------
    current_mastery : float
        Current P(L).

    p_t : float
        Learning transition probability.

    uncertainty_penalty : float
        Fraction of current mastery removed before the
        learning transition.

        Example:
        current mastery = 0.60
        penalty = 0.20

        evidence-adjusted mastery:
        0.60 * (1 - 0.20) = 0.48

    Returns
    -------
    dict
        Diagnostic information for the attempt.
    """

    _validate_probability(
        current_mastery,
        "current_mastery"
    )

    _validate_probability(
        p_t,
        "p_t"
    )

    _validate_probability(
        uncertainty_penalty,
        "uncertainty_penalty"
    )


    # --------------------------------------------------
    # 1. MODERATE NEGATIVE EVIDENCE
    # --------------------------------------------------

    evidence_mastery = (
        current_mastery
        * (1 - uncertainty_penalty)
    )


    # --------------------------------------------------
    # 2. LEARNING TRANSITION
    #
    # The student still interacted with the problem,
    # so we retain the usual BKT opportunity-to-learn
    # transition.
    # --------------------------------------------------

    next_mastery = apply_learning_transition(
        posterior_mastery=evidence_mastery,
        p_t=p_t
    )


    return {
        "mastery_before": current_mastery,
        "posterior_mastery": evidence_mastery,
        "mastery_after": next_mastery,

        "answer_type": "dont_know",
        "response_signal": "explicit_uncertainty",

        "uncertainty_detected": True,
        "uncertainty_penalty": uncertainty_penalty
    }


def process_attempt(
    current_mastery: float,
    answer_type: str,
    p_t: float,
    p_g: float,
    p_s: float,
    correct: bool | None = None,
    time_taken_seconds: float | None = None,
    confidence: float | None = None
) -> dict:
    """
    Route an attempt through the appropriate
    TutorTrace mastery update pathway.

    Supported answer types:
    - selected_option
    - dont_know
    """

    valid_answer_types = {
        "selected_option",
        "dont_know"
    }


    if answer_type not in valid_answer_types:
        raise ValueError(
            f"Unsupported answer_type: {answer_type}"
        )


    # --------------------------------------------------
    # CASE 1:
    # EXPLICIT "I DON'T KNOW"
    # --------------------------------------------------

    if answer_type == "dont_know":

        return update_mastery_dont_know(
            current_mastery=current_mastery,
            p_t=p_t
        )


    # --------------------------------------------------
    # CASE 2:
    # NORMAL SELECTED OPTION
    # --------------------------------------------------

    if correct is None:
        raise ValueError(
            "correct must be provided for selected_option."
        )


    if time_taken_seconds is None:
        raise ValueError(
            "time_taken_seconds must be provided "
            "for selected_option."
        )


    result = update_mastery_response_aware(
        current_mastery=current_mastery,
        correct=correct,
        time_taken_seconds=time_taken_seconds,
        p_t=p_t,
        p_g=p_g,
        p_s=p_s,
        confidence=confidence
    )


    result["answer_type"] = (
        "selected_option"
    )

    result["uncertainty_detected"] = (
        False
    )


    return result