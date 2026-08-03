# MCP Tool-Poisoning Detection

Research code for the dissertation *"Detecting Tool-Poisoning Attacks in Model Context Protocol (MCP) Agentic Systems Using Machine-Learning-Based Anomaly Detection"*, submitted in partial fulfilment of the requirements for CO4011, University of Central Lancashire / RKC Lancashire.

---

## Repository Structure

| Folder / File | Purpose |
| --- | --- |
| `server/tool_definitions.py` | Shared `ToolSpec` dataclass and `TOOL_CATALOG` — the five tool archetypes and associated injection fragments used across the pipeline |
| `server/testbed_server.py` | FastMCP server exposing the tool catalogue over stdio for demonstration and supervisor inspection |
| `client/testbed_client.py` | Async MCP client for manual round-trip demonstration against the testbed server |
| `corpus/generate_corpus.py` | Synthetic corpus generator — produces `data/corpus.csv` (600 sessions, balanced) and `data/corpus_skewed.csv` (600 sessions, 90/5/5) |
| `baseline/schema_validator.py` | Registration-time keyword-based schema-validator baseline |
| `detection/train_model.py` | Trains Logistic Regression, Random Forest, and Gradient Boosting classifiers on the balanced corpus |
| `evaluation/evaluate.py` | Compares all four methods on balanced and skewed corpora; writes `data/evaluation_summary.csv` |
| `tests/test_pipeline.py` | Six smoke tests validating corpus generation invariants and the baseline's structural blind spot |

---

## Evaluation Results

Results are produced by running the pipeline in sequence against the committed corpus (see Appendix C of the dissertation for the verbatim console output). Per-class recall is the headline metric: a missed attack carries a higher operational cost than a false alarm, and reporting overall recall or F1 alone would allow high poisoned-class recall to mask a rug-pull recall of zero — which is precisely the pattern the baseline exhibits.

### Balanced corpus (200 sessions per class, 70/30 stratified split)

| Method | Precision | Recall | F1 | Recall: poisoned | Recall: rug-pull |
| --- | --- | --- | --- | --- | --- |
| Baseline schema-validator | 0.909 | 0.333 | 0.488 | 0.755 | **0.000** |
| Logistic Regression | 0.862 | 0.883 | 0.872 | 0.887 | 0.881 |
| Random Forest | 0.950 | 0.942 | 0.946 | 1.000 | 0.896 |
| Gradient Boosting (primary) | 0.957 | 0.933 | **0.945** | 1.000 | 0.881 |

The baseline achieves **0.000 rug-pull recall** by structural necessity: rug-pull attacks register with a clean description, so `reg_suspicious_keyword_hits = 0` at the moment the baseline inspects the session. No tuning of the keyword list or detection threshold changes this outcome while the check operates at registration time. All three ML detectors achieve rug-pull recall between 0.881 and 0.896, using call-time features that are structurally unavailable to the baseline — principally `call_description_length` (54.5% GBT feature importance) and `call_suspicious_keyword_hits` (34.0%), which together account for 88.5% of the model's discriminative information.

### Robustness check — skewed corpus (90% benign, 5% poisoned, 5% rug-pull)

The primary GBT model (trained on the balanced corpus) is applied without retraining to a skewed distribution that approximates real-world class proportions.

| Method | Precision | Recall | F1 | Recall: rug-pull | FP rate (benign) |
| --- | --- | --- | --- | --- | --- |
| Baseline schema-validator | 0.429 | 0.400 | 0.414 | 0.000 | 5.9% |
| Gradient Boosting | 0.682 | 0.967 | 0.800 | **0.933** | 5.0% |

The ML detector's rug-pull recall rises to 0.933 under skew, confirming that detection capability generalises beyond the balanced training distribution. Precision drops to 0.682 — the expected effect of applying a balanced-trained model to a skewed set, where false positives represent a larger share of positive predictions. The baseline's rug-pull recall remains 0.000 under both distributions.

---

## Reproducing the Results

All stochastic operations use `random.seed(42)` (corpus generation) and `random_state=42` (scikit-learn train/test split and all classifiers). Running the pipeline with the pinned environment below will produce byte-for-byte identical outputs.

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

python -m corpus.generate_corpus       # → data/corpus.csv, data/corpus_skewed.csv
python -m baseline.schema_validator    # → data/baseline_results.csv
python -m detection.train_model        # → data/detector_model_*.joblib, data/model_test_results.csv
python -m evaluation.evaluate          # → data/evaluation_summary.csv

python -m pytest tests/ -v             # six smoke tests — all pass
```

The full environment specification (Python 3.13.5, scikit-learn 1.9.0, pandas 3.0.5, numpy 2.5.1) is documented in Appendix B of the dissertation and captured in `requirements.txt`.

---

## Limitations

- **Synthetic corpus.** No publicly available labelled dataset of real MCP tool-poisoning attacks exists. The corpus is generated from a documented noise model calibrated against the literature; the degree to which the trained detector generalises to real deployments is unknown. This is the primary limitation of the study, discussed in Chapter 7, §7.3.

- **Feature set.** The eleven features are protocol-level observables only — description text is not treated as natural language. An adversary who is aware of the feature set and crafts injection text to remain below keyword and length thresholds would degrade detection performance. Extensions to the feature set are identified as future work in Chapter 8, §8.4.

- **Stealthy rug-pull bound.** A rug-pull attacker who mutates and then reverts the tool description before the monitoring snapshot produces a session that is indistinguishable from benign in the eleven-feature space. The 8 false negatives in the balanced evaluation represent a hard theoretical lower bound on point-in-time recall, not a model deficiency. This bound and the case for continuous monitoring are discussed in Chapter 7, §7.2.
