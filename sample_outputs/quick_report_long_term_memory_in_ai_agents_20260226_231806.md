# Research Gap Analysis: Long-Term Memory in AI Agents

---

## 1. Executive Summary

Long-term memory in AI agents has emerged as a critical research frontier, with recent work spanning RAG-based architectures [5], episodic memory systems [6], and embodied agent memory frameworks [1]. However, the field remains fragmented: LLM agent memory research and continual/lifelong learning research have developed largely in parallel, leaving fundamental questions about knowledge accumulation, forgetting, and memory management in long-running agents unresolved [4], [13]. This report identifies seven actionable research gaps and fourteen testable hypotheses to guide the next generation of memory-augmented AI agent research.

---

## 2. Research Landscape

The study of long-term memory in AI agents spans several overlapping research communities, each contributing partial solutions to a shared problem.

- **LLM Agent Memory Architectures:** Recent systems such as KARMA [1], WebATLAS [2], and IMDMR [3] have demonstrated that augmenting language model agents with explicit memory stores—combining short- and long-term components—substantially improves task performance across conversational and web-based settings. Cognitive architecture frameworks [4] provide theoretical scaffolding for how memory subsystems (working, episodic, semantic, procedural) should interact within language agents.

- **RAG and Episodic Memory:** Retrieval-Augmented Generation has become a dominant paradigm for grounding LLM responses in stored knowledge [5]. Recent work has extended RAG toward episodic memory representations that capture richer contextual and experiential information [6], moving beyond simple fact retrieval toward more human-like memory organization.

- **Continual and Lifelong Learning:** A substantial body of work addresses catastrophic forgetting in neural networks [13], including synaptic stabilization methods [17], generative replay strategies [14], modulating masks for knowledge sharing [19], and gradient-based lifelong learning approaches [20]. Lifelong supervised and reinforcement learning frameworks [22], [23], [24] provide formal treatments of knowledge accumulation over sequential tasks.

- **Embodied and RL Agents:** Embodied agent memory [1] and lifelong reinforcement learning [15], [21], [24] represent specialized settings where memory must support not only knowledge retrieval but also planning, skill retention, and adaptation to non-stationary environments.

- **Evaluation and Benchmarking:** Existing benchmarks for agent memory are largely task-specific and short-horizon [7], [22], [23], making it difficult to assess true long-term retention or compare memory architectures systematically.

Despite progress within each of these threads, they remain poorly integrated. The following gap analysis identifies where these communities must converge to advance the field.

---

## 3. Gap Analysis

### 3.1 Integration Gaps

---

#### Gap 1: Integration of Continual Learning into LLM Agent Memory Systems

**Description:**
LLM agent memory research and continual/lifelong learning research exist as largely separate bodies of work. There is a critical gap in integrating continual learning techniques directly into the long-term memory architectures of LLM-based agents, so that agents can accumulate knowledge over time without forgetting earlier experiences.

**Evidence:**
- Systems such as KARMA [1], WebATLAS [2], and IMDMR [3] demonstrate sophisticated memory architectures for LLM agents but do not address the problem of catastrophic forgetting as agents encounter new tasks or information streams.
- Cognitive architecture frameworks [4] acknowledge the need for persistent memory but do not specify mechanisms for preventing knowledge degradation over time.
- Catastrophic forgetting is well-documented in neural networks [13], and mitigation strategies—including synaptic stabilization [17], modulating masks for shared lifelong RL knowledge [19], and task-based accumulated gradients [20]—have been validated in continual learning settings but have not been adapted for LLM agent memory pipelines.
- The absence of this integration means that current LLM agents cannot reliably accumulate knowledge across extended deployment horizons without overwriting or degrading earlier memories.

---

#### Gap 2: Uncertainty-Aware Memory Retrieval in LLM Agents

**Description:**
Current LLM agent memory retrieval systems treat all stored memories as equally reliable, without accounting for uncertainty arising from memory age, source reliability, or conflicts with newer information. Incorporating uncertainty quantification into memory retrieval pipelines could significantly improve agent decision-making.

