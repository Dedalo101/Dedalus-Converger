# Private Collaboration — Adapter Partners & SaaS Beta

This guide is for infrastructure teams joining the **private beta** or **adapter partner program**.

The public story: build adapters (open), we host the engine (SaaS).  
The private story: early access, roadmap input, and optional revenue share.

---

## Who This Is For

- Infrastructure teams running Proxmox, AWS, Hetzner, K8s, or bespoke hypervisors
- DFIR firms with Velociraptor / KAPE / custom artifact pipelines
- MSPs evaluating white-label reconciliation
- Vendors who want a featured integration before public launch

**Target for current beta:** 3–5 teams with real workloads, not tire-kickers.

---

## What Partners Get

| Benefit | Details |
|---------|---------|
| **Early SaaS access** | Private `saas/` repository and staging environment |
| **Roadmap input** | Direct channel to engineering; shape hosted features |
| **Featured adapters** | Credit on product site and `docs/INTEGRATIONS.md` |
| **Revenue share** | Optional % on SaaS signups attributed to your adapter (negotiated) |
| **First-customer pricing** | Locked beta rates for 12 months after GA |

---

## What We Need From You

1. **A real adapter use case** — not a hypothetical integration
2. **NDA execution** — protects Core Engine and SaaS roadmap (see below)
3. **Feedback cadence** — biweekly during beta (async is fine)
4. **Honest observation** — adapters must not weaken refusal semantics
5. **Optional case study** — after successful pilot (anonymized if required)

---

## Onboarding Flow

```
Interest email → NDA sent → NDA signed → saas/ repo access → kickoff call → ship adapter
```

### Step 1 — Express interest

Email [licensing@dedalo101.com](mailto:licensing@dedalo101.com):

```
Subject: Dedalus Converger — Adapter Partner / Private Beta

Team:
Stack (Proxmox / AWS / etc.):
Adapter you want to build or maintain:
SaaS interest (yes/no):
Revenue share interest (yes/no):
Timeline:
```

### Step 2 — NDA

We send a mutual NDA covering:

- Core Engine source and SaaS architecture (confidential)
- Your adapter plans and infrastructure details (confidential)
- Public adapter code remains Apache 2.0 when published
- Term: 2 years; standard carve-outs for open components

Template outline: [docs/templates/NDA-ADAPTER-PARTNER.md](templates/NDA-ADAPTER-PARTNER.md)

### Step 3 — Repository access

After NDA execution:

- GitHub collaborator invite to `Dedalo101/dedalus-converger-saas` (private)
- Staging SaaS credentials (when available)
- Slack / email support channel

### Step 4 — Kickoff

30-minute call:

- Confirm adapter scope and VMState mapping
- Agree test fixtures (replay JSON, no live infra in CI)
- Set beta milestone date

### Step 5 — Ship

- Adapter merges via partner review (not public spine PRs)
- Featured on site when stable + tested
- SaaS tier recommendation based on your use case

---

## NDA vs Open License — How They Coexist

| Material | Visibility | License |
|----------|------------|---------|
| Adapter framework docs | Public | Apache 2.0 |
| Your observation adapter (when published) | Public | Apache 2.0 (yours + Dedalo101) |
| Core spine source | Private repo / licensed | Commercial proprietary |
| SaaS control plane | Private `saas/` repo | Commercial proprietary |
| Roadmap and pricing pre-GA | NDA-covered | Confidential |

Publishing an adapter does **not** grant rights to the Core Engine or permission to operate a competing hosted reconciliation service.

---

## Revenue Share (Optional)

For partners whose adapters drive measurable SaaS pipeline:

- **Attribution:** UTM / referral code / sales tagging
- **Share:** negotiated % of first-year ARR (typical range 10–20%)
- **Duration:** 12 months from customer close
- **Eligibility:** adapter listed as Featured; maintained for GA + 6 months

Details in commercial agreement, not the NDA.

---

## Beta Expectations

| Phase | Duration | Goal |
|-------|----------|------|
| **Alpha** | Weeks 1–4 | Adapter + replay tests passing |
| **Beta** | Weeks 5–12 | Live observe/plan on partner infra |
| **Pilot** | Weeks 13+ | Hosted SaaS for one workload |
| **GA** | TBD | Public SaaS; partner becomes reference customer |

Breaking changes possible during beta. We version artifacts (`plan.json`, etc.) and notify partners before spine contract changes.

---

## Outreach Targets

We are actively looking for:

1. **Proxmox-heavy homelab / MSP** — validate Proxmox adapter + hosted scheduler
2. **AWS EC2 shop** — enterprise adapter + drift alerts
3. **DFIR consultancy** — Velociraptor/KAPE preset + gated apply
4. **Hetzner / EU cloud team** — EU data residency narrative
5. **Incident replay team** — replay ≡ live proof for post-mortems

Know a team? Intro to [licensing@dedalo101.com](mailto:licensing@dedalo101.com).

---

## FAQ

**Is the main repo public?**  
No. `Dedalo101/Dedalus-Converger` is private. Open-licensed components can be published separately later.

**Can we fork the spine?**  
No. LICENSE prohibits it. Build adapters; buy or beta-test SaaS for the engine.

**Do we have to publish our adapter?**  
No. You may keep it private under NDA. Apache 2.0 applies when we jointly publish to the open ecosystem.

**What if we only want SaaS, not building?**  
Skip to [licensing@dedalo101.com](mailto:licensing@dedalo101.com) for commercial tiers — no NDA required for standard purchase.

---

## Contact

**Partnership & NDA:** [licensing@dedalo101.com](mailto:licensing@dedalo101.com)  
**Product site:** [dedalus-converger.pages.dev](https://dedalus-converger.pages.dev)