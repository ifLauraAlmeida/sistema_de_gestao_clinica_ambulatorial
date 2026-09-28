class FakeHealthCheck:
    """Dependência simulada com resultado fixo."""

    def __init__(self, name: str, healthy: bool) -> None:
        self.name = name
        self._healthy = healthy

    def is_healthy(self) -> bool:
        return self._healthy
