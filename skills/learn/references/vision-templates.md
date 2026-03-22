# Vision Templates

Standardized description templates for visual elements found in source
documents. Use these templates when writing the `figures` frontmatter field
and the chunk body content for images, charts, and diagrams.

Consistent templates make descriptions grep-able and parseable by downstream
skills (outline, generate).

---

## Template Syntax

Replace `{placeholder}` with extracted values. If a value cannot be determined,
write `unknown` or omit the clause rather than guessing.

---

## Charts

For bar charts, line charts, pie charts, scatter plots, area charts, and
waterfall charts.

```
{type} showing {subject} over {dimension}. X-axis: {range}. Y-axis: {range}. Key data: {list}. Trend: {description}.
```

**Fields**:

| Placeholder | What to write |
|---|---|
| `{type}` | One of: Bar chart, Line chart, Pie chart, Stacked bar chart, Area chart, Scatter plot, Waterfall chart, Combo chart |
| `{subject}` | What is being measured: "revenue by quarter", "market share by vendor", "NPS over time" |
| `{dimension}` | The axis or grouping dimension: "time", "category", "region" |
| `{range}` (X) | X-axis label and range: "Q1 2024 – Q4 2025" or "Product categories: A, B, C" |
| `{range}` (Y) | Y-axis label and range: "$0M – $500M" or "0% – 100%" |
| `{list}` | Up to 5 most significant data points: "Q3 2025: $4.2B, peak; Q1 2024: $2.8B, baseline" |
| `{description}` | Direction and magnitude: "upward 12% YoY", "flat with seasonal dip in Q1", "declining from 45% to 31%" |

**Example**:

```
Bar chart showing revenue by quarter over time. X-axis: Q1 2024 – Q4 2025. Y-axis: $0M – $600M. Key data: Q1 2024: $280M; Q2 2024: $310M; Q3 2024: $390M; Q4 2024: $420M; Q3 2025: $520M (peak). Trend: upward 12% YoY with Q4 seasonality.
```

---

## Diagrams

For process flows, architecture diagrams, swim-lane diagrams, and network
topology diagrams.

```
{type} with {N} nodes/steps. Shows {relationships}. Flow: {direction}. Key stages: {list}.
```

**Fields**:

| Placeholder | What to write |
|---|---|
| `{type}` | One of: Process flow, Architecture diagram, Swim-lane diagram, Network diagram, Venn diagram, Timeline, Funnel diagram |
| `{N}` | Number of distinct nodes, boxes, or steps visible |
| `{relationships}` | What the diagram communicates: "data flow from ingestion to reporting", "approval hierarchy", "system integrations" |
| `{direction}` | One of: left-to-right, top-to-bottom, circular, branching |
| `{list}` | Names of the key stages/nodes in order: "Collect → Process → Analyze → Report" |

**Example**:

```
Process flow with 5 nodes/steps. Shows data pipeline from raw ingestion to dashboard delivery. Flow: left-to-right. Key stages: Ingest → Validate → Transform → Aggregate → Visualize.
```

---

## Infographics

For mixed-content infographic slides or image panels combining stats, icons,
and short text blocks.

```
Titled '{title}' with {N} sections. Key stats: {list}. Color coding: {meaning}.
```

**Fields**:

| Placeholder | What to write |
|---|---|
| `{title}` | Verbatim title of the infographic, or `untitled` |
| `{N}` | Number of distinct content panels or sections |
| `{list}` | Up to 6 key statistics or facts shown: "$4.2B revenue", "12 markets", "98% uptime" |
| `{meaning}` | Color associations if apparent: "blue = current year, gray = prior year", "green = on track, red = at risk" |

**Example**:

```
Titled 'Q3 Business Snapshot' with 4 sections. Key stats: Revenue $4.2B, NPS 67, Markets 12, Headcount 3,400. Color coding: blue = actuals, green = targets.
```

---

## Org Charts

For organizational hierarchy diagrams.

```
{N} levels, {M} total positions. Reports to: {top}. Key divisions: {list}.
```

**Fields**:

| Placeholder | What to write |
|---|---|
| `{N}` | Number of hierarchy levels visible |
| `{M}` | Total number of boxes/roles shown |
| `{top}` | Title of the top-level role: "CEO", "VP of Engineering" |
| `{list}` | Names of the direct-report divisions or teams: "Product, Engineering, Design, QA" |

**Example**:

```
3 levels, 14 total positions. Reports to: Chief Product Officer. Key divisions: Product Management, Design, Research, Program Management.
```

---

## Screenshots

For screenshots of applications, dashboards, web pages, or tool interfaces.

```
Screenshot of {application/page}. Shows: {key elements}. State: {current state}.
```

**Fields**:

| Placeholder | What to write |
|---|---|
| `{application/page}` | Name of the app or page: "Salesforce opportunity view", "internal analytics dashboard", "product roadmap tool" |
| `{key elements}` | Up to 5 visible UI elements or data regions: "sidebar navigation, KPI tiles (Revenue, Leads, Conversion), date filter" |
| `{current state}` | What state the UI is in: "filtered to Q3 2025, showing 3 alerts", "loading state", "empty state with onboarding prompt" |

**Example**:

```
Screenshot of internal analytics dashboard. Shows: KPI tiles (Revenue $4.2B, NPS 67, Active Users 12K), trend sparklines for each KPI, date range filter set to Q3 2025. State: filtered to Q3 2025, no alerts active.
```

---

## Tables

For data tables visible in images or extracted from documents.

```
{N} columns × {M} rows. Headers: {list}. Key figures: {extracted values}.
```

**Fields**:

| Placeholder | What to write |
|---|---|
| `{N}` | Number of columns |
| `{M}` | Number of data rows (not including the header row) |
| `{list}` | Column header names in order: "Quarter, Revenue, COGS, Gross Profit, EBITDA" |
| `{extracted values}` | Most significant cell values: "Q3 2025 Revenue: $520M (highest); Q1 2024 Revenue: $280M (lowest)" |

**Example**:

```
5 columns × 8 rows. Headers: Quarter, Revenue ($M), COGS ($M), Gross Profit ($M), EBITDA ($M). Key figures: Q3 2025 Revenue $520M (peak row); Q4 2024 EBITDA $98M (highest margin row, 23.4%).
```

---

## General Guidance

- **Extract numbers verbatim** — do not round or interpret. Write `$4,213M` not
  `approximately $4 billion`.
- **Preserve units** — `%`, `$`, `M`, `B`, `K` exactly as shown.
- **Note color-coding** only when it carries semantic meaning (status, category,
  comparison). Skip decorative color choices.
- **For illegible content** — write `[illegible: low resolution]` rather than
  guessing. Set chunk `confidence < 0.70`.
- **Multiple visuals on one page** — describe each separately, then write a
  combined `figures` array entry per visual.
- **Unlabeled axes** — note as "X-axis: unlabeled" rather than inferring.
