# Content Principles — 8 Reusable Patterns

Reference for `deck-brainstorm` skill. Eight content skills extracted from the [CLIENT]
deck project. Each pattern includes when to use it, what it produces, key rules, and a
concrete example. Apply these during brainstorm team sessions and as review criteria
against the finished deck.

---

## 1. Mechanism Before Outcome

**When to use**: Every slide that makes a claim about results or capabilities.

**What it produces**: Slides where the audience understands HOW something works before
being told WHAT it delivers. Credibility earned through demonstration, not assertion.

**Key rules**:
- Show the mechanism first, then state the outcome. Never reverse this.
- Name the specific components, not just the category. Not "AI reviews code" but
  "Our agents review code changes to YOUR provisioning system."
- If a concept is named but not explained, it is a label, not a capability.
- Target 30-37% mechanism density across the deck (mechanism slides as share of total).
  Below 25% is a credibility failure; above 45% risks losing narrative flow.

**Concrete example**: V1 slide 10 (Scoring Engine) showed 4 scoring dimensions, routing
logic, and the output dashboard BEFORE stating the 25% YoY savings claim. The council
punch list caught when v3 reversed this: "V1 built mechanism first, then asserted outcomes.
V3 reversed this." V3 had 5 of 6 core concepts rated ASPIRATIONAL because they were
named but not explained. The fix: add mechanism content to each aspirational slide before
reordering the narrative sequence.

---

## 2. Two-Layer Proof

**When to use**: Every slide that claims domain knowledge or operational capability.

**What it produces**: Slides with both an operational scenario AND execution evidence.
Neither layer alone constitutes proof. Together they are defensible.

**Key rules**:
- **Layer 1 — Operational scenario**: What happens at 2am? What does the engineer
  experience? What does the failure event look like from inside the system? This layer
  makes the claim feel real. It earns emotional credibility.
- **Layer 2 — Execution evidence**: The specific artifact, metric, decision log, or
  audit trail. The output the system produced. The number at the end of the process.
  This layer makes the claim defensible under technical scrutiny.
- You cannot have one without the other. A scenario without evidence is a story.
  Evidence without scenario is a data table.
- The scenario makes it real. The evidence makes it auditable.

**Concrete example**: V2 slide 08 (Pillar 1: Know Portfolio):
- Layer 1: [System-A] degradation at 2:47am, criticality correctly identified despite no
  explicit SLA tag — the scenario. Who was on call, what the system flagged, what the
  human engineer saw.
- Layer 2: Scored governance output showing the rationale, the override decision, and
  the audit trail — the evidence. An artifact the evaluator can examine.

The Operators team principle that emerged: "Every proof slide has two layers: operational
scenario plus execution evidence. You cannot have one without the other."

---

## 3. Drumbeat Threading

**When to use**: Any proposal with a commercial differentiator that needs to build
throughout the deck. Also applies to any concept the deck wants the audience to carry
with them from Act 1 through Act 5.

**What it produces**: A single concept that builds from plant to mechanics to culmination
across the full deck, never appearing as a one-time mention. The audience should feel
the concept growing in significance with each callback.

**Key rules**:
- **Plant** (Act 1): State the commitment as a headline. Create the question. Do not
  elaborate. The audience leaves Act 1 wondering how it works.
- **Build** (Acts 2-3): Brief callback per section — one sentence, not a slide. Ties
  the current content back to the commitment. "This pillar's KPI: [metric]."
- **Mechanics** (Act 3): Full reveal. Triggers, non-triggers, measurement methodology,
  quarterly cadence, cure periods. This slide earns the plant.
- **Culminate** (Act 4/5): Resolution. "What happens if we're wrong?" The emotional peak.
- Must appear in at least 5 slides across the deck.
- Never more than 3 consecutive slides without a mention.
- The longest gap must not exceed 15 minutes of presentation time.

**Concrete example**: V2 fee-at-risk threading map:
- Slide 3 PLANT: "[total-value] savings exposure at [fee-value] fee-at-risk" — creates the question
- Slides 8, 9, 10, 11 BUILD: Each pillar callback ("This pillar's KPI: [metric]")
- Slide 12 MECHANICS: Full reveal of triggers, non-triggers, measurement, quarterly cadence
- Slide 13 AI connection: Bridge sentence linking mechanism to intelligence layer
- Slide 20 CULMINATION: "What happens if we're wrong?" — emotional peak
- Slide 21 RESOLUTION: The answer to Act 1's question
- Slide 22 INVITATION: Discussion questions

Team B caught that slides 10-18 (15 minutes) had no fee-at-risk mention. Fix: added a
bridge sentence to slide 13. Rule: review the threading map before architecture is approved.

---

## 4. The Hallway Line

**When to use**: At the close of the methodology or architecture section (typically the
end of Act 2). One hallway line per deck; generate 3-5 candidates during brainstorm and
select the strongest.

**What it produces**: A single sentence that a committee member can repeat in their
debrief conversation, in the hallway, or to someone who did not attend the presentation.
If it spreads, it does your selling for you.

