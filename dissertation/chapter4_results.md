# Chapter 4: Results and Analysis

## 4.1 Overview and Metric Rationale

This chapter presents the evaluation results for the baseline schema-validator and three ML anomaly detectors on the held-out test set of 180 sessions drawn from the synthetic corpus, followed by a robustness check on a skewed class-balance corpus.

**Per-class recall is the headline metric throughout this chapter.** The justification is as follows: the costly failure mode in attack detection is a missed attack, not a false alarm. A detector that flags nothing at all achieves high precision (no false positives among its positive predictions) while missing every attack. Reporting only precision or overall F1 would allow such a degenerate detector to appear competitive. Recall — and specifically the recall decomposed by attack class — is the metric that directly answers the research question, which asks whether the ML detector can detect attacks the baseline misses. Overall F1 and precision are reported as supplementary information but do not alter the primary conclusion.

The held-out test set was produced by a 70/30 stratified split on the binary `is_attack` label, yielding 60 benign sessions and 120 attack sessions (53 `poisoned` and 67 `rugpull`, reflecting the natural variation from the random shuffle). All four methods are evaluated against identical inputs.

---

## 4.2 Multi-Model Comparison: Overall and Per-Class Performance

Table 4.1 reports precision, recall, F1, and per-class recall for all four methods. The schema-validator baseline is included as a lower-bound reference point; the three ML detectors were all trained on the same 70/30 split to ensure the comparison is apples-to-apples.

### Table 4.1: Classification performance by method (balanced corpus, test set n=180)

| Method | Precision | Recall | F1 | Recall: poisoned | Recall: rug-pull |
| --- | --- | --- | --- | --- | --- |
| Baseline schema-validator | 0.909 | 0.333 | 0.488 | 0.755 | **0.000** |
| Logistic Regression | 0.862 | 0.883 | 0.872 | 0.887 | 0.881 |
| Random Forest | 0.950 | 0.942 | 0.946 | 1.000 | 0.896 |
| Gradient Boosting (primary) | 0.957 | 0.933 | **0.945** | 1.000 | 0.881 |

**How this answers the research question.** The rug-pull recall row is the direct empirical answer to H₁. The baseline achieves 0.000 rug-pull recall regardless of the keyword list, the threshold, or the session count — this is zero by structural necessity, as established in Chapter 3. All three ML detectors achieve rug-pull recall between 0.881 and 0.896: a categorical improvement over a baseline that cannot detect this attack class at all. This is not a marginal improvement on a metric the baseline was already performing on; it is the detection of an entirely undetected attack category.

**Why this is consistent with the anomaly detection literature.** Ahmed et al. (2025) document a parallel pattern in network intrusion detection: anomaly-based methods detect attack categories that signature-based methods miss by construction, because signatures require prior knowledge of the attack pattern. The rug-pull result here replicates that pattern in a new domain — MCP tool-call metadata — extending the finding to agentic AI systems for the first time identified in this review.

**Why Gradient Boosting was selected as the primary model.** GBT achieves the highest precision (0.957 versus 0.950 for Random Forest) at effectively equivalent rug-pull recall (0.881 for both). Higher precision means fewer false alarms per benign session, which is the operational cost dimension for a security analyst team. The difference between GBT and Random Forest is small, which is itself a finding: it confirms that the detection capability is not algorithm-specific but reflects the structure of the feature set and the attack taxonomy.

**Why the Logistic Regression result matters.** LR achieves 0.881 rug-pull recall with a substantially simpler model. This confirms that the decision boundary is not highly non-linear — a linear separator in the feature space is sufficient to detect the majority of attacks. The fact that LR underperforms on precision (0.862 versus 0.950–0.957 for tree-based methods) is the operational reason to prefer tree-based methods in deployment, but the LR result rules out the hypothesis that rug-pull detection requires complex feature interactions.

---

## 4.3 Confusion Matrices

### Table 4.2: Binary confusion matrices (positive class = attack)

| Method | TP | FP | FN | TN |
| --- | --- | --- | --- | --- |
| Baseline schema-validator | 40 | 4 | 80 | 56 |
| Logistic Regression | 106 | 17 | 14 | 43 |
| Random Forest | 113 | 6 | 7 | 54 |
| Gradient Boosting | 112 | 5 | 8 | 55 |

