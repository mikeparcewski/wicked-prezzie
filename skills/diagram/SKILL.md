---
name: diagram
description: |
  Generates diagrams and visualizations from text descriptions. Produces SVG files
  themed to match the active slide theme. Supports timelines, process flows, org charts,
  comparison matrices, architecture diagrams, and data visualizations.

  Use when: "create a diagram", "draw a timeline", "visualize this process",
  "make a flowchart", "org chart", "comparison table", "architecture diagram",
  "add a chart", "data visualization"
---

# Diagram Generation

Generates presentation-ready diagrams from text descriptions. Outputs SVG files
themed to match the active slide theme. Diagrams can be embedded directly into
HTML slides or referenced in the outline for auto-embedding during generate.

---

## When to Use

- User describes a process, timeline, or structure to visualize
- Outline calls for a diagram on a specific slide
- User wants to replace bullet points with a visual
- User asks for a chart, flowchart, org chart, or architecture diagram
- During the build phase when a slide needs a visual element

---

## Supported Diagram Types

### 1. Timeline

Milestones, phases, or dates on a horizontal or vertical axis.

**Input signals**: "timeline", "milestones", "roadmap", "phases over time",
"when does each step happen"

**Output**: Horizontal timeline with labeled nodes, phase colors from theme,
optional date labels below each node.

### 2. Process Flow

Steps with decisions, branches, and convergence points.

**Input signals**: "flowchart", "process", "workflow", "decision tree",
"if/then", "steps to complete"

**Output**: Left-to-right or top-to-bottom flow with rectangular steps,
diamond decisions, and directional arrows. Branch labels on decision edges.

### 3. Org Chart

Hierarchy with reporting lines and optional role annotations.

**Input signals**: "org chart", "hierarchy", "reporting structure", "team
structure", "who reports to whom"

**Output**: Top-down tree with boxes per node, connecting lines, role labels.
Supports multi-level depth and lateral grouping.

### 4. Comparison Matrix

Features vs options in a grid layout with visual indicators.

**Input signals**: "comparison", "feature matrix", "vs", "options table",
"which one has what"

**Output**: Grid with row and column headers, cells containing check/cross
icons or value labels. Theme accent colors for highlights.

### 5. Architecture Diagram

Components, connections, and layers in a system view.

**Input signals**: "architecture", "system diagram", "components", "how it
connects", "infrastructure", "stack"

**Output**: Layered boxes with labeled connections. Supports grouping by
layer (presentation, logic, data) or by service boundary.

### 6. Data Visualization

Bar chart, pie chart, or line chart rendered as pure SVG.

**Input signals**: "chart", "graph", "bar chart", "pie chart", "line chart",
"visualize this data", "plot these numbers"

**Output**: SVG chart with axis labels, data labels, and theme-colored
fills. No JavaScript — static SVG only.

### 7. Quadrant / 2x2 Matrix

Four quadrants with axis labels and positioned items.

**Input signals**: "2x2", "quadrant", "matrix", "four quadrants", "plot
items on two axes"

**Output**: Four labeled quadrants with items positioned by their axis
values. Axis labels on edges, quadrant labels in corners.

### 8. Funnel Diagram

Progressive narrowing stages with counts or percentages.

**Input signals**: "funnel", "conversion funnel", "pipeline stages",
"progressive narrowing"

**Output**: Vertically stacked trapezoids narrowing from top to bottom,
with stage labels and values.

---

## Generation Strategy

### Primary: Mermaid Syntax

When mermaid-cli (`mmdc`) is available, Claude generates Mermaid syntax and
converts to SVG:

```bash
# Check availability
mmdc --version 2>/dev/null

# Generate SVG from Mermaid
mmdc -i diagram.mmd -o diagram.svg -t dark --backgroundColor transparent
```

Mermaid supports: flowcharts, sequence diagrams, class diagrams, state
diagrams, Gantt charts, pie charts, and git graphs. Use Mermaid when the
diagram type has a natural Mermaid representation.

### Fallback: Direct SVG

When mermaid-cli is not installed, Claude generates raw SVG directly. This
is also the preferred path for diagram types that Mermaid handles poorly
(architecture diagrams, comparison matrices, funnels, quadrants).

