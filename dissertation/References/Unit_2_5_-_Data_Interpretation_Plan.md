# Unit 2.5 — Data Interpretation: Applying This to the Dissertation

*Applied to: Detecting Tool-Poisoning Attacks in MCP Agentic Systems Using Machine-Learning-Based Anomaly Detection*

## The core distinction this deck is making

Analysis is what the current evaluation output already produces: a table of precision/recall/F1 numbers. Interpretation is the step that hasn't been done yet — saying what those numbers mean, why they came out that way, how they relate to the literature already reviewed, and what should actually be prioritised as a result. The deck's own line is the clearest summary: **analysis tells us what happened, interpretation tells us why it matters.** This is a real gap in the current write-up, not a stylistic nice-to-have — the evaluation chapter as it stands is analysis without interpretation.

## 1. The single most directly applicable slide: don't pick the model with the highest headline number

Slide 6 describes almost exactly this project's situation: comparing multiple models on accuracy/precision/recall, and warning against the naive conclusion "the one with the highest accuracy is best." Its own example makes the point with a cyber-attack-detection framing — if missing an attack is costly, recall matters more than accuracy, and the model with the best accuracy is not automatically the right choice.

This maps directly onto the actual results already produced:

| Method | Precision | Recall | F1 |
|---|---|---|---|
| Baseline schema validator | 1.00 | 0.51 | 0.67 |
| ML anomaly detector | 1.00 | 1.00 | 1.00 |

**Poor interpretation (analysis dressed up as interpretation):** "The ML detector achieved higher recall than the baseline, so it is the better method."

**Good interpretation, following the deck's own worked example:** "Both methods achieve perfect precision, meaning neither produces false positives on this corpus — but precision alone would be a misleading basis for comparison here, since a validator that flags nothing at all would score similarly well on precision while missing every attack. Recall is the metric that matters for this research question, because a missed tool-poisoning or rug-pull attack is the costly failure mode, not a false alarm. On that metric, the baseline's overall recall of 0.51 conceals a sharper finding: its recall is 1.0 on poisoned tools but 0.0 on rug-pull attacks specifically — it does not partially miss rug-pulls, it misses all of them, by construction. This is the result the research question was actually testing for."

This is the single change that would most improve the evaluation chapter: report per-class recall as the headline finding, not overall accuracy or overall F1, and say explicitly why recall (and specifically per-class recall) is the right metric for this research question — mirroring the deck's own reasoning about attack detection.

## 2. Interpret in relation to the research question, explicitly, every time

Slide 4's structure: state the finding, then explicitly answer "how does this finding answer my research question?" The current results should be run through this template directly:

**Research question:** To what extent can machine-learning-based anomaly detection of tool-call metadata improve detection of tool-poisoning attacks compared with schema-validation defences?

**Finding:** The ML detector achieved 1.0 recall on rug-pull attacks; the baseline achieved 0.0.

**Interpretation (following the deck's template):** This finding directly answers the research question for the rug-pull attack class: metadata-based anomaly detection can detect an attack category that registration-time schema validation is structurally unable to detect at all, not just one it detects less well. This is a categorical difference, not a marginal improvement, which is a stronger answer to the research question than the tool-poisoning result (where the baseline already performs adequately, since poisoning is visible at registration).

Writing this out explicitly for each major finding — rather than assuming the reader will draw the connection from a table — is exactly what separates analysis from interpretation per this deck.

## 3. Compare every finding against the literature review, by name

Slide 5 is explicit: interpretation should never happen in isolation, and should say plainly whether a finding agrees or disagrees with prior work. Applied to this project's own literature (Unit 2.1):

- **Agreement:** "The baseline's complete failure to detect rug-pull attacks empirically confirms the mechanism Willison (2025) described only qualitatively — this dissertation provides the first quantitative demonstration that a registration-time validator cannot detect this attack class, supporting his account with measured evidence rather than a single illustrative write-up."
- **Testing an assumption, not just confirming it:** "The improvement in recall from applying anomaly-based detection supports the general pattern reported by Ahmed et al. (2025) in network intrusion detection — that anomaly-based methods catch what signature-based methods structurally miss — and extends that pattern, for the first time identified in this review, to MCP tool-call metadata specifically."
- **Where results should be checked against Bhatt et al. (2025):** since ETDI addresses containment rather than detection, the results here should be explicitly framed as complementary to that mitigation-focused work, not competing with it or superseding it.

Each of these ties a specific result back to a specific named source, which is what the deck means by never interpreting in isolation.

## 4. Apply the cybersecurity-specific framing from slide 7 to the per-class breakdown

Slide 7's vulnerability-scan example makes a point directly transferable here: don't just report a total count, prioritise by what actually matters operationally. Applied to this project's corpus composition and results:

**Poor interpretation:** "Of the 600 sessions in the test corpus, the model correctly classified nearly all of them."

**Good interpretation, following the deck's pattern:** "Although the overall dataset is balanced across three classes, the operationally significant distinction is not overall accuracy but the recall gap between attack types. Tool-poisoning attacks are already reasonably well-handled by existing schema-validation practice; rug-pull attacks are not handled at all by that same practice. It is this second, currently undetected category that should be prioritised in any discussion of practical impact, since it represents the attack type most likely to succeed against a real MCP deployment relying on current defences."

## 5. What to actually change in the dissertation write-up

This unit doesn't require new experiments — it requires rewriting how the existing (and forthcoming, wider) results are presented:

1. Lead the evaluation chapter with **per-class recall**, not overall accuracy or F1, and justify that metric choice explicitly using the same reasoning as slide 6.
2. For every result reported, add one sentence explicitly answering "how does this answer the research question," following the slide 4 template — don't leave that connection implicit.
3. For every result reported, add one sentence explicitly comparing it to a named source from the literature review, stating agreement, disagreement, or extension — following slide 5.
4. When the wider model comparison (Logistic Regression, Random Forest, Gradient Boosting) from the Unit 2.3 plan is run, resist the instinct to declare a single "winner" on accuracy — apply the same recall-first, per-class reasoning to that comparison as well.
5. When the skewed-class-balance robustness check (also from Unit 2.3) is run, interpret any precision drop explicitly in terms of real-world operational cost (more false alarms for a security team to triage) rather than reporting it as a bare number.
