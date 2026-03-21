# Index Schema

YAML frontmatter schema for chunk files produced by `slide-learn`. Every chunk
file (`index/{source-name}/chunk-NNN.md`) begins with a `---` delimited block
containing the fields below.

Schema version: **1**

---

## Field Reference

| Field | Type | Required | Description |
|---|---|---|---|
| `schema_version` | int | yes | Always `1`. Increment if the schema changes. |
| `source` | string | yes | Safe directory name of the source file (same as the parent directory name). |
| `source_type` | string | yes | One of: `pdf` `pptx` `docx` `html` `image` |
| `chunk_id` | string | yes | Unique identifier: `{source}/{chunk-NNN}`. Used for cross-referencing in pass 2. |
| `content_type` | string[] | yes | One or more of the valid content type values below. |
| `contains` | string[] | yes | Free-form tags describing what the chunk covers (topic tags, not types). |
| `entities` | object | yes | Named entities extracted from the chunk. See sub-fields below. |
| `figures` | string[] | no | List of figure descriptions (charts, tables, diagrams). One entry per figure. |
| `narrative_theme` | string | no | Short phrase (≤ 8 words) describing the dominant narrative arc of the chunk. |
| `slide_relevance` | string[] | no | Which slide layout types this chunk could feed. Valid values below. |
| `confidence` | float | yes | Agent confidence in the extraction quality. Range `0.0`–`1.0`. |
| `indexed_at` | string | yes | ISO 8601 UTC timestamp of when this chunk was written. |

### `entities` Sub-fields

| Sub-field | Type | Description |
|---|---|---|
| `systems` | string[] | Named technical systems, platforms, or products mentioned. |
| `people` | string[] | People, roles, or job titles mentioned (use role if name is sensitive). |
| `programs` | string[] | Business programs, initiatives, or projects mentioned. |
| `metrics` | string[] | Quantitative figures in context: `"Revenue: $4.2B"`, `"NPS: 67"`. |

---

## Valid Values

### `source_type`

| Value | Meaning |
|---|---|
| `pdf` | PDF document (report, brief, research paper) |
| `pptx` | PowerPoint presentation |
| `docx` | Word document |
| `html` | HTML slide file |
| `image` | Standalone image (PNG, JPG, etc.) |

### `content_type`

| Value | Meaning |
|---|---|
| `text` | Primarily narrative or body text |
| `visual` | Primarily charts, diagrams, or images |
| `table` | Primarily tabular data |
| `mixed` | Combination of text and visuals |
| `cover` | Title/cover page or section divider |
| `summary` | Executive summary or conclusions |
| `appendix` | Supplementary or reference material |

### `slide_relevance`

| Value | When to use |
|---|---|
| `title` | Could become a title or cover slide |
| `agenda` | Contains a list of topics or agenda items |
| `stats` | Contains key statistics or KPIs |
| `chart` | Contains chart data suitable for a chart slide |
| `diagram` | Contains a process, architecture, or org diagram |
| `narrative` | Best suited to a text-heavy narrative slide |
| `cta` | Contains a call to action or next steps |
| `section` | Could introduce a new section of the deck |
| `quote` | Contains a notable quote or testimonial |
| `comparison` | Contains a before/after or A vs. B comparison |

---

## Examples

### PDF Chunk (pages 4–7 of a financial report)

```yaml
---
schema_version: 1
source: q3-financial-review.pdf
source_type: pdf
chunk_id: q3-financial-review.pdf/chunk-002
pages: 4-7
content_type:
  - text
  - table
contains:
  - financial
  - revenue
  - q3
  - forecast
entities:
  systems: []
  people:
    - CFO
  programs:
    - Q3 Operating Review
  metrics:
    - "Revenue: $4.2B (+12% YoY)"
    - "EBITDA margin: 23.4%"
    - "Free cash flow: $840M"
figures:
  - "Table: Q3 P&L summary, 6 columns × 8 rows. Revenue, COGS, Gross Profit, EBITDA, Net Income, EPS."
narrative_theme: "Q3 performance exceeded guidance"
slide_relevance:
  - stats
  - chart
confidence: 0.92
indexed_at: "2026-03-21T10:30:00Z"
---
```

### PPTX Chunk (slide 3 of a strategy deck)

```yaml
---
schema_version: 1
source: strategy-2026.pptx
source_type: pptx
chunk_id: strategy-2026.pptx/chunk-003
slide_number: 3
content_type:
  - visual
  - mixed
contains:
  - strategy
  - growth
  - markets
entities:
  systems:
    - CRM Platform
  people: []
  programs:
    - Market Expansion Initiative
  metrics:
    - "Target markets: 12 new regions"
    - "Projected growth: 35% by 2027"
figures:
  - "Diagram with 4 nodes/steps. Shows market entry sequence. Flow: left-to-right. Key stages: Assess, Pilot, Scale, Sustain."
narrative_theme: "systematic market expansion by 2027"
slide_relevance:
  - diagram
  - stats
confidence: 0.85
indexed_at: "2026-03-21T10:31:00Z"
---
```

### DOCX Chunk (section 2 of a policy document)

```yaml
---
schema_version: 1
source: data-governance-policy.docx
source_type: docx
chunk_id: data-governance-policy.docx/chunk-002
content_type:
  - text
contains:
  - data-governance
  - compliance
  - access-control
entities:
  systems:
    - Data Lake
    - Identity Provider
  people:
    - Data Steward
    - CISO
  programs:
    - Data Governance Program
  metrics: []
figures: []
narrative_theme: "role-based access as governance foundation"
slide_relevance:
  - narrative
  - diagram
confidence: 0.88
indexed_at: "2026-03-21T10:32:00Z"
---
```

### Image Chunk (standalone PNG chart)

```yaml
---
schema_version: 1
source: market-share-chart.png
source_type: image
chunk_id: market-share-chart.png/chunk-001
content_type:
  - visual
contains:
  - market-share
  - competitive
  - pie-chart
entities:
  systems: []
  people: []
  programs: []
  metrics:
    - "Our share: 34%"
    - "Competitor A: 28%"
    - "Competitor B: 19%"
    - "Other: 19%"
figures:
  - "Pie chart showing market share by competitor. Key data: Our share 34%, Competitor A 28%, Competitor B 19%, Other 19%. Color coding: blue=us, red=A, gray=B."
narrative_theme: "market leadership at 34% share"
slide_relevance:
  - chart
  - stats
confidence: 0.94
indexed_at: "2026-03-21T10:33:00Z"
---
```