**Evidence:**
- IMDMR [3] and RAG-based memory architectures [5] rely on similarity-based retrieval that does not distinguish between reliable, outdated, or conflicting memories.
- Episodic memory systems [6] introduce richer memory representations but do not provide calibrated confidence estimates for retrieved memories.
- Uncertainty-aware neural architectures—such as those using Gaussian Radial Basis Functions for feature importance [9] and dual accuracy-quality-driven networks for prediction interval generation [11]—demonstrate that uncertainty quantification is tractable in neural systems, yet this capability has not been connected to agent memory retrieval.
- The result is that agents may act on stale or contradictory memories with the same confidence as on reliable, recent ones, leading to systematic decision errors in long-running deployments.

---

### 3.2 Topical Gaps

---

#### Gap 3: Long-Term Memory Consolidation and Forgetting in LLM Agents

**Description:**
While catastrophic forgetting is well-studied in neural networks and continual learning settings, its manifestation in LLM agents with explicit memory stores (e.g., RAG-based or episodic memory) is largely unexplored. It is unclear how LLM agents should selectively consolidate, prune, or update long-term memories over extended interaction horizons—a direct analog to the stability-plasticity dilemma.

**Evidence:**
- IMDMR [3] and RAG-based memory systems [5] provide mechanisms for memory storage and retrieval but lack principled policies for memory consolidation or pruning over time.
- Episodic memory approaches [6] introduce more structured memory organization but do not address how memories should be selectively retained or discarded as the memory store grows.
- Catastrophic forgetting [13] and its mitigation via context-dependent gating and synaptic stabilization [17] are well-understood in the continual learning literature, as is generative replay in self-organizing maps [14].
- Lifelong supervised learning frameworks [22] formalize the stability-plasticity dilemma but do not translate these insights to LLM agents with explicit, queryable memory stores.
- Without consolidation mechanisms, LLM agent memory stores risk either unbounded growth or indiscriminate overwriting of valuable earlier knowledge.

---

#### Gap 4: Cross-Agent and Shared Long-Term Memory

**Description:**
Research on long-term memory in AI agents almost exclusively focuses on single-agent settings. There is a significant gap in understanding how long-term memories can be shared, transferred, or collaboratively maintained across multiple agents—enabling collective knowledge accumulation analogous to human social learning.

**Evidence:**
- KARMA [1], WebATLAS [2], IMDMR [3], and cognitive architecture frameworks [4] all treat memory as a property of individual agents, with no mechanisms for inter-agent memory sharing or transfer.
- Modulating masks for lifelong RL [19] and lifelong learning using eigentasks [21] demonstrate that knowledge transfer between learning systems is feasible, but these approaches have not been extended to shared memory stores in multi-agent LLM settings.
- The absence of shared memory protocols means that multiple agents solving related tasks must independently re-learn the same knowledge, representing a significant inefficiency and a missed opportunity for collective intelligence.

---

### 3.3 Methodological Gaps

---

#### Gap 5: Standardized Benchmarks for Long-Term Memory in AI Agents

**Description:**
There is a lack of standardized, longitudinal benchmarks specifically designed to evaluate long-term memory capabilities in AI agents. Existing evaluations are task-specific or short-horizon, making it difficult to compare memory architectures or measure true long-term retention, generalization, and retrieval fidelity.

**Evidence:**
- KARMA [1] and WebATLAS [2] evaluate memory systems on specific task domains (embodied navigation and web interaction, respectively) without longitudinal or cross-domain assessment.
- Persona-driven benchmarking [7] advances evaluation methodology for generalized AI but does not specifically target long-term memory retention or retrieval fidelity over extended horizons.
- Lifelong supervised learning frameworks [22] and latent properties of lifelong learning systems [23] provide formal evaluation criteria for continual learning but have not been instantiated as standardized benchmarks for LLM agent memory.
- The absence of shared benchmarks prevents systematic comparison of memory architectures and obscures which design choices genuinely improve long-term memory performance.

---

### 3.4 Scope Gaps

---

#### Gap 6: Long-Term Memory in Embodied and Reinforcement Learning Agents

**Description:**
Most LLM agent memory research focuses on conversational or web-based agents. There is a significant gap in understanding how long-term memory systems should be designed for embodied agents and reinforcement learning agents that must act in dynamic, non-stationary environments over extended time horizons, where memory must support both planning and skill retention.

