---
name: feedback
description: >-
  Parse Word document inline comments from team reviewers and generate a
  feedback analysis report — alignment, divergence, and narrative implications.
  Use when a team has reviewed an executive summary or document in Word and
  you need to synthesize their feedback.
triggers:
  - "analyze feedback"
  - "parse comments"
  - "feedback report"
  - "Word comments"
  - "review comments"
  - "team feedback"
  - "comment analysis"
  - "what did reviewers say"
  - "synthesize feedback"
  - "alignment and divergence"
---

# deck-feedback

Parses inline comments from a Word (.docx) document and produces a structured
feedback analysis report showing where reviewers align, where they diverge,
and what that means for narrative changes.

## When to Use

After a team has reviewed an executive summary (or any Word document) using
standard Word inline comments. This skill extracts all comments, maps them
to document sections, and analyzes the feedback patterns.

## Workflow

### Step 1: Parse the Word Document

```bash
python skills/deck-feedback/scripts/parse_word_comments.py <file.docx> --output feedback.json
```

This extracts:
- All inline comments with author, date, and text
- The referenced (highlighted) text each comment is attached to
- The document section each comment falls in
- Basic stats: reviewer count, comments per reviewer, sections with feedback

### Step 2: Analyze the Feedback

```bash
python skills/deck-feedback/scripts/analyze_feedback.py feedback.json --output report.json
```

Analysis includes:
- **Sentiment classification**: Each comment tagged as endorsement, concern, suggestion, or observation
- **Cluster detection**: Comments on the same passage grouped together
- **Alignment detection**: Where multiple reviewers raise the same concern or make the same suggestion
- **Divergence detection**: Where reviewers actively disagree on the same passage
- **Narrative implications**: What the patterns mean for the document (hotspots, silent sections, structural issues)
- **Prioritized action items**: Ranked by alignment strength and severity

### Step 3: Generate the Report

```bash
# Markdown (for review in conversation)
python skills/deck-feedback/scripts/generate_report.py report.json

# Word document (for sharing with the team)
python skills/deck-feedback/scripts/generate_report.py report.json --format docx --output feedback_report.docx
```

### One-Shot Pipeline

For quick runs, chain all three:

```bash
cd skills/deck-feedback/scripts
python parse_word_comments.py ../../../input.docx --output /tmp/fb.json && \
python analyze_feedback.py /tmp/fb.json --output /tmp/report.json && \
python generate_report.py /tmp/report.json --format docx --output ../../../feedback_report.docx
```

## Report Structure

The report contains these sections:

1. **Overview** — Total comments, reviewers, sentiment breakdown
2. **What This Means for the Narrative** — Synthesized implications:
   - 🔥 Attention Hotspot — sections with disproportionate feedback
   - 🤫 Silent Sections — sections with no feedback (consensus or disengagement?)
   - ✅ Consensus for Change — multiple reviewers flagging the same issue
   - ⚠️ Requires Discussion — reviewers disagree, can't resolve by editing alone
   - 🧭 Overall Direction — is the narrative sound or needs rethinking?
3. **Action Items** — Prioritized changes (high = aligned concerns or divergence)
4. **Where Reviewers Agree** — Detailed alignment points
5. **Where Reviewers Diverge** — Divergence with each reviewer's position
6. **Section-by-Section Breakdown** — Per-section sentiment and comment counts

## Output Formats

- **JSON** — For programmatic consumption or further analysis
- **Markdown** — For in-conversation review
- **Word (.docx)** — For sharing the report back with the review team

## Dependencies

- `python-docx` (already a project dependency)
- Standard library: `zipfile`, `xml.etree.ElementTree`, `json`, `collections`

## Limitations

- Sentiment classification is keyword-based (not LLM-powered). For nuanced
  comments, Claude should review the raw comments alongside the analysis.
- Comment threading (replies) is detected but not deeply analyzed yet.
- Track changes (insertions/deletions) are not parsed — only inline comments.
