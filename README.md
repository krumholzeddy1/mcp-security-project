# MCP Tool-Poisoning Detection — Project Code

This is the working code behind the dissertation proposal *"Detecting
Tool-Poisoning Attacks in Model Context Protocol (MCP) Agentic Systems
Using Machine-Learning-Based Anomaly Detection."*

## What's here (mapped to the WBS from Task 1.3)

| Folder | WBS item | Status |
|---|---|---|
| `server/` | 2.1 MCP client/server harness | Working — real MCP server + tool catalog |
| `client/` | 2.1 (manual sanity check) | Working — round-trips a real tool call |
| `corpus/` | 2.2/2.3 Attack corpus generation | Working — generates labelled benign/poisoned/rug-pull sessions |
| `baseline/` | 2.4 Baseline schema-validator | Working — registration-time-only keyword check |
| `detection/` | 3.1–3.3 Anomaly-detection model | Working — GradientBoostingClassifier on metadata features |
| `evaluation/` | 4.1 Evaluation vs. baseline | Working — precision/recall/F1, split by attack class |
| `tests/` | — | Smoke tests confirming the rug-pull blind spot is real, not a bug |

## Quickstart

```bash
python3 -m venv venv && source venv/bin/activate   # or your preferred env manager
pip install -r requirements.txt

python -m corpus.generate_corpus       # writes data/corpus.csv
python -m baseline.schema_validator    # writes data/baseline_results.csv
python -m detection.train_model        # writes data/detector_model.joblib
python -m evaluation.evaluate          # writes data/evaluation_summary.csv

python -m tests.test_pipeline          # smoke tests

# optional: watch a real MCP round-trip happen
python -m client.testbed_client
```

## What the first run already shows

On the current synthetic corpus (200 sessions per class):

| Method | Precision | Recall | F1 |
|---|---|---|---|
| Baseline schema validator | 1.00 | 0.51 | 0.67 |
| ML anomaly detector | 1.00 | 1.00 | 1.00 |

Broken down by attack class, the baseline gets **0% recall on rug-pull
attacks** — it structurally cannot see a description that changes after
registration, which is exactly the gap the proposal argues for.

**Honest caveat before you write this in the dissertation:** 100% recall
for the ML model is a sign the synthetic corpus is currently too clean —
poisoned/rug-pull descriptions always contain an obvious keyword, so the
model has an easy time. Before this becomes a real evaluation result,
week 4–5 work should add noisier, more ambiguous synthetic cases (e.g.
benign tools that legitimately use words like "system" or "config", and
attack variants that don't rely on an obvious keyword) so the comparison
is actually informative rather than trivially separable. Treat the numbers
above as "the pipeline runs end-to-end and the expected pattern shows up,"
not as a result to cite yet.

## Moving this into Claude Code for the rest of the term

This was built in a temporary sandbox that won't persist. To keep working
on it week over week:

1. Download this whole folder and `git init` it locally (or push to a
   private GitHub repo).
2. Install Claude Code (`curl -fsSL https://claude.ai/install.sh | bash` on
   macOS/Linux — see https://code.claude.com/docs/en/setup for Windows).
3. Open the repo folder and run `claude` — it can now read, run, and edit
   this code with full persistence across sessions, since it's just files
   on your machine plus git history.
4. Commit after each work session so weeks 4–13 of the plan build on a
   real history you (and your supervisor, if asked) can review.

## Known limitations to state in the dissertation

- The corpus is entirely synthetic; MCP reference-implementation behaviour
  is assumed to be representative of production behaviour (stated as an
  assumption in Task 1.2).
- The "attack surface" simulated here is metadata/description patterns,
  not a live prompt-injection attack against a running LLM — consistent
  with the research question, but worth being explicit about in the
  methodology section so it doesn't read as an overclaim.
- Current corpus separability is too clean (see caveat above) — treat as
  a scaffold to make more realistic during weeks 4–5, not a finished
  dataset.
