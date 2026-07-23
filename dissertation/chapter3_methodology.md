# Chapter 3: Methodology

## 3.1 Research Design Overview

This study adopts a quantitative, experimental design in which a machine-learning-based anomaly detector and a representative rule-based baseline defence are evaluated against a controlled synthetic dataset of Model Context Protocol (MCP) tool-call sessions. The choice of a fully synthetic corpus — rather than a live dataset captured from production MCP deployments — is deliberate and follows from three constraints: (i) no large-scale, publicly labelled dataset of real MCP tool-poisoning attacks exists at the time of writing; (ii) capturing data from live deployments would require third-party access that falls outside the ethical boundary of this project; and (iii) a synthetic corpus with a documented generation process and fixed random seed provides exact reproducibility, which is a prerequisite for a fair comparison between two detection methods.

The threat model covers two documented attack variants drawn from the literature: injection at the point of tool registration ("poisoned" sessions) and delayed injection after the tool has been trusted ("rug-pull" sessions). Both were identified by Invariant Labs (2025) and Radosevich and Halloran (2025) as actively exploitable in current MCP deployments. The baseline defence modelled is a schema-validator that inspects tool metadata at registration time, representative of the defences described by Bhatt, Narajala, and Habler (2025). The ML detector extends the observable window to include call-time metadata and description-change patterns, operationalising the gap identified in the research question.

---

## 3.2 Testbed Architecture

The experimental environment consists of three independent components, all executed in a locally isolated Python environment with no external network access.

**MCP server (`server/testbed_server.py`).** A FastMCP server exposes five synthetic tools (`get_weather`, `search_docs`, `create_ticket`, `send_notification`, `lookup_account`) over stdio transport. Each tool carries a benign description and, for corpus-generation purposes, a set of associated poison fragments — instruction-like strings that mirror the pattern documented in the literature (Invariant Labs, 2025) but are abstracted enough to constitute training signal rather than a working exploit. The server is used for manual demonstration and supervisor inspection; the automated pipeline does not require it to be running.

**MCP client (`client/testbed_client.py`).** An async MCP client based on the reference `ClientSession` implementation connects to the testbed server, lists exposed tools, and performs sample invocations. Like the server, this component is used for demonstration only and is not part of the training or evaluation pipeline.

**Detection pipeline.** The four pipeline modules (`corpus/`, `baseline/`, `detection/`, `evaluation/`) form a reproducible, sequentially executed pipeline that generates data, trains the model, and produces evaluation metrics entirely from Python scripts without any live MCP connection.

---

## 3.3 Synthetic Corpus Construction

### 3.3.1 Attack Taxonomy

The corpus contains 600 sessions distributed equally across three labelled classes (200 per class), generated with `random.seed(42)` for reproducibility.

**Benign.** A randomly selected tool from the five-tool catalogue is registered with its unmodified benign description. The tool is called between one and twelve times during the session. No description mutation occurs.

**Poisoned.** The tool's description at registration already contains an injected fragment appended to the benign description. This mirrors the pattern in which a malicious server operator embeds instruction-like text in tool metadata before any user interacts with the tool (Radosevich and Halloran, 2025). The description does not change during the session — both registration-time and call-time metadata contain the injection.

**Rug-pull.** The tool registers with a clean, unmodified description — indistinguishable from a benign registration — and then mutates its description partway through the session. This is the delayed-attack pattern described by Willison (2025), in which the server passes initial inspection and only injects malicious content after it has been trusted. The mutation is modelled as occurring after at least half the session's calls have completed, at a randomised point between 600 and 7,200 seconds after registration, reflecting the realistic operational window a compromised server might exploit.

### 3.3.2 Feature Extraction

Each session is represented as a single row of eleven metadata features. These features were chosen to be computable entirely from protocol-level data — tool names, descriptions, parameter schemas, and call timing — without any access to model inputs or outputs, and without treating description text as a natural-language artefact to be classified by content. This scope decision follows directly from the research question, which asks whether *metadata and description-change patterns* (rather than content analysis) can improve detection.

