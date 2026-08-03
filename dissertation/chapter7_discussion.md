# Chapter 7: Discussion and Limitations

## 7.1 Interpreting the Main Finding

The central finding of this study is that the registration-time schema-validator achieves **zero rug-pull recall** across all evaluation conditions, while all three ML detectors achieve rug-pull recall between 0.881 and 0.933. This is not a marginal improvement on a metric the baseline was already partially performing on; it is the detection of an attack category the baseline is structurally incapable of detecting at all. The improvement is therefore qualitative — a categorical difference in detection capability — rather than a quantitative improvement on a shared metric.

The baseline's zero recall on rug-pulls is not a consequence of a poorly chosen threshold or an incomplete keyword list — it is an unavoidable consequence of the defender's observation window ending at registration. Adding more keywords, tightening the detection rule, or switching to a more sophisticated rule-based classifier would not change this outcome, because the attack-relevant signal (the description mutation) occurs after the baseline has finished looking. The ML detector's 88.1% rug-pull recall is achieved by monitoring features only observable after registration: principally `call_description_length` (54.5% importance) and `call_suspicious_keyword_hits` (34.0%).

---

## 7.2 The Stealthy Rug-Pull Bound and the Case for Continuous Monitoring

The ML detector's 8 false negatives — all from the stealthy rug-pull subtype — represent a hard theoretical limit on what any point-in-time metadata detector can achieve. A stealthy rug-pull is a session in which the server mutates its tool description and subsequently reverts it before the metadata snapshot used for feature extraction is recorded. At the moment of feature extraction, the description has returned to its clean registration-time value; `description_changed_after_registration` is zero, `call_description_length` equals `reg_description_length`, and `call_suspicious_keyword_hits` is zero. Every feature value is identical to that of a genuine benign session. No classifier, regardless of architecture or training data, can distinguish these sessions from benign on the basis of the eleven features used in this study, because the sessions are literally identical in the feature space.

The stealthy rug-pull is not a hypothetical edge case. An attacker with server-side control can implement a revert-on-demand mechanism with minimal additional infrastructure: inject the poisoned description for a brief window during which the model's `tools/list` refresh would capture it, then revert. Any monitoring system that samples tool metadata at fixed intervals is vulnerable to attacks timed to fall between samples. This places a hard requirement on any detector intended to catch this subtype: the monitoring must be *continuous* rather than periodic, recording the description at every `tools/list` call and every tool invocation, rather than taking a single snapshot at a chosen checkpoint.

---

## 7.3 Limitations

**Synthetic corpus.** The primary limitation is that the evaluation corpus is entirely synthetic. The tool-poisoning class is supported by independently corroborated, empirically demonstrated exploits (Radosevich and Halloran, 2025; Invariant Labs, 2025). The rug-pull class rests on a single practitioner blog post (Willison, 2025) that has not been independently verified. The evaluation figures (F1 = 0.945 for ML, F1 = 0.488 for baseline) should be interpreted as illustrative of the relative capability difference rather than as precise estimates of real-world performance: the noise-model rates, tool descriptions, and injection patterns are design judgements rather than empirically calibrated values. A detector trained on this corpus may generalise poorly to real deployment environments without retraining. Ring et al. (2019) demonstrate that even within the network intrusion detection domain, detectors trained on one dataset generalise poorly to another; the problem is more acute when training data is synthetic. Additionally, real deployments may exhibit attack patterns not represented in the training data, including schema field name injection (noted by Radosevich and Halloran, 2025) and multi-tool coordinated attacks — the closed-world assumption inherent in any fixed training corpus.

**Feature set weaknesses.** The keyword-hit features depend on a fixed list; an adversary aware of the feature set can craft injection text that avoids all ten patterns. The dominance of `call_description_length` (54.5%) reflects corpus design — attacks append to descriptions — and would degrade against an attacker who replaces the description entirely. Extending the feature set to include schema field name entropy and mutation flags is necessary before real-world deployment.

---

## 7.4 Relationship to Existing Defences

The ML detector is best understood as a *complementary* layer rather than a replacement for existing defences. The baseline schema-validator captures attacks registered with obvious keywords at negligible overhead; removing it would be counterproductive. ETDI's OAuth-based scope binding limits what an injected tool can accomplish even when injection goes undetected, while the ML detector provides the signal needed to trigger remediation.

---

## 7.5 Project Journey and Supervisor Guidance

The original plan included an Agent2Agent (A2A) protocol testbed alongside MCP. After reviewing the initial testbed design, the supervisor questioned whether two protocols could be evaluated to sufficient depth within the project timeline. The MCP component — with its clearer attack taxonomy, reference implementation, and existing literature — offered a more tractable and defensible scope. A2A was removed and documented as future work (Section 8.4).

The second change was more substantive. An early pipeline run produced GBT F1 > 0.99 on the balanced corpus. The supervisor's feedback was direct: results at that level on a synthetic dataset require either a published justification or a more credible corpus design, because near-perfect separability on synthetic data is a sign of corpus artefacts rather than genuine detection capability. This prompted the noise model redesign documented in Chapter 3 (§3.3.3) and Chapter 5 (§5.3). The redesigned corpus yields GBT F1 = 0.945 — demonstrably better than the baseline (0.488) while reflecting the irreducible false-negative floor imposed by stealthy attacks. That floor itself became a finding rather than an embarrassment.

A third decision — to train three classifier families instead of one — responded to a supervisor query about algorithm specificity: if only Gradient Boosting was tested, the rug-pull detection result could be attributed to the boosting mechanism rather than the feature set. Adding Logistic Regression and Random Forest, and showing that all three achieve rug-pull recall between 0.881 and 0.896, produced the mechanistic argument that is now central to the contribution claim.

---

## 7.6 Summary

The ML detector's advantage is mechanistically grounded in post-registration observability. The residual false-negative rate on rug-pulls is a theoretically motivated bound reducible only by continuous monitoring. The results should not be interpreted as real-world performance estimates without domain-specific retraining.
