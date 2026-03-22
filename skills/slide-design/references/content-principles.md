# Content Principles (Slide-Level)

Design rules that apply to individual slide content. These govern what a single
slide should communicate and how to structure its content. For deck-level
narrative rules (arc, threading, persona coverage), see the slide-pipeline and
slide-outline references.

## Assertion-Evidence Structure

Every slide should be structured as: **Title = Claim, Body = Evidence**.

The title is not a label ("Revenue") — it is an assertion ("Revenue grew 40% in
Q3"). The body elements (bullets, cards, stats) are the evidence that supports
the title claim. If the body does not support the title, the slide has no focus.

**Test**: Cover the slide body. Does the title alone state something the
audience should believe? Cover the title. Does the body alone prove something?
If both are true, the structure is correct.

**Wrong**: Title = "Our Approach", Body = list of approach components
**Right**: Title = "Three mechanisms deliver the 40% reduction", Body = three mechanism cards

## One Message Per Slide

Each slide communicates one message. If you can summarize the slide in one
sentence, it passes. If you need two sentences, the slide should be two slides.

**Test**: State the slide's message in one sentence. If you cannot, identify
which two messages are competing and split them.

Common violations:
- "Problem and solution" on the same slide
- "Two case studies" on the same slide
- "Methodology overview and first step" together

The exception: a BOTH slide that pairs client proof with mechanism explanation.
This is one message (we solved this problem using this mechanism).

## Bullet Discipline

- 3-5 bullets per slide maximum
- Each bullet under 15 words
- Bullets are evidence points, not sub-topics
- No sub-bullets (nested bullets = content that belongs on a separate slide)
- Each bullet must directly support the title claim

**Wrong**: Title = "AI Reduces Costs", Bullets = [AI Overview, Cost Model, Savings Calculator, ROI, Timeline, Next Steps]
**Right**: Title = "AI reduces costs through three mechanisms", Bullets = [mechanism 1, mechanism 2, mechanism 3]

If a bullet would need a paragraph to explain, it is a slide topic, not a bullet.

## Title as Claim, Not Label

Titles that are labels waste the most valuable real estate on the slide.
Label titles tell the audience what they are about to see. Claim titles tell
them what to believe.

| Label (wrong) | Claim (right) |
|---|---|
| Revenue | Revenue grew 40% in Q3 |
| Our Approach | Three mechanisms deliver the result |
| Timeline | Phase 1 completes in 90 days |
| Security | Zero data leaves the client environment |
| Team | 12 engineers with direct [client system] experience |

Every title should pass this test: "If a committee member reads only this title,
do they know what we claim?" If the answer is "they know the topic", the title
is a label. If the answer is "they know the claim", it is an assertion.

## Proof Not Pitch (Slide Level)

At the slide level, proof means the slide demonstrates rather than asserts.

**Pitch**: "We have deep domain expertise in network operations."
**Proof**: "We identified 11 elimination candidates across 31 client platforms in Phase 0."

**Pitch**: "Our AI reduces manual effort."
**Proof**: "The Scoring Engine routes 847 tickets/day. Engineers review exceptions only."

For every capability claim on a slide:
1. Name the specific system or component (not the category)
2. Include a specific metric, figure, or named output
3. Show the mechanism if there is room — if not, ensure a companion mechanism slide exists

Generic claims ("our AI", "our platform", "our experts") are not proof.
Named systems, specific figures, and named programs are proof.

## Mechanism Before Outcome

On any slide that makes a capability or results claim:
- Show the mechanism (how it works) before stating the outcome (what it delivers)
- If space permits both, lead with the mechanism
- If space permits only one, show the mechanism and reference the outcome in speaker notes

**Wrong order**: "We deliver 25% cost savings [outcome]. Our AI scores tickets by urgency [mechanism]."
**Right order**: "Our AI scores tickets by urgency across 4 dimensions [mechanism], delivering 25% cost savings [outcome]."

This is the "V1 pattern" that produced the strongest slides. When v3 inverted it,
the council punch list noted: "V1 built mechanism first, then asserted outcomes.
V3 reversed this. 5 of 6 core concepts rated ASPIRATIONAL."

## Client Specificity Test

Before a slide is complete, apply the client specificity test:

> "Does this slide contain a named system, a dollar figure, or a named metric
> specific to this client? If not, it is incomplete."

Slides that pass: name the client's systems, platforms, programs, and figures.
Slides that fail: could be presented to any enterprise client without changes.

Acts 1-2 are most vulnerable to genericness. Apply the test to every slide in
the deck's opening acts — they need the same specificity as the methodology acts.

**Client specificity markers**:
- Named application systems (specific client system names, not categories)
- Named programs with dates (specific migration programs)
- Named technology stack (GCP, Vertex AI, Gemini)
- Named leadership (referenced by role, not by name in client-facing decks)
- Specific dollar figures from client disclosures
- Client-specific metrics (not "our customers see 40%" but "[Client]'s [System A] sees 40%")

## Whitespace as Content

Whitespace is not wasted space — it is a design element that directs attention.
Target 30%+ of every slide as empty space. When a slide feels dense, the first
fix is removing elements, not reducing font size.

**Priority order for element removal**:
1. Remove the least-important bullet (the one that supports the title least directly)
2. Remove a decorative element (divider, icon, secondary badge)
3. Merge two cards if they make the same sub-point
4. Move content to speaker notes if it is delivery guidance, not audience content

Do not reduce font sizes below minimums (18px body, 11px section label) to fit
more content. That content belongs on a different slide.