| Feature | Description |
|---|---|
| `num_schema_fields` | Number of declared parameter fields in the tool schema |
| `reg_description_length` | Character length of the description at registration time |
| `reg_description_entropy` | Shannon character entropy of the registration description |
| `reg_suspicious_keyword_hits` | Count of known injection-pattern keywords present at registration |
| `call_description_length` | Character length of the description when the monitored call is made |
| `call_description_entropy` | Shannon character entropy of the call-time description |
| `call_suspicious_keyword_hits` | Count of known injection-pattern keywords present at call time |
| `description_changed_after_registration` | Binary flag: 1 if the description at call time differs from registration |
| `time_since_registration_s` | Seconds elapsed between tool registration and the monitored call |
| `call_position_in_session` | Ordinal position of the monitored call within the session |
| `num_calls_in_session` | Total number of tool calls made during the session |

The registration-time features (`reg_*`) constitute everything a registration-time schema validator can observe. The call-time and change features (`call_*`, `description_changed_after_registration`, `time_since_registration_s`, `call_position_in_session`) are only observable by a system that monitors tool behaviour after the session is established — the category the ML detector belongs to.

The suspicious-keyword list used for `reg_suspicious_keyword_hits` and `call_suspicious_keyword_hits` comprises ten strings drawn from the injection patterns documented in the literature: `"ignore prior"`, `"ignore previous"`, `"system:"`, `"must be called before"`, `"ssh"`, `"config file"`, `"environment variable"`, `"verbose_mode"`, `"regardless of user request"`, and `"note to assistant"`.

### 3.3.3 Noise Model

An initial version of the corpus produced trivially separable classes: rug-pull sessions were perfectly identified by a single binary flag (`description_changed_after_registration`), and poisoned sessions by a non-zero keyword-hit count. This would yield evaluation results that reflect the corpus design rather than any genuine detection capability, producing an unreliable basis for the research question.

To address this, five noise mechanisms are applied during corpus generation. Their rates are set as documented constants in the source (`corpus/generate_corpus.py`) to support reproducibility:

| Mechanism | Rate | Effect |
|---|---|---|
| Benign with accidental keyword hit | 8% | Legitimate DevOps/sysadmin tool descriptions that contain terminology matching the keyword list; introduces false-positive pressure |
| Benign with legitimate description update | 20% | Tool description updated mid-session for a non-malicious reason (version bump, clarification); creates benign sessions where `description_changed = 1` |
| Benign with verbose description | 35% | Legitimately lengthy tool documentation (130–250 characters); blurs the length boundary between benign and attack sessions |
| Poisoned/rug-pull with evasive fragment | 12–15% | Injected text uses phrasing outside the keyword list, simulating adversaries aware of keyword-based filters |
| Poisoned/rug-pull with short fragment | 20–25% | Terse injection directives (20–50 characters) that minimise the description-length delta, blurring length-based discrimination |
| Stealthy rug-pull | 10% | Attacker mutates the description but reverts it before the metadata snapshot is taken; the session is ground-truth labelled as `rugpull` but all features are identical to a benign session |

The stealthy rug-pull mechanism warrants additional discussion. It represents a fundamental limitation of point-in-time metadata sampling: if an attacker can control when the description is visible and ensures it appears clean at the moment of inspection, no feature-based detector operating on a single snapshot will identify the attack. These sessions are deliberately included in the `rugpull` class to bound the expected recall of any detector and to produce a theoretically motivated rather than artificially inflated false-negative rate. Continuous monitoring — capturing description state at every tool invocation rather than at a single checkpoint — is identified as the necessary countermeasure in Section 5.3.

After applying the noise model, the class distributions of all eleven features overlap substantially, and the classifier must integrate evidence across multiple features to make predictions. This is verified by inspecting the trained model's feature importance scores (Section 4.2).

---

## 3.4 Baseline Defence Implementation

The baseline is a schema validator (`baseline/schema_validator.py`) that inspects tool metadata at registration time and flags a session as an attack if the registration description contains one or more entries from the suspicious-keyword list — that is, if `reg_suspicious_keyword_hits >= 1`. This represents the category of defences in common operational use: a single-pass check at the point of trust establishment (Bhatt et al., 2025; Hou et al., 2025).

The structural limitation of this design follows directly from the rug-pull attack class. Rug-pull sessions register with a clean description (`reg_suspicious_keyword_hits = 0` for the non-sloppy majority), so the baseline validator assigns a flag value of zero to every such session regardless of what the description later becomes. This is not a deficiency in any particular keyword list or threshold; it is a consequence of checking trust once rather than continuously. Even a perfect oracle that could identify every injection keyword would fail to catch a rug-pull that uses no keywords at registration, because the attack occurs after the check has already been completed.

