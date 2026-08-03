# Chapter 5: Implementation

## 5.1 Overview

This chapter documents the implementation of the pipeline described in Chapter 4, with particular attention to the three substantive problems that arose during development. Each is worth recording both as evidence of methodological honesty and because the corrections each required produced design changes that directly improved the validity of the results.

The pipeline is implemented in Python 3.13.5 across four independently runnable modules, a shared data model, a demonstration server, and a six-test smoke suite.

## 5.2 The Baseline Feature Leakage Bug

The first significant problem was a bug in the initial implementation of `baseline/schema_validator.py`. The baseline is designed to represent a registration-time schema validator — a defender who reads tool metadata at registration and flags sessions containing suspicious keywords. The detector should therefore read `reg_suspicious_keyword_hits` (the keyword count computed from the description at the point of registration). The initial implementation read `call_suspicious_keyword_hits` instead.

The effect on results is not merely a small accuracy error: it silently removes the baseline's structural blind spot. `call_suspicious_keyword_hits` is elevated for rug-pull sessions mid-session, so a validator using that field has access to post-registration information that a real registration-time validator cannot see. The baseline would therefore show some rug-pull recall — not because registration-time detection works, but because the implementation was cheating. Any comparison against an ML detector using the same feature would be meaningless.

The bug was identified when the initial evaluation results showed an unexpectedly non-zero rug-pull recall for the baseline. On identifying the discrepancy, the correct field was substituted and the pipeline re-run. A regression test (`test_baseline_misses_majority_of_rugpulls`) was added to `tests/test_pipeline.py` immediately after the fix. The test verifies programmatically that the baseline misses at least 70% of rug-pull sessions, which would fail if the implementation were ever changed back to using call-time features.

The episode illustrates the value of the structural invariant approach to testing: the expected rug-pull miss rate is known analytically before any data is generated, and a test that encodes that invariant catches implementation errors that a purely accuracy-focused evaluation would miss.

## 5.3 The Corpus Separability Problem

The second problem emerged at the end of the first full pipeline run: the three-class classifier achieved near-perfect accuracy (F1 > 0.99) on the initial corpus. While this appeared to be a positive result, it was recognised as a threat to validity rather than a finding. A classifier that perfectly separates a training corpus is not necessarily learning generalisable attack patterns; it may be exploiting arbitrary correlations introduced by the generation procedure itself.

Inspection of the initial corpus revealed two sources of trivial separability. First, benign sessions were generated with a uniform description-length distribution, while poisoned sessions always contained appended fragments of a fixed length range, making the description-length feature a near-perfect discriminator. Second, rug-pull sessions always and only changed their descriptions at the point of the first call, making `description_changed_after_registration` a binary flag sufficient to achieve 100% rug-pull recall without access to any other feature.

A noise model was designed and implemented to address this (documented in full in Appendix G). The mechanisms introduce accidental keyword hits in legitimate descriptions, benign mid-session description updates, evasive injection fragments that bypass the keyword list, and stealthy rug-pulls that revert before the monitoring snapshot. The noise rates were calibrated so the balanced-corpus GBT achieved F1 in the range 0.92–0.96 — measurably better than baseline but below the ceiling that signals trivial separability. Both properties are corpus artefacts rather than properties of real attacks.

## 5.4 Zero Importance of the Description-Change Flag

The third observation — not a bug, but an unexpected result that required explanation — concerns `description_changed_after_registration`. As noted in Chapter 6 (§6.5.2), this feature has approximately zero importance in the trained GBT despite being a logically strong indicator of rug-pull activity. The feature is 1 for 90% of rug-pull sessions and 0 for all poisoned sessions.

The explanation is that the call-time length and keyword features are superior splits at every node. Wherever `description_changed_after_registration` would identify a rug-pull session, `call_suspicious_keyword_hits` and `call_description_length` already do so more reliably because they carry continuous information rather than a binary flag. The model finds no point at which adding the binary split improves on the continuous split already available.

## 5.5 Testing Strategy

The test suite (`tests/test_pipeline.py`) contains six smoke tests. Five test structural properties of the generated corpus that are known analytically from the noise model and attack class definitions; one (`test_baseline_misses_majority_of_rugpulls`) tests the implementation of the baseline validator. The tests do not evaluate classifier accuracy — accuracy depends on the random seed and the noise rates, and a test against a specific accuracy value would produce a brittle test that breaks on any legitimate pipeline change. Instead, the tests verify the invariants that must hold regardless of corpus random variation: that all three classes are present, that the noise rates produce the expected approximate proportions, and that the baseline's structural blind spot is preserved in the implementation.
