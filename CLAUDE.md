# Starter repository instructions
This repository packages an AI SDLC workflow, templates and four Claude Code project skills.
Read README.md and .sdlc/workflow.md. Canonical templates live in .sdlc/templates.
Use Python 3.10+; no third-party dependencies are needed for package scripts.
Validation: python3 scripts/validate.py
Tests: python3 -m unittest discover -s tests -v
Keep skills and templates consistent; test the installer when changing package layout.
Do not claim that structural validation enforces human approval or semantic correctness.
Do not silently change example documents from illustrative draft to approved.
For workflow changes, run the relevant manual evaluations in evals/README.md.
