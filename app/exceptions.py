
class ValidationException(Exception):

    status_code = 400
    message = 'Validation error'

    def __init__(self, message=None, payload=None, status_code=None):
        super().__init__()
        self.message = message or self.message
        self.status_code = status_code or self.status_code
