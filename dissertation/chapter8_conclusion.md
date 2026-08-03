# Chapter 8: Conclusion

## 8.1 Summary of the Study

This dissertation tested whether ML-based anomaly detection of MCP tool-call metadata can detect rug-pull attacks that registration-time defences cannot. Three classifiers were trained on eleven metadata features from a 600-session synthetic corpus and compared against a schema-validator baseline, with per-class rug-pull recall as the primary metric.

## 8.2 Objectives Achieved

The following table verifies that each objective stated in Section 1.3 was met, with a reference to the section where the evidence is presented.

| Objective | Status | Evidence |
| --- | --- | --- |
| O1: Review literature on MCP, tool-poisoning, existing defences, and ML anomaly detection | Met | Chapter 2, particularly §2.3–§2.6 |
| O2: Design and implement a controlled MCP testbed | Met | `server/testbed_server.py`, `client/testbed_client.py`; §3.2; Chapter 4 |
| O3: Generate a reproducible labelled synthetic corpus with a documented noise model | Met | `corpus/generate_corpus.py`, `data/corpus.csv` (600 sessions, `random.seed(42)`); §3.3 |
| O4: Implement a registration-time schema-validator baseline and characterise its structural blind spot | Met | `baseline/schema_validator.py`; §3.4; rug-pull recall = 0.000 confirmed in §6.4.1 |
| O5: Train three candidate ML classifiers on eleven metadata features using a fixed stratified split | Met | `detection/train_model.py`; §3.5; Chapter 4, §4.4; LR, RF, GBT all trained on the same 70/30 split |
| O6: Compare ML detectors against the baseline, with per-class rug-pull recall as primary metric | Met | `evaluation/evaluate.py`; §6.2–§6.4; Table 6.1 |
| O7: Evaluate robustness under a skewed class distribution and report precision degradation in operational terms | Met | `data/corpus_skewed.csv`; §6.6; 5.0% false-alarm rate on benign sessions |
| O8: Analyse feature importance to establish mechanistic grounding and characterise the theoretical detection bound | Met | §6.5 (96.9% importance from post-registration features); §7.2 (stealthy rug-pull bound) |

All eight objectives are met. The objectives collectively address the aim stated in Section 1.3: that post-registration metadata features contain sufficient signal to detect rug-pull attacks that registration-time defences cannot see.

## 8.3 Answer to the Research Question

The research question asked: *to what extent can ML-based anomaly detection of tool-call metadata and tool-description change patterns improve detection of tool-poisoning attacks in MCP-based agentic systems, compared with existing schema-validation defences?*

The answer is that the improvement is substantial and qualitatively different in kind from incremental tuning of the baseline. The headline finding is rug-pull recall: **0% for the baseline in all conditions**, versus **88.1–93.3% for the ML detectors** across the balanced and skewed evaluation corpora. The baseline's zero rug-pull recall is not a fixable deficiency in the keyword list or threshold; it is a structural consequence of the observation window ending at registration. All three ML architectures tested achieve rug-pull recall above 0.880, confirming that the finding is a property of the post-registration feature set rather than of any specific algorithm. The feature importance analysis of the primary Gradient Boosting model confirms this mechanistically: 96.9% of its discriminative information comes from call-time features structurally unavailable to the baseline, principally `call_description_length` (54.5% importance) and `call_suspicious_keyword_hits` (34.0%).

## 8.4 Future Work

Three directions are identified as highest-priority extensions. **Continuous session monitoring**: tracking description time-series across all `tools/list` calls would expose transient mutations that stealthy rug-pulls produce, requiring a sequence-aware model with features such as maximum deviation magnitude and deviation window duration. **Real-world corpus development**: collecting labelled examples from honeypot deployments would calibrate feature distributions and expose out-of-taxonomy attack patterns. **A2A protocol extension**: applying the metadata-based detection approach to Google's Agent2Agent protocol would provide comparative analysis across the two dominant agentic frameworks.

## 8.5 Closing Remarks

This project demonstrates that the post-registration signal exists, that a practical classifier recovers most of it from point-in-time metadata, and that continuous monitoring is the architectural change needed to recover the rest. The finding is mechanistically grounded: 96.9% of the model's discriminative power comes from post-registration features, not model-specific properties.
