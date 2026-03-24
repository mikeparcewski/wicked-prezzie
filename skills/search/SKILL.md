---
name: search
description: |
  Context-aware search across indexed source documents. Adapts search strategy
  based on what's being built (deck type, audience, phase). Dispatches research
  agents that choose their own search approach.

  Use when: "find information about", "search sources", "what do we know about",
  "look up", "find evidence for", "search for data on"
---

# search — Context-Aware Search

Dispatch-based search skill that reads project context from `deck-state.json` and
adapts its search strategy to the type of deck being built. Instead of running a
single flat query, it dispatches 1-2 research agents with different scopes, then
merges and deduplicates the results.

---

## When to Use

- When building slides and you need facts, stories, or evidence from indexed sources.
- When the user asks "what do we know about X" or "find data on Y".
- When a brainstorm or build agent needs grounded content from source documents.
- When `wicked-prezzie:ask` is too heavy (ask runs a full 4-stage pipeline; search is a lighter single-pass lookup).

**Prerequisite**: Source documents must be indexed via `wicked-prezzie:learn`. If no
index exists, warn the user and recommend running learn first.

---

## Context-Aware Strategy Selection

On invocation, read `deck-state.json` (if it exists) to determine the deck type,
audience, current phase, and active workflow template. Adapt search strategy
accordingly:

| Deck Type | Primary Search Targets | Default Scopes |
|-----------|----------------------|----------------|
| **Board deck** | Metrics, outcomes, financial data, governance decisions | `facts` + `evidence` |
| **Training deck** | Examples, explanations, step-by-step processes, definitions | `narrative` + `context` |
| **Conference talk** | Stories, data points, surprising findings, quotable stats | `narrative` + `facts` |
| **Competitive analysis** | Differentiators, comparisons, market data, win/loss patterns | `facts` + `evidence` |
| **Executive briefing** | Decisions needed, risks, recommendations, status summaries | `facts` + `context` |
| **Project status** | Milestones, blockers, metrics, timelines, dependencies | `facts` + `evidence` |
| **General / unknown** | Broad search across all scopes | `facts` + `narrative` |

If `deck-state.json` does not exist or lacks a deck type, fall back to the general
strategy. Never fail because context is missing — degrade gracefully.

---

## Four Source Scopes

Every search targets one or more of these scopes, which map to different parts
of the learn index:

| Scope | What It Searches | Index Locations |
|-------|-----------------|-----------------|
| `facts` | Hard data: numbers, dates, metrics, named systems, financial figures | `_insights/key-facts.md`, `_tags/financial.md`, `_tags/metrics.md`, chunk frontmatter with `type: data` |
| `narrative` | Themes, stories, arcs, positioning language, qualitative insights | `_insights/narrative-themes.md`, `_tags/theme-*.md`, chunks with `type: narrative` |
| `evidence` | Proof points: case studies, benchmarks, testimonials, before/after comparisons | `_tags/evidence.md`, `_tags/proof.md`, chunks with `type: case-study` or `type: benchmark` |
| `context` | Background: industry context, definitions, history, organizational structure | `_relationships/`, `_tags/background.md`, chunks with `type: context` |

---

## Invocation Modes

### Scope-Prefixed (Single Agent)

A scope prefix forces a single-agent search in that scope only. This is the
fastest path when you know exactly what you need.

```
search("facts: Q3 revenue growth")        → searches facts scope only
search("narrative: digital transformation") → searches narrative scope only
search("evidence: network uptime SLA")     → searches evidence scope only
search("context: organizational structure") → searches context scope only
search("tag: financial")                   → searches a specific tag index directly
search("entity: CloudNet")                → searches for a specific named entity across all chunks
```

### Parallel Mode (Default)

Without a scope prefix, search dispatches 2 agents in parallel with different
scopes (selected based on deck type). Each agent independently searches the
index and returns ranked results. The orchestrator merges and deduplicates
by chunk ID.

```
search("network automation capabilities")
  → Agent 1: facts scope (metrics, named systems, SLA data)
  → Agent 2: narrative scope (themes, positioning, qualitative insights)
  → Merge: deduplicate by chunk ID, rank by relevance
```

