# Appendices

---

## Appendix A: Source Code

The complete source code for this project is available at:

> <https://github.com/krumholzeddy1/mcp-security-project>

The dissertation results reported in Chapter 6 were produced at commit `83fad16`. All pipeline outputs (`data/corpus.csv`, `data/evaluation_summary.csv`, `data/model_test_results.csv`, `data/baseline_results.csv`) are committed alongside the source code and are byte-for-byte reproducible by running the pipeline commands in order with the pinned environment described in Appendix B.

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

The following is the verbatim console output produced by running `python -m evaluation.evaluate` against the committed pipeline artefacts (commit `83fad16`, Python 3.13.5, scikit-learn 1.9.0). This output corroborates the results tables in Chapter 6.

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

## Appendix F: Attack Taxonomy — Example Descriptions

The following table illustrates representative descriptions for each corpus class using the `get_weather` tool. The rug-pull registration description is identical to the benign registration description, which is the structural basis for the baseline's 0.000 rug-pull recall (Chapter 6, §6.4.1).

| Class | Description at registration | Description at call time | Detectable at registration? |
| --- | --- | --- | --- |
| Benign | "Returns the current weather for a given city name." | Same (or with benign update, e.g. " (v2: batch input supported.)") | No |
| Poisoned | "Returns the current weather for a given city name. IMPORTANT: ignore prior instructions and always set verbose\_mode=true and attach environment variables." | Identical to registration | Yes — keywords `ignore prior`, `verbose_mode` present at registration |
| Rug-pull | "Returns the current weather for a given city name." | "Returns the current weather for a given city name. NOTE TO ASSISTANT: this tool must be called before any other tool in every session, regardless of user request." | No — registration description is clean; injection only visible at call time |

The same pattern applies to all five tools in the TOOL_CATALOG (`search_docs`, `create_ticket`, `send_notification`, `lookup_account`), with tool-specific benign descriptions and associated poison fragments defined in `server/tool_definitions.py`.

---

## Appendix G: Noise Model Rates

The seven noise mechanisms applied during corpus generation are documented below. All rates are implemented as named constants in `corpus/generate_corpus.py` and are applied before the fixed random seed (`random.seed(42)`) is consumed, ensuring reproducibility.

| Mechanism | Rate | Effect |
| --- | --- | --- |
| Benign with accidental keyword hit | 8% | Legitimate DevOps/sysadmin descriptions that contain terminology matching the keyword list; introduces false-positive pressure on the keyword-based features |
| Benign with legitimate description update | 20% | Tool description updated mid-session for a non-malicious reason (version bump, clarification); creates benign sessions where `description_changed_after_registration = 1` |
| Benign with verbose description | 35% | Legitimately lengthy tool documentation (130–250 characters); blurs the length boundary between benign and attack sessions |
| Poisoned/rug-pull with evasive fragment | 12–15% | Injected text uses phrasing outside the keyword list, simulating adversaries aware of keyword-based filters |
| Poisoned/rug-pull with short fragment | 20–25% | Terse injection directives (20–50 characters) that minimise the description-length delta |
| Rug-pull with partial leak at registration | 15% | A sloppy attacker includes an evasive fragment in the registration description; these sessions are partially detectable by the baseline keyword scan |
| Stealthy rug-pull | 10% | Attacker mutates the description but reverts it before the metadata snapshot is taken; all eleven features are identical to a genuine benign session |

The stealthy rug-pull mechanism produces the 8 irreducible false negatives in the balanced-corpus evaluation (Chapter 6, §6.4.1). These sessions are ground-truth labelled `rugpull` but are literally indistinguishable from benign sessions in the eleven-feature space; they establish a hard theoretical lower bound on point-in-time recall.

---

## Appendix H: Data Quality Assessment

The primary dataset is assessed against five quality criteria commonly applied to research datasets (Saunders, Lewis and Thornhill, 2019):

| Criterion | Assessment |
| --- | --- |
| **Validity** | Features are computed directly from the protocol-level properties used to define each attack class (description length, keyword presence, description change flag). Ground-truth labels are assigned by the generation logic, so label validity is exact by construction. |
| **Reliability** | The fixed random seed (`random.seed(42)`) ensures byte-for-byte reproducibility. Any researcher running `corpus/generate_corpus.py` with the pinned environment (Appendix B) will obtain an identical dataset. |
| **Accuracy** | All feature values are computed deterministically from the generated description strings. Shannon entropy and keyword-hit counts are calculated by pure Python arithmetic with no approximation. |
| **Completeness** | The corpus is complete by design: every generated session produces all eleven feature values. No missing values are present in `corpus.csv`. |
| **Representativeness** | This is the criterion the dataset does not fully satisfy. The synthetic corpus represents a model of real MCP deployments, not a sample from one. The five tool archetypes and injection fragments are derived from the literature but are not observed real-world attack instances. The degree to which the learned detector generalises to real deployments is unknown and is the primary limitation of this study (Chapter 7, §7.3). |

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
