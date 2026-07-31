# Critical Analysis of Sources: S.A.R.A.

**Source:** Willison, S. (2025) 'Model Context Protocol has prompt injection security problems', *simonwillison.net*, 9 April. Available at: https://simonwillison.net/2025/Apr/9/mcp-prompt-injection/ (Accessed: 23 July 2026).

## 1) Summarize

**Central argument/focus:** MCP tools can be poisoned in a delayed manner — a "rug pull" — where a tool's description is legitimate at the point of approval and is rewritten only after the tool has already been connected and trusted; a related pattern involves one server intercepting and answering on behalf of another it is not authorised to represent.

**Key supporting claims:** Servers can honestly pass initial review and mutate afterward without triggering any re-check; the visible behaviour of the tool to the end user need not change even as its underlying instructions do.

**Evidence used:** A first-hand technical write-up with illustrative examples and reasoning about the protocol's trust model, not a controlled study or systematic audit.

## 2) Assess

**Logic:** The mechanism described is plausible and requires no unusual assumption about MCP's design — nothing in the protocol prevents a description from changing post-connection, so the argument follows directly from how tool registration works.

**Emotion:** Direct, practitioner-toned, occasionally informal, but not emotionally loaded relative to the technical severity being described.

**Omission:** This is the most significant weakness of this source, and it matters more here than for the other sources in this reference list: there is no methodology section, no discussion of how the author verified the attack works beyond the write-up itself, and no data on how common this pattern is in the wild. As an independent blog post rather than a peer-reviewed or vendor-audited paper, it has not been externally verified by any reviewing body.

**Research methodology:** None in the formal sense — a practitioner disclosure/write-up, published April 2025. The author's independence (no product being sold in connection with the post) supports good-faith disclosure, but currency is also a limitation: the MCP ecosystem has moved quickly since publication, and no independent follow-up validation was identified in this review.

## 3) Reflect

This is worth being direct about in the dissertation: the entire "rug pull" half of the attack taxonomy rests on this one non-peer-reviewed source, unlike the tool-poisoning half, which is corroborated independently by both Invariant Labs (2025) and Radosevich and Halloran (2025). It would be worth actively searching for any subsequent academic or vendor source that has independently reproduced or formally documented the rug-pull pattern before relying on it as heavily as the current draft does.

## 4) Advance the argument

The issue remains important regardless of this source's informal status, because the underlying mechanism (no re-verification after registration) is independently supported by Hou et al.'s (2025) architectural analysis of MCP's trust model — the pattern is structurally plausible even without a second empirical account confirming it. The implication for this dissertation is to state this evidentiary asymmetry explicitly in the methodology or limitations section, rather than let the rug-pull category appear as well-established as the tool-poisoning category when it is not.
