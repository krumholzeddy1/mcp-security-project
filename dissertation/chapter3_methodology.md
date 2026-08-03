# Chapter 3: Methodology

## 3.1 Research Design Overview

### 3.1.1 Research Philosophy

This study adopts a **positivist** research philosophy: knowledge is produced through systematic measurement, controlled experimentation, and falsifiable hypothesis testing that can be verified by independent replication (Saunders, Lewis and Thornhill, 2019). The research question is empirical and quantitative, answered by metrics on a held-out test set, with every variable precisely defined before measurement begins.

### 3.1.2 Hypotheses and Variables

**H₀ (null hypothesis):** A schema-validator that inspects tool metadata at registration time will achieve equivalent rug-pull attack recall to an ML detector trained on session-level metadata features.

**H₁ (alternative hypothesis):** An ML detector trained on session-level metadata features will achieve measurably higher rug-pull attack recall than a registration-time schema validator, demonstrating that the metadata observable only after registration contains signal sufficient to detect attacks the baseline structurally cannot see.

The independent variable is the **detection method** — schema-validator baseline versus ML anomaly detector. The dependent variable is **per-class recall on the held-out test set**, specifically rug-pull recall, because that is the class the baseline is structurally incapable of detecting. Controlled variables include corpus composition, feature set, test split, and evaluation metrics — all identical for both methods.

### 3.1.3 Overall Design

An ML-based anomaly detector and a representative rule-based baseline are evaluated against a controlled synthetic dataset of MCP tool-call sessions. The corpus is synthetic because no publicly labelled dataset of real MCP tool-poisoning attacks exists and capturing live data would require third-party access outside the project's ethical boundary.

---

## 3.2 Testbed Architecture

The experimental environment consists of three independent components, all executed in a locally isolated Python environment with no external network access. The five tools in the catalogue (`get_weather`, `search_docs`, `create_ticket`, `send_notification`, `lookup_account`) — including their parameter schemas and base descriptions — are documented in Appendix E.

**MCP server (`server/testbed_server.py`).** A FastMCP server exposes the five tools over stdio transport for manual demonstration and supervisor inspection only; the automated pipeline does not require it to be running.

**MCP client (`client/testbed_client.py`).** An async MCP client for demonstration only, not part of the training or evaluation pipeline.

**Detection pipeline.** The four pipeline modules (`corpus/`, `baseline/`, `detection/`, `evaluation/`) form a reproducible, sequentially executed pipeline that generates data, trains the model, and produces evaluation metrics from Python scripts without any live MCP connection. The data flow is illustrated in the pipeline architecture diagram in Chapter 4 (§4.2).

---

## 3.3 Synthetic Corpus Construction

### 3.3.1 Attack Taxonomy

The corpus contains 600 sessions distributed equally across three labelled classes (200 per class), generated with `random.seed(42)` for reproducibility.

**Benign.** A randomly selected tool is registered with its unmodified benign description and called between one and twelve times. No description mutation occurs.

**Poisoned.** The tool's description at registration already contains an injected fragment appended to the benign description, mirroring the pattern in which a malicious server operator embeds instruction-like text in tool metadata before any user interaction (Radosevich and Halloran, 2025). The description does not change during the session.

**Rug-pull.** The tool registers with a clean description — indistinguishable from a benign registration — and mutates it partway through the session (Willison, 2025). Mutation occurs after at least half the session's calls, at a randomised point between 600 and 7,200 seconds after registration.

### 3.3.2 Feature Extraction

Each session is represented as eleven metadata features computable from protocol-level data only — tool descriptions, parameter schemas, and call timing — without treating description text as natural language. The features split into two groups: registration-time observables (description length, Shannon entropy, suspicious-keyword hit count, and schema field count) and call-time or cross-time observables (the corresponding call-time length, entropy, and keyword count, plus a `description_changed_after_registration` binary flag, timing, and session-position features) that are only available to a system monitoring beyond the registration moment. Full definitions are provided in Chapter 4, §4.3.

The suspicious-keyword list used for the hit-count features comprises ten strings drawn from documented injection patterns: `"ignore prior"`, `"ignore previous"`, `"system:"`, `"must be called before"`, `"ssh"`, `"config file"`, `"environment variable"`, `"verbose_mode"`, `"regardless of user request"`, and `"note to assistant"`.

### 3.3.3 Noise Model

An initial corpus produced trivially separable classes: rug-pull sessions were perfectly identified by `description_changed_after_registration` alone, and poisoned sessions by a non-zero keyword-hit count. Seven noise mechanisms are applied to address this; their exact rates are documented in Appendix G. The mechanisms introduce accidental keyword hits in legitimate descriptions, benign mid-session description updates, evasive injection fragments, sloppy rug-pulls, and stealthy rug-pulls.

