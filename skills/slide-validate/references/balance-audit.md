# Balance Audit

Methodology for checking content ratio, redundancy, and flow cohesion. Run at
80%+ deck completion before final review.

## When to Run

- After the deck reaches 80% completion (before polish phase)
- When slide count exceeds the cap (e.g., 30+ main slides)
- When validation finds Acts 2-3 feel "overweight" or "catalog-like"
- When the council identifies redundancy clusters

## Step 1: Categorize Every Slide

For each slide, assign one category:

- **PROOF** — demonstrates client knowledge, operational history, or domain
  credibility. Evidence of who we are, what we've done.
- **SOLUTION** — explains a mechanism, capability, or methodology. Evidence of
  what we do and how it works.
- **BOTH** — combines client context with mechanism explanation. The strongest
  slide type.

## Step 2: Calculate the Ratio

Count slides in each category:

```
Proof slides:    N_proof    = ___
Solution slides: N_solution = ___
Both slides:     N_both     = ___
Total:           N_total    = ___

Proof ratio:    N_proof / N_total    (target: 30%)
Solution ratio: N_solution / N_total (target: 40%)
Both ratio:     N_both / N_total     (target: 30%)
```

**Target ratio**: 30% proof / 40% solution / 30% both.

**Threshold**: If proof exceeds 40%, the deck is over-indexed on client
demonstration. A technically sophisticated evaluator will find it unscoreable
on methodology criteria.

## Step 3: Redundancy Cluster Detection

A redundancy cluster = 3+ slides making the same core claim.

Common clusters to check for:
- "We know your portfolio" — 3+ slides asserting domain knowledge
- "We understand urgency" — 3+ slides asserting priority/timeline awareness
- "Trust us" — 3+ slides asserting competence without mechanism
- Repeated pillar enumeration — pillar names appearing 3+ times without deepening

For each cluster:
- List the slide numbers and their core claim
- Recommend: reduce to 1-2 slides maximum
- Assign freed positions to missing solution mechanism slides

**Example output**:
```
Cluster: "We know your portfolio" — Slides 4, 18, 24 (3 slides, 1 claim)
  Recommendation: Merge slides 4 and 18. Retool slide 24 as a mechanism slide.
  Freed position: Use slide 24 for Scoring Engine internals.
```

## Step 4: Missing Concept Identification

List concepts that appear in the outline or RFP but have no dedicated slide:

```
Missing concepts (zero slides):
- Scoring Engine internals
- Predictive Quality Engine
- Self-Healing Pipeline
- Security Automation
- Compliance Stage Gates
- Code Graph architecture
- Agentic authority boundaries
```

For each missing concept: recommend which existing slide could be retooled or
where a new slide should be inserted.

## Step 5: Flow Cohesion Review

### Per-Act Rating

Rate each act through 5 persona lenses:

| Persona | Act 1 | Act 2 | Act 3 | Act 4 | Act 5 |
|---|---|---|---|---|---|
| CIO / Champion | /10 | /10 | /10 | /10 | /10 |
| Principal Engineer | /10 | /10 | /10 | /10 | /10 |
| CFO Proxy | /10 | /10 | /10 | /10 | /10 |
| CISO | /10 | /10 | /10 | /10 | /10 |
| VP Sourcing | /10 | /10 | /10 | /10 | /10 |

Flag any act rated below 7 by any Tier 1 persona (CIO, Principal Engineer, CFO).

### One-Line-Per-Act Test

Each act must be stateable in one sentence. If not, the act is unfocused.

```
Act 1: ___ (one sentence)
Act 2: ___ (one sentence — if you cannot, flag as unfocused)
Act 3: ___
Act 4: ___
Act 5: ___
```

### Reorder Recommendations

List any slides that would land better in a different position:
- Slides that should move earlier (context needed sooner)
- Slides that should move later (reveal too early)
- Slides that should be merged (same claim, adjacent positions)

## Council Punch List Format

After the balance audit, produce a punch list of 10-15 items:

```
Punch list (15 items):

BLOCKING:
1. [Slide 19] Mechanism missing: Knowledge Layer named but not shown. Add architecture diagram.
2. [Slide 22-24] Three slides make the same "trust us" claim. Cut 2, retool 1 as mechanism.
3. [Act 2] No slides cover: Scoring Engine, Predictive Quality Engine, Self-Healing Pipeline.

RECOMMENDED:
4. [Slide 5] Genericness: Replace "mission-critical apps" with [System-A], CONNECT, Omega.
5. [Act 3] One-line test fails: "Act 3 explains five pillars" — but pillars are named, not explained.
...

3 THINGS THAT WILL LOSE THE DEAL:
1. Five core concepts rated ASPIRATIONAL — a technically sophisticated evaluator cannot score us.
2. Zero slides for 7 solution concepts — our methodology section is an assertion, not a demonstration.
3. Acts 1-2 are indistinguishable from a capable-but-generic AI delivery proposal.

3 THINGS THAT WILL WIN THE DEAL:
1. Slide 3 is a moat slide — 31 named platforms, 9 personas, 11 elimination candidates.
2. Fee-at-risk threading (slides 3→8→12→20) is the most differentiated commercial structure.
3. The 2am scenario is the most human moment in the deck — close it in Act 5.
```

## Rebalancing Recipe

When proof > 40%:

1. Identify redundancy clusters (Step 3)
2. Select N slides to cut or merge (from clusters)
3. Identify N missing mechanism concepts (Step 4)
4. Replace cut slides with mechanism slides
5. Re-run ratio calculation
6. Target: proof at 30%, solution at 40%, both at 30%

The cut/add should be equal — the slide count stays constant. Every addition
must justify a corresponding removal.
