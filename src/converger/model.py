from dataclasses import dataclass
from typing import Literal, Optional


@dataclass(frozen=True)
class VMState:
    vmid: int
    name: str
    status: Literal["running", "stopped", "unknown"]
    cpus: Optional[int] = None
    maxmem: Optional[int] = None
    source: str = "live"
    node: Optional[str] = None


@dataclass
class Desired:
    vmid: int
    name: str
    target: Literal["running", "stopped"]
    cpus: Optional[int] = None
    memory: Optional[int] = None


@dataclass
class PlanStep:
    vmid: int
    name: str
    action: Literal["start", "stop", "resize", "noop"]
    reason: str
    node: Optional[str] = None
    target_cpus: Optional[int] = None
    target_memory: Optional[int] = None
