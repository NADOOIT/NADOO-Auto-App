from mentat.config import Config


class AppConfig(Config):
    def __init__(self):
        super().__init__()
        self.provider = "anthropic"
        self.model = "claude-3-5-sonnet-20240620"

    @staticmethod
    def get_provider(self):
        return self.provider

    @staticmethod
    def get_model(self):
        return self.model
