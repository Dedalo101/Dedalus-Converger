Domain-agnostic reconciliation engine with explicit refusal semantics.

Observe → Plan → Safety → [Audit | Apply]

Encodes restraint: refuses partial truth, protects prod workloads, immutable spine.
Replay ≡ live. No blind healing. Swappable adapters.

If truth is incomplete, it does nothing.

# Dedalus Converger

**Domain-agnostic reconciliation with explicit refusal semantics.**

Dedalus Converger is a reconciliation engine that encodes restraint.  
It converges declared intent against observed reality — and refuses to act when truth is incomplete.

Observe → Plan → Safety → [Audit | Apply]


> If truth is partial, the system does nothing.

---

## What This Is

Dedalus Converger is **not** a Proxmox tool.

It is a **reconciliation primitive** built around a tight contract:

- Observation is read-only and honest
- Planning is deterministic and pure
- Safety is enforced through explicit invariants
- Application is the only mutating phase

Any system that can emit the `VMState` contract can use the same spine:
- hypervisors
- cloud APIs
- incident replays
- DFIR reconstructions
- synthetic test fixtures

Live data and replayed data are equivalent.

---

## Core Guarantees (Locked)

Dedalus Converger encodes refusal as a first-class behavior.

The system will **never**:

- Act on incomplete or partial truth
- Treat “missing” as “stopped”
- Retry or heal failed observations
- Discover or expand scope implicitly
- Mutate state during audit or plan modes
- Bypass safety policies via replay
- Reinterpret history or time-travel outcomes
- Stop production workloads by default

If a decision cannot be made safely, the system refuses to act.

These guarantees are enforced in code and documented in `docs/DESIGN.md`.

---

## The Spine (Immutable)

desired.yaml → observe → plan → safety → [audit|apply]


The spine lives in `converger/` and will never change.  
Adapters swap only at the observation boundary.

See `docs/ARCHITECTURE.md` for the full diagram and contract.

---

## Quick Start

```bash
git clone https://github.com/Dedalo101/Dedalus-Converger.git
cd Dedalus-Converger
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Replay-based audit (no live infra required)
converger audit --desired examples/desired.yaml --replay examples/replay.json

# Write plan artifact
converger plan --desired examples/desired.yaml --replay examples/replay.json --output plan.json

# Apply against live Proxmox (requires credentials + --confirm)
converger apply --desired examples/desired.yaml --confirm

pytest tests/ -v
ruff check .
black --check .
```
