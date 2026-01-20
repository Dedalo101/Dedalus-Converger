from typing import List
import json
from ..model import VMState

def observe_replay(file: str) -> List[VMState]:
    with open(file) as f:
        data = json.load(f)
    return [VMState(**vm) for vm in data]