**Evidence:**
- KARMA [1] is a notable exception, addressing embodied agent memory, but its focus on short- and long-term memory integration does not fully address the challenges of non-stationary environments or lifelong skill retention.
- Cognitive architecture frameworks [4] discuss memory in the context of language agents but do not provide concrete designs for embodied or RL settings.
- Scalable continual RL frameworks [15] and model-free generative replay for lifelong RL [24] address knowledge retention in RL agents but do not incorporate explicit long-term memory stores of the kind used in LLM agents.
- Lifelong learning using eigentasks [21] demonstrates skill separation and transfer in sequential RL but does not connect these capabilities to explicit memory architectures.
- The result is that embodied and RL agents lack principled long-term memory designs that can support both planning over extended horizons and retention of previously acquired skills.

---

### 3.5 Temporal Gaps

---

#### Gap 7: Temporal Decay and Memory Staleness in Long-Running Agents

**Description:**
As AI agents operate over long time horizons, stored memories become stale or contextually irrelevant. There is little research on how to model temporal decay of memory relevance, when to expire or update memories, and how to handle contradictions between old and new information—a problem distinct from but related to catastrophic forgetting.

**Evidence:**
- KARMA [1] and WebATLAS [2] implement memory systems without explicit mechanisms for modeling the temporal relevance of stored memories or detecting when memories have become outdated.
- Cognitive architecture frameworks [4] and RAG-based memory systems [5] do not address temporal decay or contradiction resolution as first-class design concerns.
- Task-based accumulated gradients [20] and lifelong learning using eigentasks [21] manage knowledge evolution in continual learning but focus on model parameters rather than explicit, queryable memory entries.
- Lifelong supervised learning frameworks [22] acknowledge that knowledge relevance changes over time but do not provide concrete mechanisms for memory staleness modeling in LLM agents.
- Without temporal decay and contradiction-awareness, long-running agents risk making decisions based on outdated or internally inconsistent knowledge, with no mechanism to detect or correct these errors.

---

## 4. Suggested Hypotheses

---

### H1: Synaptic Stabilization Mechanisms Reduce Catastrophic Forgetting in LLM Agent Memory

**Description:**
Integrating synaptic stabilization techniques (e.g., Elastic Weight Consolidation or Synaptic Intelligence) into the memory update mechanisms of LLM-based agents will significantly reduce catastrophic forgetting of earlier experiences while preserving the agent's ability to acquire new knowledge. By selectively protecting memory parameters or embeddings critical to previously learned tasks, agents can maintain stable long-term knowledge without sacrificing plasticity for new interactions.

**Suggested Methodology:**
Implement EWC or Synaptic Intelligence within the memory encoder and retrieval layers of an existing LLM agent framework (e.g., KARMA or a RAG-based agent). Train agents sequentially on a series of diverse tasks and measure forward/backward transfer, retention accuracy, and task performance degradation over time. Compare against baseline agents without continual learning integration and against generative replay baselines using standardized sequential task benchmarks.

---

### H2: Generative Replay of Episodic Memories Enables Lifelong Knowledge Accumulation in LLM Agents

**Description:**
Incorporating a generative replay module—where the LLM agent periodically synthesizes and rehearses pseudo-memories of past experiences—into its long-term memory architecture will enable continual accumulation of knowledge across extended interaction horizons without catastrophic forgetting. This mirrors the complementary learning systems theory in neuroscience and adapts it to the LLM agent setting.

**Suggested Methodology:**
Design a generative replay component (using a smaller auxiliary generative model or the LLM itself) that samples and reconstructs past episodic memories during idle or low-activity periods. Integrate this into an LLM agent's memory pipeline and evaluate on a lifelong agent benchmark spanning hundreds of interaction sessions. Measure memory retention fidelity, task performance on old versus new tasks, and computational overhead compared to agents using no replay or exact experience replay.

---

### H3: Importance-Weighted Memory Consolidation Mitigates the Stability-Plasticity Dilemma in LLM Agents

**Description:**
Applying an importance-weighting scheme—analogous to memory consolidation in biological systems—to selectively retain, prune, or update entries in an LLM agent's explicit memory store will effectively balance stability and plasticity over extended interaction horizons. Memories deemed highly relevant or frequently accessed would be consolidated, while stale or low-utility memories would be pruned.

**Suggested Methodology:**
Develop an importance scoring function combining recency, access frequency, and semantic relevance to govern memory consolidation and pruning decisions in an LLM agent's memory store. Deploy agents in long-horizon dialogue and task-completion environments over simulated months of interaction. Evaluate using metrics for knowledge retention (accuracy on historical queries), adaptability to new information, and memory store efficiency. Ablate individual importance factors to identify their relative contributions.

