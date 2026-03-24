---
name: notes
description: |
  Writes or upgrades speaker notes for HTML slides to presentation-ready quality.
  Three fields per slide: notes, talking_points, and a template-configurable third
  field. Batch mode for 4+ slides with parallel subagent dispatch.

  Use when: "write speaker notes", "add notes", "improve the notes",
  "upgrade notes quality", "batch notes", "add talking points"
---

# Speaker Notes Generator

Writes or upgrades speaker notes for HTML slide decks. Each slide gets three
structured note fields that transform raw slides into a complete presenter
package. The third field is configurable per workflow template, making the
same skill useful for proposals, training decks, board presentations, and
general keynotes.

---

## When to Use

- User asks for speaker notes on a slide deck
- After generate produces HTML slides (notes are thin or missing)
- After manual edits to slides (notes may be stale)
- User wants talking points for a presentation rehearsal
- User asks to "upgrade" or "improve" existing notes
- Before building the presenter view (presenter-html needs notes)

---

## Three-Field Note Structure

Every slide produces three note fields, stored as a JSON object:

### Field 1: `notes` (200-500 characters)

The presenter's walk sequence through the slide. Not a script — a map.

**Must contain**:
- Walk sequence: which visual element to reference first, second, third
- Key phrases: exact words the presenter should say (quoted)
- Named concepts: systems, frameworks, or terminology to name explicitly
- Audience connection: one sentence linking the slide to audience concerns

**Prohibited**:
- Generic filler ("This slide shows..." or "As you can see...")
- Repeating the slide title as the opening line
- Instructions to the presenter ("Click to advance")

### Field 2: `talking_points` (4-8 speakable bullets)

Bullets the presenter can read naturally. Each is one breath — 10-20 words.

**Must contain**:
- 4-8 speakable bullets covering the slide's content
- 1-2 objection handlers or anticipated questions (prefixed with "If asked:")
- At least one transition phrase connecting to the next slide

**Prohibited**:
- Bullets that duplicate slide text verbatim
- More than 8 bullets (forces the presenter to rush)
- Abstract bullets without concrete details

### Field 3: Template-Configurable

The third field's name and content type are read from the active workflow
template's `notes.tab3` configuration. If no template is active, defaults
to `references`.

| Template | Field Name | Content Type |
|----------|------------|--------------|
| general | `references` | Source attributions, data citations, page numbers |
| rfp-exec | `decision_points` | Key decisions this slide supports, approval actions |
| training | `learning_objectives` | What the learner should know/do after this slide |
| architecture | `data_sources` | System names, API endpoints, metric sources |
| board-strategy | `metrics` | KPI definitions, measurement methodology, baselines |

---

## Notes JSON Format

Notes are stored alongside slides in `notes.json`:

```json
{
  "slides": [
    {
      "slide_index": 0,
      "slide_file": "01-ai-powered-analytics.html",
      "notes": "Start with the headline number — say 'sixty percent faster decisions.' Point to the three stat cards left to right: cycle time, insight speed, adoption. Pause on adoption — this is the surprise number that proves it's not just a tool upgrade.",
      "talking_points": [
        "Our AI platform cut decision latency from 14 days to under 6",
        "That's not a lab number — it's measured across 200 active users",
        "Adoption hit 92% in the first quarter without a mandate",
        "If asked: 'What about the remaining 8%?' — They're in departments still onboarding, not resistant users",
        "This sets up the expansion case we'll cover next"
      ],
      "references": [
        "Decision cycle data: Q4 2025 Operations Dashboard, p.12",
        "Adoption survey: Internal UX Research, January 2026"
      ]
    }
  ],
  "template": "general",
  "tab3_field": "references",
  "generated_at": "2026-03-23T10:00:00Z"
}
```

---

## Batch Mode

When processing 4 or more slides, batch mode activates automatically.

### Dispatch Strategy

1. Read all slide HTML files and any existing `notes.json`
2. Group slides into batches of 3
3. Dispatch each batch as a parallel subagent
4. Each subagent receives: the slide HTML content, the outline JSON (for
   narrative context), and any existing notes to preserve
5. Collect results, validate against the quality gate, merge into `notes.json`

### Why Groups of 3

- Small enough for focused attention per slide
- Large enough to maintain narrative continuity between adjacent slides
- Overlapping context: batch N gets the last slide of batch N-1 for transition awareness

### Preserving Existing Notes

Before overwriting, read existing `notes.json`. For each slide:
- If notes exist and are marked `"user_edited": true`, preserve them entirely
- If notes exist but are auto-generated, upgrade them
- If no notes exist, generate fresh

---

## Quality Gate Checklist

Every generated note must pass these checks before writing:

- [ ] `notes` field is 200-500 characters (not shorter, not longer)
- [ ] `notes` field references specific visual elements on the slide
- [ ] `notes` field does not start with the slide title
- [ ] `talking_points` has 4-8 bullets
- [ ] At least one bullet starts with "If asked:" (objection handler)
- [ ] At least one bullet contains a transition to the next slide
- [ ] No bullet duplicates slide text verbatim
- [ ] Tab 3 field is populated with content matching its type
- [ ] No generic filler phrases present ("This slide shows", "As you can see",
  "Let me walk you through", "Moving on to")

If any check fails, revise that slide's notes before writing.

---

## Integration with Other Skills

### Reads From

| Skill | What | Why |
|-------|------|-----|
| generate | HTML slide files | Source content for note generation |
| outline | `outline.json` | Narrative context, slide purpose, audience |
| workflow | `deck-state.json` | Active template name for tab3 configuration |
| config | `config.json` | User preferences (verbosity, language) |

### Produces For

| Skill | What | Why |
|-------|------|-----|
| presenter-html | `notes.json` | Three-tab notes panel content |
| checkpoint | Notes generation status | Session state tracking |

---

## Usage

```bash
# Generate notes for all slides in a directory
python ${CLAUDE_SKILL_DIR}/scripts/slide_notes.py \
  --slides-dir ./slides \
  --outline outline.json \
  --output notes.json

# Upgrade existing notes (preserves user edits)
python ${CLAUDE_SKILL_DIR}/scripts/slide_notes.py \
  --slides-dir ./slides \
  --existing notes.json \
  --upgrade \
  --output notes.json

# Generate notes for a single slide
python ${CLAUDE_SKILL_DIR}/scripts/slide_notes.py \
  --slide ./slides/03-key-metrics.html \
  --outline outline.json \
  --output notes.json

# Override tab3 field name
python ${CLAUDE_SKILL_DIR}/scripts/slide_notes.py \
  --slides-dir ./slides \
  --tab3-field learning_objectives \
  --output notes.json
```

---

## How Claude Should Use This Skill

1. **Read the outline first** — notes quality depends on understanding each
   slide's purpose in the narrative arc, not just its visible content.
2. **Read existing notes** — never overwrite without checking for user edits.
3. **Write notes in slide order** — transitions depend on knowing the next slide.
4. **Run the quality gate** — every note, every time. No exceptions.
5. **Ask about tab3** — if no template is active, ask the user what the third
   field should contain before generating.
