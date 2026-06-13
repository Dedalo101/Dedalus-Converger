# Vision — Open Adapters, Proprietary Engine, SaaS Revenue

Dedalus Converger is infrastructure reconciliation with **refusal semantics**: if truth is incomplete, the system does nothing.

This document explains why we split the product into three layers and where we are going.

---

## The Problem

Infrastructure teams reconcile desired state against reality every day — Proxmox, cloud APIs, DFIR artifacts, incident replays. Most tools either:

- **Guess** when observation is partial (dangerous)
- **Couple** reconciliation logic to one vendor (brittle)
- **Hide** decisions in logs (unauditable)

Dedalus Converger refuses to guess. The spine is domain-agnostic. Adapters swap at the observation boundary.

---

## The Strategy

### Proprietary — SaaS Moat

The core stays ours:

- Reconciliation spine (`observe → plan → safety → apply`)
- Safety guarantees and enforcement (`prod-*` protection, refusal on `unknown`)
- Multi-tenant orchestration
- Audit trails and compliance artifacts

This is what customers pay for. This is what cannot fork into a competing hosted service.

### Open — Community Ecosystem

The edges are open (Apache 2.0):

- Adapter framework (`ObservationAdapter`, registry, contract docs)
- Example adapters (Replay, Proxmox)
- Basic CLI for audit/plan against open adapters
- Testing utilities and replay schema

Collaborators build adapters. They get ownership, credit, and a path to revenue share. More adapters make the SaaS offering irresistible.

### SaaS — Revenue

What we sell:

| Capability | Tier |
|------------|------|
| Hosted reconciliation scheduler | Pro+ |
| Drift alerts and artifact history | Pro+ |
| Pre-built enterprise adapters (AWS, Hetzner) | Pro / Enterprise |
| DFIR presets (Velociraptor, KAPE) | DFIR |
| Compliance and audit reporting | DFIR / Enterprise |
| White-label multi-tenant | MSP |
| Support and consulting | Enterprise |

**Site:** [dedalus-converger.pages.dev](https://dedalus-converger.pages.dev)  
**Contact:** [licensing@dedalo101.com](mailto:licensing@dedalo101.com)

---

## Why This Wins

```
More adapters ──→ more use cases ──→ more SaaS signups
       ↑                                    │
       └──────── partners feel ownership ───┘
```

| Mechanism | Effect |
|-----------|--------|
| Open adapters | Low friction for integrators; network effects |
| Proprietary spine | Moat; hosted service cannot be trivially replicated |
| Quality free adapters | Lock-in through value, not legal threats |
| Private beta partners | Reference customers before public launch |
| Revenue share option | Aligns partner incentives with SaaS growth |

This is the Redis / MongoDB / Elastic / Confluent playbook. It works because **the engine is hard; the integrations are communal**.

---

## Roadmap

### Now (private beta)

- [x] Immutable spine with contract verification (`docs/DESIGN.md` hash)
- [x] Open adapter framework + Replay / Proxmox examples
- [x] Product site on Cloudflare Pages
- [x] Dual licensing (LICENSE + LICENSE-ADAPTERS)
- [ ] Private `saas/` collaborator repo under NDA
- [ ] 3–5 infrastructure teams in adapter partner program

### Next — SaaS MVP

- Hosted reconciliation (scheduled observe → plan → alert)
- Artifact storage and drift diff UI
- Approval workflow before apply
- Proxmox + Replay on hosted tier; AWS/Hetzner on Pro+

### Later — Enterprise

- Compliance reporting (SOC2-ready audit exports)
- Multi-tenant MSP console
- DFIR case workspace with gated apply
- Marketplace for partner adapters

---

## What We Will Not Do

Aligned with [DESIGN.md](DESIGN.md) — these are product decisions, not roadmap items:

- Open-source the spine "to be nice"
- Remove refusal semantics for convenience
- Allow adapter code to weaken safety policies
- Compete with partners on their niche adapters

---

## Join

| Role | Path |
|------|------|
| **Build an adapter** | [INTEGRATIONS.md](INTEGRATIONS.md) → [CONTRIBUTING.md](../CONTRIBUTING.md) |
| **Private beta / NDA** | [PRIVATE_COLLABORATION.md](PRIVATE_COLLABORATION.md) |
| **Buy SaaS** | [licensing@dedalo101.com](mailto:licensing@dedalo101.com) |

---

## Principles

1. **Refusal is a feature** — partial truth is not actionable truth
2. **Adapters own the edges** — spine owns the guarantees
3. **Replay ≡ live** — if it works in CI, it works in prod
4. **Artifacts over logs** — every decision is structured JSON
5. **Partners before pixels** — reference customers beat marketing pages