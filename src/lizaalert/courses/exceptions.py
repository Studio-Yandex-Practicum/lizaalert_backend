class WrongMethodException(BaseException):
    """Кастомное исключение для миксина."""

    def __init__(self, message="Данный метод не поддерживается для этого класса.") -> None:
        self.message = message
        super().__init__(self.message)
