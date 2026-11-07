"""Errores de negocio que la API traduce al sobre {\"error\": ...}."""


class DomainError(Exception):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message
