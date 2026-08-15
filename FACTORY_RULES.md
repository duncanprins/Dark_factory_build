# FACTORY_RULES.md — dark_factory

> Process rules that exist **because nobody is watching a given run in real time.**
> Scope/mission questions live in MISSION.md. PRP.md is the source of truth for both.

## Two factories, different rules

- **Coding factory** — autonomous within these rules. May implement, open PRs, and
  self-validate, bounded by the caps below.
- **Governance factory** — human-in-the-loop is mandatory (MISSION.md). No autonomous
  merge or publication of governance output, regardless of how confident the run is.

## Forbidden actions

A run that does any of the following is invalid, regardless of whether it "passes":

- **Editing tests to make them pass**, instead of fixing the code under test.
- **Adding dependencies** that aren't required by the task at hand.
- **Exceeding the issue's stated scope** — implement what was asked, not what seems
  adjacent-useful.
- **Editing the files that define the rules a run is judged by** (workflow YAMLs, this
  file, MISSION.md, PRP.md) as part of an ordinary implementation run. This is the same
  principle as forbidding an exam-taker from editing the answer key.

## Governance-output rules (§13 of PRP)

Governance output specifically must never:
- state something with more confidence than its source basis supports
- present one option as "the truth" instead of a compared set
- conceal risks
- leave assumptions unstated
- create false certainty

## Caps

- **Fix attempts**: max 2 fix attempts per PR. A third failure escalates rather than retries.
- **PR size**: max 500 changed lines. Larger changes must be split into multiple issues/PRs.
- **Triage batch**: max 10 issues processed per triage run.

## Escalation triggers

A run escalates — stops and actively notifies a human, instead of failing silently — when:

- the **fix-attempt cap is reached** (2 failed fix attempts on the same PR)
- a **factory-guard rejection** fires on a protected path (Fase 4b)
- the **stop-switch** is engaged (Fase 4b)

Weak source basis in a governance run does **not** trigger a separate escalation — the
mandatory review-gate already surfaces it to a human on every governance run.

**Notification channels** (decided 2026-08-15, wiring is a Fase 4b implementation task —
not yet built):
- **Gotify**, existing instance at `192.168.70.40:8081`, dedicated app **"Dark-factory"**.
  App-token created and verified 2026-08-15 (test push received). Token itself is **not**
  stored in this repo — lives as a secret/env var on the Archon server, set up in Fase 4b.
- **Telegram**, via Archon's existing built-in Telegram integration — needs verification
  that a workflow node can *send* a message through it (today's known usage is inbound
  triggers), not a new bot/token.

Both channels get the same message: which trigger fired, the issue/PR reference, and a
link. No channel is authoritative over the other — either is sufficient to reach the human.

## Rejection bias

When in doubt whether to accept or reject a run/issue/PR: **reject.** A wrongful rejection
costs less than a wrongful acceptance — a human can requeue a rejected issue; an
autonomously accepted bad result has already done its damage.

## Decision rules under doubt (PRP §16)

1. Archon instability → stop and fix Archon first, before continuing any other work.
2. Speed vs. explainability → choose explainability.
3. Autonomy vs. control → choose control.
4. Large vs. small workflow → choose small.
5. Weak source basis (governance) → state uncertainty explicitly, never bluff.