---

### H4: Selective Memory Replay Schedules Preserve Earlier Knowledge in Long-Horizon LLM Agents

**Description:**
Scheduling periodic, selective replay of older memory entries—prioritized by their utility and recency gap—will prevent the degradation of earlier knowledge in LLM agents operating over extended time horizons, directly addressing the stability-plasticity dilemma in explicit memory stores.

**Suggested Methodology:**
Implement a replay scheduler within an LLM agent's memory management module that periodically retrieves and re-encodes a subset of older memories based on a prioritized experience replay strategy. Test across long-horizon conversational and task-based benchmarks. Measure the agent's ability to answer queries about early versus recent interactions, and compare against agents using FIFO memory eviction, random pruning, or no memory management.

---

### H5: A Longitudinal Multi-Domain Benchmark Reveals Systematic Gaps in LLM Agent Long-Term Memory

**Description:**
Constructing a standardized, longitudinal benchmark—spanning multiple domains, interaction types, and time horizons—will expose systematic weaknesses in current LLM agent memory architectures that short-horizon evaluations fail to detect, and will enable rigorous, reproducible comparison of memory systems across the research community.

**Suggested Methodology:**
Design and release a benchmark suite (e.g., *LongMemBench*) comprising sequential interaction episodes across domains such as personal assistance, scientific research, and customer support, with evaluation metrics for retention accuracy, retrieval fidelity, generalization to novel queries, and temporal consistency. Include both automated metrics and human evaluation protocols. Baseline multiple existing memory architectures (RAG, episodic, KARMA-style) and publish a public leaderboard to encourage community participation.

---

### H6: Simulated Long-Horizon Interaction Environments Expose Retrieval Fidelity Degradation in Agent Memory

**Description:**
Purpose-built simulation environments that compress long-horizon agent interactions (e.g., simulating years of agent deployment in accelerated time) will reveal measurable degradation in retrieval fidelity and generalization that is invisible in current short-horizon evaluations, motivating new memory architecture designs.

**Suggested Methodology:**
Develop a simulation framework that generates synthetic long-horizon interaction logs with controlled knowledge evolution (facts that change, accumulate, or become contradictory over time). Evaluate LLM agents with various memory architectures on retrieval accuracy, contradiction detection, and cross-temporal generalization at multiple time-horizon checkpoints. Use the simulation to identify failure modes and correlate them with specific architectural choices.

---

### H7: Hierarchical Long-Term Memory Architectures Improve Planning and Skill Retention in Embodied RL Agents

**Description:**
Embodied RL agents equipped with hierarchical long-term memory systems—separating episodic (event-based) from semantic (skill/knowledge-based) memory—will demonstrate superior planning performance and skill retention in dynamic, non-stationary environments compared to agents using flat or no long-term memory.

**Suggested Methodology:**
Design a hierarchical memory module with distinct episodic and semantic memory stores, integrated into an embodied RL agent (e.g., in a 3D navigation or manipulation environment such as Habitat or MiniGrid). Train agents over extended, non-stationary task sequences and evaluate on task success rate, skill transfer efficiency, and memory retrieval latency. Compare against agents with flat memory, no memory, and standard recurrent architectures (e.g., LSTM-based agents).

---

### H8: Memory-Augmented Lifelong RL Agents Outperform Memoryless Baselines in Non-Stationary Environments

**Description:**
Lifelong reinforcement learning agents augmented with explicit long-term memory stores—capable of storing and retrieving past policies, environmental observations, and reward signals—will significantly outperform memoryless or short-memory baselines in non-stationary environments by leveraging historical experience for faster adaptation.

**Suggested Methodology:**
Integrate an external long-term memory module (e.g., a differentiable key-value memory or episodic buffer) into a standard RL agent (e.g., PPO or SAC). Evaluate in non-stationary environments with periodic task shifts (e.g., ContinualWorld or custom MuJoCo task sequences). Measure cumulative reward, adaptation speed after task shifts, and skill retention across tasks. Ablate memory capacity, retrieval mechanisms, and update frequencies to identify optimal configurations.

---

### H9: Uncertainty-Aware Retrieval Scoring Improves Decision Quality in LLM Agents with Stale or Conflicting Memories

