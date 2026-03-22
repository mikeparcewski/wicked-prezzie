# Search Patterns

The 10 most common agent query patterns for the slide-learn index. Start with
`_insights/` (synthesized), narrow to `_tags/` (aggregated), then read
individual chunks only when you need the full source text.

Progressive search order:

```
_insights/   →  _tags/   →  {source-name}/chunk-NNN.md   →  .cache/
(overview)      (filter)     (full context)                  (freshness)
```

---

## 1. Find All Financial Figures

Goal: locate chunks that contain revenue, cost, or performance metrics.

```bash
grep -r "financial" index/_tags/
grep -r "revenue\|margin\|EBITDA\|cost" index/_tags/
cat index/_insights/key-facts.md
```

Refine by reading the tagged chunks:

```bash
grep -rl "metrics" index/*/chunk-*.md
grep -r "Revenue:" index/*/chunk-*.md
```

---

## 2. Find Content About a Named System

Goal: find all chunks that mention a specific system (e.g., "OrderHub", "CRM", "Data Lake").

```bash
grep -rl "OrderHub" index/
grep -r "OrderHub" index/_relationships/systems.md
```

Then read the relationship entry for cross-source references:

```bash
cat index/_relationships/systems.md | grep -A 5 "OrderHub"
```

---

## 3. Find Slide Candidates

Goal: surface chunks that the agent has already identified as good slide fodder.

```bash
cat index/_insights/key-facts.md
cat index/_insights/narrative-themes.md
```

Filter by slide type:

```bash
grep -r "slide_relevance" index/*/chunk-*.md | grep "stats"
grep -r "slide_relevance.*chart" index/*/chunk-*.md
```

---

## 4. Find Charts and Diagrams

Goal: locate visual assets suitable for chart or diagram slides.

```bash
grep -r "chart\|diagram\|flow\|infographic" index/_tags/
grep -r "content_type.*visual" index/*/chunk-*.md
grep -r "figures:" index/*/chunk-*.md -A 3
```

Using ripgrep for speed on large indexes:

```bash
rg "content_type.*visual" index/ --glob "chunk-*.md"
rg "Bar chart|Line chart|Process flow" index/ --glob "chunk-*.md"
```

---

## 5. Find Narrative Themes

Goal: identify recurring themes that should shape the deck narrative arc.

```bash
cat index/_insights/narrative-themes.md
grep -r "narrative_theme:" index/*/chunk-*.md
```

Cluster by theme keyword:

```bash
grep -r "narrative_theme:" index/*/chunk-*.md | grep "growth"
grep -r "narrative_theme:" index/*/chunk-*.md | sort -t: -k3
```

---

## 6. Find Content for Stats Slides

Goal: find chunks suitable for a KPI or statistics slide layout.

```bash
grep -r "slide_relevance.*stats" index/*/chunk-*.md
grep -r "metrics:" index/*/chunk-*.md -A 5
```

With ripgrep:

```bash
rg "slide_relevance" index/ --glob "chunk-*.md" -A 2 | grep "stats"
```

---

## 7. Find Cross-Document Relationships

Goal: identify entities (systems, people, programs) that appear in multiple
source documents — indicating strategic importance.

```bash
cat index/_relationships/systems.md
cat index/_relationships/people.md
grep -c "chunk-" index/_relationships/systems.md
```

Find entities mentioned in 3 or more chunks:

```bash
awk '/^## /{name=$0} /chunk-/{count++} /^$/{if(count>=3) print name; count=0}' \
  index/_relationships/systems.md
```

---

## 8. Find Gaps in Coverage

Goal: identify topics that are mentioned but not elaborated, or slide types
with no indexed source material.

```bash
cat index/_insights/gaps.md
```

Verify gap by checking tag coverage:

```bash
ls index/_tags/
grep -r "slide_relevance" index/*/chunk-*.md | grep -v "stats\|chart\|diagram"
```

---

## 9. Find All Chunks from One Source

Goal: review everything indexed from a specific document.

```bash
ls index/q3-financial-review.pdf/
cat index/q3-financial-review.pdf/chunk-001.md
```

Read all frontmatter from one source quickly:

```bash
grep -r "narrative_theme\|slide_relevance\|confidence" \
  index/q3-financial-review.pdf/
```

Using ripgrep:

```bash
rg "narrative_theme|slide_relevance" index/q3-financial-review.pdf/ -g "chunk-*.md"
```

---

## 10. Check Index Freshness

Goal: determine when the index was last updated and whether documents have
changed since indexing.

```bash
cat index/_manifest.json
```

Check if a specific document has been re-indexed:

```bash
cat index/.cache/q3-financial-review.pdf.hash
```

Compare cache hash against current file:

```bash
# macOS
shasum -a 256 /path/to/q3-financial-review.pdf | cut -c1-16

# Linux
sha256sum /path/to/q3-financial-review.pdf | cut -c1-16
```

If the hashes differ, re-run `slide_learn.py --doc /path/to/q3-financial-review.pdf`.

---

## Progressive Search Pattern (Decision Tree)

```
Start: "I need content about X"
│
├─ 1. Check _insights/key-facts.md and narrative-themes.md
│       Hit? → Use the fact/theme directly.
│       Miss? → Continue.
│
├─ 2. Search _tags/ for topic keywords
│       grep -r "X" index/_tags/
│       Hit? → Read the tag file to get chunk IDs.
│       Miss? → Continue.
│
├─ 3. Search chunk frontmatter across all sources
│       grep -r "X" index/*/chunk-*.md (frontmatter lines only)
│       Hit? → Read those chunk files for full context.
│       Miss? → Continue.
│
├─ 4. Check _relationships/ for cross-doc connections
│       cat index/_relationships/systems.md | grep -i "X"
│       Hit? → Multiple chunks mention X — read them for synthesis.
│       Miss? → Continue.
│
└─ 5. Check gaps.md — X may be a coverage gap
        cat index/_insights/gaps.md
        Result? → Flag to user that source material for X is missing.
```

---

## Useful Aliases

Add to shell config for frequent index work:

```bash
alias idx-facts="cat index/_insights/key-facts.md"
alias idx-themes="cat index/_insights/narrative-themes.md"
alias idx-gaps="cat index/_insights/gaps.md"
alias idx-fresh="cat index/_manifest.json | python3 -m json.tool | grep lastIndexed"
alias idx-systems="cat index/_relationships/systems.md"
```
