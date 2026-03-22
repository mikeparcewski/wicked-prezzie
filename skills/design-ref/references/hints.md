# Hints — Contextual Hints & REVIEW Flagging

Two systems: **contextual hints** (surface during creation and conversion flows) and
**REVIEW flags** (embedded in speaker notes when human judgment is needed).

---

## Contextual Hints

### When to fire
Hints are brief, friendly, and actionable. Fire them at the right moment — not all at once.
One hint at a time. Don't repeat the same hint in a session.

### Hint Catalog

**No style theme**
Condition: no active theme set in config
Moment: before generation starts
> *"No active theme set — using midnight-purple default. Run 'learn my brand' on your existing
> decks to match your brand, or pick a built-in theme."*

**Topic only, no content**
Condition: user provided topic but no source files
Moment: during outline generation
> *"This will be AI-generated without source material. The result will be reasonable but won't
> reflect your specific data. Consider adding a file or pasting a few bullet points."*

**Slide count >> content volume**
Condition: requested slide count is more than 2× what content supports
Moment: during outline generation
> *"That's a lot of slides for the available content — I'd suggest [N] based on what you've
> shared. Want me to adjust, or keep your target?"*

**Nothing to work with**
Condition: no content + topic is fewer than 5 words with no elaboration
Moment: before starting generation
> *"Not much to work with yet. Try providing a file, or describing the topic in more detail.
> Even a rough bullet list helps significantly."*

**Image/PDF provided without context**
Condition: user provides image or PDF files without explanation
Moment: immediately after input received
> *"Got it — should I use these for content, style reference, or both?"*

**Prior versions exist**
Condition: versioned deck files already exist for this slug
Moment: before starting generation
> *"Found [N] prior versions of '[slug]'. Start fresh, or build from v[latest]?"*

**Large deck + best fidelity**
Condition: > 12 slides and best fidelity requested
Moment: before starting pipeline
> *"Best fidelity on [N] slides will take multiple passes — estimated [2-4x] longer than draft.
> Proceed, or use draft now and upgrade fidelity later?"*

**Format guidance — sharing as URL**
Condition: user mentions "sharing", "sending a link", "hosting" the deck
Moment: during output format selection
> *"This sounds like something you'd share as a link — HTML output opens in any browser. Want
> to include HTML format?"*

**Format guidance — needs post-editing**
Condition: user mentions "clean it up", "edit after", "hand off to client"
Moment: during output format selection
> *"Sounds like you'll want to edit this — PPTX keeps it fully editable in PowerPoint."*

---

## REVIEW Flags

Embedded in speaker notes on slides that need human judgment before finalizing.

### Format
```
[REVIEW: reason — brief description of what needs checking]
```

### When to flag

| Trigger | Flag text |
|---|---|
| Conflicting data across sources | `[REVIEW: conflicting figures — source A says X, source B says Y]` |
| Stat or claim without a clear source | `[REVIEW: unverified stat — confirm before presenting]` |
| Ambiguous direction (made a judgment call) | `[REVIEW: assumed [direction] — verify this framing]` |
| Content gap (no source material found) | `[REVIEW: content gap — no source material for this slide]` |
| Image placeholder (no match found) | `[REVIEW: no image found — add manually or adjust keywords]` |
| Estimated/inferred data | `[REVIEW: estimated value — replace with actual data]` |
| Audience assumption | `[REVIEW: assumed executive audience — adjust tone if different]` |

### Flag Summary Slide

When flag count > 3, prepend a hidden summary slide (slide 0):
```
REVIEW SUMMARY — [N] slides flagged

  Slide 3:  conflicting figures on cost estimate
  Slide 7:  content gap — migration timeline
  Slide 11: unverified stat — 40% efficiency claim
  Slide 14: no image found

This slide is for internal review only. Delete before presenting.
```

### Strict Mode

When strict mode is requested, instead of flagging and continuing, pause at each conflict and
ask the user to resolve inline. Best for high-stakes decks.

---

## Preview-to-Confirm

Fired when direction is genuinely ambiguous. Use sparingly.

**Triggers:**
- More than 20% of slides have no clear source content
- Topic is ambiguous enough that structure could go multiple ways

**Format:**
> "Here's the structure I'm planning:
>
> 1. Title — [proposed title]
> 2. The Challenge — [summary]
> 3. Our Approach — [summary]
> 4–6. [section name] — [brief]
> 7. Next Steps — [CTA framing]
>
> ⚠ Slides 4–6 are light on content — marked [GAP].
>
> Does this look right, or want to adjust before I build?"
