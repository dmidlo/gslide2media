from .google_api_project import ManualSteps

class ImportClientSecret:
    def __init__(self):
        self.import_google_client_secret_json_dialog = ManualSteps.import_google_client_secret_json_dialog

    def __call__(self):
        return self.import_google_client_secret_json_dialog()
