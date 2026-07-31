**Task Unit 1.1 — Project Objectives and Scope**

**1. Three Candidate Project Ideas**

**Idea 1**

I'm interested in agentic AI systems, specifically the emerging protocols (Model Context Protocol, Agent2Agent) that let AI agents call tools and other agents autonomously, because I work with agentic AI platforms professionally and have seen how quickly these systems are being deployed in production without security keeping pace.

**End goal**

- What the end of the project looks like: a working, evidence-based answer to whether machine-learning-based anomaly detection can catch attacks that current schema-validation defenses miss.

- What I want to build: a local testbed that reproduces tool-poisoning attacks against an MCP client/server, plus an ML-based anomaly detector trained on tool-call metadata.

- What I want to research: the published threat taxonomy for MCP (tool poisoning, rug-pull redefinition, cross-server interception) and how existing defenses fail.

- What I want to investigate: whether detection accuracy from behavioral/metadata signals outperforms static schema checks, and by how much.

**Idea 2**

I'm interested in AI-assisted software development because AI coding assistants and “spec-driven” workflows are now embedded directly in enterprise SDLC pipelines I work with, and it isn't yet clear whether traditional security tooling can catch what these assistants introduce.

**End goal**

- What the end of the project looks like: a comparative evaluation of detection approaches for vulnerabilities introduced via AI-assisted code generation.

- What I want to build: a small corpus of AI-generated code samples (some seeded with known vulnerability classes) and a detection pipeline.

- What I want to research: existing SAST/DAST tool coverage against AI-generated code vulnerability patterns.

- What I want to investigate: whether ML-based static or behavioral analysis outperforms conventional SAST on this specific code population.

**Idea 3**

I'm interested in security operations and explainable AI because alert fatigue is a well-documented, measurable problem for SOC analysts, and I want to test whether explainability changes analyst behavior rather than being a nice-to-have.

**End goal**

- What the end of the project looks like: measured evidence of whether an explainable triage model changes analyst trust and miss rates versus a black-box model.

- What I want to build: an XAI-enhanced alert-triage prototype using a public SIEM/alert dataset.

- What I want to research: existing literature on analyst trust calibration and XAI in security operations.

- What I want to investigate: measurable differences in trust calibration and missed true positives between explainable and black-box triage.