**Key rules**:
- Maximum 10-15 words. If it is longer, it will not be remembered.
- Must be surprising — not a restatement of what the audience already believes.
  If they could have said it themselves before the presentation, it is not the hallway line.
- Must teach something — not just inspire. The audience should understand something new
  after hearing it.
- Must differentiate — a competitor cannot say the same thing. If any vendor could claim
  this line, it is not differentiated enough.
- Test: "Would a committee member repeat this sentence in their debrief?"

**Concrete examples from [CLIENT] session**:
- Selected: "Don't give an agent a task. Give it a world to work in."
  Surprising (inverts how people think about AI agents), teaching (context architecture
  is the mechanism, not task assignment), differentiating (few vendors operate this way),
  repeatable (12 words).
- Alternate: "Your engineers aren't the bottleneck. Your ability to give AI the right
  context is." Also strong — surprising, teaching, differentiating. Slightly longer.

Generation process: Team 1 generates 3-5 candidates during the brainstorm session.
The synthesis round selects one based on the four criteria. The selected line must appear
on the hallway-line slide and in the speaker notes for Act 2's closing slide.

---

## 5. Protagonist Arc

**When to use**: When the deck opens with a human scenario or provocation. Applies to
most proposal decks — the human opening is the most common and most effective opening.

**What it produces**: An emotional arc that begins with a specific human moment and
returns to it in the close, transformed. The audience experiences a narrative resolution,
not just a product presentation.

**Key rules**:
- Open with a specific human scenario, not an abstraction. Not "digital transformation
  challenges" but "The last time [System-A] triggered a P1 at 2am, someone in this room was
  on the phone for six hours."
- Name the protagonist (the engineer at 2am, the PM on the phone, the ops director
  during the [network-event] event). The person must be recognizable to the audience.
- The protagonist must be revisited at the close of the deck. Act 5 must return to that
  person transformed: "That engineer at 2am — this is what changes for them."
- The close shows what changes for the PROTAGONIST, not just for the organization.
  Organizational outcomes (cost savings, efficiency) are less emotionally resonant than
  personal outcomes (that engineer sleeps through the night because the system escalates
  correctly before they are called).
- Abandoning the protagonist is the most common missed opportunity in proposal decks.
  If you open with a person and never return, you have a dramatic setup with no resolution.

**Concrete example**: Marketing brainstorm (session 17) caught the failure in V1:
"The P1 story opens the deck and is never closed. That engineer at 2am — what happens
to them? Act 5 should return: 'That engineer at 2am. This is what changes for them.'
The deck has a protagonist it abandons." This finding led to the Act 5 resolution slide
becoming a mandatory element of the approved architecture.

---

## 6. Proof Not Pitch

**When to use**: As the governing principle for every slide in the deck. This is not a
technique for one slide — it is the standard that all content must meet.

**What it produces**: Slides that earn credibility through demonstrated evidence rather
than asserting it through confident language. Evaluators who test claims will find them
defensible. Evaluators who read superficially will still find them compelling.

**Key rules**:
- "Incumbents with real data don't pitch transformation. They demonstrate it." Every slide
  that could be replaced with the word "trust us" has failed this test.
- Every performance claim must specify which tier, segment, or workstream it applies to.
  No averages across all applications. Show variance at the tail.
- Every AI claim must have a client-specific example. Not "AI reviews code" but "Our
  agents review code changes to YOUR provisioning system." The possessive matters.
- Named systems, not categories. [System-A], CONNECT, [System-C] — not "mission-critical
  applications." If the system has a name, use it.
- Named metrics, not ranges. If a range is required, provide base/expected/upside.
  A range without anchors is not a metric.

**Concrete example**: V1 slide 3 was rated the "moat slide" — it named 31 platforms,
9 personas with headcount, 11 elimination candidates, and specific programs (Cheetah,
FIM-to-3GIS, Visible). That level of specificity cannot be faked. A competitor cannot
replicate it. The validation brainstorm caught when v3 weakened this: "NorthStar
authorship is buried in a legal caveat. 'We built this assessment' is not stated."
The fix was one sentence: "There is no handover. We operate [System-A] today."

---

## 7. Client Specificity

**When to use**: As a review test applied to every slide before the deck ships. Also
applied during brainstorm as a filter on Team 2's proof slide requirements.

**What it produces**: Slides that could not be reused for another client without
substantial changes. Slides that prove the team did the homework — not by claiming it,
but by demonstrating it through specific content.

**Key rules**:
- "Every slide that does not have an app name, a dollar figure, or a named metric should
  be considered incomplete." This is the test. Apply it to every slide.
- Acts 1-2 are most vulnerable to genericness. The impulse is to lead with the universal
  argument and save the specific evidence for later. Resist this. Acts 1-2 need the same
  specificity medicine as Acts 3-4.