---

## 3.5 Machine-Learning Anomaly Detector

### 3.5.1 Model Selection

A `GradientBoostingClassifier` from scikit-learn (version 1.9.0) was selected as the detection model. Gradient-boosted trees were preferred over alternatives (logistic regression, random forests, neural networks) for three reasons specific to this project's constraints.

First, GBTs handle heterogeneous feature types — binary flags, counts, and continuous values appear in the eleven-feature set — without requiring normalisation or encoding transformations. Second, GBTs produce interpretable feature importance scores, which allow the relative contribution of registration-time versus call-time features to be measured directly, providing evidence relevant to the research question. Third, tree-based ensemble methods are robust to the moderate class imbalance introduced by the noise model and do not require hyperparameter tuning to produce competitive results within a 13-week project timeline.

Default hyperparameters were used (`n_estimators=100`, `max_depth=3`, `learning_rate=0.1`), consistent with the proposal's guidance to keep the model architecture simple and well-understood rather than risk overfitting a more complex architecture to the synthetic corpus.

### 3.5.2 Target Variable

The model is trained as a binary classifier. Sessions labelled `benign` in the corpus are assigned `is_attack = 0`; sessions labelled `poisoned` or `rugpull` are assigned `is_attack = 1`. This framing treats both attack types as the positive class, which is appropriate for an operational detector where the cost of a missed attack outweighs the cost of a false positive.

### 3.5.3 Training and Inference

The corpus is partitioned into a 70% training set and a 30% held-out test set using a stratified split (`random_state=42`) that preserves the three-class proportions within each partition. The model is trained on the 420 training rows and evaluated on the 180 test rows. The held-out test set is also used to evaluate the baseline validator, ensuring that both methods are compared on identical inputs.

The trained model is serialised to `data/detector_model.joblib` for inspection and demonstration purposes. Call-time features — including `description_changed_after_registration` and `call_suspicious_keyword_hits` — are present at inference time, reflecting a deployment context where the monitor has access to the full session metadata rather than only the registration snapshot.

---

## 3.6 Evaluation Protocol

Both the baseline and the ML detector are evaluated on the same 180-session held-out test set, with performance reported using three standard binary classification metrics computed by scikit-learn:

- **Precision** — of the sessions flagged as attacks, the proportion that are genuine attacks. High precision indicates few false positives.
- **Recall** — of the genuine attack sessions, the proportion that are flagged. High recall indicates few missed attacks.
- **F1 score** — the harmonic mean of precision and recall, providing a single summary measure that penalises imbalances between the two.

Overall recall is reported at two levels of granularity: aggregated across both attack classes, and decomposed by class (`poisoned` and `rugpull` separately). Class-level decomposition is necessary because the two attack types have fundamentally different observability properties: the baseline can in principle detect poisoned sessions but is structurally unable to detect rug-pulls. Aggregating the two would conceal the most important finding.

No cross-validation is performed. Given that both the corpus and the test split are generated with fixed random seeds and the model uses default hyperparameters without tuning, cross-validation would add computational cost without improving the validity of the comparison. The appropriate caveat — that synthetic-data evaluation overstates expected real-world performance — is addressed in the limitations discussion (Section 5.2).

---

## 3.7 Ethical Considerations

All experimental work was conducted within an isolated, locally hosted Python environment. No tool-poisoning scenarios were tested against external, third-party, or production MCP servers, in accordance with the ethics commitment made in the project proposal. No live language model was involved; the detection pipeline operates on metadata features computed from synthetic description strings, so no real model was subjected to injection attempts.

The poison fragments included in the corpus are abstracted from the documented attack patterns in the literature (Invariant Labs, 2025; Radosevich and Halloran, 2025). They are not intended to function as a working exploit against any deployed model; their role is to produce realistic feature values (description length, entropy, keyword hits) for training signal. No ready-to-use exploit toolkit is produced by or derivable from this project's artefacts.

All synthetic data was generated specifically for this project and will be retained only for the duration of the project, consistent with UK GDPR data-minimisation principles. No personal data is involved at any stage.
