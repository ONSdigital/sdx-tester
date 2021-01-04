

class Result:

    def __init__(self, survey_dict) -> None:
        self.survey_dict = survey_dict
        self.dap_message = None
        self.receipt = None
        self.quarantine = None
        self.files = {}
        self._errors = []

    def get_tx_id(self):
        return self.survey_dict['tx_id']

    def set_dap(self, dap_message):
        self.dap_message = dap_message

    def set_receipt(self, receipt):
        self.receipt = receipt

    def set_quarantine(self, quarantine):
        self.quarantine = quarantine

    def set_files(self, files: dict):
        self.files = files

    def record_error(self, error):
        self._errors.append(error)

    def __str__(self) -> str:
        return f'''dap_message: {self.dap_message}
                receipt: {self.receipt}
                quarantine: {self.quarantine}
                files: {self.files}
                errors: {self._errors}
              '''
