class GrapheneException(Exception):
    def __init__(self, message, status=400):
        self.context = {"message": message, "status": status}
        super().__init__(message)
