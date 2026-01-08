from typing import List

from .model import VMState


def observe_live() -> List[VMState]:
    """
    Live observation — replaced by real adapter at runtime.
    """
    raise NotImplementedError("Live observation not implemented — use an adapter")


def observe_replay(path: str) -> List[VMState]:
    """
    Replay observation from JSON snapshot — enables time-travel testing.
    Replay ≡ live → deterministic plan guaranteed.
    """
    import json
    from pathlib import Path

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [VMState(**item) for item in data]