**Description:**
Augmenting LLM agent memory retrieval pipelines with uncertainty quantification—assigning confidence scores to retrieved memories based on their age, source reliability, and consistency with current context—will lead to measurably better decision-making compared to agents that treat all retrieved memories as equally reliable.

**Suggested Methodology:**
Develop an uncertainty scoring module that estimates memory reliability using factors such as temporal decay, retrieval frequency, source provenance, and semantic consistency with recent observations. Integrate this module into an LLM agent's RAG-based memory pipeline. Evaluate on tasks requiring agents to navigate conflicting or outdated information (e.g., fact-changing QA, evolving knowledge graphs). Measure decision accuracy, calibration (ECE), and robustness to memory corruption compared to agents using standard similarity-based retrieval.

---

### H10: Bayesian Memory Retrieval Frameworks Enable Calibrated Uncertainty Estimation in LLM Agent Decision-Making

**Description:**
Replacing point-estimate similarity-based retrieval in LLM agent memory systems with a Bayesian retrieval framework—which maintains posterior distributions over memory relevance and reliability—will yield better-calibrated uncertainty estimates and improved agent performance on tasks where memory reliability is variable.

**Suggested Methodology:**
Formulate memory retrieval as Bayesian inference, where the posterior over relevant memories is updated based on prior reliability estimates and current query evidence. Implement this using approximate inference methods (e.g., variational inference or Monte Carlo sampling over memory embeddings). Benchmark on knowledge-intensive NLP tasks with injected noise and contradictions. Evaluate calibration, retrieval precision/recall, and downstream task accuracy versus deterministic retrieval baselines.

---

### H11: Exponential Temporal Decay Functions Improve Memory Relevance Estimation in Long-Running LLM Agents

**Description:**
Modeling memory relevance as an exponentially decaying function of time—parameterized by memory type and domain—will allow LLM agents to more accurately prioritize recent, contextually relevant memories over stale ones, reducing decision errors caused by outdated information in long-running deployments.

**Suggested Methodology:**
Implement a temporal decay scoring layer within an LLM agent's memory retrieval system, where each memory entry's relevance score is modulated by a learned or heuristic decay function. Train and evaluate agents in simulated long-running environments where facts change over time (e.g., dynamic knowledge bases or evolving user preferences). Measure retrieval accuracy for time-sensitive queries, contradiction detection rates, and overall task performance. Compare exponential, linear, and step-function decay models against no-decay baselines.

---

### H12: Contradiction-Aware Memory Update Policies Prevent Knowledge Degradation in Long-Horizon Agents

**Description:**
Equipping LLM agents with explicit contradiction detection and resolution policies—triggered when new information conflicts with existing memory entries—will prevent the accumulation of inconsistent knowledge and improve long-term decision reliability compared to agents that naively append new memories without conflict resolution.

**Suggested Methodology:**
Design a contradiction detection module (using NLI models or LLM-based consistency checking) that flags conflicting memory entries upon new information ingestion. Implement resolution strategies (e.g., recency-wins, confidence-weighted merging, or flagging for human review) and integrate into an agent's memory management pipeline. Evaluate on long-horizon tasks with deliberately introduced contradictory information streams. Measure contradiction resolution accuracy, downstream task performance, and memory store consistency over time.

---

### H13: Federated Long-Term Memory Sharing Enables Collective Knowledge Accumulation Across LLM Agent Networks

**Description:**
A federated memory sharing protocol—where multiple LLM agents asynchronously contribute to and retrieve from a shared long-term memory store while preserving privacy and managing conflicting contributions—will enable collective knowledge accumulation that significantly outperforms isolated single-agent memory systems on complex, distributed tasks.

**Suggested Methodology:**
Design a federated memory architecture with a shared memory server and local agent memory caches. Implement conflict resolution and provenance tracking for shared memories. Deploy multiple LLM agents on complementary subtasks (e.g., distributed web research or collaborative scientific literature review) and evaluate collective task performance, knowledge coverage, and retrieval accuracy versus single-agent baselines. Assess scalability with increasing numbers of agents and analyze the impact of memory conflict resolution strategies.

---

### H14: Memory Transfer Protocols Between Heterogeneous Agents Accelerate Skill Acquisition via Social Learning

**Description:**
Structured memory transfer protocols—allowing agents to selectively share and adapt memories from other agents with different architectures or specializations—will accelerate skill acquisition and knowledge generalization in multi-agent systems, analogous to social learning in humans.