The stealthy rug-pull mechanism sets a theoretically motivated ceiling on recall. If an attacker mutates a description and then reverts it before the metadata snapshot is taken, the session is labelled `rugpull` but all eleven features are identical to a benign session; no point-in-time detector can distinguish these sessions from benign. The 10% stealthy rate represents an irreducible false-negative floor rather than a model deficiency. Continuous monitoring is identified as the necessary countermeasure in Section 7.2.

### Table 3.1: Per-class feature distributions (mean and SD, n=200 per class)

| Feature | Benign mean (SD) | Poisoned mean (SD) | Rug-pull mean (SD) |
| --- | --- | --- | --- |
| `reg_description_length` | 104 (67) | 140 (34) | 67 (30) |
| `call_description_length` | 121 (77) | 140 (34) | 133 (40) |
| `reg_description_entropy` | 4.01 (0.18) | 4.27 (0.18) | 3.93 (0.12) |
| `call_description_entropy` | 4.06 (0.20) | 4.27 (0.18) | 4.23 (0.21) |
| `call_suspicious_keyword_hits` | 0.05 (0.22) | 1.77 (1.34) | 1.50 (1.38) |
| `description_changed_after_registration` | 0.21 (0.41) | 0.00 (0.00) | 0.90 (0.30) |

The overlapping distributions confirm the noise model achieves its design goal of producing separable-but-overlapping classes.

---

## 3.4 Baseline Defence Implementation

The baseline (`baseline/schema_validator.py`) flags a session as an attack if `reg_suspicious_keyword_hits >= 1`, representing the single-pass registration-time check described in the literature (Bhatt et al., 2025; Hou et al., 2025).

The structural limitation follows directly from the rug-pull attack class. Rug-pull sessions register with a clean description, so `reg_suspicious_keyword_hits = 0` for the non-sloppy majority, and the baseline assigns a negative prediction to every such session regardless of what the description later becomes. This is not a deficiency in any keyword list or threshold — it is a consequence of checking trust once rather than continuously. Even a perfect oracle that could identify every injection keyword would fail to catch a rug-pull that uses no keywords at registration, because the attack occurs after the check has already been completed.

---

## 3.5 Machine-Learning Anomaly Detector

Three classifier families were trained on the same 70/30 stratified split; model selection rationale and training details are documented in Chapter 4, §4.4.

---

## 3.6 Evaluation Protocol

### 3.6.1 Primary Evaluation — Balanced Corpus

Both the baseline and all three ML detectors are evaluated on the same 180-session held-out test set, reporting precision, recall, and F1. Per-class recall is the headline metric for H₁: aggregating across classes would allow high poisoned-class recall to mask a rug-pull recall of zero, which is precisely the pattern the baseline exhibits. Both attack classes are reported separately because their observability properties are fundamentally different.

### 3.6.2 Robustness Check — Skewed Class Balance

A second evaluation applies the primary GBT model (trained on the balanced corpus) to a skewed corpus of 600 sessions (540 benign, 30 poisoned, 30 rug-pull) without retraining, testing whether detection capability generalises under class imbalance. The expected precision drop is reported in operational terms — false positives per benign session — because the cost is analyst workload rather than a bare metric number. No cross-validation is performed; the synthetic-data limitation is addressed in Section 7.2.

---

## 3.7 Ethical Considerations

All experimental work was conducted in an isolated locally hosted Python environment with no external network access. No tool-poisoning scenarios were tested against external or production MCP servers. The poison fragments are abstracted from documented attack patterns; they are not a ready-to-use exploit toolkit. All synthetic data will be retained only for the project duration, consistent with UK GDPR data-minimisation principles (European Parliament, 2024). All work complies with the Computer Misuse Act 1990 (HM Government, 1990) and the NCSC (2023) guidelines for secure AI system development.

---

## 3.8 Data Sources and Quality

### 3.8.1 Data Quality Assessment

The primary dataset is assessed against five quality criteria commonly applied to research datasets (Saunders, Lewis and Thornhill, 2019); the full assessment is reproduced in Appendix H. In summary: the corpus satisfies validity, reliability, accuracy, and completeness by construction — the fixed seed and deterministic feature computation ensure byte-for-byte reproducibility with no missing values. The criterion the dataset does not fully satisfy is **representativeness**: the synthetic corpus represents a model of real MCP deployments, not a sample from one, and the degree to which the learned detector generalises to real deployments is unknown.

The complete source code, pinned environment specification, verbatim pipeline console output, full test suite output, and a testbed demonstration are provided in Appendices A–E.
