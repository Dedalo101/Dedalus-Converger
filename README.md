# Dedalus Converger

**The honest reconciliation engine. Build adapters — we host the engine.**

Observe → Plan → Safety → [Audit | Apply]

If truth is incomplete, the system does nothing.

**Product site:** [dedalus-converger.pages.dev](https://dedalus-converger.pages.dev)  
**Commercial SaaS & licensing:** [licensing@dedalo101.com](mailto:licensing@dedalo101.com)

---

## The Model

Dedalus Converger follows the Redis / MongoDB / Elastic playbook: **open ecosystem at the edges, proprietary moat at the core, SaaS for revenue.**

```
┌─────────────────────────────────────────────────────────────────┐
│  YOUR ADAPTERS (open)          │  CORE SPINE (proprietary)      │
│  Proxmox, AWS, Replay, DFIR…   │  observe → plan → safety       │
│  docs/INTEGRATIONS.md          │  enforcement, audit, apply       │
└───────────────┬────────────────┴───────────────┬────────────────┘
                │                                │
                └──────── VMState contract ──────┘
                                 │
                    ┌────────────▼────────────┐
                    │  DEDALUS SAAS (revenue) │
                    │  hosted reconciliation  │
                    │  enterprise adapters    │
                    │  compliance & support   │
                    └─────────────────────────┘
```

| Layer | What | License | Who it's for |
|-------|------|---------|--------------|
| **Open** | Adapter framework, example adapters, CLI (basic), test utilities | [LICENSE-ADAPTERS](LICENSE-ADAPTERS) (Apache 2.0) | Integrators, infra teams, DFIR shops |
| **Proprietary** | Reconciliation spine, safety guarantees, multi-tenant orchestration, audit trails | [LICENSE](LICENSE) | Dedalo101 + licensed customers |
| **SaaS** | Hosted service, pre-built enterprise adapters, compliance reporting, SLAs | Commercial subscription | Enterprises, MSPs, DFIR firms |

See [docs/VISION.md](docs/VISION.md) for the full strategy and roadmap.

---

## For Everyone — Use the CLI, Build Adapters

The adapter framework is open. You can observe, plan, and audit without touching the proprietary spine source.

```bash
git clone https://github.com/Dedalo101/Dedalus-Converger.git
cd Dedalus-Converger
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Replay-based audit (no live infra required)
converger audit --desired examples/desired.yaml --replay examples/replay.json

# Write plan artifact
converger plan --desired examples/desired.yaml --replay examples/replay.json --output plan.json

# Live Proxmox (requires converger.yaml + --confirm for apply)
cp examples/converger.yaml.example converger.yaml
converger apply --desired examples/desired.yaml --dry-run
```

**Build your own adapter:** [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md)  
**Contribute or partner:** [CONTRIBUTING.md](CONTRIBUTING.md)

Every run emits structured JSON — no log parsing:

- `current.json` — observation snapshot
- `plan.json` — reconciliation steps
- `result.json` — apply outcomes
- `post_apply_report.json` — convergence verification

---

## For Enterprises — Hosted Reconciliation (SaaS)

Stop tying apply to one engineer's laptop.

| Tier | From | Includes |
|------|------|----------|
| **Pro** | $49/mo | Hosted scheduler, drift alerts, artifact history |
| **DFIR** | $199/mo | Velociraptor / KAPE presets, case workspace, gated apply |
| **MSP** | $299/mo | White-label multi-tenant reconciliation |
| **Enterprise** | Custom | Compliance reporting, dedicated support, custom SLAs |

Contact [licensing@dedalo101.com](mailto:licensing@dedalo101.com) or visit [dedalus-converger.pages.dev](https://dedalus-converger.pages.dev).

---

## For Partners — Private Beta & Adapter Program

Infrastructure teams building adapters get early SaaS access, roadmap input, and featured placement.

1. Read [docs/PRIVATE_COLLABORATION.md](docs/PRIVATE_COLLABORATION.md)
2. Sign the adapter partner NDA
3. Get access to the private `saas/` collaborator repo
4. Ship an adapter → we host the engine

**Target:** 3–5 infrastructure teams for private beta. Revenue-share option for featured adapters.

---

## Core Guarantees (Locked)

The spine encodes refusal as first-class behavior. It will **never**:

- Act on incomplete or partial truth
- Treat "missing" as "stopped"
- Retry or heal failed observations
- Discover or expand scope implicitly
- Mutate state during audit or plan modes
- Bypass safety policies via replay
- Stop production workloads by default (`prod-*` protection)

Guarantees are enforced in code. See [docs/DESIGN.md](docs/DESIGN.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## Repository Layout

```
src/converger/
├── observe.py, plan.py, safety.py, apply.py   # Proprietary spine
├── adapters/
│   ├── base.py, registry.py                   # Open framework
│   ├── replay.py, proxmox.py                  # Open examples
│   └── aws.py, hetzner.py, …                  # Enterprise / SaaS
docs/
├── INTEGRATIONS.md      # Adapter authoring guide (open)
├── VISION.md            # Strategy & SaaS roadmap
├── PRIVATE_COLLABORATION.md
├── ARCHITECTURE.md
└── DESIGN.md
```

---

## Why This Wins

- **Collaborators feel ownership** — they build adapters, get them featured
- **Lock-in through quality** — free adapters make SaaS irresistible
- **Moat stays protected** — core spine stays proprietary
- **Network effects** — more adapters → more SaaS signups
- **Reference customers early** — private collaborators become first paying customers

---

## License

- **Core engine** (`src/converger/` spine, safety, orchestration): [LICENSE](LICENSE) — commercial proprietary
- **Adapter framework & examples** (`docs/INTEGRATIONS.md`, `adapters/base.py`, `replay.py`, `proxmox.py`, tests): [LICENSE-ADAPTERS](LICENSE-ADAPTERS) — Apache 2.0

© 2026 Dedalo101. All rights reserved.