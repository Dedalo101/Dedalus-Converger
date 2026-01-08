from dataclasses import dataclass
from typing import Literal, Optional

Status = Literal["running", "stopped", "unknown"]


@dataclass(frozen=True)
class VMState:
    vmid: int
    name: str
    status: Status
    cpus: Optional[int] = None
    maxmem: Optional[int] = None
    source: str = "live"


@dataclass(frozen=True)
class Desired:
    vmid: int
    name: str
    target: Literal["running", "stopped"]
    cpus: Optional[int] = None
    memory: Optional[int] = None


@dataclass(frozen=True)
class PlanStep:
    vmid: int
    name: str
    action: Literal["start", "stop", "noop"]
    reason: str
