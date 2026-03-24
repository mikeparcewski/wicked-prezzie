---
name: collaborate
description: |
  Multi-person review workflow with inline annotations, per-slide verdicts,
  and automated feedback analysis. File-based collaboration for shared drives.
  No server required — all state stored as flat JSON and markdown files.

  Use when: "get feedback", "review session", "send for review", "collect feedback",
  "what did reviewers say", "approve slides", "collaborative review", "start a review",
  "gather opinions", "review round"
---

# collaborate — Multi-Person Review Workflow

File-based collaborative review for slide decks. Creates review sessions where
multiple reviewers annotate slides, cast per-slide verdicts, and leave threaded
comments — all stored as flat files on a shared drive. No server, no accounts,
no network dependency.

## When to Use

- Before finalizing a deck — send slides out for team review
- When multiple stakeholders need to weigh in on content, design, or messaging
- After a build phase to collect approval/rejection per slide
- When consolidating feedback from reviewers who work asynchronously

## Workflow Overview

```
--start-review     Create session, assign reviewers, prepare annotation files
       |
  Reviewers annotate slides (offline, async, file-based)
       |
--collect          Merge all reviewer annotations into a single unified file
       |
--analyze          Sentiment analysis, consensus/divergence, prioritized actions
       |
--apply            Generate a change plan from approved feedback items
```

Each step is independent — you can collect without analyzing, or analyze
without applying. The pipeline is incremental: re-running `--collect` after
a late reviewer submits picks up the new annotations.

---

## Storage Structure

All review state lives under `.reviews/` inside the deck directory. Each review
session gets a unique timestamped ID. Multiple sessions can coexist (e.g., a
design review followed by a content review).

```
{deck_dir}/
  .reviews/
    session-{YYYYMMDD-HHMMSS}/
      config.json              — session metadata, reviewer list, status, created_at
      reviewer-{name}/
        slide-01.json          — annotations for slide 1
        slide-02.json          — annotations for slide 2
        ...
        summary.json           — per-slide verdicts: approved / needs-work / rejected
      collected.json           — merged annotations from all reviewers (after --collect)
      analysis.md              — feedback analysis report (after --analyze)
      change-plan.md           — proposed changes with action items (after --apply)
```

### config.json Schema

```json
{
  "sessionId": "20260320-143022",
  "createdAt": "2026-03-20T14:30:22Z",
  "status": "open",
  "slideCount": 12,
  "slideFiles": ["slide-01.html", "slide-02.html"],
  "reviewers": [
    {"name": "alex", "role": "content", "assignedAt": "2026-03-20T14:30:22Z"},
    {"name": "jordan", "role": "design", "assignedAt": "2026-03-20T14:30:22Z"}
  ],
  "settings": {
    "requireAllReviewers": false,
    "allowAnonymous": false,
    "verdictOptions": ["approved", "needs-work", "rejected"]
  }
}
```

### Annotation File Schema (per-slide)

```json
{
  "slideFile": "slide-03.html",
  "slideIndex": 3,
  "reviewer": "alex",
  "annotations": [
    {
      "id": "a1",
      "region": {"x": 120, "y": 340, "width": 200, "height": 60},
      "comment": "This stat needs a source citation",
      "category": "content",
      "severity": "medium",
      "createdAt": "2026-03-21T09:15:00Z",
      "thread": []
    }
  ],
  "verdict": null
}
```

### summary.json Schema

```json
{
  "reviewer": "alex",
  "completedAt": "2026-03-21T11:00:00Z",
  "verdicts": {
    "slide-01": "approved",
    "slide-02": "needs-work",
    "slide-03": "rejected"
  },
  "overallComment": "Slides 1 and 4-8 look good. Slide 2 needs tighter messaging."
}
```

---

## Step 1: Start a Review Session (`--start-review`)

1. **Determine deck directory** — use the current project or ask the user.
2. **Enumerate slides** — scan for HTML slide files in the deck directory.
3. **Create session directory** — `.reviews/session-{timestamp}/`.
4. **Register reviewers** — user provides names and optional roles (content, design, executive).
5. **Scaffold reviewer directories** — create empty annotation files for each slide per reviewer, pre-populated with slide metadata and null verdict.
6. **Write config.json** — session metadata, reviewer list, status = "open".
7. **Report** — print the session path and instructions for reviewers.

### Reviewer Instructions Template

Generate a brief instruction file (`.reviews/session-{id}/REVIEW-INSTRUCTIONS.md`)
explaining how to annotate:

- Open each `slide-NN.json` file in your reviewer directory
- Add annotation objects to the `annotations` array
- Set `verdict` to `"approved"`, `"needs-work"`, or `"rejected"`
- Fill in `summary.json` with your overall verdicts when done
- Save files and sync to the shared drive

---

## Step 2: Collect Annotations (`--collect`)

