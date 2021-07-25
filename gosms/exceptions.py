class ApiError(BaseException):
    def __init__(self, data: dict) -> None:
        self.message = data.get('message', '')

        super().__init__(self.message)

        self.error_code = data.get('errorCode')

    def __str__(self) -> str:
        return f"{self.message}; Code: {self.error_code}"
