from pathlib import Path


APP_DIR = Path(__file__).resolve().parents[1]

BACKEND_DIR = APP_DIR.parent

DATA_DIR = (
    BACKEND_DIR / "data"
)


BKT_PARAMS_PATH = (
    DATA_DIR / "bkt_params.json"
)

SKILL_TAXONOMY_PATH = (
    DATA_DIR / "skill_taxonomy.json"
)

QUESTIONS_PATH = (
    DATA_DIR / "questions.json"
)

PREREQUISITES_PATH = (
    DATA_DIR / "prerequisites.json"
)

MOCK_STUDENTS_PATH = (
    DATA_DIR / "mock_students.json"
)