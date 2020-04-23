class NetworkException(Exception):
    def __init__(self, error_code, error_message = "", *args, **kwargs):
        self.error_code = error_code
        self.error_message = error_message

class BadRequest(NetworkException):
    def __init__(self):
        super().__init__(error_code = 400, error_message="Bad Request")

class GenericError(NetworkException):
    def __init__(self):
        super().__init__(error_code = 500, error_message="Something Went Wrong")

class NotFound(NetworkException):
    def __init__(self):
        super().__init__(error_code = 404, error_message="Microservice Not Found")

class RSAKeyFailed(NetworkException):
    def __init__(self):
        super().__init__(error_code = 407, error_message="Public Key not Correct")

class OperationNotAllowed(NetworkException):
    def __init__(self):
        super().__init__(error_code = 405, error_message="Operation not allowed")
