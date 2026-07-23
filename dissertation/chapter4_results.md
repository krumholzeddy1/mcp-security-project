# Chapter 4: Results and Analysis

## 4.1 Overview

This chapter presents the evaluation results for both the baseline schema-validator and the ML anomaly detector on the held-out test set of 180 sessions drawn from the synthetic corpus. Results are reported at two levels: overall binary classification performance (attack versus benign), and per-class recall decomposed by attack type. Feature importance scores from the trained model are then examined to identify which features drive detection and to assess how much of the model's discriminative power derives from call-time and description-change signals that the baseline structurally cannot observe.

The held-out test set was produced by a 70/30 stratified split on the binary `is_attack` label, preserving the 1:2 benign-to-attack ratio from the full corpus. Within the 120 attack sessions, the split distributed 53 sessions to the `poisoned` class and 67 to the `rugpull` class, reflecting the natural variation introduced by the random shuffle prior to splitting. Both detectors are evaluated against identical inputs.

---

## 4.2 Overall Classification Performance

Table 4.1 reports precision, recall, and F1 score for both detectors on the test set. The binary positive class is "attack" (comprising both poisoned and rug-pull sessions); the negative class is "benign".

**Table 4.1: Overall binary classification performance (test set, n=180)**

| Method | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|---|
| Baseline schema-validator | 40 | 4 | 80 | 56 | 0.909 | 0.333 | 0.488 |
| ML anomaly detector | 112 | 5 | 8 | 55 | 0.957 | 0.933 | **0.945** |

The ML detector achieves an F1 score of 0.945 compared to 0.488 for the baseline — an absolute improvement of 0.457 F1 points, or approximately 94% relative improvement. The most pronounced difference is in recall: the ML detector correctly flags 112 of 120 attack sessions (93.3%) against the baseline's 40 of 120 (33.3%). Both detectors achieve high precision — 0.957 and 0.909 respectively — indicating that false positives are low in both cases (five and four mis-flagged benign sessions respectively, out of 60). The similarity in precision reflects the fact that both detectors rarely raise false alarms; the decisive difference is in their ability to *find* attacks in the first place.

---

## 4.3 Per-Class Recall Analysis

Aggregated recall conceals the most important finding in these results. Table 4.2 reports recall decomposed by attack class.

**Table 4.2: Recall by attack class (test set)**

| Attack class | n | Baseline TP | Baseline FN | Baseline recall | ML TP | ML FN | ML recall |
|---|---|---|---|---|---|---|---|---|
| `poisoned` | 53 | 40 | 13 | 0.755 | 53 | 0 | **1.000** |
| `rugpull` | 67 | 0 | 67 | **0.000** | 59 | 8 | **0.881** |

### 4.3.1 Rug-Pull Detection

The baseline validator achieves zero recall on rug-pull sessions — not one of the 67 rug-pull sessions in the test set is flagged. This result is deterministic rather than statistical: as established in Chapter 3, a rug-pull by definition registers with a clean description, producing a registration-time keyword-hit count of zero. The baseline validator's decision rule (`reg_suspicious_keyword_hits >= 1`) therefore assigns a negative prediction to every rug-pull session regardless of the session count, the description it later adopts, or the timing of the mutation. No tuning of the keyword list or detection threshold can alter this outcome while the validator remains a registration-time check.

The ML detector flags 59 of 67 rug-pull sessions, achieving 88.1% recall. All 8 false negatives are rug-pull sessions of the stealthy subtype introduced by the noise model: sessions in which the attacker mutated the description and subsequently reverted it before the metadata snapshot was recorded. In the feature space these sessions are identical to benign sessions — the same description length, the same entropy, zero keyword hits, and `description_changed_after_registration = 0` — and no feature-based point-in-time detector can distinguish them from a genuine benign session on the basis of a single snapshot. The 8 false negatives are therefore a theoretically motivated bound on recall rather than a failure of the model, and are discussed further in Chapter 5.

### 4.3.2 Poisoned Session Detection

