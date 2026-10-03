---
name: start
description: Start or resume a change using the minimal AI-native SDLC: intent, spec, plan, then implementation and verification.
argument-hint: "[describe a change or give a change id]"
disable-model-invocation: true
---

# Intent → Spec → Plan → Code

The user's request is: $ARGUMENTS

Work in the current repository. Read its existing instructions first. Store lifecycle artifacts in `changes/<short-slug>/`.

## Find the stage

If the user describes new work, create a short slug and start with `intent.md`.

If the user gives no description, inspect `changes/*/`:
- resume the only unfinished change;
- if several are unfinished, ask which one;
- if none exist, ask what they want to change.

An artifact with `Status: draft` is waiting for review. An artifact with `Status: approved` is accepted workflow state. Never mark an artifact approved without explicit human approval.

## 1. Intent

Read `${CLAUDE_PLUGIN_ROOT}/templates/intent.md`.

Discuss only what is needed to make the problem clear, then write a concise `intent.md`. Prefer a useful draft over a long interview.

Stop and ask the human to approve or change the intent.

When explicitly approved:
1. change its status to `approved`;
2. commit only that artifact with a clear message;
3. continue immediately to the spec.

## 2. Spec

Read the approved intent and inspect the relevant codebase. Read `${CLAUDE_PLUGIN_ROOT}/templates/spec.md`.

Write the smallest spec that makes the required behavior and important design decisions unambiguous. Flag unresolved concerns instead of inventing answers.

Stop and ask the human to approve or change the spec.

When explicitly approved, mark it approved, commit only that artifact, and continue to the plan.

## 3. Plan

Read the approved intent and spec. Read `${CLAUDE_PLUGIN_ROOT}/templates/plan.md`.

Write a concrete implementation plan naming the important files or components, order of work, risks, and proof.

Stop and ask the human to approve or change the plan.

When explicitly approved, mark it approved, commit only that artifact, then implement.

## 4. Implement and verify

Implement the approved plan using the repository's existing conventions and tools.

Run the relevant existing tests, build, lint, or other checks. Review the final diff against `intent.md`, `spec.md`, and `plan.md`; fix mismatches before reporting done.

If implementation reveals a decision that materially changes the approved plan or spec, update that artifact, return it to `Status: draft`, and get approval again before continuing.

Do not invent approvals, weaken checks, or bypass the repository's existing PR, merge, security, or release controls.

At each pause, keep the message short: show what changed, link the artifact, and state the one decision needed next. Keep small changes small; delete empty template sections rather than filling them with ceremony.