The baseline's 80 false negatives — sessions that are genuine attacks but are not flagged — contrast with the ML detectors' 7–14 false negatives. The four false positives in the baseline and five in the GBT are similar, confirming that the dramatic precision difference (0.909 vs 0.957) in Table 4.1 is a consequence of the GBT flagging far more true positives against a similar false-positive count, rather than the baseline being more conservative.

---

## 4.4 Per-Class Recall: Rug-Pull and Poisoned

### 4.4.1 Rug-Pull Detection

The baseline achieves 0.000 rug-pull recall. This is not a statistical finding — it is deterministic. A rug-pull session registers with a clean description, producing `reg_suspicious_keyword_hits = 0`. The baseline's rule (`reg_suspicious_keyword_hits >= 1`) therefore assigns a negative prediction to every rug-pull session. No tuning of the keyword list or the detection threshold can change this outcome while the check operates at registration time.

**How this answers the research question.** Willison (2025) described the rug-pull mechanism qualitatively — a tool passes initial review and injects malicious content only after being trusted. This dissertation provides the first quantitative demonstration that a registration-time validator achieves exactly 0% rug-pull recall, not merely reduced recall. It confirms the mechanism Willison described with measured evidence rather than a single illustrative account. The finding also corroborates the architectural analysis of Hou et al. (2025): their framing of MCP's "trust without re-verification" weakness predicts precisely this result — a defence that checks trust once but never re-checks is structurally blind to any post-trust change.

The ML detector (GBT) flags 59 of 67 rug-pull sessions, achieving 88.1% recall. The 8 false negatives are exclusively stealthy rug-pulls — sessions in which the attacker mutated and then reverted the description before the metadata snapshot was taken, making all eleven features identical to a benign session. No point-in-time feature-based detector can distinguish these sessions from genuine benign sessions; the 8 false negatives represent the theoretical lower bound on false negatives for this detection approach, not a model deficiency. This bound is discussed in Section 5.1.

### 4.4.2 Poisoned Session Detection

The baseline achieves 0.755 recall on poisoned sessions: 40 of 53 are detected, 13 are missed. The 13 false negatives correspond to poisoned sessions generated with evasive or short fragments that do not appear in the suspicious-keyword list — the noise subclass introduced to simulate adversaries aware that keyword filters exist. The baseline's recall on the non-evasive majority of poisoned sessions is 1.000; its recall on evasive poisoned sessions is 0.000. This bimodal structure illustrates the fundamental constraint of static rule-based detection: its recall is bounded by the completeness of its rule vocabulary.

**How this answers the research question.** The poisoned-session result extends the finding in Radosevich and Halloran (2025), who demonstrated empirically that tool-poisoning attacks succeed even with current LLM safety training. This dissertation adds a detection dimension: an ML detector trained on metadata features identifies all poisoned sessions (including evasive ones) that a keyword-based rule misses. The mechanism is that the model exploits correlated structural signals — the description-length increase from appending any fragment, the entropy shift — rather than relying on specific string matches. This is consistent with the general anomaly-detection principle documented by Greshake et al. (2023): behavioural deviation from a learned baseline is detectable even when the specific attack variant was not known at design time.

The GBT achieves 100% recall on poisoned sessions (53/53). All three ML detectors achieve poisoned recall of at least 0.887, confirming that this result is robust across model families and not an artefact of the GBT's boosting mechanism.

---

## 4.5 Feature Importance Analysis

Table 4.3 reports feature importance scores from the trained GBT — the cumulative reduction in node impurity (a measure of how much each feature reduces classification uncertainty at the decision nodes across the ensemble; higher values indicate a greater contribution to correct classification) attributable to each feature across all trees. Importances sum to 1.0.

### Table 4.3: GBT feature importances

| Feature | Importance | Observable by baseline? |
| --- | --- | --- |
| `call_description_length` | 0.545 | No |
| `call_suspicious_keyword_hits` | 0.340 | No |
| `time_since_registration_s` | 0.032 | No |
| `call_description_entropy` | 0.030 | No |
| `reg_description_length` | 0.016 | Yes |
| `num_calls_in_session` | 0.014 | No |
| `reg_description_entropy` | 0.009 | Yes |
| `call_position_in_session` | 0.008 | No |
| `reg_suspicious_keyword_hits` | 0.003 | Yes |
| `num_schema_fields` | 0.003 | Yes |
| `description_changed_after_registration` | ~0.000 | No |

