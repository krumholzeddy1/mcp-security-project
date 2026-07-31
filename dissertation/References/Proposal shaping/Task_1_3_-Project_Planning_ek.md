**Task Unit 1.3 — Project Planning**

**Project:** Detecting Tool-Poisoning Attacks in MCP Agentic Systems Using Machine-Learning-Based Anomaly Detection. Deadline: 25 October 2026 (13-week window from 21 July 2026).

**1. SMART Deliverables**

| **Deliverable**           | **SMART statement**                                                                                                                                       |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| Local MCP testbed         | A running MCP client/server harness capable of executing at least 3 documented tool-poisoning/rug-pull scenarios, completed by end of week 4.             |
| Synthetic attack corpus   | A labelled dataset of at least 150 benign and 150 poisoned tool-call sessions, generated from documented CVE/attack patterns, completed by end of week 5. |
| Baseline schema validator | A rule-based schema-validation defence implemented and run against the full corpus, completed by end of week 5.                                           |
| Anomaly-detection model   | A trained ML classifier evaluated on a held-out test split of the corpus, achieving a documented precision/recall figure, completed by end of week 8.     |
| Comparative evaluation    | A quantitative comparison (precision, recall, F1) between the ML detector and the baseline validator, completed by end of week 10.                        |
| Final report              | A complete, supervisor-reviewed dissertation submitted by 25 October 2026.                                                                                |

**2. Work Breakdown Structure (WBS)**

- 1.0 Literature & Scope

  - 1.1 Confirm scope (MCP-only) and refine research question

  - 1.2 Ethics sign-off for sandboxed, synthetic-data study

- 2.0 Testbed & Data

  - 2.1 Stand up MCP client/server reference implementation

  - 2.2 Implement tool-poisoning and rug-pull attack scenarios

  - 2.3 Generate labelled synthetic attack corpus

  - 2.4 Implement baseline schema-validation defense

- 3.0 Detection Model

  - 3.1 Feature engineering on tool-call metadata / description-change patterns

  - 3.2 Train candidate anomaly-detection models

  - 3.3 Select final model configuration

- 4.0 Evaluation & Analysis

  - 4.1 Run comparative evaluation vs. baseline

  - 4.2 Analyze results and document limitations

- 5.0 Write-up

  - 5.1 Full draft

  - 5.2 Supervisor feedback and revision

  - 5.3 Final formatting and submission

**3. Timeline — Deliverables, Milestones, Checkpoints, Resources**

| **Week(s)** | **Milestone / checkpoint**                                                 | **Key resource needed**                      |
|-------------|----------------------------------------------------------------------------|----------------------------------------------|
| W1-2        | Milestone: scope confirmed; ethics sign-off obtained                       | Supervisor time                              |
| W2-4        | Checkpoint: testbed runs a benign tool call end-to-end                     | Dev machine, open-source MCP client/server   |
| W4-6        | Milestone: labelled attack corpus complete; baseline validator implemented | MCP threat-pattern references (CVE reports)  |
| W6-8        | Checkpoint: first trained model produces a result on held-out data         | Python ML libraries (scikit-learn / PyTorch) |
| W9-10       | Milestone: comparative evaluation complete                                 | Testbed + trained model from prior weeks     |
| W11         | Checkpoint: results analysed, limitations documented                       | —                                            |
| W12         | Milestone: full draft complete                                             | Supervisor review slot                       |
| W13         | Milestone: final submission (25 Oct 2026)                                  | —                                            |

**Gantt chart:**

| **Activity**                                        | **W1** | **W2** | **W3** | **W4** | **W5** | **W6** | **W7** | **W8** | **W9** | **W10** | **W11** | **W12** | **W13** |
|-----------------------------------------------------|--------|--------|--------|--------|--------|--------|--------|--------|--------|---------|---------|---------|---------|
| Literature review & scope confirmation              |        |        |        |        |        |        |        |        |        |         |         |         |         |
| Ethics sign-off (sandboxed, synthetic data)         |        |        |        |        |        |        |        |        |        |         |         |         |         |
| MCP testbed setup (client/server harness)           |        |        |        |        |        |        |        |        |        |         |         |         |         |
| Attack corpus generation (tool poisoning, rug-pull) |        |        |        |        |        |        |        |        |        |         |         |         |         |
| Baseline schema-validator implementation            |        |        |        |        |        |        |        |        |        |         |         |         |         |
| Anomaly-detection model design & training           |        |        |        |        |        |        |        |        |        |         |         |         |         |
| Evaluation vs. baseline defense                     |        |        |        |        |        |        |        |        |        |         |         |         |         |
| Analysis of results & limitations                   |        |        |        |        |        |        |        |        |        |         |         |         |         |
| Full draft write-up                                 |        |        |        |        |        |        |        |        |        |         |         |         |         |
| Supervisor feedback & revision                      |        |        |        |        |        |        |        |        |        |         |         |         |         |
| Final formatting & submission (Oct 25)              |        |        |        |        |        |        |        |        |        |         |         |         |         |

**4. Evaluating Resources Against the Plan**

All required resources (a development machine, an open-source MCP reference implementation, and standard Python ML libraries) are already available with no procurement lead time, which supports the compressed 13-week schedule. The tightest point is weeks 6-8, where model design and training happen in parallel with corpus generation finishing, if model training overruns, the fallback is to use a simpler model family (e.g., gradient-boosted trees over hand-engineered features) rather than a more complex architecture, which keeps the evaluation deliverable achievable without slipping the deadline.

**5. Review and Re-evaluation**

The plan will be reviewed at each milestone checkpoint (end of weeks 2, 4, 6, 8, 10) against actual progress. If the testbed or corpus generation phase overruns by more than a few days, the model complexity will be reduced first (Section 4) before the evaluation or write-up phases are compressed, since the comparative evaluation and final report are the non-negotiable deliverables for the 25 October deadline.
