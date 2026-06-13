# Adapter Integrations

**Open framework (Apache 2.0).** Build adapters — Dedalo101 hosts the engine.

Adapters are the only swappable layer in Dedalus Converger. The reconciliation spine (`observe → plan → safety → apply`) never sees your infrastructure types.

---

## The Contract

Every adapter emits `VMState`:

```python
@dataclass(frozen=True)
class VMState:
    vmid: int
    name: str
    status: Literal["running", "stopped", "unknown"]
    cpus: Optional[int] = None
    maxmem: Optional[int] = None
    source: str = "live"
    node: Optional[str] = None
    external_id: Optional[str] = None
    instance_type: Optional[str] = None
    server_type: Optional[str] = None
```

### Status semantics

| Status | Meaning | Planner behavior |
|--------|---------|------------------|
| `running` | Entity is executing | Diff against desired |
| `stopped` | Entity exists, not running | May start if desired |
| `unknown` | Partial or failed observation | **Refuse** — empty plan |
| *(absent)* | Not in observation list | Treated as **missing**, not stopped |

**Critical:** `missing ≠ stopped`. Never map a failed API call to `stopped`.

---

## Adapter Interface

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from converger.model import VMState

class ObservationAdapter(ABC):
    name: str = NotImplemented
    required_config_keys: set[str] = set()

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._validate_config()

    @abstractmethod
    def observe(self) -> List[VMState]:
        """Complete honest observation or raise ObservationError.
        Never retry. Never partial results. Never side effects."""
        ...
```

Register your adapter:

```python
from converger.adapters.registry import AdapterRegistry

class MyCloudAdapter(ObservationAdapter):
    name = "mycloud"
    required_config_keys = {"api_token", "region"}

    def observe(self) -> List[VMState]:
        # ... fetch from API ...
        return states

AdapterRegistry.register(MyCloudAdapter)
```

---

## Reference Implementations (Open)

| Adapter | File | Use case |
|---------|------|----------|
| **Replay** | `adapters/replay.py` | JSON fixtures, CI, time-travel tests |
| **Proxmox** | `adapters/proxmox.py` | Live hypervisor observation |
| **Proxmox apply** | `adapters/proxmox_apply.py` | Reference apply path (mutations) |

Enterprise adapters (AWS, Hetzner, DFIR presets) ship with SaaS tiers or commercial licenses.

---

## Step-by-Step: New Adapter

### 1. Create the adapter module

```
src/converger/adapters/mycloud.py
```

### 2. Implement `observe()`

Rules:

- **Read-only** — no mutations in observe
- **Complete or fail** — raise `ObservationError`, never return partial lists
- **No retries** — one honest attempt
- **No discovery** — observe only what config specifies
- **Map honestly** — if CPU count is unavailable, omit field; if status is ambiguous, use `unknown`

### 3. Add config example

```
examples/converger.mycloud.yaml.example
```

```yaml
source: mycloud
mycloud:
  api_token: ${MYCLOUD_TOKEN}
  region: eu-central-1
```

### 4. Add replay fixture for tests

```
examples/replay/mycloud.json   # conforms to schemas/replay.schema.json
```

### 5. Write tests

```python
def test_mycloud_adapter_replay():
    config = {"source": "replay", "path": "examples/replay/mycloud.json"}
    states = observe_from_config(config)
    assert all(s.status in ("running", "stopped", "unknown") for s in states)
```

### 6. Register in docs

Add a row to the adapter table below and open a PR or partner submission.

---

## Replay Schema

Offline adapters and tests use `schemas/replay.schema.json`:

```json
[
  {
    "vmid": 100,
    "name": "web-01",
    "status": "running",
    "cpus": 2,
    "maxmem": 4294967296,
    "source": "replay"
  }
]
```

Validate with:

```bash
converger plan -d examples/desired.yaml -r examples/replay.json
```

---

## Adapter Registry

| Name | License | Maintainer | Status |
|------|---------|------------|--------|
| `replay` | Apache 2.0 | Dedalo101 | Stable |
| `proxmox` | Apache 2.0 | Dedalo101 | Stable |
| `aws` | Commercial | Dedalo101 | SaaS / Enterprise |
| `hetzner` | Commercial | Dedalo101 | SaaS / Enterprise |
| `dfir` | Commercial | Dedalo101 | SaaS / DFIR tier |
| *your adapter* | Apache 2.0 (yours) | Partner | Submit → |

Want your adapter featured? See [CONTRIBUTING.md](../CONTRIBUTING.md) and [PRIVATE_COLLABORATION.md](PRIVATE_COLLABORATION.md).

---

## Apply Adapters (Advanced)

Observation adapters feed the spine. **Apply** is a separate, mutating path with its own applier registry (`appliers.py`). Apply adapters require stricter review and are typically Dedalo101-maintained or partner-maintained under NDA.

For observation-only integrations (audit/plan), you only need an observation adapter.

---

## Anti-Patterns

| Do not | Why |
|--------|-----|
| Retry failed API calls in `observe()` | Hides incomplete truth |
| Default `unknown` → `stopped` | Violates refusal semantics |
| Import Proxmox types in `plan()` | Coupling leaks into spine |
| Auto-discover VMs not in desired list | Scope expansion is forbidden |
| Mutate infrastructure in `observe()` | Only `apply` may mutate |

---

## CLI Usage

```bash
# Your adapter via config
converger audit -c examples/converger.mycloud.yaml.example -d examples/desired.yaml

# Source override (once registered in CLI choices)
converger plan -c converger.yaml -d examples/desired.yaml -s mycloud
```

---

## Support

- Technical adapter questions: open an issue or email [licensing@dedalo101.com](mailto:licensing@dedalo101.com)
- Partner program & featured placement: [PRIVATE_COLLABORATION.md](PRIVATE_COLLABORATION.md)