from werkzeug.exceptions import HTTPException
from flask import make_response
import json

class BusinessValidationError(HTTPException):
    def __init__(self, status_code, error_code, error_message, **kwargs):
        data = { "error_code" : error_code, "error_message": error_message }
        self.response = make_response(json.dumps({**data, **kwargs}), status_code)

class NotFoundError(HTTPException):
    def __init__(self, status_code):
        self.response = make_response('', status_code)