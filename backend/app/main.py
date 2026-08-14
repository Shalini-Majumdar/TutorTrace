from fastapi import (
    FastAPI,
    HTTPException
)
from backend.app.services.teacher_service import (
    get_classroom,
    get_classroom_alerts
)
from backend.app.models.schemas import (
    SubmitAnswerRequest
)

from backend.app.services.student_service import (
    start_student,
    get_next_question,
    submit_answer,
    get_student_mastery,
    get_student_diagnostics
)


app = FastAPI(
    title="TutorTrace API",
    description=(
        "Adaptive tutoring backend using "
        "Bayesian Knowledge Tracing, "
        "response-aware evidence, "
        "misconception diagnostics and "
        "prerequisite reasoning."
    ),
    version="0.1.0"
)


# ==========================================================
# ROOT
# ==========================================================

@app.get("/")
def root():

    return {
        "name": "TutorTrace",
        "status": "running"
    }


# ==========================================================
# HEALTH
# ==========================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ==========================================================
# START STUDENT
# ==========================================================

@app.post(
    "/students/{student_id}/start"
)
def start_student_endpoint(
    student_id: str
):

    try:

        state = start_student(
            student_id
        )

        return {
            "message":
                "Student initialized.",

            "student_id":
                student_id,

            "skills":
                state["skills"],

            "cold_start":
                state["cold_start"]
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# ==========================================================
# NEXT QUESTION
# ==========================================================

@app.get(
    "/students/{student_id}/next-question"
)
def next_question_endpoint(
    student_id: str
):

    try:

        return get_next_question(
            student_id
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


# ==========================================================
# SUBMIT ANSWER
# ==========================================================

@app.post(
    "/students/{student_id}/submit-answer"
)
def submit_answer_endpoint(
    student_id: str,
    request: SubmitAnswerRequest
):

    try:

        return submit_answer(
            student_id=student_id,
            payload=request.model_dump()
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# ==========================================================
# MASTERY
# ==========================================================

@app.get(
    "/students/{student_id}/mastery"
)
def mastery_endpoint(
    student_id: str
):

    try:

        return get_student_mastery(
            student_id
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


# ==========================================================
# DIAGNOSTICS
# ==========================================================

@app.get(
    "/students/{student_id}/diagnostics"
)
def diagnostics_endpoint(
    student_id: str
):

    try:

        return get_student_diagnostics(
            student_id
        )

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

# ==========================================================
# TEACHER CLASSROOM
# ==========================================================

@app.get(
    "/teacher/classroom"
)
def teacher_classroom_endpoint():

    try:

        return get_classroom()

    except ValueError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ==========================================================
# TEACHER ALERTS
# ==========================================================

@app.get(
    "/teacher/alerts"
)
def teacher_alerts_endpoint():

    try:

        return get_classroom_alerts()

    except ValueError as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )