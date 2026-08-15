# MISSION.md — dark_factory

> Compact, machine-readable summary for workflow-node prompts (triage, validate).
> PRP.md remains the source of truth. On conflict, PRP.md wins — flag it, don't resolve it here.

## Mission

Build a reusable AI factory on the Archon workflow engine, specialized into two lanes:

1. **Coding factory** — issue-driven implementation and validation. Runs autonomously
   within FACTORY_RULES.md.
2. **Governance research factory** — researches, compares, and prepares governance
   decisions. Never decides autonomously. Human-in-the-loop is mandatory (see below).

## Two factories, different autonomy

| | Coding factory | Governance factory |
|---|---|---|
| Autonomy | Autonomous within the rules | Human-in-the-loop mandatory |
| May decide | Implementation details | Nothing final — advice only |
| May publish/merge | Within PR-caps (FACTORY_RULES.md) | Never autonomously |

## In scope

- Issue-driven workflow execution: triage → implement → validate → review, on Archon.
- Governance research: investigate a question, compare options, prepare a decision with
  explicit sourcing. Output is always advice, never a final decision.
- Validation against clear, checkable acceptance criteria per run.

## Out of scope — forever

These are not "not yet" — they are permanently rejected. Concrete enough to close a test
issue that proposes one of these:

- **A public open issue factory for third parties.** This factory serves this project only.
- **Automatic governance decisions without human review.** Any workflow output that skips
  the review-gate and treats a governance conclusion as final is rejected.
- **Auto-merge or auto-deploy for governance workflows.** Governance output always ends in
  `pending` review status, never auto-applied.
- **A copy of Cole Medin's RAG-chat application** (`dark-factory-experiment`). This project
  uses the same Archon engine, not his application layer.
- **Broad enterprise integrations** beyond what a reliable first version needs.
- **Full production hardening for multi-user use.** This factory has one operator.

## Governance rules (when in the governance lane)

**Human-in-the-loop is mandatory.** AI may research, summarize, compare, and advise. AI may
**never** independently make final policy, compliance, or implementation decisions.

**Source priority**, in order:
1. Official vendor documentation
2. Official standards, law, or regulatory sources
3. Reliable technical documentation
4. Only after the above: blogs, community sources

**Every governance run must record**: the input question, search queries used, sources
consulted, comparison of options, explicit assumptions, open risks, the preferred proposal,
and review status (`pending` / `approved` / `rejected`).

## Reference

Full rationale, phase history, and detailed criteria: `PRP.md`. Process rules (what's
forbidden, caps, escalation): `FACTORY_RULES.md`.
