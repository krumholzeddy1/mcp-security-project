# Critical Analysis of Sources: S.A.R.A.

**Source:** Radosevich, B. and Halloran, J. (2025) 'MCP safety audit: LLMs with the Model Context Protocol allow major security exploits', *arXiv preprint arXiv:2504.03767*. Available at: https://arxiv.org/abs/2504.03767 (Accessed: 23 July 2026).

## 1) Summarize

**Central argument/focus:** A systematic safety audit of MCP-based systems reveals that large language models using the protocol are vulnerable to major security exploits, including tool-poisoning-style attacks that manipulate the model through crafted tool metadata rather than through the visible conversation.

**Key supporting claims:** Existing safety and alignment training does not protect a model from instructions embedded in tool descriptions or schemas; successful exploits were demonstrated that extracted sensitive information or performed unauthorised actions without the tool visibly misbehaving.

**Evidence used:** An empirical audit involving constructed attack scenarios run against real MCP-integrated LLM systems, with reported exploit outcomes — a more systematic evidence base than a single illustrative write-up.

## 2) Assess

**Logic:** The audit methodology (systematically testing a set of attack scenarios rather than describing one exploit) is a logically stronger form of evidence than a single demonstration, since it speaks to reproducibility across scenarios rather than a one-off finding.

**Emotion:** The title itself ("major security exploits") is stronger, more attention-seeking language than the more measured framing used by Hou et al. (2025); worth noting this is a rhetorical choice common in security-audit papers seeking visibility, not necessarily a sign of overstated findings, but worth reading the results section on its own merits rather than taking the framing at face value.

**Omission:** As an arXiv preprint, this has not yet been confirmed as peer-reviewed at the time of writing. The audit does not appear to report a denominator — how many MCP deployments or configurations were tested relative to how many were found vulnerable — which limits how confidently this dissertation can describe the exploits as representative of MCP deployments generally rather than of the specific configurations audited.

**Research methodology:** Empirical security audit with constructed attack scenarios, published in 2025. Methodologically the strongest of the MCP-specific sources reviewed here, since it involves systematic testing rather than a single case or architectural argument alone.

## 3) Reflect

This source strengthens the tool-poisoning half of the dissertation's attack taxonomy considerably, since it corroborates Invariant Labs (2025) independently and with a more systematic methodology. Worth reading further into the audit's full methodology section (scenario count, target diversity) to assess how broadly the findings generalise before citing exploit rates, if any are reported, as representative figures.

## 4) Advance the argument

This remains important because it is the strongest empirical evidence in the review that tool poisoning is a demonstrated, not merely theoretical, class of vulnerability — which directly justifies why a detection-focused dissertation is a timely contribution rather than a solution in search of a problem. The implication for this dissertation is to lean on this source, alongside Invariant Labs (2025), as the primary empirical grounding for the tool-poisoning attack category, while being explicit that the rug-pull category (Willison, 2025) does not yet have comparably systematic evidence behind it.
