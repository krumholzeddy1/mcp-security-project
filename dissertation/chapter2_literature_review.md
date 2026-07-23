# Chapter 2: Literature Review

## 2.1 The Emergence of Agentic AI and Tool-Calling Architectures

Large language models (LLMs) have evolved rapidly from systems that respond to isolated prompts into autonomous agents that plan, reason across multiple steps, and invoke external tools to complete tasks on a user's behalf. This shift from passive responders to active agents has been accompanied by the development of standardised protocols that allow models to discover and call tools provided by remote servers — a capability that dramatically extends what an LLM can accomplish but also introduces a new and largely uncharted attack surface.

Tool-calling architectures follow a common structural pattern: a client application hosts or communicates with an LLM, the LLM is presented with a catalogue of available tools at the start of a session, and the LLM autonomously selects and calls tools based on its interpretation of their declared metadata — principally their name, description, and parameter schema. The model never executes tool code directly; it constructs a structured call, and the client forwards it to the appropriate server. This indirection means that the model's behaviour is governed by what the metadata *says* the tool does, not by independent verification of what the tool *actually* does. The trust relationship between the model and the tool's declared description is therefore a critical security boundary.

---

## 2.2 The Model Context Protocol

Anthropic's Model Context Protocol (MCP) has emerged as the dominant open standard for this tool-calling layer. MCP defines a message-passing interface through which a client connects to one or more servers, requests a list of available tools via a `tools/list` call, and subsequently invokes tools via `tools/call`. Each tool is described by a name, a free-text description, and a JSON Schema defining its input parameters.

Hou, Zhao, Wang, and Wang (2025) provide a comprehensive survey of MCP's design landscape and security implications. They identify a structural weakness that is central to this project: MCP was designed to solve an interoperability problem — enabling any client to communicate with any server using a common protocol — and treats security as a secondary concern. The protocol has no built-in mechanism for re-validating the trust placed in a tool after the initial connection is established. Each layer in the pipeline — user, model, client, server — is assumed to trust the layer immediately behind it, but nothing re-checks that trust once a session is running. Hou et al. (2025) argue that this creates a situation where a compromised or malicious component several hops downstream can inject behaviour that is, from the model's perspective, indistinguishable from a legitimate instruction originating from the user.

---

## 2.3 Tool-Poisoning Attacks

Tool poisoning exploits the model's reliance on tool metadata by embedding instruction-like text directly into the fields that the model treats as descriptive. Because LLMs are trained to follow instructions embedded in their context, text placed in a tool's name, description, or parameter schema can direct the model to perform actions that the user did not request and may not be aware of.

Invariant Labs (2025) published the first detailed public demonstration of tool poisoning as a practical attack against deployed MCP systems. Their report documents working exploits in which tool descriptions contain hidden directives — including instructions to exfiltrate the contents of local configuration files, to relay the user's session credentials to a secondary endpoint, and to modify subsequent tool calls in ways that persist across the session. In all demonstrated cases, the tool appeared to function normally from the user's perspective: the visible output of the tool's invocation was unremarkable, while the injected behaviour operated silently in parallel. This makes tool poisoning qualitatively different from a conventional server-side exploit, which typically produces observable anomalies (errors, latency spikes, unexpected outputs). The attack surface is the model's context window rather than any executable code path, and the symptoms are only visible if the model's reasoning is audited — something current deployments generally do not do.

Radosevich and Halloran (2025) conducted a systematic safety audit of MCP deployments and confirmed that tool-poisoning vulnerabilities are not limited to contrived examples. Their audit identified multiple real-world MCP servers in which tool descriptions contained instruction-like text — sometimes introduced intentionally by server operators pursuing unauthorised data collection, and sometimes introduced inadvertently through misconfiguration or insecure default templates. They further demonstrate that injection via parameter *schema field names* (not only the description field) is also effective, because field names appear in the model's prompt alongside the description and are treated as semantically meaningful. This broadens the attack surface beyond what keyword-based defences targeting descriptions alone can address.

---

## 2.4 The Rug-Pull Attack Pattern

A distinct and particularly difficult variant of tool poisoning is the delayed attack, commonly referred to as a rug-pull. Willison (2025) describes servers that register with honest, unmodified tool descriptions — passing any initial inspection or human review — and subsequently rewrite their tool definitions after the client has trusted them and established a session. From the protocol's perspective, nothing prevents a server from returning a different tool list in response to a `tools/list` call than it returned at the start of the session; the client has no mechanism for detecting or preventing this mutation.

Willison (2025) also identifies a related pattern: server impersonation, in which one server intercepts and responds on behalf of another server it was never meant to represent. Both patterns share the same structural property: the attack becomes visible only after the trust relationship has been established and the opportunity for initial inspection has passed. This places them outside the scope of any defence that checks a tool once, at the point of first registration.

