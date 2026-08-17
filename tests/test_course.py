"""Tests del curso de fermentación (4.4): listado, detalle, i18n y frontend."""

from app.main import app
from app.services.course import MODULES, module_detail, module_list
from fastapi.testclient import TestClient

client = TestClient(app)


def test_five_modules():
    assert len(MODULES) == 5


def test_module_list_fields():
    mods = module_list("es")
    m = mods[0]
    assert {"slug", "title", "subtitle", "difficulty", "estimated_hours", "lesson_count"} <= set(m)
    assert m["lesson_count"] >= 1


def test_module_list_bilingual():
    es = module_list("es")
    en = module_list("en")
    assert es[0]["title"] != en[0]["title"]


def test_module_detail_lessons():
    d = module_detail("seguridad", "es")
    assert d is not None
    assert d["lesson_count"] == len(d["lessons"])
    assert d["lessons"][0]["duration_min"] > 0
    assert all(s["bullets"] for lesson in d["lessons"] for s in lesson["sections"] if lesson["slug"] == "alarmas")


def test_module_detail_unknown():
    assert module_detail("nope") is None


def test_endpoint_list():
    r = client.get("/course")
    assert r.status_code == 200
    assert len(r.json()) == 5


def test_endpoint_detail_en():
    r = client.get("/course/seguridad?lang=en")
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "Safety"
    assert body["lesson_count"] == 4


def test_endpoint_404():
    assert client.get("/course/nope").status_code == 404


def test_endpoint_public_api():
    assert client.get("/api/v1/course").status_code == 200


def test_frontend_course_integration():
    html = client.get("/").text
    assert 'id="course-btn"' in html
    assert 'id="course-modal"' in html
    js = client.get("/static/app.js").text
    for marker in ["openCourseModal", "renderCourseLesson", "showCourseCertificate",
                   "pantry_course_progress", "course-next-btn", "course_title"]:
        assert marker in js, marker


def test_course_i18n_keys_in_sync():
    js = client.get("/static/app.js").text
    assert 'course_title: "Curso de Fermentación"' in js
    assert 'course_title: "Fermentation Course"' in js