---

## Agent Prompt Template

Each dispatched agent receives this prompt structure:

```
## Your Role
Research agent searching indexed source documents.

## Search Query
{user_query}

## Scope
{scope} — {scope_description}

## Deck Context
Type: {deck_type}
Audience: {audience}
Phase: {current_phase}

## Strategy Selection
Choose the best approach for this query:
1. Entity-first: Start with _relationships/, then fan out to chunks mentioning the entity
2. Tag-first: Start with _tags/{relevant_tag}.md, then read linked chunks
3. Insight-first: Start with _insights/, use key-facts or narrative-themes as entry point
4. Content grep: Search chunk content directly for keywords (fallback when structured entry points miss)
5. Hybrid: Combine two approaches (e.g., tag-first + content grep)

State which strategy you chose and why before presenting results.

## Output Format
Return results as:
RESULTS:
- chunk_id: {id}, source: {document}, relevance: {high|medium|low}
  excerpt: {key passage, max 3 sentences}
  ...

CORRELATION:
{how these results connect to each other and to the deck context}

RELATED:
{other search queries that would complement this one}
```

---

## Output Contract

Every search invocation returns three blocks:

1. **RESULTS** — Ranked list of matching chunks with source attribution, chunk ID,
   and a brief excerpt. Deduplicated by chunk ID when running parallel mode.

2. **CORRELATION** — How the results connect to each other and to the current deck
   context. This is the synthesis value: not just "here are 5 chunks" but "chunks
   2 and 4 tell a consistent story about X, while chunk 3 contradicts them on Y."

3. **RELATED** — 2-3 follow-up search queries that would deepen or broaden the
   results. Enables the user (or a build agent) to iteratively refine.

---

## Workflow

```
read deck-state.json (if exists)
    │
    ├─ determine deck type, audience, phase
    │
    ├─ check for scope prefix in query
    │   ├─ prefix found → single-agent mode (one scope)
    │   └─ no prefix → parallel mode (two scopes from deck type table)
    │
    ├─ verify index exists (check _manifest.json)
    │   ├─ index exists → proceed
    │   └─ no index → warn user, recommend wicked-prezzie:learn, abort
    │
    ├─ dispatch agent(s) with prompt template
    │   each agent: choose strategy → search index → rank results → return
    │
    ├─ merge results (parallel mode only)
    │   deduplicate by chunk_id, preserve highest relevance ranking
    │
    └─ format output: RESULTS + CORRELATION + RELATED
```

---

## Invocation Examples

```
"Find data on customer retention"          → search("customer retention")
"What do our sources say about cloud migration?" → search("cloud migration")
"Search for financial metrics"             → search("facts: financial metrics")
"Find stories about digital transformation" → search("narrative: digital transformation")
"Look up anything tagged compliance"       → search("tag: compliance")
"What do we know about the Aurora platform?" → search("entity: Aurora")
```

---

## Integration with Other Skills

| Skill | How It Uses Search |
|-------|-------------------|
| **ask** | Dispatches search as part of its Stage 2 specialist research |
| **brainstorm** | Teams query search for proof points and named systems during ideation |
| **generate** | Enriches slide content with source-grounded facts via targeted searches |
| **workflow** | Build agents search for specific data when populating approved slide plans |
| **outline** | Queries search for key facts to ground outline bullets in source material |

---

## Configuration

Search respects `index_dirs` from project config (set via `wicked-prezzie:config`).
If multiple index directories are configured, search queries all of them and merges
results across indexes. The first `index_dirs` entry is treated as the primary index.

---

## Limitations

- Search quality depends entirely on index quality. Poorly chunked or stale indexes
  produce poor results. Check `_manifest.json` freshness before trusting results.
- Parallel mode dispatches 2 agents maximum. For exhaustive searches across all 4
  scopes, run two sequential searches or use `wicked-prezzie:ask` instead.
- Entity search (`entity:` prefix) relies on entities being captured in
  `_relationships/` during learn Pass 2. Entities not cross-referenced there may
  be found via content grep fallback but with lower recall.
