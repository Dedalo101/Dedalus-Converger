# Contributing to Dedalus Converger

Dedalus Converger is not a traditional open-source project. The **core reconciliation engine is proprietary**. The **adapter ecosystem is open** (Apache 2.0).

We want infrastructure teams to build adapters, get them featured, and optionally become SaaS customers. That is the whole point.

---

## What You Can Contribute (Open)

| Area | License | How |
|------|---------|-----|
| New observation adapters | Apache 2.0 | PR or partner submission |
| Adapter documentation | Apache 2.0 | PR to `docs/INTEGRATIONS.md` |
| Replay fixtures & test cases | Apache 2.0 | PR to `examples/` and `tests/` |
| Schema improvements (`replay.schema.json`) | Apache 2.0 | PR with test coverage |

Read [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md) before writing an adapter.

---

## What You Cannot Contribute Without a License

| Area | Why |
|------|-----|
| Changes to `observe.py`, `plan.py`, `safety.py`, `apply.py` | Proprietary spine — contract is locked |
| Safety policy changes | Enforced guarantees — see `docs/DESIGN.md` |
| Multi-tenant / SaaS infrastructure | Lives in private collaborator repo |

If you believe the spine needs a change, open a **design discussion** via the partner channel (below). We will not merge spine changes via public PR.

---

## Adapter Partner Program

For teams shipping production adapters or joining the private SaaS beta:

### 1. Express interest

Email [licensing@dedalo101.com](mailto:licensing@dedalo101.com) with:

- Team name and infrastructure stack (Proxmox, AWS, K8s, DFIR tooling, etc.)
- Adapter you plan to build or maintain
- Whether you want SaaS early access, revenue share, or both

### 2. Sign the NDA

Adapter partners receive:

- Early access to the private `saas/` collaborator repository
- Roadmap input and direct channel to Dedalo101 engineering
- Featured placement for shipped adapters (site + docs)
- Optional revenue share for adapters that drive SaaS signups

NDA process: [docs/PRIVATE_COLLABORATION.md](docs/PRIVATE_COLLABORATION.md)

### 3. Build against the contract

Your adapter must:

- Inherit from `ObservationAdapter` ([base.py](src/converger/adapters/base.py))
- Emit honest `VMState` — raise `ObservationError` on partial truth
- Register via `AdapterRegistry`
- Include tests with replay fixtures (no live infra required in CI)

### 4. Submit for review

**Option A — Partner (recommended):** Push to your branch in the collaborator repo after NDA.

**Option B — Direct PR:** Open a PR against this repository with:

- Adapter code under `src/converger/adapters/`
- Tests in `tests/`
- Example config in `examples/`
- Entry in `docs/INTEGRATIONS.md` adapter table

We review for contract compliance, not style preferences.

---

## Code Standards

```bash
pip install -e ".[dev]"
pytest tests/ -v
ruff check .
black --check .
```

Adapters must pass existing spine tests. Do not weaken refusal semantics to make an adapter "work."

---

## Recognition

Featured adapters are credited on:

- [dedalus-converger.pages.dev](https://dedalus-converger.pages.dev)
- `docs/INTEGRATIONS.md` adapter registry table
- Release notes when the adapter ships

Partners who convert to SaaS customers keep priority support for their adapter.

---

## Questions

- **Adapter technical:** read [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md), then open an issue or email licensing@
- **Partnership / NDA / SaaS beta:** [docs/PRIVATE_COLLABORATION.md](docs/PRIVATE_COLLABORATION.md)
- **Commercial licensing:** [licensing@dedalo101.com](mailto:licensing@dedalo101.com)