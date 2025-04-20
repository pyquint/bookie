from flask import jsonify
from werkzeug.exceptions import HTTPException
from werkzeug.http import HTTP_STATUS_CODES

from app.api.books import api

# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xxiii-application-programming-interfaces-apis


def error_response(status_code, message=None):
    payload = {"error": HTTP_STATUS_CODES.get(status_code, "Unknown error")}
    if message:
        payload["message"] = message
    return payload, status_code


def bad_request(message):
    return error_response(400, message)


@api.errorhandler(HTTPException)
def handle_http_exception(e):
    return error_response(e.code)


def forbidden(message=None):
    response = jsonify({"error": "Forbidden", "message": message})
    response.status_code = 403
    return response


