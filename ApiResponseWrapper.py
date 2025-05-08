class ApiResponseWrapper:
    def __init__(self, response):
        self._response = response
        try:
            self._json = response.json()
        except ValueError:
            self._json = {}

    @property
    def status_code(self):
        return self._response.status_code

    @property
    def data(self):
        return self._json.get("data")

    @property
    def status(self):
        return self._json.get("status")

    @property
    def errors(self):
        return self._json.get("errors")

    @property
    def full(self):
        return self._json
