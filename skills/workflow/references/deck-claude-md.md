# Per-Deck CLAUDE.md — Generation and Consumption

Every deck project gets its own `CLAUDE.md` file that captures editorial and
design directives specific to that deck. This file is the single source of truth
for "how should this deck sound, look, and feel" — distinct from `constraints.json`
which captures runtime-learned rules about what breaks during production.

---

## When It Is Generated

The per-deck `CLAUDE.md` is created at the end of Phase 1 (Source Inventory),
after the facts manifest is complete and the workflow template is confirmed. The
generation sequence is:

1. `facts-manifest.json` passes its gate check (source documents cataloged,
   user confirms completeness)
2. The workflow template is selected (general, rfp-response, or custom)
3. The orchestrator generates `{deck_dir}/CLAUDE.md` from three inputs:
   - User-provided directives (audience, tone, preferences stated in conversation)
   - Source document signals (audience markers, language style, terminology
     extracted during Phase 1)
   - Template editorial defaults (if the selected template defines default
     voice, formality, or content style)

The file is updated incrementally throughout the session as the user provides
editorial feedback. Any user correction that represents an editorial preference
(not a CSS bug or layout constraint) is written to `CLAUDE.md` rather than
`constraints.json`. Examples:

- "Make it less salesy" → update the Tone section
- "Always say 'platform' not 'solution'" → update the Terminology section
- "The CFO cares most about margin impact" → update the Audience section
- "Cards break when centered" → this is a constraint, goes to `constraints.json`

---

## Where It Is Written

```
{deck_dir}/CLAUDE.md
```

The deck project directory, set during Phase 1 initialization. This is NOT the
repository root CLAUDE.md — it is a per-project file that lives alongside the
deck's slides, state files, and assets.

Example path: `~/Projects/acme-q3-kickoff/CLAUDE.md`

The orchestrator writes it directly. No script is involved — this is methodology,
not automation.

---

## Tools and Content Navigation

The per-deck `CLAUDE.md` must include a section directing agents to use
wicked-prezzie's own tools for navigating and grounding content. This ensures
agents don't hallucinate facts when indexed source material is available.

```markdown
## Content Tools

When building slides or writing narrative, use these tools to find and verify content:

- **wicked-prezzie:learn** — Index source documents before building. Run this first.
- **wicked-prezzie:outline** — Search the outline for slide structure and key messages.
- Use `_insights/key-facts.md` for verified facts, figures, and proof points.
- Use `_insights/narrative-themes.md` for recurring themes to reinforce.
- Use `_tags/` for faceted lookup by topic (technical, financial, competitive, etc.).
- Use `_relationships/` for entity cross-references across source documents.
- Grep specific chunk files for detailed content when a fact needs source attribution.

Never invent statistics, client names, or technical claims. If the indexed
content doesn't support a claim, flag it for the user rather than fabricating.
```

This section is generated automatically and should not be removed by the user.

---

## Required Sections

Every per-deck `CLAUDE.md` must contain these six sections plus the Content Tools
section above. The orchestrator populates each section from the sources described
below. Sections may be sparse at initial generation (end of Phase 1) and are
enriched as the workflow progresses.

### Audience

Who the deck is for. This section drives persona creation in Phase 2, content
specificity in Phase 5, and validation lens calibration in Phase 6.

