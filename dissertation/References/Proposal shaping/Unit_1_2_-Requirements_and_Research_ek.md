**Task Unit 1.2 — Requirements and Research**

**1. Screen of All Three Ideas**

Each idea was screened against feasibility within the established completion timeline (submission 25 October 2026).

| **Idea**                                      | **Feasibility check**                                                                                                                          | **Outcome** |
|-----------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|-------------|
| 1\. MCP tool-poisoning detection              | Fully reproducible in an isolated local testbed; no human participants or personal data required.                                              | Selected    |
| 2\. AI-generated code vulnerability detection | Requires assembling a sufficiently large, realistic AI-generated vulnerability corpus, not achievable at the scale needed within the timeline. | Abandoned   |
| 3\. XAI for SOC alert triage                  | Evaluation depends on real analyst participants or a live SOC dataset, raising human-subjects ethics review that would not clear in time.      | Abandoned   |

**2. Full Requirements & Research — Idea 1 (Selected)**

**Stakeholders**

- MCP protocol maintainers and the wider agentic-AI developer community (consumers of any detection method proposed).

- Enterprise security teams deploying MCP-based agents in production (end beneficiaries of improved detection).

- Academic security research community (MCP security is an active, recent research area).

- Project supervisor and Lancashire assessment panel.

**Requirements**

**Functional**

- The system must ingest MCP tool-call metadata and tool-description content from a testbed session.

- The system must flag sessions/tool calls it judges anomalous, with a confidence score.

- The system must support comparison against a rule-based schema-validation baseline on the same test set.

**Non-functional**

- Detection should run at a latency compatible with near-real-time use (seconds, not minutes) to be practically relevant.

- The approach should be reasonably explainable, and a security analyst should be able to see why a call was flagged.

- The system must not depend on any production or personal data.

**MoSCoW Analysis**

| **Priority** | **Item**                                                                                           |
|--------------|----------------------------------------------------------------------------------------------------|
| Must         | Local MCP client/server testbed reproducing tool-poisoning and rug-pull scenarios                  |
| Must         | Synthetic attack corpus generated from documented CVE/attack patterns                              |
| Must         | ML-based anomaly detector evaluated against a schema-validation baseline                           |
| Should       | Basic explainability output (e.g., feature attribution) alongside each flagged call                |
| Could        | Testing transferability of the detector across more than one open-source MCP client implementation |
| Won't        | Coverage of the Agent2Agent (A2A) protocol is explicitly out of scope, proposed as future work     |

**Refining Scope**

Scope is deliberately narrowed to MCP only (dropping the initially broader agentic-protocol framing) and to tool-poisoning/rug-pull attack classes specifically, rather than the full MCP threat taxonomy, so that testbed build, dataset generation, model training, and evaluation each fit within one to three weeks of the available term.

**Initial Literature Review**

Early reading confirms this is a live, recent research gap rather than a solved problem: MCP's trust model pushes validation responsibility downstream with each hop from user input to server, widening the attack surface; documented CVEs and vendor security notices (Invariant Labs, 2025; Willison, 2025) describe tool-poisoning and rug-pull attacks in the wild; and current published mitigations (Radosevich & Halloran, 2025; Bhatt et al., 2025) are schema- and OAuth-scope based rather than behavioral/ML-based, which is the gap this project targets.

**Risks, Assumptions, and Constraints**

| **Type**   | **Detail**                                                                                                          | **Mitigation / note**                                                                                                                           |
|------------|---------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| Risk       | Synthetic attack corpus may not capture the full diversity of real-world attacker behavior.                         | Ground synthetic scenarios in published CVEs and documented attack taxonomies rather than inventing patterns from scratch.                      |
| Risk       | Model training/evaluation (weeks 6-8) is the tightest part of a 13-week schedule.                                   | Keep the model architecture simple (e.g., gradient-boosted trees or a small autoencoder) rather than attempting a novel deep-learning approach. |
| Assumption | An open-source MCP reference client/server adequately represents production MCP behavior for this study's purposes. | Stated explicitly as a limitation in the final report.                                                                                          |
| Constraint | Fixed submission deadline of 25 October 2026.                                                                       | Scope narrowed to MCP-only; A2A explicitly excluded.                                                                                            |

References:

- Bhatt, M., Narajala, V.S. and Habler, I. (2025) 'ETDI: Mitigating tool squatting and rug pull attacks in Model Context Protocol (MCP) by using OAuth-enhanced tool definitions and policy-based access control', in *Proceedings of the Cyber Awareness and Research Symposium (CARS)*. IEEE.

- Invariant Labs (2025) *MCP security notification: Tool poisoning attacks*. Available at: [<u>https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks</u>](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks) (Accessed: 21 July 2026).

- Radosevich, B. and Halloran, J. (2025) *MCP safety audit: LLMs with the Model Context Protocol allow major security exploits*. arXiv:2504.03767. Available at: [<u>https://arxiv.org/abs/2504.03767</u>](https://arxiv.org/abs/2504.03767) (Accessed: 21 July 2026).

- Willison, S. (2025) *Model Context Protocol has prompt injection security problems*. Available at: [<u>https://simonwillison.net/2025/Apr/9/mcp-prompt-injection/</u>](https://simonwillison.net/2025/Apr/9/mcp-prompt-injection/) (Accessed: 21 July 2026).
