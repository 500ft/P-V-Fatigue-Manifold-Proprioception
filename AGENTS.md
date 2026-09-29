# Agent instructions

## Scope discipline — owner rule, 2026-09-29

This repository exists to be finished. A PR must do at least one of these:
add a measurement or an executed run, change a result, close an item on the
critical path below, or record an owner decision. If it does none, don't open it.

- **No plan-only PRs.** A plan belongs in the PR that implements it, or in a
  `.txt` handoff outside the repo. Never open a PR that supersedes another plan
  PR; edit the open one.
- **One home per number.** A consequential number lives in one canonical file
  (a results JSON or the parameter register). Other documents link to it and
  don't restate it. If a correction would need edits in more than one document,
  replace the copies with links first.
- **No hardening before first use.** Don't add or extend intake, manifest,
  contract or provenance checkers for data that doesn't exist yet. Build a
  checker in the same PR as the first real data it checks. A fix to a fix
  (`-b`, `-c`) is the signal to stop.
- **No cross-repo template passes.** Don't apply a change here because it was
  applied to a sibling repository (literature reviews, presentation passes,
  audits, traceability indexes) unless this repo's critical path needs it.
- **When blocked on the owner, say so in one line and stop.** Don't fill the wait
  with documents.
- Dependency updates arrive as Dependabot's grouped monthly PRs; don't hand-edit
  pins to chase them.

**Critical path (2026-09-29):** Author review of the v1.4 manuscript candidate (owner) -> separately versioned rendered PDF -> deposit. The simulation work is complete; new studies are off-path.
