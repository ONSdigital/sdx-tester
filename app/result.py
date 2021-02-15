

class Result:

    def __init__(self, tx_id: str) -> None:
        self.tx_id = tx_id
        self.dap_message = None
        self.receipt = None
        self.quarantine = None
        self.files = {}
        self.errors = []
        self.timeout = False

    def get_tx_id(self):
        return self.tx_id

    def set_dap(self, dap_message):
        self.dap_message = dap_message

    def set_receipt(self, receipt):
        self.receipt = receipt

    def set_quarantine(self, quarantine):
        self.quarantine = quarantine

    def set_timeout(self, timeout):
        self.timeout = timeout

    def set_files(self, files: dict):
        self.files = files

    def record_error(self, error):
        self.errors.append(error)

    def __str__(self) -> str:
        return f'''dap_message: {self.dap_message}
                receipt: {self.receipt}
                quarantine: {self.quarantine}
                files: {self.files.keys()}
                errors: {self.errors}
                timeout: {self.timeout}
              '''
