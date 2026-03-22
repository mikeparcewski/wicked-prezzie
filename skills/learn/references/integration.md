# Integration

How other skills in the wicked-prezzie pipeline consume the learn index.

The index is an optional enrichment layer. Skills work without it — but when
`index_dirs` is configured, they query `_insights/` and `_tags/` to ground
slide content in source material rather than model-only recall.

---

## Configuration

Set `index_dirs` in config to point at one or more index directories:

```bash
# Single directory
python skills/config/scripts/slide_config.py set index_dirs /path/to/docs/index

# Multiple directories (comma-separated)
python skills/config/scripts/slide_config.py set index_dirs \
  /path/to/docs/index,/path/to/research/index
```

`index_dirs` is a project-level key. Resolution order applies:
user config → project config (project wins).

At runtime, each skill checks `load_config()["index_dirs"]` before proceeding.
If the key is absent or the directory does not exist, the skill runs in
model-only mode with no source grounding.

---

## convert

**When**: At the start of any pipeline run.

**What it reads**:
- `_manifest.json` — checks `lastIndexed` to warn if the index is stale
  (> 7 days old).
- `_insights/key-facts.md` — passes top facts to the outline step as
  `source_context`.
- `_insights/narrative-themes.md` — selects the dominant theme to pass as the
  `narrative_hint` parameter to `outline`.

**Behavior**:

```
if index_dirs is set:
    read _manifest.json → warn if stale
    read _insights/key-facts.md → extract top 10 facts
    read _insights/narrative-themes.md → pick dominant theme
    pass {source_context, narrative_hint} to outline
else:
    proceed with model-only mode
```

**No script changes required.** The pipeline reads the index files directly as
part of its orchestration logic.

---

## workflow

**When**: When building a full deck from a brief, before generating the outline.

**What it reads**:
- `_insights/key-facts.md` — the `facts-manifest` for populating stat slides.

**Behavior**: workflow reads `key-facts.md` and treats each bullet as an
input fact for the relevant slide. Facts are attributed to their source chunk
via the `_(source: {chunk_id})_` suffix.

**Audit trail**: The workflow writes `source_chunks` into the outline JSON
(see outline section below).

---

## outline

**When**: Before generating the outline structure.

**What it reads**:
- `_insights/key-facts.md` — extracts metrics for `stats` slides.
- `_insights/narrative-themes.md` — informs the Pyramid Principle arc.
- `_tags/{topic}.md` — queries specific topic tags when a slide topic matches.

**Behavior**:

```
for each slide in outline:
    search _tags/ for the slide topic
    if matching chunks found:
        attach top 3 chunk IDs to the slide as source_chunks
        extract supporting facts for the slide body
```

**Outline JSON output** — when source material is found, outline adds
a `source_chunks` array to each slide entry:

```json
{
  "slide": 4,
  "title": "Q3 Revenue Performance",
  "layout": "stats",
  "bullets": ["Revenue: $4.2B (+12% YoY)", "EBITDA margin: 23.4%"],
  "source_chunks": [
    "q3-financial-review.pdf/chunk-002",
    "strategy-2026.pptx/chunk-007"
  ]
}
```

The `source_chunks` field is the audit trail. It persists through
generate so the final PPTX knows which source documents backed each slide.

---

## generate

**When**: When enriching a slide with source-grounded content.

**What it reads**:
- Per-chunk files referenced in `source_chunks` (from the outline JSON).
- `_insights/key-facts.md` for stat-type slides without explicit `source_chunks`.

**Behavior**:

```
for each slide with source_chunks:
    read each referenced chunk file
    extract: metrics, narrative_theme, figures
    use metrics to populate stat callouts
    use figures list to decide if a chart description should be included
    use narrative_theme to set the slide's speaker note tone
```

**No hallucinated numbers** — generate must use values from chunk
`entities.metrics` for any numeric callout. If a number is not in the index,
it must either be omitted or marked `[ESTIMATE]` in speaker notes.

---

## Audit Trail: source_chunks

The `source_chunks` field propagates through the pipeline as an immutable
record of which index chunks backed each slide.

```
outline → adds source_chunks[] to outline JSON
generate → reads source chunks, preserves source_chunks[] in slide HTML comments
convert → logs source_chunks in the run summary
```

HTML comment format (written by generate into the slide div):

```html
<!-- source_chunks: q3-financial-review.pdf/chunk-002, strategy-2026.pptx/chunk-007 -->
```

This allows post-hoc auditing: given a PPTX, trace back to the exact source
document pages that backed each slide.

---

## Index Staleness Policy

| Age | Behavior |
|---|---|
| < 7 days | Use index without warning |
| 7–30 days | Log warning: "Index may be stale. Run slide_learn.py to refresh." |
| > 30 days | Log error and prompt user to confirm before proceeding |

Staleness is calculated from `_manifest.json["lastIndexed"]`.

---

## Minimal Integration Snippet

For any skill that wants to read the index:

```python
import json
from pathlib import Path

def load_index_config() -> list[str]:
    """Return configured index directories from config."""
    _root = Path(__file__).parent.parent.parent  # skills/
    sys.path.insert(0, str(_root / "config" / "scripts"))
    from slide_config import load_config
    config = load_config()
    dirs = config.get("index_dirs", [])
    if isinstance(dirs, str):
        dirs = [d.strip() for d in dirs.split(",")]
    return [d for d in dirs if Path(d).exists()]


def read_key_facts(index_dir: str) -> list[str]:
    """Return bullet lines from _insights/key-facts.md."""
    facts_path = Path(index_dir) / "_insights" / "key-facts.md"
    if not facts_path.exists():
        return []
    lines = facts_path.read_text(encoding="utf-8").splitlines()
    return [l.lstrip("- ").strip() for l in lines if l.startswith("- ")]


def read_narrative_themes(index_dir: str) -> list[str]:
    """Return theme names from _insights/narrative-themes.md."""
    themes_path = Path(index_dir) / "_insights" / "narrative-themes.md"
    if not themes_path.exists():
        return []
    lines = themes_path.read_text(encoding="utf-8").splitlines()
    return [l[3:].strip() for l in lines if l.startswith("## ")]
```

---

## Dependency Map

```
learn (produces index)
    │
    ├─ convert (reads _insights/, _manifest.json)
    │       └─ passes source_context → outline
    │
    ├─ workflow (reads _insights/key-facts.md)
    │
    ├─ outline (reads _insights/, _tags/, writes source_chunks)
    │       └─ passes source_chunks[] → generate
    │
    └─ generate (reads chunk files via source_chunks)
```

All consumption is read-only. No other skill writes to the index directory.
Only `slide_learn.py` writes index files.