Direct SVG generation follows these rules:
- ViewBox: `0 0 1280 720` (matches slide dimensions)
- Font family: read from active theme JSON, fallback to `system-ui, sans-serif`
- Colors: read from active theme palette (primary, secondary, accent, background)
- Text: all text as `<text>` elements, not `<foreignObject>` (PPTX compatibility)
- Arrows: defined once as `<marker>` in `<defs>`, referenced by lines

---

## Theme Integration

The diagram skill reads the active theme to ensure visual consistency:

```python
# Theme resolution order:
# 1. Explicit --theme flag
# 2. Active theme from config.json
# 3. Default theme (midnight-purple)

theme = load_theme(theme_name)
colors = {
    "primary": theme["colors"]["primary"],
    "secondary": theme["colors"]["secondary"],
    "accent": theme["colors"]["accent"],
    "background": theme["colors"]["background"],
    "text": theme["colors"]["text"],
}
```

All diagram elements use theme colors. No hardcoded color values in generated SVG.

---

## Output Format

Diagrams are written to `output/diagrams/` by default:

```
output/diagrams/
  process-flow-onboarding.svg
  timeline-q1-roadmap.svg
  architecture-platform.svg
```

Filenames are auto-generated from diagram type and a slug of the description.
The `--output` flag overrides the path entirely.

---

## Slide Embedding

### During Generate

Reference a diagram in the outline JSON to auto-embed during slide generation:

```json
{
  "type": "content",
  "title": "Platform Architecture",
  "diagram": {
    "type": "architecture",
    "description": "Three-layer platform: API gateway, service mesh, data lake",
    "file": "output/diagrams/architecture-platform.svg"
  }
}
```

The generate skill checks for the `diagram` field and embeds the SVG inline.

### After Generate

To add a diagram to an existing slide, generate the SVG and then edit the
slide HTML to include it:

```html
<div class="diagram-container">
  <!-- SVG content inlined here -->
</div>
```

---

## Usage

```bash
# Generate a process flow diagram
python ${CLAUDE_SKILL_DIR}/scripts/slide_diagram.py \
  --type process-flow \
  --description "User signs up, verifies email, completes profile, gets matched" \
  --output output/diagrams/onboarding-flow.svg

# Generate a timeline with theme colors
python ${CLAUDE_SKILL_DIR}/scripts/slide_diagram.py \
  --type timeline \
  --description "Q1: Research, Q2: Prototype, Q3: Beta, Q4: Launch" \
  --theme midnight-purple \
  --output output/diagrams/roadmap.svg

# Generate from a data file (for charts)
python ${CLAUDE_SKILL_DIR}/scripts/slide_diagram.py \
  --type bar-chart \
  --data '{"labels":["Jan","Feb","Mar"],"values":[100,150,200]}' \
  --output output/diagrams/quarterly-growth.svg
```

---

## Integration with Other Skills

### Reads From

| Skill | What | Why |
|-------|------|-----|
| theme | Active theme JSON | Colors, fonts for diagram styling |
| outline | `outline.json` | Diagram references in slide specs |
| config | `config.json` | Default theme, output directory |

### Produces For

| Skill | What | Why |
|-------|------|-----|
| generate | SVG files | Inline embedding in slide HTML |
| convert | SVG elements in slides | Handled by SVG extraction pipeline |
| presenter-html | SVG renders at full resolution | Embedded in presenter view |

---

## Limitations

- Mermaid-cli is optional — install with `npm install -g @mermaid-js/mermaid-cli`
  for best flowchart and sequence diagram output.
- Data visualizations are simple — for complex statistical charts, use a
  dedicated charting tool and import the SVG.
- SVG text may render differently across browsers. The skill uses standard
  font stacks to minimize variation.
- Architecture diagrams with more than 15 components become visually crowded
  at slide dimensions. Split into multiple diagrams if needed.

---

## How Claude Should Use This Skill

1. **Identify the diagram type** — map the user's description to one of the
   eight supported types. If ambiguous, ask.
2. **Check theme** — load the active theme before generating. Diagrams that
   clash with the slide palette look jarring.
3. **Prefer Mermaid when available** — check for `mmdc` first. Fall back to
   direct SVG only when necessary or when the diagram type is not well-served
   by Mermaid.
4. **Size for slides** — all diagrams should be readable at 1280x720. If the
   content is too dense, suggest splitting into multiple diagrams.
5. **Embed inline** — when adding to a slide, inline the SVG content rather
   than referencing an external file. This ensures the presenter-html and
   PDF exports include the diagram without external dependencies.
