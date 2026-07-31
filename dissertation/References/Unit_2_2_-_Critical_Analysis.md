# Unit 2.2 — Critical Analysis

*Applied to: Detecting Tool-Poisoning Attacks in MCP Agentic Systems Using Machine-Learning-Based Anomaly Detection*

## What "critical" means here

The deck's core distinction: descriptive says what happened, critical says why it matters, where it fails, and what should have been done differently. The test throughout this document is the deck's own line — "criticisms must be supported by evidence," not just asserted.

## 1. Turning descriptive lit-review statements into critical ones

The literature review (Unit 2.1) mostly *reports* what each source found. That's a necessary first layer, but on its own it's descriptive. Below is the same material pushed one level further, following the deck's descriptive → critical table.

| Descriptive (what the lit review currently says) | Critical (what it should also say) |
|---|---|
| Hou et al. (2025) identify that MCP has no re-validation point between layers. | This is a structural claim, not an empirical one — the paper characterises the architecture but doesn't measure how often that gap is actually exploited in the wild. The claim is plausible and matches the incident reports (Invariant Labs, Willison), but it's worth being honest that "structurally possible" and "commonly exploited" are different strengths of evidence. |
| Radosevich and Halloran (2025) and Invariant Labs (2025) documented working tool-poisoning exploits. | Both are proof-of-concept demonstrations, not incidence data. They show the attack *can* work, not how often it *does* work in production MCP deployments. The dissertation should not imply prevalence it hasn't measured. |
| Bhatt et al. (2025) propose OAuth-enhanced tool definitions as a mitigation. | Their own mitigation is registration-time, same as the practices it's meant to improve on — so it doesn't actually close the rug-pull gap it's cited next to. Worth stating explicitly that citing this paper as "current practice" is fair, but citing it as evidence the field has no answer to rug-pulls yet is stronger and more defensible. |
| The IDS literature shows anomaly-based detection catches things signature-based methods miss (Ahmed et al., 2025). | This finding is from a completely different application domain (network intrusion detection). The transfer to MCP tool-call metadata is an analogy, not a validated result — the dissertation is testing whether that analogy holds, not relying on it as already proven. This should be stated as the hypothesis it is, not a settled precedent. |

## 2. Questioning the sources (Who / What / Where / When / Why / How)

Applying the deck's six questions to the sources carrying the most weight in the argument:

**Willison (2025)** — the "rug pull" source
- Who: independent practitioner/blogger, well-regarded in the developer community, not an academic.
- What: describes a real, named attack pattern with technical detail; claim is plausible but self-published, not peer-reviewed.
- Where/When: published April 2025, very early in MCP's public life — the ecosystem has moved fast since, so specifics may already be dated even if the underlying pattern isn't.
- Why: appears to be genuine security disclosure, not commercially motivated (no product being sold in the post).
- How: no formal methodology section — it's a write-up, not a study. This is the weakest source methodologically in the whole review, and it's also the one the entire "rug pull" framing of the project rests on. That combination is worth acknowledging directly rather than leaving implicit.

**Invariant Labs (2025)** — vendor security notification
- Who: a security company with a commercial product in this exact space.
- What: documents a real exploit, but a vendor publishing a vulnerability in the category their product defends against has an incentive to frame the risk as more severe/widespread than an independent party might.
- How: technical write-up, not independently verified by a third party in the review.
- Judgement: still worth citing — the exploit is real and technically credible — but should be flagged as a source with a commercial interest, not treated as neutral in the same way as an academic paper.

**Ahmed et al. (2025)** — the IDS bridge citation
- Who/Where: peer-reviewed, published in Scientific Reports — the strongest source in the review methodologically.
- What: findings are from network intrusion detection, not agentic AI or MCP.
- Why this matters critically: this is the source doing the most argumentative work (it's the whole justification for trying ML at all) while being the most distantly related to the actual subject. The lit review should be explicit that this is a cross-domain inference, and that its plausibility, not its proof, is what's being borrowed.

## 3. Evaluating the method choices, not just describing them

Descriptive version: "Gradient boosting was chosen for the detector."

Critical version, following "evaluating options and which should be used, and why":

| Option | Why it was rejected or accepted |
|---|---|
| Logistic regression | Rejected — unlikely to capture interaction effects between features like time-since-registration and description-change; a fast baseline to sanity-check the pipeline, not a serious candidate for the final model. |
| Isolation Forest (unsupervised) | Arguably the more conceptually honest choice — the research question says "anomaly detection," and an unsupervised method doesn't need labelled attacks to work, which is closer to a real deployment where labelled attack examples won't exist. Not chosen because the synthetic corpus is fully labelled anyway, which makes the supervised approach easier to evaluate cleanly — but this is a pragmatic choice, not a methodologically superior one, and should be named as a limitation rather than glossed over. |
| Small autoencoder | Closer in spirit to some of the adjacent ML-security literature, but harder to justify and tune within 13 weeks. Rejected on project-management grounds, not technical grounds — worth being honest in the dissertation that this was a scope decision, not a claim that gradient boosting is the best possible architecture. |
| Gradient boosting (chosen) | Interpretable (feature importances map directly back to the "why" a session was flagged, which supports the explainability requirement from Unit 1.2), works well on small tabular data, realistic to implement and tune in the time available. |

The critical point to carry into the dissertation: gradient boosting is the *defensible* choice given the constraints, not the *objectively best* choice for the stated research question. Naming that gap directly is stronger than implying the method was obviously correct.

## 4. Where the argument currently has holes

Being direct about weaknesses, per the deck's "look for holes, where does it fail, where is it robust":

- **The "no one has done this yet" gap claim rests on a handful of targeted searches, not a systematic literature search.** Robust enough to justify a proposal; not yet robust enough to survive a viva question like "how do you know no one has published this since April?"
- **The rug-pull attack class is evidenced by one non-peer-reviewed blog post.** The project's second most important attack category rests on the weakest source in the review. This should be flagged explicitly in the dissertation's limitations, not left for an examiner to notice first.
- **The synthetic corpus makes every attack keyword-obvious.** This is a real methodological weakness, not a minor caveat — it means current results show the pipeline works, not that the underlying research question has been answered yet.
- **The IDS-to-MCP transfer is an analogy the project is testing, not a precedent it can lean on.** If the results don't hold, that's a legitimate and interesting finding, not a failure — but only if the dissertation is honest upfront that this was uncertain rather than presenting it as an obvious extension.

## 5. Why this makes the dissertation stronger, not weaker

Naming these weaknesses in the dissertation itself — in the literature review's limitations and in the methodology chapter — is what actually satisfies "critical" rather than "descriptive." A reviewer who reads a literature review that only summarises sources approvingly will ask exactly the questions above. A dissertation that raises them first, with evidence, is doing the thing this unit is asking for.
