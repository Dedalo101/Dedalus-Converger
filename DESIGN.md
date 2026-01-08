Domain-agnostic reconciliation with explicit refusal semantics.

Dedalus Converger is a reconciliation engine that encodes restraint. It converges declared intent against observed reality — and refuses to act when truth is incomplete.

Observe → Plan → Enforce → Apply
If truth is partial, the system does nothing.

What This Is
Dedalus Converger is not a Proxmox tool.

It is a reconciliation primitive built around a tight contract:

Observation is read-only and honest
Planning is deterministic and pure
Safety is enforced through explicit invariants
Application is the only mutating phase
Any system that can emit the EntityState contract can use the same spine:

hypervisors
cloud APIs
incident replays
DFIR reconstructions
synthetic test fixtures
Live data and replayed data are equivalent.

Core Guarantees (Locked)
Dedalus Converger encodes refusal as a first-class behavior.

The system will never:

Act on incomplete or partial truth
Treat “missing” as “stopped”
Retry or heal failed observations
Discover or expand scope implicitly
Mutate state during audit or plan modes
Bypass safety policies via replay
Reinterpret history or time-travel outcomes
Stop production workloads by default
If a decision cannot be made safely, the system refuses to act.

These guarantees are enforced in code and documented in DESIGN.md.

The Spine (Immutable)
