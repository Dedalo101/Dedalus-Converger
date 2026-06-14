# Design Partner Outreach Email

One-page templates for private beta recruitment.  
**Goal:** 3–5 teams with real workloads — not demos, not tire-kickers.

---

## Before you send

- [ ] Personalize the **first line** (reference their blog, GitHub repo, conference talk, or stack)
- [ ] Pick the **right variant** (Proxmox / DFIR / Cloud)
- [ ] Keep body under ~200 words — founders delete novels
- [ ] One ask: **15-minute call** or **async reply** with four fields (below)
- [ ] Log in [partner-tracker.csv](partner-tracker.csv)

**Subject line options** (A/B test):

- `Proxmox reconciliation — private beta (adapter partners)`
- `DFIR + honest reconciliation — looking for 3 design partners`
- `Build the adapter, we host the engine — early access`
- `Reconciliation that refuses partial truth — beta invite`

---

## Variant A — Proxmox MSP / homelab-pro

**Best for:** MSPs, hosting providers, homelab operators running 20+ VMs on Proxmox.

```
Subject: Proxmox reconciliation — private beta (adapter partners)

Hi [Name],

I saw [personalize: your post on X / your Proxmox setup / your MSP work with Y] —
looks like you're living the "desired state vs what's actually running" problem
on Proxmox.

I'm building Dedalus Converger: reconciliation that refuses to act when
observation is incomplete. No guessing. No treating "missing" as "stopped."
Replay ≡ live for audit and plan.

We're opening a private beta for 3–5 infrastructure teams:

  • Open adapter framework (Apache 2.0) — you can ship a Proxmox integration
  • We host the engine (SaaS) — scheduling, drift alerts, artifact history
  • Featured placement + optional revenue share for partner adapters
  • Locked beta pricing for 12 months after GA

Not looking for feedback on slides — looking for a team with real VMs and
a willingness to run audit/plan against production (apply is gated, dry-run first).

Worth a 15-minute call next week? Or reply with:

  Team / stack:
  Adapter you'd maintain:
  Rough VM count or environment:
  SaaS interest (yes/no):

Product overview: https://dedalus-converger.pages.dev

— Dedalo
Dedalo101 | licensing@dedalo101.com
```

---

## Variant B — DFIR consultancy

**Best for:** Firms using Velociraptor, KAPE, or custom artifact pipelines.

```
Subject: DFIR + honest reconciliation — looking for 3 design partners

Hi [Name],

[Personalize: your Velociraptor deployment / KAPE workflow / DFIR case study on X.]

Dedalus Converger is infrastructure reconciliation with refusal semantics:
if truth is partial, the system does nothing. That maps cleanly to DFIR —
audit and plan from artifacts without risky auto-apply.

We're recruiting 3 DFIR-oriented design partners for private beta:

  • Import presets for Velociraptor / KAPE (open adapter layer)
  • Cases default to audit/plan; apply requires explicit unlock
  • Hosted case workspace + artifact history on SaaS tier
  • Early access under NDA; optional revenue share for featured integrations

Ideal partner: a consultancy with repeat engagements where you reconcile
"what should be running" against collected host state — and you care about
chain-of-custody more than flashy automation.

15 minutes to see if there's a fit?

  Firm / tooling:
  Typical case size:
  Apply in cases (yes/no/gated):
  Interest in hosted DFIR tier:

https://dedalus-converger.pages.dev

— Dedalo
Dedalo101 | licensing@dedalo101.com
```

---

## Variant C — AWS / cloud infra team

**Best for:** Teams managing EC2/Hetzner fleets with drift pain.

```
Subject: Cloud drift detection — private beta (3 slots)

Hi [Name],

[Personalize: your infra post / your AWS automation repo / your Hetzner setup.]

Most drift tools guess when the API returns partial data. Dedalus Converger
doesn't — unknown observation means empty plan, full stop.

Open adapters at the edge, proprietary reconciliation spine, hosted service
for scheduling and alerts. We're looking for 3 cloud teams for private beta
before public SaaS launch.

You get:
  • Early hosted reconciliation (Pro-tier features during beta)
  • Input on AWS/Hetzner adapter roadmap
  • First-customer pricing locked 12 months post-GA

You bring:
  • A real fleet (EC2, Hetzner, or both)
  • Willingness to run plan/audit weekly for ~8 weeks
  • Honest feedback async (no standing meetings required)

Quick call, or reply with stack + fleet size + biggest drift pain?

https://dedalus-converger.pages.dev

— Dedalo
Dedalo101 | licensing@dedalo101.com
```

---

## Variant D — LinkedIn DM (short)

**Best for:** Warm-ish connections; keep under 300 characters for first message.

```
Hi [Name] — saw your work on [X]. Building reconciliation that refuses
partial truth (Proxmox/cloud/DFIR). Recruiting 3 design partners for
private beta: build adapters (open), we host the engine. Real workloads,
not demos. Worth a quick chat? dedalus-converger.pages.dev
```

Follow-up DM if they engage:

```
Happy to send a one-pager. Main ask: audit/plan on your stack for ~8 weeks,
NDA for early SaaS access. Featured adapter credit + beta pricing if it's
a fit. licensing@dedalo101.com works too.
```

---

## Follow-up (5–7 days, no reply)

```
Subject: Re: [original subject]

Hi [Name] — bumping this once. Still have [2/3] beta slots for
[Proxmox / DFIR / cloud] teams.

If timing's wrong, no worries — a one-line "not now" helps me close the loop.

— Dedalo
```

---

## Reply handling — copy-paste ack

When they reply positively:

```
Great — thanks for the detail.

Next steps:
1. I'll send the mutual NDA (2-page, standard carve-outs for open adapter code)
2. 30-min kickoff to confirm VMState mapping + test fixtures
3. GitHub access to the private collaborator repo after NDA

Does [day/time] or [day/time] work for kickoff? Timezone: [yours].

— Dedalo
```

Point them to [PRIVATE_COLLABORATION.md](../PRIVATE_COLLABORATION.md) after NDA.

---

## What not to say

- Don't claim SOC2 / ISO yet unless you have them
- Don't promise revenue share % in cold email (say "optional, negotiated")
- Don't open-source the spine in email — say "open adapters, hosted engine"
- Don't ask for free consulting disguised as "feedback"