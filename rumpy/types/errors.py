class RequestError(BaseException):
    def __init__(self, status_code, method, url, message):
        self.status_code = status_code
        self.method = method
        self.url = url
        self.message = message
        super().__init__(message)