1. **Read config.json** — get reviewer list and slide count.
2. **Walk each reviewer directory** — read all `slide-NN.json` files and `summary.json`.
3. **Merge** — combine annotations from all reviewers into a unified structure, keyed by slide:

```json
{
  "sessionId": "20260320-143022",
  "collectedAt": "2026-03-22T10:00:00Z",
  "reviewerCount": 3,
  "slides": {
    "slide-01": {
      "verdicts": {"alex": "approved", "jordan": "needs-work", "sam": "approved"},
      "consensusVerdict": "approved",
      "annotations": [...]
    }
  }
}
```

4. **Compute consensus** — per slide, majority vote determines consensus. Ties resolve to `"needs-work"`. Any single `"rejected"` flags the slide for attention.
5. **Write collected.json** — the unified file for analysis.
6. **Report** — summary table showing per-slide verdicts from each reviewer and consensus.

---

## Step 3: Analyze Feedback (`--analyze`)

Reuses the feedback skill's analysis methodology adapted for slide annotations.

1. **Read collected.json**.
2. **Sentiment classification** — tag each annotation as endorsement, concern, suggestion, or question.
3. **Cluster detection** — group annotations targeting the same slide region or topic.
4. **Alignment detection** — where 2+ reviewers flag the same issue on the same slide.
5. **Divergence detection** — where reviewers disagree (one approves, another rejects).
6. **Priority scoring** — rank by alignment strength, severity, and reviewer role weight.
7. **Write analysis.md** with sections:
   - Overview: reviewer count, annotation count, verdict distribution
   - Consensus slides: slides where all reviewers agree (approved or rejected)
   - Contested slides: slides with mixed verdicts, ranked by divergence
   - Top action items: prioritized list of changes needed
   - Silent slides: slides with no annotations (consensus or oversight?)

---

## Step 4: Apply Changes (`--apply`)

1. **Read analysis.md** and **collected.json**.
2. **Filter to actionable items** — annotations tagged as suggestions or concerns with medium+ severity.
3. **Group by slide** — produce a per-slide change plan.
4. **Write change-plan.md**:

```markdown
## Slide 3: Key Metrics

### Must Fix (consensus concerns)
- [ ] Add source citation to revenue stat (alex, jordan both flagged)
- [ ] Reduce bullet count from 8 to 5 (sam: "too dense")

### Consider (single-reviewer suggestions)
- [ ] Swap bar chart for horizontal bars (jordan: "easier to scan")

### Rejected Changes
- Suggestion to remove the slide entirely (1 reviewer, overruled by 2 approvals)
```

5. **Present to user** — the change plan is a proposal, not auto-executed. User approves items before any edits happen.

---

## Comment Threads

Annotations support threaded replies. When running `--collect`, if a reviewer
references another reviewer's annotation ID, it is linked as a thread:

```json
{
  "id": "a3",
  "inReplyTo": "a1",
  "comment": "Agreed — the Q2 figure is from last year's report",
  "reviewer": "jordan"
}
```

Threads are preserved in collected.json and displayed as conversations in the
analysis report.

---

## Integration with Other Skills

| Skill | Integration Point |
|-------|-------------------|
| **feedback** | `--analyze` reuses feedback's sentiment classification and clustering logic |
| **validate** | Run structural validation alongside human review — include validation results in the review session as an automated "reviewer" |
| **workflow** | Review sessions can gate Phase 6 (Validate) — require all slides approved before advancing |
| **checkpoint** | Checkpoint captures review session status, outstanding feedback, next steps |
| **convert** | After `--apply`, re-run convert on modified slides to regenerate PPTX |

---

## Invocation Examples

```
"Start a review with Alex and Jordan"
  → collaborate --start-review --reviewers alex,jordan

"Collect the feedback"
  → collaborate --collect --session latest

"What did reviewers say about slide 3?"
  → collaborate --analyze (then filter to slide 3)

"Apply the approved changes"
  → collaborate --apply --session latest

"Show me the review status"
  → Read config.json + walk reviewer directories for completion %
```

---

## Concurrency & Shared Drives

- **No locking** — each reviewer writes only to their own directory. No conflicts.
- **Late submissions** — re-running `--collect` picks up new or updated annotations.
- **Multiple sessions** — each session is independent. Compare sessions to track review-over-review improvement.
- **Offline-first** — all files are plain JSON/markdown. Works on Dropbox, Google Drive, OneDrive, NAS, USB, or git.

---

## Anti-Pattern Guards

**Guard 1 — No auto-apply**: The change plan is always a proposal. Never edit
slides based on reviewer feedback without explicit user approval. Reviewers
can disagree — the deck owner decides.

**Guard 2 — No anonymous overwrite**: Each reviewer writes to their own
directory. The collect step merges read-only. No reviewer can overwrite another
reviewer's annotations.

**Guard 3 — Verdict before advance**: If the review session is linked to a
workflow phase gate, all slides must have a consensus verdict before the gate
can pass. Slides with no verdict block advancement.
