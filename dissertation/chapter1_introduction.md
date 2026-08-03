# Chapter 1: Introduction

## 1.1 Background and Motivation

Agentic artificial intelligence systems — in which large language models autonomously discover, select, and invoke external tools to complete tasks on a user's behalf — have moved rapidly from research prototypes to production deployment. Anthropic's Model Context Protocol (MCP) has emerged as the dominant open standard for this tool-calling layer, providing a common interface through which any model client can communicate with any compliant tool server. As MCP adoption has grown, so has the attack surface it introduces: a class of vulnerabilities in which malicious or compromised servers embed instruction-like text in tool metadata fields, causing the model to take actions the user did not authorise and may not be aware of. A distinct and more difficult variant — the rug-pull attack — compounds this risk by delaying the injection: a malicious server registers with a clean, honest description, passes any initial inspection, and only injects content after the client has established trust and the session is underway (Willison, 2025). Every existing defence against tool poisoning — schema validation, OAuth-based scope control, human review — checks tool metadata once, at the point of registration; a rug-pull mutation that occurs after registration is structurally invisible to all three, regardless of how sophisticated the checking logic is.

## 1.2 Research Question

This project addresses that specific gap:

> *To what extent can machine-learning-based anomaly detection of tool-call metadata and tool-description change patterns improve the detection of tool-poisoning attacks in MCP-based agentic systems, compared with existing schema-validation defences?*

## 1.3 Aim and Objectives

**Aim.** To determine whether a machine-learning classifier trained on MCP tool-call metadata features observable after tool registration can detect rug-pull attacks that registration-time schema-validation defences are structurally incapable of detecting, and to quantify the extent of that improvement against a representative baseline.

**Objectives.**

1. Review literature on MCP architecture, documented tool-poisoning and rug-pull attacks, existing defences, and ML anomaly detection to identify the research gap.
2. Design and implement a controlled, isolated MCP testbed capable of reproducing tool-poisoning and rug-pull attack scenarios.
3. Generate a reproducible labelled synthetic corpus of 600 tool-call sessions across three classes, with a documented noise model producing overlapping feature distributions.
4. Implement a registration-time schema-validator baseline and characterise its structural blind spot on the rug-pull class.
5. Train Logistic Regression, Random Forest, and Gradient Boosting classifiers on eleven metadata features using a fixed stratified split.
6. Compare all three ML detectors against the baseline on the held-out test set, using per-class rug-pull recall as the primary metric.
7. Evaluate detection robustness under a skewed class distribution (90% benign, 5% each attack class) and report precision degradation operationally.
8. Analyse feature importance scores to establish mechanistic grounding and characterise the theoretical detection bound imposed by stealthy attacks.

## 1.4 Approach and Scope

The study adopts a positivist, quantitative, experimental design. A controlled, isolated testbed is constructed comprising a real MCP server and client built on the reference implementation, and a reproducible synthetic labelled corpus of 600 tool-call sessions is generated across three classes (benign, poisoned, and rug-pull). Three ML classifiers — Logistic Regression, Random Forest, and Gradient Boosting — are each trained on eleven metadata features extracted from each session and compared against a baseline schema-validator on a held-out test set, with performance reported as precision, recall, and F1 score decomposed by attack class. A separate robustness check on a skewed corpus (90% benign, 5% each attack class) evaluates whether detection capability generalises under realistic class imbalance.

The scope is limited to MCP tool-poisoning detection; A2A protocol analysis is proposed as future work (Section 8.4). All experimental work uses synthetic data in a sandboxed local environment.

## 1.5 Contributions

This project makes three contributions to the nascent literature on MCP security:

1. **A characterisation of the detection gap.** It provides a formal demonstration — grounded in a controlled experiment with documented noise assumptions — that a registration-time schema-validator achieves zero recall on rug-pull attacks by structural necessity, and quantifies how much of that gap post-registration ML detectors can close (88.1–93.3% rug-pull recall across three model families, versus 0% for the baseline).

2. **A reproducible synthetic testbed.** The corpus generator, feature extraction pipeline, and evaluation harness are published as open-source artefacts with a fixed random seed and pinned dependencies, providing a reproducible baseline against which future detection methods can be compared.

3. **A theoretical bound on point-in-time detection.** The stealthy rug-pull analysis (Chapter 7) establishes a hard false-negative floor set by attacks that revert their mutation before the monitoring snapshot, and identifies continuous session monitoring as the necessary architectural response.

## 1.6 Dissertation Structure

**Chapter 2** surveys the literature on MCP's security landscape, documented tool-poisoning attacks, existing defences, and the ML techniques applied to anomaly detection in security contexts.

**Chapter 3** describes the methodology: the testbed architecture, corpus generation design, noise model, feature set, baseline implementation, ML model selection, and evaluation protocol.

**Chapter 4** documents the system design: functional and non-functional requirements, pipeline architecture, and feature-design and model-selection rationale.

**Chapter 5** documents the implementation: the three substantive problems encountered during development (baseline feature leakage, corpus separability, zero-importance flag) and the testing strategy.

**Chapter 6** presents the evaluation results — multi-model comparison, per-class recall decomposition, feature importance scores, and the skewed corpus robustness check.

**Chapter 7** discusses the implications of the results, the theoretical bound imposed by point-in-time sampling, the limitations of the synthetic corpus and feature set, the relationship between the ML detector and existing defences, and the project journey.

**Chapter 8** concludes by verifying that each objective has been met, answering the research question, and identifying directions for future work.
