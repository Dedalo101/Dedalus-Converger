from abc import ABC, abstractmethod
from typing import List, Dict, Any

from ..model import VMState


class ObservationError(Exception):
    """Raised when observation cannot be completed honestly and completely.
    Adapters MUST raise this instead of returning partial/invalid data."""

    pass


class ObservationAdapter(ABC):
    """All observation adapters MUST inherit from this class."""

    name: str = NotImplemented
    required_config_keys: set[str] = set()

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._validate_config()

    def _validate_config(self) -> None:
        missing = self.required_config_keys - set(self.config.keys())
        if missing:
            raise ObservationError(
                f"Adapter {self.name!r} missing required config keys: {', '.join(sorted(missing))}"
            )

    @abstractmethod
    def observe(self) -> List[VMState]:
        """Must return complete, honest observation or raise ObservationError.
        Never retry. Never partial results. Never side effects."""
        raise NotImplementedError
