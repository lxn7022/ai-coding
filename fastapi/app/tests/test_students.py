from collections.abc import Generator
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.database import Base, get_db
from app.main import app

TEST_DB_FILE = Path(__file__).resolve().parent / "test_students.db"
TEST_DB_URL = f"sqlite:///{TEST_DB_FILE}"
test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function() -> None:
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)


def test_student_crud_flow() -> None:
    create_payload = {
        "student_no": "S10001",
        "name": "Alice",
        "age": 20,
        "gender": "female",
        "major": "Computer Science",
    }
    create_resp = client.post("/students", json=create_payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    student_id = created["id"]

    get_resp = client.get(f"/students/{student_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["student_no"] == "S10001"

    update_payload = {
        "student_no": "S10001",
        "name": "Alice Zhang",
        "age": 21,
        "gender": "female",
        "major": "Software Engineering",
    }
    update_resp = client.put(f"/students/{student_id}", json=update_payload)
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Alice Zhang"

    delete_resp = client.delete(f"/students/{student_id}")
    assert delete_resp.status_code == 204

    missing_resp = client.get(f"/students/{student_id}")
    assert missing_resp.status_code == 404


def test_duplicate_student_no_returns_409() -> None:
    payload = {
        "student_no": "S10002",
        "name": "Bob",
        "age": 19,
        "gender": "male",
        "major": "Math",
    }
    first = client.post("/students", json=payload)
    assert first.status_code == 201

    second = client.post("/students", json=payload)
    assert second.status_code == 409


def test_invalid_age_returns_422() -> None:
    payload = {
        "student_no": "S10003",
        "name": "Carol",
        "age": 0,
        "gender": "female",
        "major": "Physics",
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422
