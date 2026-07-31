# Chapter 1: Introduction

## 1.1 Background and Motivation

Agentic artificial intelligence systems — in which large language models autonomously discover, select, and invoke external tools to complete tasks on a user's behalf — have moved rapidly from research prototypes to production deployment. Anthropic's Model Context Protocol (MCP) has emerged as the dominant open standard for this tool-calling layer, providing a common interface through which any model client can communicate with any compliant tool server. As MCP adoption has grown, so has the attack surface it introduces: a class of vulnerabilities in which malicious or compromised servers embed instruction-like text in tool metadata fields, causing the model to take actions the user did not authorise and may not be aware of.

Tool-poisoning attacks exploit a fundamental property of how LLMs are used in agentic settings: the model trusts what a tool's metadata says the tool does, because there is no independent mechanism for verifying that claim. An attacker who controls a server can write a tool's description, name, or parameter schema so that the text inside it reads as an instruction rather than as documentation. Because large language models are trained to follow instructions, the injection is processed as if it had originated from the legitimate user. Working exploits of this class have been demonstrated against deployed MCP systems, including attacks that silently exfiltrated credentials and file contents without producing any visible anomaly in the tool's output (Invariant Labs, 2025; Radosevich and Halloran, 2025).

A distinct and more difficult variant — the rug-pull attack — compounds this risk by delaying the injection. A malicious server registers with a clean, honest description, passes any initial inspection, and only injects content after the client has established trust and the session is underway (Willison, 2025). Every existing defence against tool poisoning — schema validation, OAuth-based scope control, human review — checks tool metadata once, at the point of registration. None of them re-checks anything once the session is running, so a rug-pull mutation that occurs after registration is structurally invisible to all three, regardless of how sophisticated the checking logic is.

## 1.2 Research Question

This project addresses that specific gap:

> *To what extent can machine-learning-based anomaly detection of tool-call metadata and tool-description change patterns improve the detection of tool-poisoning attacks in MCP-based agentic systems, compared with existing schema-validation defences?*

The key term in the research question is the observability window. Existing defences observe tool metadata once; the hypothesis tested here is that extending observation to include call-time metadata and the pattern of description changes across a session provides the additional signal needed to detect the rug-pull class that registration-time checks cannot reach.

## 1.3 Aim and Objectives

**Aim.** To determine whether a machine-learning classifier trained on MCP tool-call metadata features observable after tool registration can detect rug-pull attacks that registration-time schema-validation defences are structurally incapable of detecting, and to quantify the extent of that improvement against a representative baseline.

**Objectives.**

1. Review published literature on MCP's architecture, documented tool-poisoning and rug-pull attacks, existing defences, and ML-based anomaly detection techniques, to identify the research gap this study addresses.

2. Design and implement a controlled, isolated MCP testbed capable of reproducing tool-poisoning and rug-pull attack scenarios without interacting with any external or production server.

3. Generate a reproducible, labelled synthetic corpus of at least 600 tool-call sessions spanning benign, poisoned, and rug-pull classes, incorporating a documented noise model that produces overlapping feature distributions across classes.

4. Implement a registration-time schema-validator baseline representative of defences currently described in the literature, and characterise its structural blind spot with respect to the rug-pull class.

5. Train three candidate ML classifiers — Logistic Regression, Random Forest, and Gradient Boosting — on eleven metadata features extracted from each session, using a fixed stratified split to ensure the comparison is reproducible and apples-to-apples.

6. Compare all three ML detectors against the baseline on the held-out test set, reporting per-class precision, recall, and F1 score, with per-class recall on rug-pull sessions as the primary metric for evaluating the research question.

7. Evaluate detection robustness under a realistically skewed class distribution (90% benign, 5% each attack class) and report any precision degradation in operational terms.

8. Analyse feature importance scores from the trained models to establish whether any improvement in detection is mechanistically grounded in access to post-registration features, and to characterise the theoretical bound imposed on point-in-time detection by attacks that revert their mutation before observation.

## 1.4 Approach and Scope

The study adopts a positivist, quantitative, experimental design. A controlled, isolated testbed is constructed comprising a real MCP server and client built on the reference implementation, and a reproducible synthetic labelled corpus of 600 tool-call sessions is generated across three classes (benign, poisoned, and rug-pull). Three ML classifiers — Logistic Regression, Random Forest, and Gradient Boosting — are each trained on eleven metadata features extracted from each session and compared against a baseline schema-validator on a held-out test set, with performance reported as precision, recall, and F1 score decomposed by attack class. A separate robustness check on a skewed corpus (90% benign, 5% each attack class) evaluates whether detection capability generalises under realistic class imbalance.

The scope is deliberately limited to MCP tool-poisoning detection. A comparable analysis of the Agent2Agent (A2A) protocol is identified in the literature as a natural extension of this work but falls outside the project timeline and is proposed as future work (Section 6.4). All experimental work is conducted within a sandboxed, locally hosted environment using entirely synthetic data; no live third-party servers are accessed at any stage.

## 1.5 Contributions

This project makes three contributions to the nascent literature on MCP security:

1. **A characterisation of the detection gap.** It provides a formal demonstration — grounded in a controlled experiment with documented noise assumptions — that a registration-time schema-validator achieves zero recall on rug-pull attacks by structural necessity, and quantifies how much of that gap post-registration ML detectors can close (88.1–93.3% rug-pull recall across three model families, versus 0% for the baseline).

2. **A reproducible synthetic testbed.** The corpus generator, feature extraction pipeline, and evaluation harness are published as open-source artefacts with a fixed random seed and pinned dependencies, providing a reproducible baseline against which future detection methods can be compared.

3. **A theoretical bound on point-in-time detection.** The stealthy rug-pull analysis (Chapter 5) establishes that any detector operating on a single metadata snapshot has a hard false-negative floor set by attacks timed to revert before the snapshot is taken, and identifies continuous session monitoring as the necessary architectural response.

## 1.6 Dissertation Structure

**Chapter 2** surveys the literature on MCP's security landscape, documented tool-poisoning attacks, existing defences, and the ML techniques applied to anomaly detection in security contexts *(Objective 1)*.

**Chapter 3** describes the methodology: the testbed architecture, corpus generation design, noise model, feature set, baseline implementation, ML model selection, and evaluation protocol *(Objectives 2–5)*.

**Chapter 4** presents the evaluation results — multi-model comparison, per-class recall decomposition, feature importance scores, and the skewed corpus robustness check — and interprets each finding in relation to the research question and the literature *(Objectives 6–8)*.

**Chapter 5** discusses the implications of the results, the theoretical bound imposed by point-in-time sampling, the limitations of the synthetic corpus and feature set, and the relationship between the ML detector and existing registration-time defences *(Objective 8)*.

**Chapter 6** concludes by verifying that each objective has been met, answering the research question, summarising the project's contributions, and identifying the directions for future work.