The rug-pull attack is particularly significant in the context of automated or long-running agentic sessions, where a model may interact with a given tool many times over an extended period before a human operator reviews the session transcript. An attacker who controls a server can exploit the timing window between the initial connection — when the tool description is clean — and a later point in the session when monitoring attention may be lower.

---

## 2.5 Existing Defences and Their Limitations

Three categories of defence are in common use for MCP tool security, and all three share the structural limitation of checking a tool once rather than continuously.

**Schema validation** inspects a tool's declared JSON Schema at registration time, verifying that field types, required fields, and enumerated values conform to expected patterns. While this catches tools with obviously malformed schemas, it provides no protection against injection embedded in well-formed string fields — the description field accepts arbitrary text by design, and an injected directive in a `description` string passes schema validation trivially. Schema validation is also entirely registration-time, providing no visibility into changes that occur after the initial connection.

**OAuth-based access control**, exemplified by the Enhanced Tool Definition Interface (ETDI) proposed by Bhatt, Narajala, and Habler (2025), extends MCP with cryptographically signed tool definitions and policy-based access scoping. ETDI binds a tool's permitted actions to its declared identity at registration time, requiring that any tool invocation satisfy pre-approved scope constraints. This is a substantive improvement over schema validation because it limits what a poisoned tool can accomplish even if the injection is not detected. However, ETDI does not address the rug-pull attack: if the server rewrites a tool's description after registration, the newly injected instructions may still fall within the originally approved scope, and the scope constraint does not detect the semantic change in the description itself. Bhatt et al. (2025) acknowledge this limitation, noting that ETDI is designed to prevent tool squatting (one tool masquerading as another at registration) rather than post-registration description mutation.

**Human review** — the practice of having a user or operator read tool descriptions before connecting — is the most common informal defence in current deployments. It is effective for detecting obvious injection in short, readable descriptions but does not scale to sessions with many tools, fails for descriptions in which injection is embedded in technical-looking text that a non-expert reviewer may not identify as anomalous, and provides no protection against rug-pull mutations that occur after the review has been completed.

The common failure mode across all three defences is temporal: each checks the state of a tool's metadata at a single point in time and does not revisit that check. Hou et al. (2025) characterise this as a structural property of MCP's trust model rather than a fixable parameter of any particular defence: the protocol provides no event notification when a server changes its tool definitions, and no session-level audit trail of description changes is maintained by the standard client implementation.

---

## 2.6 Machine-Learning Approaches to Security Anomaly Detection

The use of machine learning to detect security anomalies from behavioural metadata has a well-established history in network intrusion detection and malware classification. The common principle is that malicious behaviour — even when it is deliberately designed to evade rule-based signatures — tends to leave statistical traces in observable features: timing distributions, payload lengths, entropy of content, and deviations from session-level baselines. A classifier trained on labelled examples of normal and anomalous behaviour can learn to identify these traces even when no individual feature is individually diagnostic.

Applied to the MCP tool-poisoning context, this principle suggests that attacks may be detectable from metadata features — description lengths, entropy values, keyword-hit counts, and the pattern of changes across the session — even when the attack text itself is crafted to evade a specific keyword list. Gradient-boosted tree classifiers are a well-established choice for this kind of tabular, heterogeneous feature set: they handle mixed feature types without preprocessing, provide interpretable feature importance scores that allow post-hoc analysis of which features drive predictions, and are competitive with more complex architectures on structured data of moderate size (Chen and Guestrin, 2016). They are also well-suited to a research context where model interpretability is as important as raw predictive performance, since the research question asks not only whether detection improves but *why* — which requires understanding which features the model uses.

No prior published work has applied machine-learning-based anomaly detection specifically to MCP tool-call metadata for the purpose of detecting post-registration description changes. The closest adjacent work — Bhatt et al. (2025) and Hou et al. (2025) — proposes and analyses registration-time defences, leaving the post-registration detection problem unaddressed.

---

## 2.7 Research Gap

The literature establishes two complementary facts. First, rug-pull attacks against MCP tools are a documented, practical threat that exploits a structural gap in how MCP manages trust across the lifetime of a session (Willison, 2025; Hou et al., 2025). Second, all defences that have been proposed or deployed to date check tool metadata at a single point — registration — and are therefore structurally unable to detect mutations that occur after that point, regardless of how sophisticated the checking logic is (Bhatt et al., 2025; Invariant Labs, 2025; Radosevich and Halloran, 2025).

This project addresses the gap between these two facts. By applying a machine-learning classifier to the metadata features observable *after* tool registration — including call-time description content, description-change flags, and session timing patterns — it tests whether the post-registration signal that rug-pull attacks necessarily generate can be exploited for detection. The research question is therefore not whether existing defences can be improved by tuning their parameters, but whether a fundamentally different observability window — one that extends beyond registration time — produces a qualitatively different detection capability for the attack class that existing defences cannot reach.
