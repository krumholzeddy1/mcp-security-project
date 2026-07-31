# Critical Analysis of Sources: S.A.R.A.

**Source:** Invariant Labs (2025) *MCP security notification: Tool poisoning attacks*. Available at: https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks (Accessed: 23 July 2026).

## 1) Summarize

**Central argument/focus:** MCP tool descriptions and schema fields can be crafted by a malicious or compromised server to embed instruction-like content that the calling model interprets as legitimate developer intent, resulting in a working tool-poisoning exploit.

**Key supporting claims:** Ordinarily descriptive metadata fields (tool name, description, parameter schema) are not treated as untrusted input by the model, allowing injected instructions to cause unintended behaviour such as data exfiltration; the attack does not require the user to notice anything unusual in the visible conversation.

**Evidence used:** A demonstrated proof-of-concept exploit with technical walkthrough, published as a vendor security notification.

## 2) Assess

**Logic:** The mechanism described is technically plausible and consistent with how MCP tool metadata is passed to the model without a separate trust channel — the claim requires no unusual assumption about model behaviour.

**Emotion:** More urgent in tone than an academic source, consistent with a security notification intended to prompt action, though not overtly sensationalist.

**Omission:** As a notification from a company selling a security product in this exact space, the piece has a commercial interest in establishing the severity and reach of the threat class it describes. It does not report how widespread this specific exploit pattern is across real deployments, nor does it disclose whether the finding was independently verified by a third party before publication.

**Research methodology:** A vendor-published technical disclosure rather than a peer-reviewed or independently verified study; published in 2025, close to MCP's emergence, so no long-term data on prevalence exists yet.

## 3) Reflect

This source is one of two independent accounts (alongside Radosevich and Halloran, 2025) of working tool-poisoning exploits, which gives the tool-poisoning half of this dissertation's attack taxonomy more support than the rug-pull half has (see the S.A.R.A. entry for Willison, 2025). Worth reading further into whether Invariant Labs or another vendor has published follow-up data on how many real MCP deployments were found vulnerable, which would meaningfully strengthen the "this is a live, not just theoretical, problem" framing.

## 4) Advance the argument

This remains important because it is one of the pieces of evidence that moves tool poisoning from a theoretical architectural concern (Hou et al., 2025) to a demonstrated, working exploit — but the dissertation should be explicit that this is a vendor disclosure with a commercial interest in the threat's perceived severity, not a neutral academic account. Treating it as corroborating evidence alongside Radosevich and Halloran (2025), rather than as a standalone authority, is the more defensible way to use it.
