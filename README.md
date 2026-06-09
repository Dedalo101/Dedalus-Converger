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

# Apply against live Proxmox (requires converger.yaml + --confirm)
cp examples/converger.yaml.example converger.yaml
converger apply --desired examples/desired.yaml --confirm

# Dry-run apply (records Proxmox API calls, no mutations)
converger apply --desired examples/desired.yaml --dry-run

# Cloud / DFIR observation
converger plan -c examples/converger.aws.yaml.example -d examples/desired.yaml -s aws
converger plan -c examples/converger.dfir.yaml.example -d examples/desired.yaml --dfir examples/dfir_systems.json

# DFIR import presets (Velociraptor / KAPE field maps)
converger plan -d examples/desired.yaml --dfir examples/dfir/velociraptor_clients.json --dfir-preset velociraptor
converger plan -d examples/desired.yaml --dfir examples/dfir/kape_hosts.json --dfir-preset kape

# Cloud apply (dry-run records API calls; live requires --confirm)
converger apply -c examples/converger.aws.yaml.example -d examples/desired.yaml -s aws --dry-run
converger apply -d examples/desired.yaml -s hetzner --dry-run

# Scheduled reconciliation (cron / GitHub Actions)
bash scripts/reconcile.sh plan                    # replay default
CONVERGER_SOURCE=proxmox bash scripts/reconcile.sh audit
# GitHub Actions: .github/workflows/reconcile.yml (every 6h + workflow_dispatch)

# Artifacts emitted on every run:
# current.json          — observation snapshot
# plan.json             — reconciliation steps
# result.json           — apply outcomes
# post_apply.json       — post-apply re-observation
# post_apply_report.json — convergence verification

pytest tests/ -v
ruff check .
black --check .
```