- The competitor test: "Could a capable-but-generic AI delivery vendor present this slide
  list for Acts 1-2 and be indistinguishable from this proposal?" If yes, Acts 1-2 need work.
- Must name the client's specific technology ecosystem (e.g., "Vertex AI and Gemini native
  — we work in your stack"). Generic AI capability claims fail this test.
- Must name operational history with specific programs. Not "extensive client experience"
  but "Cheetah, FIM-to-3GIS, Visible — programs we ran, not programs we advised on."
- Must include the client's internal terminology (application names, initiative names,
  leadership names where appropriate for discussion questions).

**Concrete example**: Validation 4 ("Know Them") found Acts 1-2 named [System-A] but missed
CONNECT, [System-C], NTAS, and vRepair. Operational history (Cheetah, FIM-3GIS,
Visible) was absent. The client's AI ecosystem (GCP/Vertex/Gemini) had no slide reference.
Three non-negotiable additions and five additional slide edits were required.

---

## 8. [union-agreement]-Safe Language

**When to use**: For any deck involving workforce transformation at a unionized client,
or any client where workforce impact is politically sensitive. Apply as a slide-by-slide
audit during the review phase.

**What it produces**: A deck that addresses workforce implications without triggering
labor relations concerns. The workforce narrative feels affirmative and forward-looking,
not defensive.

**Key rules**:

Never say these terms:
- Leaner teams
- Fewer people
- Headcount reduction
- Labor savings
- Offshore substitution
- Right-sizing
- Role elimination

Always say instead:
- Workforce effectiveness
- Team throughput
- Capacity for sophisticated work
- Engineer productivity
- Expanded capability model (not "role transformation")
- Delivery model evolution
- Capacity redeployment (for any numerical workforce data — not headcount figures)

The governing principle: "AI handles volume, repetition, and low-judgment triage.
Humans handle complexity, judgment, and high-stakes decisions." Frame AI as expanding
human capability, not replacing it.

[union-agreement]-impacted workflows must be explicitly routed to full-board review. Do not embed
[union-agreement]-sensitive commitments in a slide deck without that routing documented.

The workforce slide must feel affirmative, not defensive. If a reader's first reaction
is to think about job losses, the framing has failed.

**Concrete example**: Review Team C (session 08) flagged 5 slides for [union-agreement] sensitivity:
- Slide 18: "Role Transformation" renamed to "Expanded Capability Model"
- Slide 37: Workforce capacity data labeled as capacity redeployment, not headcount
- C2 appendix: Framing rewritten to affirmative language
- Slide 7: "right-sizing" phrase replaced
- Slide 10: "Agile-era" replacement language applied
The workforce slide was rewritten to follow the principle: "AI handles volume, repetition,
and low-judgment triage. Humans handle complexity, judgment, and high-stakes decisions."

---

## Speaker Notes with RFP Mapping

Every slide in an RFP-response deck requires structured speaker notes. Notes that simply
restate the slide text are not speaker notes — they are a transcript. Speaker notes enable
an unprepared presenter to deliver confidently while maintaining RFP traceability.

### Three-Section Format

```
notes: >
  Delivery instructions. How to stand, what to pause on, what NOT to say.
  Example: "Make eye contact before speaking. Read the quote slowly. Let two full
  seconds of silence land before advancing."

rfp:
  - "Section: [Section Name] — '[exact RFP quote]'"
  - "Section: [Section Name] — '[exact RFP quote]'"

talking_points:
  - "Substantive point with objection handler. Example: 'If challenged on the [revenue-figure]
    figure: Source is [client]'s published IT spend disclosures. Not our estimate.'"
  - "Additional substantive point."
```

### Format Rules

- `notes` must NOT restate slide text. It provides delivery guidance: timing, tone,
  what to make eye contact for, what silence to let land. Written for a presenter who
  has seen the slide for the first time today.
- `rfp` entries must include the RFP section name and the exact quote from the RFP
  document. Not paraphrased. Not summarized. The exact language.
- `talking_points` must include anticipate-the-objection framing for every controversial
  or high-stakes claim. Format: state the claim, then "If challenged on [X]: [exact
  response language]."

### Slide-to-RFP Mapping Summary

The final slide or a notes appendix should include a mapping table: every RFP requirement
mapped to the slide(s) that address it. Evaluators use this to score submissions. If an
RFP requirement has no corresponding slide, it is a gap — not a slide structure problem.

### Example from [CLIENT] Session

V1 slide 1 notes included:
- Delivery: "Pause after 'that's the last time.' Let two full seconds of silence land."
- 6 RFP citations with exact section quotes
- 6 talking points including: "If challenged on the [revenue-figure] figure: 'Source is [CLIENT]'s
  published IT spend disclosures, not our estimate. The line item is on slide 3 of the
  2023 annual report.'"

The format was codified in `notes-data.js` as a structured JavaScript object with keys
for each slide number and three fields per slide: `notes`, `rfp` (array), `talking_points`
(array). The nav.js reads this and renders a notes panel, toggled by pressing N during
the presentation.