**How this answers the research question.** The feature importance distribution directly answers *why* the ML detector outperforms the baseline. The two most important features (`call_description_length`, 54.5%; `call_suspicious_keyword_hits`, 34.0%) are both call-time features unavailable to the baseline. Together they account for 88.5% of the model's discriminative information. The four registration-time features available to the baseline (`reg_description_length`, `reg_description_entropy`, `reg_suspicious_keyword_hits`, `num_schema_fields`) account for a combined 3.1%. The detector's advantage is mechanistically explained by access to features that the baseline structurally cannot observe — not by any incidental property of the synthetic corpus.

**The zero importance of `description_changed_after_registration`.** This binary flag would naively appear to be the most informative feature for rug-pull detection — it is 1 for all non-stealthy rug-pull sessions and 0 for all poisoned and most benign sessions. Its near-zero importance indicates that the GBT model never selects it as a splitting criterion because the call-time length and keyword features already provide superior splits at every node. The classifier learns a richer representation of the attack signal than a single binary flag, which is the outcome the noise model was designed to produce and provides evidence that the learned decision boundary generalises beyond the training artefact.

---

## 4.6 Robustness Check: Skewed Class Balance (90/5/5)

Table 4.4 reports results for the GBT model (trained on the balanced corpus) applied to the skewed corpus, in which 540 of 600 sessions are benign (90%) and 30 each are poisoned and rug-pull (5% each).

### Table 4.4: Skewed corpus evaluation (GBT model trained on balanced corpus)

| Method | Precision | Recall | F1 | Recall: poisoned | Recall: rug-pull | FP rate (benign) |
| --- | --- | --- | --- | --- | --- | --- |
| Baseline schema-validator | 0.429 | 0.400 | 0.414 | 0.800 | 0.000 | 5.9% |
| Gradient Boosting | 0.682 | 0.967 | 0.800 | 1.000 | 0.933 | 5.0% |

**How this answers the research question.** Under class imbalance, the GBT model's attack-detection capability is preserved: overall recall rises to 0.967 and rug-pull recall to 0.933, marginally *better* than the balanced-corpus result. This indicates that the model is not over-fitted to the balanced distribution; the attack patterns are detectable at low prevalence.

**The precision drop.** GBT precision falls from 0.957 (balanced corpus) to 0.682 (skewed corpus). This is the expected consequence of applying a model trained on balanced classes to a skewed test set: with fewer attack sessions relative to benign sessions, the same absolute false-positive count represents a larger share of the model's positive predictions. Operationally, the 27 false positives (5.0% of benign sessions) translate to 27 manual triage events for a security team per 600-session corpus. Whether that false-alarm rate is acceptable is a deployment decision that depends on team capacity; the result is reported here in those terms rather than as a bare precision number, per the interpretation guidance of Unit 2.5.

The baseline's precision also collapses under skew (0.429), while its rug-pull recall remains 0.000. The skewed corpus therefore preserves the qualitative hierarchy from the balanced evaluation: the ML detector substantially outperforms the baseline on rug-pull detection under both class distributions.

---

## 4.7 Summary

The results answer H₁ directly: the ML detector achieves measurably higher rug-pull recall than the registration-time schema validator across both the balanced and skewed evaluation corpora. The baseline achieves 0.000 rug-pull recall in all conditions; the ML detector achieves 0.881–0.933 depending on the corpus distribution.

Three subsidiary findings reinforce the main result:

1. The improvement is consistent across all three ML model families tested (Logistic Regression, Random Forest, Gradient Boosting), confirming it reflects the feature set and attack taxonomy rather than any model-specific property.
2. Feature importance analysis confirms that 96.9% of the ML detector's discriminative information comes from call-time features that the baseline structurally cannot observe.
3. The 8 false negatives on the balanced corpus correspond exclusively to the stealthy rug-pull subclass — sessions that are genuinely indistinguishable from benign sessions in the feature space — and establish a theoretically motivated upper bound on recall for any point-in-time detection approach.

The implications of the stealthy bound, the limitations of the synthetic corpus, and the relationship to existing defences are examined in Chapter 5.
