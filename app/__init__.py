from typing import Optional

from flask import Flask, Response, jsonify

from .exceptions import ValidationException
from .models import db
from .api import api


def create_app(config: Optional[dict] = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE="sqlite:///polynomial.db",
    )
    if config:
        app.config.update(config)

    db.init_app(app)

    @app.errorhandler(ValidationException)
    def handle_validation_error(error: ValidationException) -> Response:
        """Transforms caught ValidationException into a Json response"""
        response = jsonify(errors=error.message, detail="Validation Error")
        response.status_code = error.status_code
        return response

    app.register_blueprint(api)

    return app
