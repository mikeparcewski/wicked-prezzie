# Spacing Negotiation Protocol

How to handle spacing requests without falling into blind iteration loops.

## Non-Negotiable Minimums

These values cannot be reduced regardless of content pressure:

| Property | Minimum | Rationale |
|---|---|---|
| Edge margin | 48px from all slide edges | Content must not bleed to edge |
| Body text size | 18px | Readability at presentation distance |
| Card padding | 12px (vertical) / 14px (horizontal) | Text must not touch card border |
| Line height | 1.4 (body) / 1.15 (titles) | Readability and visual breathing room |
| Whitespace | 30% of slide area empty | Prevents visual density overload |
| Element gap | 12px minimum between sibling elements | Prevents visual crowding |

If content cannot fit within these minimums, the correct fix is to split the
slide, not to reduce spacing below minimums.

## Three-Options Protocol

When a spacing request is ambiguous ("make this tighter", "more breathing room",
"spread it out"), do not make a single blind edit. Instead, offer three options
with specific pixel values:

```
I can adjust the spacing in three ways:

Option A — Compact (16px gap): Cards closer together, more content visible.
  Gap: 16px between cards, padding: 12px 16px per card.

Option B — Balanced (24px gap): Current target. Standard presentation density.
  Gap: 24px between cards, padding: 16px 20px per card.

Option C — Spacious (36px gap): Maximum breathing room, fewer elements per row.
  Gap: 36px between cards, padding: 20px 24px per card.

Which looks right for this slide? You can also open the slide in your browser
and tell me which option you prefer after seeing it.
```

Always offer options with **specific pixel values**, not adjectives.

## Browser Preview Guidance

For visual adjustments where intent is unclear, ask the user to open the slide
during edits:

> "Open [path/slide-NN.html] in your browser. I will make three spacing options —
> tell me which looks right before I finalize."

This prevents multiple back-and-forth iterations for purely visual decisions.
The browser renders immediately; Claude's text description cannot substitute
for visual inspection.

## Batch Editing

When the user mentions multiple elements or multiple slides:
- Fix all related spacing in one pass, not one element at a time
- Identify all elements of the same type (all cards, all section headers) and
  update them consistently
- Do not ask for confirmation between each element — batch the full pass,
  then present the result

Example: If the user says "the cards feel cramped on slides 3, 7, and 12":
- Read all three slides first
- Identify the common pattern causing the issue
- Write a single fix that addresses all three in one edit
- Report: "Updated card gap to 24px and padding to 16px 20px on slides 3, 7, 12."

## When to Compress vs. Split

### Compress (reduce spacing/font) when:
- Content is over by <10% (one extra bullet, slightly oversized metric)
- Reducing padding from 20px to 16px would fix it
- Font size reduction from 18px to 16px stays above minimums
- Two-column layout would fit content without reducing text size

**Compression adjustments in order of preference**:
1. Reduce gap between cards (24px → 16px)
2. Reduce card padding (20px → 14px)
3. Reduce section header size (11px → 10px is acceptable)
4. Switch to two-column layout
5. Reduce body font (never below 16px for cards, 18px for main body)

### Split the slide when:
- Content is over by >15% (multiple bullets, substantial overflow)
- Any minimum would be violated to fit
- Reducing font would harm readability for the slide's purpose
- The slide has two distinct topics that could each stand alone

## Anti-Pattern: Blind Iteration Loops

A blind iteration loop occurs when:
- The same file is edited 3+ times in 5 minutes
- Each edit is a single-value change without visual confirmation
- The user says "still not right" after each attempt

Signs you are in a loop:
- 6 messages in 4 minutes for one spacing element
- Each message changes a single px value
- No visual verification between attempts

**Break the loop by**:
1. Stopping and offering the three-options protocol
2. Asking the user to open the slide in browser
3. Batching all remaining spacing changes into one pass based on what the user
   describes as the target feel ("more spacious", "more compact")

The `micro-iteration-detector` hook fires after 3 edits to the same file within
5 minutes and suggests this intervention automatically.

## Diagnostic Questions Before Editing

Before any spacing edit, confirm:

1. **What is the reference?** — Is there another slide in the deck that looks right?
   Match that slide's spacing values exactly.
2. **What is the target feel?** — Compact (content-dense), balanced (standard),
   or spacious (impactful). Maps to the three options above.
3. **What is changing?** — Gap between elements, padding inside elements, or
   margin from slide edge? These are different properties.

Getting answers to these three questions eliminates most iteration loops.
