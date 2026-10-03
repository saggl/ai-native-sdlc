# Playbook coverage and automation boundary

The playbook explicitly supports adopting modular plays and starting with manually
invoked transitions. This plugin implements a reusable guided path through all six stages.
It does not install the organization's engineering systems or their access policies.

| Playbook stage / capability | Included in 0.2 | Project-specific next step |
| --- | --- | --- |
| Plan | Guided intent capture, issue/source links, committed artifact, human decision | Connect existing intake system if useful |
| Design | Repository-aware spec, policy references, stable ACs, flagged concerns | Add authoritative domain/company skills |
| Build | Approved plan, project context, bounded implementation and feedback loop | Supply real build/test tooling and target access |
| Test | Criterion-to-evidence reports, failed/unrun checks, stale-result detection | Product test suite; continuous model/skill eval runner |
| Review and deploy | Fresh reviewer, diff-versus-artifact review, PR/check/fix instructions, release evidence | Configure host/CI tools, protected gates and release credentials |
| Maintain | Observed-outcome report, triage, lessons and linked next intent | Monitoring integration, deterministic detection and event-triggered runner |
| Reusable distribution | Native Claude Code plugin, one entry command, managed version updates | Approved team marketplace/version rollout |
| Approval enforcement | Evidence references and content-change detection only | Authenticated external decision source, branch rules and protected environments |

## What is executable

The standard-library Python helper creates project/change files, binds recorded decisions
to committed content, derives the next stage, and detects changed artifacts/code/reports.
It never calls a model, executes a configured product command or contacts a remote system.
Claude follows the skills to do the engineering work using its available tools.

## What needs a runtime pilot

Package and lifecycle tests validate deterministic behavior. Fresh-agent walkthroughs
probe instruction quality. Claude Code installation, permission prompts, real project
commands and connector-based delivery need a pilot in the intended environment. They
must not be reported as validated merely because Python tests passed.
