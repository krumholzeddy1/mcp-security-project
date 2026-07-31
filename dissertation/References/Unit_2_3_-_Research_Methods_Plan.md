# Unit 2.3 — Research Methods: Applying This to the Dissertation

*Applied to: Detecting Tool-Poisoning Attacks in MCP Agentic Systems Using Machine-Learning-Based Anomaly Detection*

## What the deck actually adds that the proposal doesn't have yet

The proposal already has a research question and a rough plan (testbed → corpus → model → evaluation). What it doesn't have, and what this unit is asking for, is the formal research-design vocabulary that makes a methodology chapter defensible: a stated philosophy, explicitly named independent/dependent variables, and controlled variables named on purpose rather than left implicit. Below is each concept from the deck, applied directly.

## 1. Research philosophy — state it, don't leave it implied

The deck offers three: positivism, interpretivism, pragmatism.

This project is **positivist**: it treats detection accuracy as an objective, measurable outcome (precision/recall/F1), makes no claim about human perception or lived experience, and is falsifiable — the ML detector could underperform the baseline, and that would be a valid result, not a failed project. This is worth one explicit sentence in the methodology chapter, because it also justifies a decision already made back in Unit 1.2: interpretivist methods (interviews with SOC analysts, perception studies) were considered and dropped, not overlooked — partly for feasibility/ethics reasons already documented, but also because they answer a different kind of question than the one being asked here. Naming this explicitly turns a scope decision into a methodological justification.

**Add to dissertation:** one paragraph in the methodology chapter stating the positivist stance and explicitly noting interpretivist alternatives were considered and ruled out, with reference back to the Unit 1.2 feasibility screening.

## 2. Quantitative structure — use the deck's own template properly

Slide 10 gives an exact template: Independent Variable → Dependent Variable → Example Experiment → Compare → Evaluate. The current proposal doesn't use this structure explicitly. It should:

| Element | Current proposal (implicit) | Should state explicitly |
|---|---|---|
| Independent variable | "the detection method" (vaguely) | **Detection method**, with defined levels: {baseline schema validator, ML anomaly detector} |
| Dependent variable | "how well it detects attacks" | **Detection performance**: precision, recall, F1 — measured per attack class (poisoned, rug-pull), not just overall |
| Example research question | the RQ as written | "Which detection method — schema validation or ML-based anomaly detection — better identifies tool-poisoning and rug-pull attacks in MCP tool-call metadata?" |
| Compare | one ML model vs. baseline | See Section 3 below — this is worth widening |
| Evaluate | accuracy implied | Precision, recall, F1, **per class**, not collapsed into one overall figure |

## 3. Strengthen the "Compare" step — don't compare only one algorithm

The deck's own worked example (slide 10) compares three algorithms (Random Forest, SVM, XGBoost) against a baseline, not one. The current build only trains a single Gradient Boosting model. This is a real gap worth closing before the evaluation chapter is written, not after:

- Add Logistic Regression (simple linear baseline within the ML side itself) and Random Forest alongside Gradient Boosting.
- This turns the independent variable "detection method" into three or four levels instead of two, which is a stronger, more defensible experimental design and directly mirrors the deck's own template.
- It also produces a naturally interesting result either way: if all three ML methods beat the baseline similarly, that's evidence the *category* of approach (behavioural/metadata-based) is what matters, not the specific algorithm — a more robust finding than "one model happened to work."

## 4. Name the controlled variables — this is the deck's sharpest warning

Slide 9's example (pin down email language before comparing classifiers) is a direct warning: an unpinned variable can invalidate the whole comparison. Applied here, several variables need to be stated as deliberately controlled, not left implicit:

- **Corpus generation parameters** (random seed, class balance, tool catalog) must be identical across every method being compared — already true in the current code (all methods run against the same `data/corpus.csv` and the same train/test split), but this needs to be *stated* as a controlled variable in the methodology chapter, not just be true in the code.
- **Class balance (200/200/200)** is currently a controlled variable but an unrealistic one — real MCP traffic is overwhelmingly benign. This should be named explicitly as a deliberate simplification for this experiment, with a stated follow-up (re-run under a skewed class balance, e.g. 90/5/5) as a robustness check, not a hidden limitation discovered later.
- **Keyword design in the synthetic corpus** is currently a confound, not a controlled variable: every attack contains an unambiguous keyword, which may be doing most of the separating work rather than the modelling approach itself. This needs either (a) an explicit acknowledgement as a limitation, or (b) a second corpus variant with subtler, non-keyword-based attacks, so the experiment can show detection still works when the obvious signal is removed. Given the timeline, (a) now with (b) flagged as future work is the realistic choice — but it must be named, not left implicit.

## 5. State a formal hypothesis

Positivist, quantitative research is typically framed as testable hypotheses, which the proposal doesn't currently state explicitly:

- **H0 (null):** There is no difference in detection recall between the schema-validation baseline and ML-based anomaly detection methods for tool-poisoning and rug-pull attacks.
- **H1 (alternative):** ML-based anomaly detection methods achieve higher recall than the schema-validation baseline, particularly for rug-pull attacks that occur after registration.

Stating this explicitly gives the evaluation chapter a clean structure: report the metrics, then state whether H0 is rejected, rather than just describing numbers.

## 6. Updated methodology chapter skeleton

Suggested structure, pulling all of the above together:

1. **Research philosophy** — positivist; interpretivist alternatives considered and ruled out (cross-reference Unit 1.2).
2. **Research design** — quantitative, comparative experiment.
3. **Variables** — IV: detection method (baseline, Logistic Regression, Random Forest, Gradient Boosting); DV: precision/recall/F1 per attack class.
4. **Controlled variables** — corpus generation parameters, train/test split, random seed, tool catalog (all held constant across methods being compared).
5. **Hypotheses** — H0/H1 as above.
6. **Data source** — synthetic corpus, with explicit justification (Unit 1.2/1.4) and explicit limitation (keyword-based separability, class balance).
7. **Analysis method** — precision/recall/F1 comparison, per-class breakdown, feature importance inspection for interpretability.

## What this changes in the actual build

Two concrete code changes fall out of this, both small:
- Add two more model options to `detection/train_model.py` (Logistic Regression, Random Forest) so the comparison in `evaluation/evaluate.py` covers three ML methods against the baseline, not one.
- Add a second evaluation run using a skewed class balance (e.g. regenerate the corpus at 90% benign / 5% poisoned / 5% rug-pull) as a robustness check, reported alongside the balanced result rather than replacing it.

Both are small, contained changes — they strengthen the experimental design considerably without threatening the 13-week timeline.