The baseline achieves 75.5% recall on poisoned sessions (40 of 53 detected, 13 missed). The 13 false negatives correspond to poisoned sessions generated with either a short injection fragment (a terse directive of 20–50 characters from a pool of phrases that do not appear in the suspicious-keyword list) or a deliberately evasive fragment that also avoids the keyword list. Both categories were introduced by the noise model specifically to simulate adversaries who are aware that keyword-based filters exist. The baseline's recall is therefore constrained by the completeness of the keyword list — a limitation that is inherent to static rule-based detection and improves only as the keyword vocabulary is extended.

The ML detector achieves 100% recall on poisoned sessions: all 53 poisoned test sessions are correctly flagged. Rather than relying on the presence of specific keyword strings, the model is able to exploit correlated signals — the description-length increase caused by appending any fragment, the entropy shift, and the interaction between registration-length and call-length — to identify injected descriptions even when the injection text itself does not trigger the keyword list.

---

## 4.4 Feature Importance Analysis

Table 4.3 reports the feature importance scores from the trained GradientBoostingClassifier, measured as the cumulative reduction in impurity attributable to each feature across all trees in the ensemble. Importances sum to 1.0.

**Table 4.3: Feature importance scores (GradientBoostingClassifier)**

| Feature | Importance | Observable by baseline? |
|---|---|---|
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

Three observations from Table 4.3 are directly relevant to the research question.

**First**, the two most important features — `call_description_length` (54.5%) and `call_suspicious_keyword_hits` (34.0%) — are both call-time features that the baseline validator cannot observe. Together they account for 88.5% of the model's total impurity reduction. The baseline's single most important observable feature, `reg_suspicious_keyword_hits`, contributes only 0.3% of the model's information gain. This confirms that the ML detector's advantage over the baseline is not incidental but is grounded in access to features that are structurally unavailable to registration-time checks.

**Second**, the four registration-time features available to the baseline — `reg_description_length`, `reg_description_entropy`, `reg_suspicious_keyword_hits`, and `num_schema_fields` — account for a combined 3.1% of the model's importance. This is consistent with the expectation that registration metadata alone is a weak discriminator for attack detection: an attacker who registers with a clean description provides no registration-time signal, and the numeric features (`reg_description_length`, `reg_description_entropy`) are not informative without a call-time counterpart to compare against.

**Third**, `description_changed_after_registration` has a feature importance of effectively zero, despite being a perfect predictor of the non-stealthy rug-pull class in isolation. In a GBT ensemble, a feature's importance is zero only if the model never selects it as a splitting criterion. This occurs when other features in combination already provide a superior split at every node in the tree construction. The zero importance of `description_changed_after_registration` indicates that the classifier achieves equivalent discrimination by using call-time length and keyword features, which subsume the information this binary flag provides. This is a useful calibration check: the model is not relying on a single binary rule — the problem that motivated the noise model in the first place — but on a combination of graded continuous features.

---

## 4.5 Summary

The results answer the research question as follows. Machine-learning-based anomaly detection of tool-call metadata — specifically, the metadata features observable after tool registration rather than only at it — substantially improves detection of tool-poisoning attacks in MCP-based agentic systems compared with an existing schema-validation defence. The improvement is most pronounced for the rug-pull attack class, where the baseline achieves 0% recall by structural necessity and the ML detector achieves 88.1% recall, identifying attacks that no registration-time defence can see by definition.

The residual 11.9% false-negative rate on rug-pulls is attributable entirely to the stealthy subtype, in which the attack description is reverted before the metadata snapshot. This rate is not a failure of the GBT model but a hard bound set by the information available in a single-point-in-time feature set: no classifier operating on these features, regardless of architecture or hyperparameters, can do better. The implications of this bound for the deployment design of a real-world detector — specifically, the requirement for continuous rather than point-in-time monitoring — are discussed in Chapter 5.

The feature importance analysis confirms that the ML detector's advantage is mechanistically grounded in access to call-time features that are structurally unavailable to the baseline, rather than in any incidental property of the synthetic corpus. Features observable only after tool registration account for 96.9% of the model's total discriminative information, versus 3.1% for the registration-time features that the baseline has access to.
