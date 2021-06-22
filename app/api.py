from flask import Blueprint, Response, request, jsonify
from playhouse.flask_utils import get_object_or_404
from sympy.parsing.sympy_parser import (
    convert_xor,
    parse_expr,
    implicit_multiplication,
    auto_number,
    lambda_notation,
    repeated_decimals,
)
from sympy import symbols, poly

from .exceptions import ValidationException
from .models import Polynomial


api = Blueprint("api", __name__, url_prefix="/api")

# convert xor is used to convert ^ to ** and consider 3x as 3 * x
transformations = (
    lambda_notation,
    repeated_decimals,
    auto_number,
    convert_xor,
    implicit_multiplication,
)


@api.route("/poly", methods=("POST",))
def add_poly() -> Response:
    polynomial_str = (request.form.get("polynomial") or "").strip()
    x, y = symbols("x, y")

    # check if string is a valid expression
    try:
        poly_expr = parse_expr(
            polynomial_str,
            local_dict={"x": x, "y": y, "xy": x + y},
            evaluate=False,
            transformations=transformations)
    except Exception:
        raise ValidationException(message="Invalid polynomial expression.")

    # check if expression is a valid polynomial
    if not poly_expr.is_polynomial():
        raise ValidationException(message="Expression is not a valid polynomial.")

    # check if polynomial is of 2 variables (x, y)
    gens = poly(poly_expr).gens
    if len(gens) < 2 or gens[0] is not x or gens[1] is not y:
        raise ValidationException(message="Polynomial expression is not of 2 variables (x, y).")

    try:
        Polynomial.get(expression=polynomial_str)
        raise ValidationException(message="Polynomial expression already exists.")
    except Polynomial.DoesNotExist:
        pass

    polynomial = Polynomial.create(expression=polynomial_str)
    return jsonify({"polynomial_id": polynomial.id})


@api.route("/poly/eval/<int:poly_id>", methods=("GET",))
def eval_poly(poly_id: int) -> Response:
    polynomial = get_object_or_404(Polynomial, Polynomial.id == poly_id)
    x_value = request.args.get("x", type=float)
    y_value = request.args.get("y", type=float)

    if not x_value and not y_value:
        raise ValidationException(message="X and Y are required.")

    x, y = symbols("x, y")
    poly_expr = parse_expr(
        polynomial.expression,
        local_dict={"x": x, "y": y},
        evaluate=False,
        transformations=transformations)
    value = poly(poly_expr).eval({x: x_value, y: y_value})
    return jsonify({"value": float(value)})