**Suggested Methodology:**
Develop a memory transfer protocol that encodes agent memories into a shared, architecture-agnostic representation (e.g., natural language summaries or standardized embedding spaces). Implement selective transfer mechanisms where receiving agents filter and integrate shared memories based on relevance and source credibility. Evaluate in a multi-agent collaborative environment (e.g., multi-agent MiniWoB++ or cooperative text-based games) measuring task performance improvement, knowledge transfer efficiency, and generalization to novel tasks. Compare against no-transfer and full-memory-sharing baselines.

---

## 5. Key References

- [1] KARMA: Augmenting Embodied AI Agents with Long-and-short Term Memory Systems (2024). https://arxiv.org/pdf/2409.14908v2
- [2] WebATLAS: An LLM Agent with Experience-Driven Memory and Action Simulation (2025). https://arxiv.org/pdf/2510.22732v2
- [3] IMDMR: An Intelligent Multi-Dimensional Memory Retrieval System for Enhanced Conversational AI (2025). https://arxiv.org/pdf/2511.05495v1
- [4] Cognitive Architectures for Language Agents (2023). https://arxiv.org/pdf/2309.02427v3
- [5] RAG-Driven Memory Architectures in Conversational LLMs—A Literature Review With Insights Into Emerging Agriculture Data Sharing (2025). https://doi.org/10.1109/access.2025.3589241
- [6] Beyond Fact Retrieval: Episodic Memory for RAG with Generative Semantic Workspaces (2025). https://arxiv.org/pdf/2511.07587v2
- [7] Persona-Driven Benchmarking for Generalizable and Human-Aware Artificial General Intelligence (2022). https://doi.org/10.48550/arxiv.2210.03629
- [8] Continual Learning for Recurrent Neural Networks: an Empirical Evaluation (2021). https://arxiv.org/pdf/2103.07492v4
- [9] Learning Active Subspaces and Discovering Important Features with Gaussian Radial Basis Functions Neural Networks (2023). https://arxiv.org/pdf/2307.05639v2
- [10] A Recurrent Probabilistic Neural Network with Dimensionality Reduction Based on Time-series Discriminant Component Analysis (2019). https://arxiv.org/pdf/1911.06009v1
- [11] Dual Accuracy-Quality-Driven Neural Network for Prediction Interval Generation (2022). https://arxiv.org/pdf/2212.06370v4
- [12] The Deep Arbitrary Polynomial Chaos Neural Network or how Deep Artificial Neural Networks could benefit from Data-Driven Homogeneous Chaos Theory (2023). https://arxiv.org/pdf/2306.14753v1
- [13] Measuring Catastrophic Forgetting in Neural Networks (2018). https://doi.org/10.1609/aaai.v32i1.11651
- [14] Reducing Catastrophic Forgetting in Self Organizing Maps with Internally-Induced Generative Replay (Student Abstract) (2022). https://doi.org/10.1609/aaai.v36i11.21671
- [15] SCRIPT: A Scalable Continual Reinforcement Learning Framework for Autonomous Penetration Testing (2025). https://doi.org/10.1016/j.eswa.2025.127827
- [16] A survey on data‐efficient algorithms in big data era (2021). https://doi.org/10.1186/s40537-021-00419-9
- [17] Alleviating catastrophic forgetting using context-dependent gating and synaptic stabilization (2018). https://doi.org/10.1073/pnas.1803839115
- [18] Intervention strategies to improve nutrition and health behaviours before conception (2018). https://doi.org/10.1016/s0140-6736(18)30313-1
- [19] Sharing Lifelong Reinforcement Learning Knowledge via Modulating Masks (2023). https://arxiv.org/pdf/2305.10997v1
- [20] TAG: Task-based Accumulated Gradients for Lifelong learning (2021). https://arxiv.org/pdf/2105.05155v3
- [21] Lifelong Learning using Eigentasks: Task Separation, Skill Acquisition, and Selective Transfer (2020). https://arxiv.org/pdf/2007.06918v1
- [22] An Introduction to Lifelong Supervised Learning (2022). https://arxiv.org/pdf/2207.04354v2
- [23] Latent Properties of Lifelong Learning Systems (2022). https://arxiv.org/pdf/2207.14378v1
- [24] Model-Free Generative Replay for Lifelong Reinforcement Learning: Application to Starcraft-2 (2022). https://arxiv.org/pdf/2208.05056v2
