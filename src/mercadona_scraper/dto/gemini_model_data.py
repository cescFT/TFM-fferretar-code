class GeminiModelDTO:
    def __init__(self, model_name: str, hours_since_last_petition: int, is_blocked: bool):
        self.model_name = model_name
        self.hours_since_last_petition = hours_since_last_petition
        self.is_blocked = is_blocked == 1

    def get_model_name(self):
        return self.model_name


    def get_hours_since_last_petition(self):
        return self.hours_since_last_petition

    def get_is_blocked(self):
        return self.is_blocked

    def set_is_blocked(self, is_blocked: bool):
        self.is_blocked = is_blocked