# Chapter 6: Conclusion

## 6.1 Summary of the Study

This dissertation investigated whether machine-learning-based anomaly detection of tool-call metadata can improve detection of tool-poisoning attacks in MCP-based agentic AI systems, with particular attention to the rug-pull attack class that existing registration-time defences are structurally unable to detect.

A controlled testbed was constructed comprising a real MCP server, a reference client, and a reproducible synthetic corpus of 600 labelled tool-call sessions across three classes: benign sessions, sessions poisoned at registration, and rug-pull sessions in which the description mutated after the tool was trusted. Three ML classifiers — Logistic Regression, Random Forest, and Gradient Boosting — were each trained on eleven metadata features and compared against a schema-validator baseline that inspects only registration-time metadata. A deliberate noise model was applied to ensure that class distributions overlap across the feature space, preventing trivially separable classes and producing evaluation results that reflect the relative capability of the two approaches rather than an artefact of corpus construction. A robustness check on a skewed corpus (90% benign, 5% each attack class) confirmed that the detection capability generalises under realistic class imbalance, though at the cost of reduced precision.

## 6.2 Objectives Achieved

The following table verifies that each objective stated in Section 1.3 was met, with a reference to the section where the evidence is presented.

| Objective | Status | Evidence |
| --- | --- | --- |
| O1: Review literature on MCP, tool-poisoning, existing defences, and ML anomaly detection | Met | Chapter 2, particularly §2.3–§2.7 |
| O2: Design and implement a controlled MCP testbed | Met | `server/testbed_server.py`, `client/testbed_client.py`; §3.2 |
| O3: Generate a reproducible labelled synthetic corpus with a documented noise model | Met | `corpus/generate_corpus.py`, `data/corpus.csv` (600 sessions, `random.seed(42)`); §3.3 |
| O4: Implement a registration-time schema-validator baseline and characterise its structural blind spot | Met | `baseline/schema_validator.py`; §3.4; rug-pull recall = 0.000 confirmed in §4.4.1 |
| O5: Train three candidate ML classifiers on eleven metadata features using a fixed stratified split | Met | `detection/train_model.py`; §3.5; LR, RF, GBT all trained on the same 70/30 split |
| O6: Compare ML detectors against the baseline, with per-class rug-pull recall as primary metric | Met | `evaluation/evaluate.py`; §4.2–§4.4; Table 4.1 |
| O7: Evaluate robustness under a skewed class distribution and report precision degradation in operational terms | Met | `data/corpus_skewed.csv`; §4.6; 5.0% false-alarm rate on benign sessions |
| O8: Analyse feature importance to establish mechanistic grounding and characterise the theoretical detection bound | Met | §4.5 (96.9% importance from post-registration features); §5.2 (stealthy rug-pull bound) |

All eight objectives are met. The objectives collectively address the aim stated in Section 1.3: that post-registration metadata features contain sufficient signal to detect rug-pull attacks that registration-time defences cannot see.

## 6.3 Answer to the Research Question

The research question asked: *to what extent can ML-based anomaly detection of tool-call metadata and tool-description change patterns improve detection of tool-poisoning attacks in MCP-based agentic systems, compared with existing schema-validation defences?*

The answer is that the improvement is substantial and qualitatively different in kind from incremental tuning of the baseline. The headline finding is rug-pull recall: **0% for the baseline in all conditions**, versus **88.1–93.3% for the ML detectors** across the balanced and skewed evaluation corpora. The baseline's zero rug-pull recall is not a fixable deficiency in the keyword list or threshold; it is a structural consequence of the observation window ending at registration. All three ML architectures tested achieve rug-pull recall above 0.880, confirming that the finding is a property of the post-registration feature set rather than of any specific algorithm. The feature importance analysis of the primary Gradient Boosting model confirms this mechanistically: 96.9% of its discriminative information comes from call-time features structurally unavailable to the baseline, principally `call_description_length` (54.5% importance) and `call_suspicious_keyword_hits` (34.0%).

The residual 11.9% false-negative rate on rug-pulls is attributed to stealthy attacks that revert their description mutation before the metadata snapshot is recorded. These are genuine false negatives that no point-in-time detector can avoid; they establish a hard lower bound on the achievable recall of the current approach and motivate the architectural change described in Section 6.4.

## 6.4 Future Work

Three directions are identified as the highest-priority extensions of this work.

**Continuous session monitoring.** Moving from a single metadata snapshot to a time-series of description observations at every `tools/list` call and every tool invocation would expose the transient mutation pattern that stealthy rug-pulls produce. New features — maximum description deviation from the registration value, duration of deviation windows, and temporal correlation between deviations and tool invocations — would provide signal that is theoretically unavailable to the current point-in-time detector. Evaluating a sequence-aware model (for example, a recurrent classifier or a change-point detection algorithm applied to the description-length time series) against both the current attack taxonomy and stealthy variants is the most direct path to closing the remaining false-negative gap.

**Real-world corpus development.** The synthetic corpus used in this study is reproducible and controlled but distributes over a narrow range of tool descriptions and attack patterns. Collecting labelled examples of real MCP tool-call sessions — either through instrumented honeypot deployments or through collaboration with MCP server operators — would allow the feature distributions to be calibrated against genuine deployments and the noise model to be grounded empirically rather than by design judgement. A real-world corpus would also expose attack patterns not represented in the current taxonomy, including multi-tool coordinated attacks and injection via parameter schema field names.

**Extension to the Agent2Agent (A2A) protocol.** Google's Agent2Agent protocol defines an analogous tool-calling interface for multi-agent systems, and is expected to face a similar class of tool-poisoning vulnerabilities given its structural resemblance to MCP. Applying the metadata-based detection approach developed in this project to A2A sessions — adapting the feature set to the A2A message schema and extending the attack taxonomy to cover A2A-specific patterns — would provide a comparative analysis of detection difficulty across the two dominant agentic protocols. This extension was identified in the project proposal as out of scope for the current timeline but is the natural next phase of the research.

## 6.5 Closing Remarks

The central argument of this dissertation is simple: the existing defences against MCP tool poisoning look at the wrong moment. They check a tool when it arrives and assume that what was true at arrival remains true throughout the session. Rug-pull attacks are possible precisely because that assumption is false. A detector that keeps watching — that treats each tool invocation as an opportunity to re-evaluate the tool's current description against its registration-time baseline — can catch what registration-time checks miss. This project demonstrates that the signal is there to be caught, quantifies how much of it a practical classifier can recover from point-in-time metadata alone, and identifies what architectural change is required to recover the rest.
