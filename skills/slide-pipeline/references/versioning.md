# Versioning — Naming Conventions & History

Simple, non-destructive versioning using file naming conventions. Every generation run produces
a new versioned file. Never overwrites existing output.

---

## Naming Convention

```
{deck-slug}_v{N}.pptx
{deck-slug}_v{N}-{label}.pptx
```

### Examples
```
sales-kickoff_v1.pptx
sales-kickoff_v2.pptx
sales-kickoff_v2-client-review.pptx
sales-kickoff_v3.pptx
quarterly-retro_v1-draft.pptx
quarterly-retro_v2-final.pptx
```

### Rules
- Slug: derived from deck title, lowercased, spaces → hyphens, special chars stripped
- Version number: auto-increments from highest existing version for this slug in the output dir
- Label: optional, appended with hyphen, alphanumeric + hyphens only
- Never overwrite an existing file — always increment

---

## Version Labels

### Interactive flows
After generation, prompt (optional):
> "Want to add a label to this version? (e.g., draft, client-review, final) — or skip"

### Fast path
Silently auto-increments. No label prompt.

### Suggested labels
Suggest a label based on context:
- Overview/skeleton flow → suggest `skeleton`
- First pass → suggest `draft`
- After audit remediation → suggest `revised`
- Final polish → suggest `final`

---

## Version Metadata

Store version metadata in `~/.something-wicked/wicked-prezzie/versions/{deck-slug}.json`
(user-level, so version history persists across project directories):

```json
[
  {
    "version": 1,
    "label": "draft",
    "filename": "sales-kickoff_v1-draft.pptx",
    "fidelity": "draft",
    "created_at": "2025-03-01T09:15:00Z",
    "slide_count": 16,
    "theme": "midnight-purple",
    "source_files": ["strategy-doc.md"],
    "image_mode": "icons",
    "review_flags": 3,
    "audit_score": null
  },
  {
    "version": 2,
    "label": "client-review",
    "filename": "sales-kickoff_v2-client-review.pptx",
    "fidelity": "best",
    "render_passes": 3,
    "slides_corrected": 2,
    "created_at": "2025-03-03T14:30:00Z",
    "slide_count": 18,
    "theme": "midnight-purple",
    "source_files": ["strategy-doc.md", "team-feedback.md"],
    "image_mode": "unsplash",
    "review_flags": 1,
    "audit_score": 88
  }
]
```

---

## Operations

### List versions
Say "show version history" or "list versions of sales-kickoff":

```
sales-kickoff — 2 versions

  v1  [draft]          2025-03-01  16 slides  midnight-purple  3 flags  fidelity:draft
  v2  [client-review]  2025-03-03  18 slides  midnight-purple  1 flag   fidelity:best (3 passes)

Latest: sales-kickoff_v2-client-review.pptx
```

### Diff two versions
Say "diff v1 and v2 of sales-kickoff":

```
sales-kickoff: v1 → v2

  Slide count:   16 → 18  (+2)
  Fidelity:      draft → best
  Theme:         midnight-purple (same)
  Images:        icons → unsplash
  Review flags:  3 → 1  (-2)
  Audit score:   — → 88

  New source files: team-feedback.md
```

### Build from prior version
If versions exist for a topic:
> "Found 2 prior versions of 'sales-kickoff'. Start fresh or build from v2 (latest)?"

If building from prior: load that version's source files and structure as starting point.

---

## Storage Cleanup

Say "clean up versions" to list all versions and choose which to keep. Removes metadata records
for deleted files. Does not delete actual PPTX files — user manages their own filesystem.
