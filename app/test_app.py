import pytest
from peewee import SqliteDatabase

from . import create_app
from .models import Polynomial


MODELS = (Polynomial,)


@pytest.fixture
def client():
    test_db = SqliteDatabase(":memory:")
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()
    test_db.create_tables(MODELS)

    app = create_app(config={"DATABASE": "sqlite:///:memory:"})
    with app.test_client() as client:
        yield client

    test_db.drop_tables(MODELS)
    test_db.close()


def test_post_poly(client):
    expr = "4x^2y - 2xy^2 + x - 7"
    resp = client.post("/api/poly", data={"polynomial": expr})
    assert resp.status_code == 200

    assert Polynomial.select().count() == 1
    polynomial = Polynomial.select().first()
    assert polynomial.expression == expr

    assert resp.json == {"polynomial_id": polynomial.id}


def test_post_duplicate_poly(client):
    expr = "4x^2y - 2xy^2 + x - 7"
    Polynomial.create(expression=expr)
    resp = client.post("/api/poly", data={"polynomial": expr})
    assert resp.status_code == 400
    assert resp.json == {
        "detail": "Validation Error",
        "errors": "Polynomial expression already exists.",
    }
    assert Polynomial.select().count() == 1


def test_post_poly_invalid_expr(client):
    expr = "lorem ipsum dolor sit amed"
    resp = client.post("/api/poly", data={"polynomial": expr})
    assert resp.status_code == 400
    assert resp.json == {
        "detail": "Validation Error",
        "errors": "Invalid polynomial expression.",
    }
    assert Polynomial.select().count() == 0


def test_post_univariate_polynomial(client):
    expr = "2x^2"
    resp = client.post("/api/poly", data={"polynomial": expr})
    assert resp.status_code == 400
    assert resp.json == {
        "detail": "Validation Error",
        "errors": "Polynomial expression is not of 2 variables (x, y)."
    }
    assert Polynomial.select().count() == 0


def test_post_not_valid_polynomial(client):
    expr = "x2+1x"
    resp = client.post("/api/poly", data={"polynomial": expr})
    assert resp.status_code == 400
    assert resp.json == {
        "detail": "Validation Error",
        "errors": "Invalid polynomial expression."
    }
    assert Polynomial.select().count() == 0


def test_eval_poly(client):
    expr = "x^2 + 3y^3"
    polynomial = Polynomial.create(expression=expr)
    resp = client.get(f"/api/poly/eval/{polynomial.id}?x={2}&y={3}")
    assert resp.status_code == 200
    assert resp.json == {"value": 85.0}


def test_eval_poly_invalid_arguments(client):
    expr = "x^2 + 3y^3"
    polynomial = Polynomial.create(expression=expr)
    resp = client.get(f"/api/poly/eval/{polynomial.id}?x=x&y=y")
    assert resp.status_code == 400
    assert resp.json == {
        "detail": "Validation Error",
        "errors": "X and Y are required.",
    }


def test_eval_poly_not_found(client):
    expr = "x^2 + 3y^3"
    Polynomial.create(expression=expr)
    resp = client.get("/api/poly/eval/1000?x=x&y=y")
    assert resp.status_code == 404
