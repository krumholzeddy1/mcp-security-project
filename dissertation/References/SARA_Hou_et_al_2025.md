# Critical Analysis of Sources: S.A.R.A.

**Source:** Hou, X., Zhao, Y., Wang, S. and Wang, H. (2025) 'Model Context Protocol (MCP): Landscape, security threats, and future research directions', *arXiv preprint arXiv:2503.23278*. Available at: https://arxiv.org/abs/2503.23278 (Accessed: 23 July 2026).

## 1) Summarize

**Central argument/focus:** MCP's layered architecture (user → model → client → server) assumes trust between adjacent layers but provides no mechanism to re-verify that trust once a session is running, which the authors identify as the structural root of MCP's security weaknesses.

**Key supporting claims:** The protocol's design prioritises interoperability over security; validation responsibility is pushed downstream with each hop; this creates a wider attack surface than a single-model chat application without external tool access.

**Evidence used:** Architectural analysis of the MCP specification and worked-through attack scenarios, rather than empirical incident data or a controlled experiment.

## 2) Assess

**Logic:** The claims follow clearly from the architectural description — if no layer re-verifies the layer before it, a compromise anywhere in the chain propagates outward. The reasoning is internally consistent and does not depend on contested assumptions.

**Emotion:** Measured and technical throughout; no alarmist or promotional language.

**Omission:** The paper characterises what is *structurally possible* but does not report how often these weaknesses are actually exploited in production deployments — a distinction this dissertation should preserve when citing it, rather than implying prevalence data exists where it does not. There is also no comparison to structurally similar prior plugin/tool architectures that predate MCP, which would have helped establish whether this is a genuinely new problem class or a recurring one.

**Research methodology:** A landscape/survey analysis of the protocol specification and known threat classes, published as an arXiv preprint in 2025 — not yet confirmed as peer-reviewed at the time of writing. Being contemporaneous with MCP's own emergence is a strength for currency but means the field has had little time to mature a response or independently verify the survey's completeness.

## 3) Reflect

This source shapes the dissertation's framing of *why* MCP is vulnerable, not just *that* it is — its "trust without re-verification" framing underpins the Problem Statement directly. It raises a question worth following up: how do structurally similar agent-communication protocols (e.g. Agent2Agent) handle the same trust-propagation problem, and is this weakness protocol-specific or a general property of this class of architecture.

## 4) Advance the argument

This issue remains important because MCP adoption is accelerating faster than its security tooling is maturing — precisely the window in which foundational architectural weaknesses become entrenched in production systems before defences catch up. The implication for this dissertation is direct: if the weakness is structural rather than a specific, patchable bug, detection approaches that do not rely on a fixed known pattern are more likely to remain useful as the protocol and its attacks continue to evolve.