**Must include**:
- Primary audience role and seniority level (e.g., "C-suite executives at a
  mid-market SaaS company")
- Their key concerns — what keeps them up at night, what they need to believe
  after seeing this deck
- Decision-making context — are they approving a budget, evaluating a vendor,
  aligning on strategy?
- Secondary audiences if the deck will be forwarded or presented in multiple
  contexts

**Derived from**:
- Direct user input ("this is for the board", "the audience is engineering
  managers")
- Source document audience markers — RFP addressees, prior deck title slides,
  executive summary salutations
- Template defaults — the `rfp-response` template defaults to procurement
  evaluators; `general` defaults to asking the user

**Example**:
```markdown
## Audience

Primary: VP-level and above at [Company], specifically the transformation
steering committee (8 members, mix of business and IT leadership).

Key concerns: They need confidence that the proposed approach will deliver
measurable outcomes within the 18-month timeline. The CFO will scrutinize
total cost of ownership. The CTO will probe technical feasibility of the
integration architecture.

Secondary: The deck will be forwarded to the broader leadership team (~30
people) who were not in the room. It must be self-explanatory without a
presenter.
```

---

### Tone

Where this deck sits on the formal-to-conversational and technical-to-accessible
spectra. Tone is not a single word — it is a calibrated position with rationale.

**Must include**:
- Formality level with rationale (formal/semiformal/conversational and why)
- Technical depth target (executive summary level, practitioner level, or mixed)
- Emotional register — is this aspirational, pragmatic, urgent, reassuring?
- What to avoid — specific anti-patterns for this audience ("no buzzwords",
  "no fear-based selling", "no unsubstantiated superlatives")

**Derived from**:
- Template editorial voice defaults (if the template specifies a voice profile)
- Source document style — an RFP written in formal procurement language suggests
  a formal response; a startup pitch doc suggests conversational
- User preference — explicit instructions override all defaults

**Example**:
```markdown
## Tone

Semiformal, pragmatic. This audience is senior enough to reject corporate-speak
but expects structured argumentation, not casual storytelling.

Technical depth: mixed. Lead with business outcomes on every slide, but include
a technical appendix section for the CTO's team. Do not hide complexity — frame
it as "here is the hard part and here is how we solve it."

Avoid: superlatives without evidence ("world-class", "best-in-class"),
hypothetical futures without named mechanisms, passive voice on action items.
```

---

### Key Themes

The 3-5 core messages that the deck must reinforce throughout. These are not
slide titles — they are the throughlines that connect the narrative arc. Every
slide should trace back to at least one theme.

**Must include**:
- 3-5 themes, each stated as a complete sentence (not a label)
- For each theme: which slides or sections will carry it, and how it connects
  to the audience's concerns
- Priority ordering — if slides must be cut, which themes survive?

**Derived from**:
- `slide-learn` output: `_insights/narrative-themes.md` (if source documents
  were indexed)
- Brainstorm synthesis output (updated after Phase 3)
- User input — explicit theme statements override extracted themes
- Facts manifest — recurring patterns across source documents suggest themes

**Example**:
```markdown
## Key Themes

1. **Modernization reduces risk, not just cost.** The primary argument. Every
   technical slide must connect back to risk reduction (operational, regulatory,
   talent retention). Carries the narrative arc from problem → approach → proof.

2. **The integration architecture is proven, not experimental.** Counter the
   audience's skepticism about feasibility. Supported by the three reference
   implementations in the facts manifest.

3. **Speed to value is measured in quarters, not years.** Addresses the CFO's
   timeline concern. The phased roadmap slide and the quick-wins section both
   reinforce this.

Priority: If the deck must shrink, themes 1 and 3 survive. Theme 2 can be
moved to a technical appendix.
```

---

### Terminology

Preferred and forbidden terms, acronyms with expansions, and language
conventions. This section prevents inconsistency across slides built by
different agents and catches domain-specific language that generic AI might
get wrong.

**Must include**:
- Preferred terms with context ("say X, not Y" format)
- Forbidden terms with rationale (why this term is wrong for this audience)
- Acronyms with full expansions (first use expands, subsequent uses abbreviated)
- Client-specific or industry-specific naming conventions

**Derived from**:
- Source documents — extract the exact terms the client uses for their own
  systems, programs, and initiatives. Never rename a client's named system.
- Industry conventions — if the audience is in healthcare, use "patient" not
  "customer"; if financial services, use "client" not "user"
- User corrections during the session — any "don't call it X, call it Y"
  feedback is captured here immediately

**Example**:
```markdown
## Terminology

Preferred:
- "platform" not "solution" (user preference, stated in session)
- "modernization" not "transformation" (client's own language in all source docs)
- "Horizon" — the client's internal name for their ERP system. Always capitalize.

Forbidden:
- "disrupt" / "disruptive" — this audience associates it with risk, not innovation
- "leverage" as a verb — the CPO flagged this in prior feedback as corporate jargon
- "AI-powered" without specifying which model or technique

Acronyms:
- TCO — Total Cost of Ownership (expand on first use per slide)
- SLA — Service Level Agreement
- CSAT — Customer Satisfaction Score
```

---

### Brand Constraints

Visual and identity guidelines that apply to every slide. This section is
consumed by `slide-generate` (Phase 5) and `slide-validate` (Phase 6) to
enforce brand consistency.

**Must include**:
- Color guidance — primary/secondary/accent colors, background preferences,
  colors to avoid
- Font preferences — heading and body fonts, size ranges, weight conventions
- Logo usage rules — placement, minimum size, clear space, when to include
  vs. omit
- Visual style — photography vs. illustration, icon style, chart aesthetics,
  data visualization preferences

**Derived from**:
- Active theme (`slide-theme` skill) — if a theme is loaded, its color palette
  and font stack are the starting point
- Brand guide — if the user provided a brand guide and it was indexed via
  `slide-learn`, extract the relevant rules
- User input — explicit overrides ("use dark backgrounds", "no stock photos")

**Example**:
```markdown
## Brand Constraints

Colors: Dark backgrounds (midnight navy #1a1a2e or charcoal #2d2d3d). Accent
color is electric blue (#00a8ff) — used for highlights, stats, and CTAs only.
Avoid red except for risk/warning callouts.

Fonts: Headings in Montserrat Bold, body in Inter Regular. Minimum body size
18pt for readability in large rooms. No italics in body text.

Logo: Client logo top-right on title and closing slides only. Do not place
on every slide. Minimum clear space is 20px on all sides.

Visual style: Prefer abstract geometric patterns over stock photography.
Icons should be line-style (not filled), matching the accent color. Charts
use the brand palette — no default Excel colors.
```

---

### Editorial Preferences

A catch-all section for user-supplied preferences that do not fit neatly into
the other sections. This section starts empty and grows as the user provides
feedback during the session.

**Must include**:
- Any user preference that affects content creation but is not a constraint
  (constraints go to `constraints.json`)
- Timestamped entries so the orchestrator can see when preferences were added
- Source attribution — was this stated by the user or inferred from feedback?

**Derived from**:
- User feedback during the session — captured incrementally
- Corrections that reveal preferences ("I changed that slide because..." implies
  a preference)
- Explicit instructions ("always include a takeaway box at the bottom of
  content slides")

**Example**:
```markdown
## Editorial Preferences

- [Phase 3] Keep bullet points to 3 per slide maximum. If more content is
  needed, split into two slides rather than adding bullets. (User stated.)

- [Phase 5] Every content slide should end with a "So what?" takeaway line
  in the bottom-right. Use the accent color for this element. (User stated.)

- [Phase 5] Stat slides should lead with the number, not the label. "4.2M
  active users" not "Active users: 4.2M". (Inferred from user edits to
  slides 7 and 12.)

- [Phase 7] The closing slide should mirror the opening slide's visual
  structure but with a forward-looking message. (User stated during polish.)
```

---

## How Agents Consume It

Every agent prompt dispatched by the orchestrator must include the full contents
of `{deck_dir}/CLAUDE.md` under a dedicated section header. This is mandatory —
the same enforcement level as constraint injection (Guard 1).

### Agent Prompt Structure (Updated)

```
## Your Role
[Role-specific instructions from the agent catalog]

## Project Context
[Compressed facts manifest summary]

## Deck Editorial Context
[Full contents of {deck_dir}/CLAUDE.md — all six sections, verbatim.
 Do not summarize, abbreviate, or selectively include sections.
 If the file does not exist yet (Phase 1 not complete), omit this section
 entirely rather than inserting a placeholder.]

## Constraints (MANDATORY)
[All constraints from constraints.json where applies_to includes current phase]

## Your Task
[Specific task for this agent instance]

## Output Format
[Exact file paths, schema, definition of done]
```

### Enforcement Rules

1. **No agent dispatch without CLAUDE.md after Phase 1**: Once Phase 1 is
   complete and `CLAUDE.md` has been generated, every subsequent agent prompt
   must include the `## Deck Editorial Context` section. An agent prompt
   dispatched after Phase 1 without this section is malformed and must not be
   sent.

2. **Full inclusion, not summary**: The entire `CLAUDE.md` is included verbatim.
   Agents may receive context they do not directly use (e.g., a validation agent
   receives Brand Constraints even though it does not build slides). This is
   intentional — it allows agents to flag violations they observe even if fixing
   them is not their primary task.

3. **Phase 1 agents are exempt**: During Phase 1 (Source Inventory), the
   per-deck `CLAUDE.md` does not yet exist. Source-scanner agents do not receive
   it. This is the only phase where the section may be absent.

4. **Updates propagate immediately**: When the orchestrator updates `CLAUDE.md`
   mid-session (e.g., user provides new terminology preferences during Phase 5),
   all subsequent agent dispatches use the updated file. Agents already running
   are not recalled — but if their output violates the new preference, it will
   be caught during validation (Phase 6) or polish (Phase 7).

---

## Relationship to constraints.json

Per-deck `CLAUDE.md` and `constraints.json` are complementary, not competing.
They capture different categories of project knowledge:

| Dimension | CLAUDE.md | constraints.json |
|-----------|-----------|-----------------|
| **What it captures** | Editorial and design directives — how the deck should sound, look, and feel | Runtime-learned rules — what breaks during production and how to avoid it |
| **When it is written** | End of Phase 1, updated on editorial feedback | Initialized from defaults, updated when bugs recur |
| **Who writes it** | Orchestrator, from user input and source analysis | Orchestrator, from failed build/validation attempts |
| **Example entry** | "Say 'platform' not 'solution'" | "Never use `justify-content: center` on card grids — it collapses vertical spacing" |
| **Consumed by** | All agents after Phase 1 (editorial alignment) | All agents in applicable phases (defect prevention) |
| **Persistence** | Per-deck, lives in deck directory | Per-deck, lives in `state/constraints.json` |

**Routing rule**: If the user's feedback is about content, language, audience,
tone, or visual identity → `CLAUDE.md`. If the user's feedback is about
something that broke or renders incorrectly → `constraints.json`. If unclear,
ask the user: "Is this a preference for how the deck should feel, or a rule
about what not to do because it breaks?"

---

## Generation Procedure (Phase 1 Completion)

When Phase 1's gate condition is satisfied, the orchestrator generates
`CLAUDE.md` using this procedure:

1. **Gather user-stated directives**: Review the conversation for any
   explicit statements about audience, tone, terminology, or visual style.
   These take highest priority.

2. **Extract source document signals**: From `facts-manifest.json`, identify:
   - Addressees and audience markers (RFP headers, exec summary recipients)
   - Language style (formal procurement language vs. casual pitch language)
   - Named systems, programs, and domain-specific terms
   - Any brand or style guide references in the source documents

3. **Apply template defaults**: If the selected workflow template defines
   editorial defaults (e.g., `rfp-response` implies formal tone and
   procurement-evaluator audience), use these as the baseline. User-stated
   directives override template defaults.

4. **Write the file**: Generate all six sections. Sections with insufficient
   data should state what is unknown and what assumptions are being made,
   rather than being left empty. For example:
   ```markdown
   ### Brand Constraints

   No brand guide was provided. Using the active theme (midnight-purple) as
   the default palette. If a brand guide exists, provide it and this section
   will be updated.
   ```

5. **Present to user for review**: After writing, show the user the generated
   `CLAUDE.md` and ask: "Does this capture your editorial direction? Anything
   to add or change?" Incorporate feedback before advancing to Phase 2.

6. **Log generation**: Record in `deck-state.json` that `CLAUDE.md` was
   generated, with a timestamp and the sources used.

---

## Update Protocol

Updates to `CLAUDE.md` happen inline during the session. The orchestrator does
not wait for a phase boundary to update — it writes immediately when:

- The user states a preference ("make it less formal")
- The user corrects content in a way that reveals a preference (changing
  "leverage" to "use" across multiple slides implies a terminology rule)
- A brainstorm output (Phase 3) surfaces themes not previously captured
- A validation finding (Phase 6) reveals an editorial gap

Each update appends to the relevant section rather than rewriting it, unless the
update contradicts an existing entry (in which case the old entry is replaced
and the change is noted in Editorial Preferences with a timestamp).
