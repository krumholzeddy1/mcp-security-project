# Critical Analysis of Sources: S.A.R.A.

**Source:** Bhatt, M., Narajala, V.S. and Habler, I. (2025) 'ETDI: Mitigating tool squatting and rug pull attacks in Model Context Protocol (MCP) by using OAuth-enhanced tool definitions and policy-based access control', *Proceedings of the Cyber Awareness and Research Symposium (CARS)*. IEEE.

## 1) Summarize

**Central argument/focus:** Tool squatting and rug-pull attacks in MCP can be mitigated by strengthening the tool-registration mechanism itself — specifically, by requiring OAuth-enhanced tool definitions and enforcing policy-based access control over what a registered tool is permitted to do.

**Key supporting claims:** Unscoped, unauthenticated tool definitions are a root enabler of both tool-squatting (a malicious tool impersonating a trusted one) and rug-pull attacks; adding an authentication and policy layer at the point of tool definition constrains the damage a malicious or compromised tool can do even if it is later trusted.

**Evidence used:** A proposed system design (ETDI) with an architectural/technical description of how OAuth-scoping and policy enforcement would integrate into the MCP tool-registration flow, rather than a large-scale empirical deployment study.

## 2) Assess

**Logic:** The reasoning is sound within its own frame — if a tool's permitted actions are scoped and enforced by policy rather than left to convention, the blast radius of a rug-pull is reduced even if the description itself is not re-checked. The claim is about damage limitation, not detection, which is a narrower and more defensible scope than it might first appear.

**Emotion:** Neutral, technical register consistent with a systems-security conference paper.

**Omission:** The proposal does not address the actual detection problem this dissertation is concerned with — ETDI limits what a rug-pulled tool can *do*, but it does not claim to *notice* that a rug-pull has occurred. This distinction matters: citing this paper as evidence that rug-pulls are "being addressed" would overstate what it actually solves. There is also no discussion of enforcement overhead or the practical burden of retrofitting OAuth scoping onto the large number of already-deployed MCP servers.

**Research methodology:** A system/architecture proposal presented at a specialist symposium (CARS, published via IEEE) rather than a longitudinal or empirical study. Very recent (2025), close to MCP's own emergence, so it has not yet had time to be independently evaluated or adopted at scale.

## 3) Reflect

This source is useful for showing the dissertation is aware of what mitigation research already exists, and for drawing a sharp, defensible line between prevention/containment (what ETDI offers) and detection (what this dissertation investigates). Worth reading further into whether any follow-up work has evaluated ETDI's real-world adoption or overhead, since a policy-based control layer that is too costly to deploy would not meaningfully change the threat landscape regardless of its technical soundness.

## 4) Advance the argument

This remains important because it represents the current state of the art in *response* to tool-poisoning and rug-pull attacks, and the dissertation needs to be positioned clearly relative to it: ETDI and the proposed anomaly-detection approach are complementary, not competing — one limits damage after the fact, the other aims to notice the attack is happening. Stating this relationship explicitly in the dissertation strengthens the justification for why detection is still a meaningfully separate contribution even though mitigation research already exists.
