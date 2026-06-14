# Partner Directory — Where to Find Design Partners

Target: **3–5 teams** across Proxmox, DFIR, and cloud.  
Use with [design-partner-email.md](design-partner-email.md) and log sends in [partner-tracker.csv](partner-tracker.csv).

---

## Priority segments

| Priority | Segment | Why | Email variant | Quota |
|----------|---------|-----|---------------|-------|
| **P1** | Proxmox MSP / hosting | Core adapter exists; acute drift pain | A | 2 partners |
| **P1** | DFIR consultancy | High ARPU; gated apply story resonates | B | 1–2 partners |
| **P2** | AWS / Hetzner infra team | Enterprise adapter validation | C | 1 partner |
| **P3** | Homelab-pro / creator | Fast feedback; lower revenue | A (shorter) | 0–1 (optional) |
| **P3** | Incident replay / SRE | Replay ≡ live proof | C | 1 (stretch) |

---

## Channels — where to hunt

### Proxmox MSP & homelab-pro

| Channel | URL / location | How to use |
|---------|----------------|------------|
| Proxmox Support Forum | https://forum.proxmox.com | Search "automation", "terraform", "ansible", "drift". Reply helpfully, then DM active posters. |
| r/Proxmox | https://reddit.com/r/Proxmox | Weekly help threads — find people managing 10+ nodes. |
| r/homelab | https://reddit.com/r/homelab | Proxmox tag; look for multi-VM setups, not single Plex boxes. |
| Proxmox VE Facebook group | Facebook | MSP operators in EU especially. |
| LowEndTalk | https://lowendtalk.com | Hosting providers discussing automation at scale. |
| Hetzner + Proxmox community | Hetzner Community, Discord | Common stack; good for EU partners. |
| YouTube / blogs | Search `proxmox ansible`, `proxmox terraform` | Creators with comment sections full of operators. |

**Signals someone is a fit:** mentions desired state, Ansible playbooks, VM sprawl, "afraid to reboot", multi-node Proxmox.

### DFIR consultancy

| Channel | URL / location | How to use |
|---------|----------------|------------|
| Velociraptor Google Group | https://groups.google.com/g/velociraptor-discuss | Practitioners discussing artifact collection. |
| Velociraptor GitHub discussions | https://github.com/Velocidex/velociraptor | Active DFIR engineers. |
| r/cybersecurity, r/digitalforensics | Reddit | Firms posting case workflows. |
| SANS DFIR community | SANS forums / alumni networks | Consultancies with budget. |
| KAPE / Eric Zimmerman tooling community | Discord, Twitter/X | Host-state artifact people. |
| BSides / local DFIR meetups | Meetup.com, Eventbrite | Talk to presenters, not attendees. |
| FIRST.org members | https://www.first.org | Incident response teams at orgs (longer sales cycle). |

**Signals:** Velociraptor/KAPE in bio, "host visibility", case workspace tooling, chain-of-custody language.

### Cloud infra (AWS / Hetzner)

| Channel | URL / location | How to use |
|---------|----------------|------------|
| r/devops, r/aws, r/hetzner | Reddit | Drift / reconciliation pain threads. |
| Hacker News | https://news.ycombinator.com | Comment on infra posts; Who's Hiring threads. |
| Cloud-native meetups | Meetup, CNCF chapters | Platform engineers. |
| GitHub | Search `proxmoxer`, `hetzner cloud terraform` | Maintainers and heavy users of adjacent tools. |
| DevOps Discord servers | DevOps Chat, etc. | #infrastructure channels. |

**Signals:** Terraform state drift posts, "who owns prod changes", multi-account AWS.

### Warm paths (highest conversion)

| Path | Action |
|------|--------|
| Your existing network | List every person who runs Proxmox or does DFIR — email first |
| Edomite / music infra contacts | Cross-domain but may know homelab-pros |
| Dedalo101 site inbound | licensing@ replies get partner track, not generic sales |
| Conference CFP reviewers | Proxmox VE Summit, BSides — speakers are practitioners |

---

## Named prospects (filled)

**15 verified contacts** with emails, forms, and personalization hooks:

→ **[partner-prospects.md](partner-prospects.md)** — full profiles + ready-to-send drafts  
→ **[partner-tracker.csv](partner-tracker.csv)** — import to Excel/Sheets and log status

**P1 this week:** ClearPath MSP, partimus, DG-i, DynFi, credativ, InfoGuard, SEC Consult

**Still to hunt (add to tracker):** AWS EC2 platform team, Hetzner Cloud shop, post-incident SRE team — see channels above.

---

## Outreach tracker (markdown)

Duplicate in CSV for sorting/filtering.

| Company | Contact | Email | Segment | Channel | Date sent | Follow-up | Status | Notes |
|---------|---------|-------|---------|---------|-----------|-----------|--------|-------|
| | | | Proxmox MSP | | | | `lead` | |
| | | | Proxmox MSP | | | | `lead` | |
| | | | DFIR | | | | `lead` | |
| | | | DFIR | | | | `lead` | |
| | | | Cloud | | | | `lead` | |

**Status values:** `lead` → `sent` → `replied` → `call booked` → `NDA sent` → `NDA signed` → `beta active` → `passed` / `not now`

---

## Weekly cadence (suggested)

| Day | Action |
|-----|--------|
| Mon | Add 5 new names to tracker from one channel |
| Tue–Wed | Send 5 personalized emails |
| Thu | LinkedIn DMs to 3 warm connections |
| Fri | One follow-up batch; update tracker |

**Stop at 5 active beta partners** — quality over volume.

---

## Qualification checklist (before kickoff call)

Answer yes to at least **3 of 5**:

- [ ] Runs Proxmox, AWS, Hetzner, or DFIR artifacts in production (not toy lab only)
- [ ] Has felt drift / partial-truth pain in last 90 days
- [ ] Willing to run `converger audit` or `plan` weekly for 8 weeks
- [ ] Has someone technical who can read YAML and JSON artifacts
- [ ] Understands engine is proprietary; adapters are open

**Disqualify:** wants free MSP tooling forever, expects open-source spine, no real workloads.

---

## Links

- Email templates: [design-partner-email.md](design-partner-email.md)
- CSV tracker: [partner-tracker.csv](partner-tracker.csv)
- Partner onboarding: [PRIVATE_COLLABORATION.md](../PRIVATE_COLLABORATION.md)
- Product: https://dedalus-converger.pages.dev