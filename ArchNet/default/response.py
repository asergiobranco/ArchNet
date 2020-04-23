class ArchNetResponse(dict):

    def __init__(self):
        super().__init__()
        self.set_message("")
        self.set_data([])
        self.set_code(200)

    def set_message(self, message):
        self.__setitem__("message", message)

    def set_code(self, code):
        self.__setitem__("code", code)

    def set_data(self, data):
        self.__setitem__("data", data)

    def set_key(self, key, value):
        self.__setitem__(key, value)

    def generic_error(self):
        self.error("Something went wrong")

    def bad_request(self):
        self.set_code(400)

    def Exception_Raised(self, code, message):
        self.set_code(code)
        self.set_message(message)

    def error(self, message):
        self.set_code(500)
        self.set_message(message)
