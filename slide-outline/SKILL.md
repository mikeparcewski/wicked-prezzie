---
name: Slide Outline
description: >
  Structures a topic or brief into a presentation outline using the Pyramid
  Principle — one key message per slide, supporting evidence, narrative arc.
  Use this skill whenever the user wants to plan a presentation, create a deck
  outline, structure talking points, or says "make me a presentation about X",
  "outline a deck on Y", "plan the slides", or "what slides do I need". This is
  the first step in the content creation pipeline — it produces a structured
  outline JSON that slide-generate consumes to produce themed HTML slides.
  Also use when the user has a wall of text or bullet points and wants them
  organized into a coherent deck structure.
---

# Slide Outline

## Purpose

Good presentations start with structure, not slides. The Slide Outline skill
takes a topic, brief, or unstructured content and produces a structured outline
following the Pyramid Principle: each slide has one key message, supporting
evidence, and a clear role in the narrative arc.

The outline is the blueprint that slide-generate uses to produce HTML slides.
Without it, slide generation is ad-hoc and the resulting deck lacks narrative
coherence.

## When to Use

- User provides a topic and wants a presentation planned
- User has bullet points or a document to turn into slides
- User wants to restructure an existing deck's flow
- Before calling slide-generate (outline first, then generate)
- User asks "how many slides do I need?" or "what's the right structure?"

## The Pyramid Principle

Every slide outline follows the Pyramid Principle adapted for presentations:

1. **Lead with the conclusion** — The title slide states the main takeaway.
   Don't build up to it; state it, then prove it.

2. **Group by argument** — Slides are organized into acts (sections), each
   making one supporting argument for the main conclusion.

3. **One message per slide** — Each slide's title is an assertion (not a topic
   label). "Revenue grew 40% YoY" not "Revenue Update".

4. **Support with evidence** — Body content on each slide supports its title
   assertion with data, examples, or logic.

5. **Narrative arc** — The deck follows a structure:
   - **Setup** (1-2 slides): Context, problem statement, or hook
   - **Argument** (3-8 slides): Key points with evidence
   - **Resolution** (1-2 slides): Conclusion, next steps, or call to action

## Outline JSON Format

The outline is stored as JSON consumed by slide-generate:

```json
{
  "title": "AI-Powered Analytics Platform",
  "subtitle": "Board Presentation — Q1 2026",
  "author": "Strategy Team",
  "theme": "midnight-purple",
  "target_audience": "Executive leadership",
  "key_message": "Our AI platform reduced decision latency by 60%",
  "acts": [
    {
      "name": "Setup",
      "color_hint": "primary",
      "slides": [
        {
          "type": "title",
          "title": "AI-Powered Analytics",
          "subtitle": "Transforming Data into Decisions",
          "notes": "Welcome, set context for the board"
        },
        {
          "type": "content",
          "title": "Decision speed is our competitive advantage",
          "body": [
            "Market moves 3x faster than 5 years ago",
            "Competitors with faster analytics win 70% of contested deals",
            "Our average decision cycle: 14 days → need to reach 5 days"
          ],
          "layout": "bullets",
          "notes": "Frame the problem before presenting the solution"
        }
      ]
    },
    {
      "name": "Evidence",
      "color_hint": "secondary",
      "slides": [
        {
          "type": "content",
          "title": "AI platform reduced decision latency by 60%",
          "body": [
            {"stat": "14→5.6 days", "label": "Decision cycle"},
            {"stat": "3.2x", "label": "Faster insights"},
            {"stat": "92%", "label": "User adoption"}
          ],
          "layout": "stats",
          "notes": "Lead with the headline number, then break it down"
        }
      ]
    },
    {
      "name": "Close",
      "color_hint": "accent",
      "slides": [
        {
          "type": "cta",
          "title": "Expand AI analytics to all business units by Q3",
          "body": [
            "Phase 2 rollout plan ready",
            "Budget request: $2.4M",
            "Expected ROI: 4.1x within 18 months"
          ],
          "notes": "Clear ask with supporting justification"
        }
      ]
    }
  ]
}
```

## Slide Types

| Type | Purpose | Layout Options |
|---|---|---|
| `title` | Opening slide — deck title and subtitle | centered, left-aligned |
| `section` | Section divider between acts | centered with accent bar |
| `content` | Standard content slide | bullets, two-column, image-text |
| `stats` | Key metrics or data points | card-grid, big-number |
| `comparison` | Before/after or option A vs B | split, table |
| `quote` | Pull quote or testimonial | centered-quote |
| `cta` | Call to action / next steps | bullets with emphasis |
| `blank` | Intentionally minimal | spacer or visual-only |

## Usage

```bash
# Generate outline from a topic
python slide-outline/scripts/slide_outline.py --topic "Q1 Sales Results" \
  --audience "Sales leadership" \
  --key-message "We exceeded target by 15%" \
  --output outline.json

# Generate outline from a brief/document
python slide-outline/scripts/slide_outline.py --brief brief.txt \
  --output outline.json

# Validate an existing outline
python slide-outline/scripts/slide_outline.py --validate outline.json

# Show outline summary
python slide-outline/scripts/slide_outline.py --summary outline.json

# Set the theme for the outline
python slide-outline/scripts/slide_outline.py --outline outline.json \
  --set-theme corporate-light
```

## Outline Validation Rules

The `--validate` flag checks:

- Every slide has a `type` and `title`
- Slide titles are assertions, not topic labels (heuristic: contains a verb or number)
- No act has more than 5 slides (split if needed)
- Total slide count is between 3 and 20
- The deck has at least a Setup and Close act
- No slide body exceeds 75 words
- The `theme` field references a valid theme in slide-theme
- Speaker notes exist for every slide

## Slide Count Guidelines

| Presentation Length | Recommended Slides | Pace |
|---|---|---|
| 5 minutes (lightning) | 5-7 | ~45 sec/slide |
| 15 minutes | 10-12 | ~80 sec/slide |
| 30 minutes | 15-20 | ~90 sec/slide |
| 60 minutes | 20-30 | ~120 sec/slide |

These are guidelines — data-heavy slides need more time, title/divider slides
need less.

## How Claude Should Use This Skill

When a user asks for a presentation, follow this workflow:

1. **Clarify scope** — Ask about audience, time limit, and key message if not provided.
2. **Generate outline** — Use the Pyramid Principle to structure the content.
3. **Review with user** — Present the outline for feedback before generating slides.
4. **Save outline** — Write the JSON file for slide-generate to consume.

The outline is the contract between the user's intent and the generated slides.
Getting it right here prevents expensive rework later.
