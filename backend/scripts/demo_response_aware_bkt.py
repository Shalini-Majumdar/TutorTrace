from backend.app.core.bkt_engine import (
    update_mastery,
    update_mastery_response_aware,
    update_mastery_dont_know
)


CURRENT = 0.30

PARAMS = {
    "p_t": 0.15,
    "p_g": 0.25,
    "p_s": 0.10
}


print(
    "\n========== STANDARD CORRECT =========="
)

standard_correct = update_mastery(
    current_mastery=CURRENT,
    correct=True,
    **PARAMS
)

print(
    "Mastery:",
    round(standard_correct, 4)
)


print(
    "\n========== SLOW CORRECT =========="
)

slow_correct = update_mastery_response_aware(
    current_mastery=CURRENT,
    correct=True,
    time_taken_seconds=45,
    **PARAMS
)

print(
    slow_correct
)


print(
    "\n========== NORMAL INCORRECT =========="
)

normal_incorrect = (
    update_mastery_response_aware(
        current_mastery=0.60,
        correct=False,
        time_taken_seconds=10,
        **PARAMS
    )
)

print(
    normal_incorrect
)


print(
    "\n========== FAST INCORRECT =========="
)

fast_incorrect = (
    update_mastery_response_aware(
        current_mastery=0.60,
        correct=False,
        time_taken_seconds=2,
        **PARAMS
    )
)

print(
    fast_incorrect
)
print(
    "\n========== I DON'T KNOW =========="
)

dont_know = update_mastery_dont_know(
    current_mastery=0.60,
    p_t=0.15
)

print(
    dont_know
)