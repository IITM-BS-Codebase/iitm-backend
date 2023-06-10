import json
from werkzeug.exceptions import HTTPException
from flask import make_response

class BusinessValidationError(HTTPException):
    def __init__(self, error_code, error_message, status_code,**kwargs):
        data = { "error_code" : error_code, "error_message": error_message }
        self.response = make_response(json.dumps({**data, **kwargs}), status_code)

class NotFoundError(HTTPException):
    def __init__(self, status_code):
        self.response = make_response('Requested Resource Not Foudn', status_code)
