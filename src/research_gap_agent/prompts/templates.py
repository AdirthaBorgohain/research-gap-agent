"""Prompt template constants for LLM calls."""

QUERY_DECOMPOSITION_PROMPT = """You are a research librarian. Given the user's research domain or question, produce 3-5 orthogonal search queries to run against academic paper databases (Semantic Scholar, OpenAlex, arXiv). Each query should capture a different angle: main topic, synonyms, related subfields, or key methods.

User input: {query}

Output a list of 3-5 search query strings (each will be run against multiple APIs).
"""

RELEVANCE_SCORING_PROMPT = """You are evaluating how relevant each academic paper is to a research question. Score each paper from 0.0 (not relevant) to 1.0 (highly relevant) based on title and abstract only.

Research question: {query}

Papers (one per line, format "INDEX. TITLE | ABSTRACT"):
{papers_text}

Return a JSON object mapping each paper index (as string) to a number in [0.0, 1.0]. Example: {{"0": 0.9, "1": 0.3}}
"""

TOPIC_CLUSTERING_PROMPT = """You are grouping academic papers into thematic clusters for literature analysis. Given the list of papers (title and abstract), assign each paper to exactly one cluster. Produce {min_clusters}-{max_clusters} clusters. Each cluster should have a short label and a one-sentence description. Output the cluster label, description, and the list of paper indices (0-based) belonging to that cluster.

Papers:
{papers_text}

Return a list of clusters. Each cluster: label (string), description (string), paper_indices (list of integers).
"""

DEEP_ANALYSIS_PROMPT = """Analyze this cluster of academic papers in depth.

Cluster label: {cluster_label}

Papers in this cluster (numbered 1, 2, ... for citation; use these numbers in findings.paper_numbers):
{papers_text}

For this cluster, provide:
1. Methodologies: What methods, frameworks, or approaches are used across these papers?
2. Findings: Synthesize the main findings. For each finding, list the paper number(s) that support it (1 = first paper above, 2 = second, etc.). Use paper_numbers so claims can be attributed to specific papers.
3. Limitations: What limitations do the authors state?
4. Trend: Is attention to this topic "increasing", "stable", "decreasing", or "unknown" over time?
5. Contradictions: Any conflicting findings or claims across the papers?

Be concise but evidence-based. Every finding should have at least one supporting paper number when possible.
"""

GAP_FINDER_PROMPT = """You are a research analyst identifying gaps in the literature. Based on the following cluster analyses (each summarizing a group of related papers), identify research gaps. Consider these gap types:
- topic: Under-explored sub-topics or questions
- methodological: Methods not yet applied, or methodological limitations
- scope: Populations, settings, or domains not covered
- temporal: Outdated assumptions, or need for replication in new context
- contradiction: Conflicting results that need resolution
- integration: Lack of integration across fields or findings

Cluster analyses:
{cluster_analyses_text}

Original research question: {query}

Analyzed papers (you may ONLY cite these; use the number as the 1-based index):
{citation_list}

For each gap provide: title, description, gap_type (one of the six), evidence (short quotes or references), supporting_paper_indices (list of paper numbers from the list above, 1-based; only use numbers that appear in the analyzed papers list). Output a list of research gaps. Focus on the most actionable 3-8 gaps.
"""

HYPOTHESIS_GENERATION_PROMPT = """For each research gap below, suggest 1-2 actionable follow-up hypotheses that could address the gap.

Research gaps:
{gaps_text}

For each hypothesis provide: title, description, related_gap_title (must match one of the gap titles above), suggested_methodology. Output a list of hypotheses.
"""

REPORT_WRITING_PROMPT = """Compile a structured markdown report for the research gap analysis.

Research question: {query}

Analyzed papers (cite ONLY using these numbers as [1], [2], etc.; do not invent any reference):
{citation_list}

Findings with supporting citations (when describing specific findings or evidence in sections 2–3, use the citation keys listed for each finding so that claims are attributed to the correct papers):
{findings_citations_text}

Research gaps identified (each line includes the supporting citations to use in the narrative):
{gaps_text}

Hypotheses suggested:
{hypotheses_text}

In the body of the report, cite papers using [1], [2], etc. Only use numbers from 1 to {n_papers}. Do not invent references. Weave in the supporting citations for each gap where appropriate. When describing specific findings or evidence, use the citation keys listed for each finding above so that claims are attributed to the correct papers.

Write a single markdown document with these sections (do NOT write section 5 Key References; it will be added automatically):
1. Executive Summary (2-3 sentences; cite key papers where relevant)
2. Research Landscape (brief overview; cite using the findings and their supporting citation keys above)
3. Gap Analysis (organize by gap type; for each gap: title, description, evidence with in-line citations and the citation keys shown for that gap)
4. Suggested Hypotheses (for each: title, description, suggested methodology)
5. (Omit — will be inserted automatically)

Use clear headings (##) and bullet points. Keep the report concise and actionable.
"""
