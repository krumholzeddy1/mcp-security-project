# Appendices

---

## Appendix A: Source Code

The complete source code for this project is available at:

> <https://github.com/krumholzeddy1/mcp-security-project>

The dissertation results reported in Chapter 4 were produced at commit `83fad16`. All pipeline outputs (`data/corpus.csv`, `data/evaluation_summary.csv`, `data/model_test_results.csv`, `data/baseline_results.csv`) are committed alongside the source code and are byte-for-byte reproducible by running the pipeline commands in order with the pinned environment described in Appendix B.

The six source modules that constitute the implemented system are listed below with their roles:

| File | Role |
| --- | --- |
| `server/tool_definitions.py` | Shared `ToolSpec` dataclass and `TOOL_CATALOG` — the five benign tools and their associated poison fragments |
| `server/testbed_server.py` | FastMCP server exposing the tool catalogue over stdio for demonstration and supervisor inspection |
| `client/testbed_client.py` | Async MCP client for manual round-trip demonstration against the testbed server |
| `corpus/generate_corpus.py` | Synthetic corpus generator producing `data/corpus.csv` (balanced) and `data/corpus_skewed.csv` (90/5/5) |
| `baseline/schema_validator.py` | Registration-time keyword-based baseline validator |
| `detection/train_model.py` | Trains Logistic Regression, Random Forest, and Gradient Boosting classifiers on the balanced corpus |
| `evaluation/evaluate.py` | Compares all four methods on the balanced and skewed corpora and writes `data/evaluation_summary.csv` |
| `tests/test_pipeline.py` | Six smoke tests validating corpus generation invariants and the baseline's structural blind spot |

---

## Appendix B: Reproducibility and Environment

### B.1 Environment

All experiments were conducted on macOS 25.5.0 (Darwin) using Python 3.13.5. The complete set of pinned dependencies is stored in `requirements.txt` in the repository root. To reproduce the environment:

```bash
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
pip install -r requirements.txt
```

The key package versions are:

| Package | Version | Role |
| --- | --- | --- |
| `scikit-learn` | 1.9.0 | ML classifiers and evaluation metrics |
| `pandas` | 3.0.5 | Data loading and manipulation |
| `numpy` | 2.5.1 | Numerical computation |
| `scipy` | 1.18.0 | Statistical utilities |
| `joblib` | 1.5.3 | Model serialisation |
| `mcp` | 1.28.1 | MCP reference implementation (FastMCP) |

### B.2 Pipeline Execution

The pipeline stages must be run in sequence from the repository root with the virtual environment active:

```bash
python -m corpus.generate_corpus       # → data/corpus.csv, data/corpus_skewed.csv
python -m baseline.schema_validator    # → data/baseline_results.csv
python -m detection.train_model        # → data/detector_model_*.joblib, data/model_test_results.csv
python -m evaluation.evaluate          # → data/evaluation_summary.csv
```

Each stage reads from the outputs of the prior stage; running them out of order will fail with a missing-file error.

### B.3 Random Seed

All stochastic operations use `random.seed(42)` (corpus generation) and `random_state=42` (scikit-learn train/test split and all three ML classifiers). Running the pipeline with any other seed will produce different class assignments and different evaluation numbers.

---

## Appendix C: Pipeline Console Output

The following is the verbatim console output produced by running `python -m evaluation.evaluate` against the committed pipeline artefacts (commit `83fad16`, Python 3.13.5, scikit-learn 1.9.0). This output corroborates the results tables in Chapter 4.

```
======================================================================
PRIMARY RESULTS — Balanced corpus (200 per class, 70/30 split)
======================================================================

Headline metric: per-class recall (attack-class recall is the
operationally critical measure — a missed attack costs more than
a false alarm, per the research question framing).

                   method  precision  recall    f1  recall_poisoned  recall_rugpull
baseline_schema_validator      0.909   0.333 0.488            0.755           0.000
      logistic_regression      0.862   0.883 0.872            0.887           0.881
            random_forest      0.950   0.942 0.946            1.000           0.896
        gradient_boosting      0.957   0.933 0.945            1.000           0.881

Baseline blind spot — rug-pull recall by construction:
  baseline schema validator: rug-pull recall = 0.000
  (Registration-time keyword check sees only reg_suspicious_keyword_hits;
   rug-pull attacks start clean, so this is structurally zero.)

Confusion matrices (binary: benign=0, attack=1):
  baseline_schema_validator: TP=40 FP=4 FN=80 TN=56
  logistic_regression: TP=106 FP=17 FN=14 TN=43
  random_forest: TP=113 FP=6 FN=7 TN=54
  gradient_boosting: TP=112 FP=5 FN=8 TN=55

Saved summary to data/evaluation_summary.csv

======================================================================
ROBUSTNESS CHECK — Skewed corpus (90% benign / 5% poisoned / 5% rug-pull)
======================================================================
Model trained on balanced corpus, applied directly to skewed distribution.

  baseline_schema_validator
    precision=0.429  recall=0.4  f1=0.414  recall_poisoned=0.8  recall_rugpull=0.0
    False-alarm rate: 32 false positives out of 540 benign sessions (5.9% of benign flagged)

  gradient_boosting (balanced-trained)
    precision=0.682  recall=0.967  f1=0.8  recall_poisoned=1.0  recall_rugpull=0.933
    False-alarm rate: 27 false positives out of 540 benign sessions (5.0% of benign flagged)

Operational interpretation: any precision drop under class imbalance
translates directly to analyst workload — each false alarm is a session
a security team must manually triage. Reported here per Unit 2.5 guidance.
```

The model training console output, produced by `python -m detection.train_model`, confirms the GBT feature importance scores reported in Table 4.4:

```
Trained and saved: logistic_regression
Trained and saved: random_forest
Trained and saved: gradient_boosting

GBT feature importances:
call_description_length                   0.545
call_suspicious_keyword_hits              0.340
time_since_registration_s                 0.032
call_description_entropy                  0.030
reg_description_length                    0.016
num_calls_in_session                      0.014
reg_description_entropy                   0.009
call_position_in_session                  0.008
reg_suspicious_keyword_hits               0.003
num_schema_fields                         0.003
description_changed_after_registration    0.000

Saved test-set predictions to data/model_test_results.csv
```

---

## Appendix D: Test Suite Output

The following is the verbatim output of `python -m pytest tests/ -v` (pytest 9.1.1, Python 3.13.5). All six tests pass, validating the corpus generation invariants and the baseline's structural blind spot against the rug-pull class.

```
============================= test session starts ==============================
platform darwin -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0
rootdir: /path/to/mcp-security-project
plugins: anyio-4.14.2
collecting ... collected 6 items

tests/test_pipeline.py::test_generate_produces_all_three_classes PASSED  [ 16%]
tests/test_pipeline.py::test_benign_mostly_has_no_keyword_hits PASSED    [ 33%]
tests/test_pipeline.py::test_rugpull_mostly_changes_description PASSED   [ 50%]
tests/test_pipeline.py::test_rugpull_mostly_invisible_at_registration PASSED [ 66%]
tests/test_pipeline.py::test_baseline_misses_majority_of_rugpulls PASSED [ 83%]
tests/test_pipeline.py::test_text_entropy_and_keyword_hits_basic_sanity PASSED [100%]

============================== 6 passed in 0.45s ===============================
```

The six tests and what they assert:

| Test | What it validates |
| --- | --- |
| `test_generate_produces_all_three_classes` | Corpus contains exactly the three labelled classes with the correct total row count |
| `test_benign_mostly_has_no_keyword_hits` | Benign sessions have keyword-hit rates below 20% (registration) and 25% (call time), consistent with the noise model rates |
| `test_rugpull_mostly_changes_description` | At least 80% of rug-pull sessions set `description_changed_after_registration = 1` (the 10% stealthy rate bounds the remainder) |
| `test_rugpull_mostly_invisible_at_registration` | At least 70% of rug-pull registrations are clean (`reg_suspicious_keyword_hits = 0`), confirming baseline structural blindness |
| `test_baseline_misses_majority_of_rugpulls` | The baseline misses at least 70% of rug-pull sessions, providing a programmatic guard against regressions that would give the baseline unfair access to call-time features |
| `test_text_entropy_and_keyword_hits_basic_sanity` | Shannon entropy returns 0.0 for an empty string; `keyword_hits` correctly identifies and ignores injection-patterned and clean text |

---

## Appendix E: Testbed Demonstration

The testbed MCP server (`server/testbed_server.py`) is a working FastMCP implementation that exposes the five-tool catalogue over stdio transport. It can be run independently of the detection pipeline for manual inspection and supervisor demonstration:

```bash
# Terminal 1 — start the server
source venv/bin/activate
python -m server.testbed_server
# Output: FastMCP server running on stdio

# Terminal 2 — run the client
source venv/bin/activate
python -m client.testbed_client
```

The client connects to the server, issues a `tools/list` call, and prints the full tool catalogue as returned by the MCP protocol. A representative excerpt of the client output:

```
Connected to MCP server.

Available tools (5):
  get_weather         — Returns the current weather for a given city name.
  search_docs         — Searches an internal document index and returns matching titles.
  create_ticket       — Creates a support ticket with a title and description.
  send_notification   — Sends a notification message to a named channel.
  lookup_account      — Looks up a customer account record by account ID.

Invoking get_weather(city='London', units='metric') ...
  Result: [get_weather] ok - city=London, units=metric
```

This demonstrates that the five tools described in Chapter 3 (Section 3.2) are implemented as a genuine MCP server, not merely as data structures in the corpus generator. The corpus generator (`corpus/generate_corpus.py`) imports `TOOL_CATALOG` from `server/tool_definitions.py` — the same shared module the testbed server uses — ensuring that the tool metadata used to generate training data is identical to the metadata the server would expose in a live session.
