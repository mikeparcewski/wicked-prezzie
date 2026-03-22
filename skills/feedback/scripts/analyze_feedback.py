"""Analyze parsed Word comments to find alignment, divergence, and narrative implications.

Takes the output of parse_word_comments.py and produces a structured feedback
report showing where reviewers agree, where they diverge, and what that means
for the narrative.

Usage:
    python analyze_feedback.py feedback.json [--output report.json]

Or programmatically:
    from analyze_feedback import analyze_feedback
    report = analyze_feedback(parsed_comments_dict)
"""

import json
import sys
from collections import defaultdict
from pathlib import Path


def _cluster_comments_by_topic(comments_in_section):
    """Group comments that reference the same or overlapping text passages."""
    if not comments_in_section:
        return []

    clusters = []
    used = set()

    for i, c in enumerate(comments_in_section):
        if i in used:
            continue

        cluster = [c]
        used.add(i)
        ref_text = c.get("referenced_text", "").lower()

        for j, other in enumerate(comments_in_section):
            if j in used:
                continue
            other_ref = other.get("referenced_text", "").lower()

            # Same passage if significant text overlap
            if ref_text and other_ref:
                overlap = _text_overlap(ref_text, other_ref)
                if overlap > 0.5:
                    cluster.append(other)
                    used.add(j)

            # Same surrounding paragraph
            elif (c.get("surrounding_paragraph", "").strip()
                  and c["surrounding_paragraph"] == other.get("surrounding_paragraph", "")):
                cluster.append(other)
                used.add(j)

        clusters.append(cluster)

    return clusters


def _text_overlap(a, b):
    """Simple word-level Jaccard similarity."""
    if not a or not b:
        return 0.0
    words_a = set(a.split())
    words_b = set(b.split())
    if not words_a or not words_b:
        return 0.0
    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)


def _classify_sentiment(text):
    """Basic sentiment classification of a comment."""
    text_lower = text.lower()

    positive_signals = [
        "agree", "good", "strong", "like", "works", "clear", "effective",
        "well done", "great", "nice", "solid", "perfect", "love", "excellent",
        "support", "endorse", "approve", "+1", "yes", "correct", "right",
    ]
    negative_signals = [
        "disagree", "concern", "weak", "unclear", "confusing", "remove",
        "delete", "wrong", "issue", "problem", "doesn't work", "misleading",
        "vague", "too ", "not sure", "question", "reconsider", "rethink",
        "missing", "lacks", "needs work", "needs rewriting", "rewrite",
        "revise", "rephrase", "not clear", "doesn't make sense", "off",
        "fix", "broken", "awkward", "clunky", "wordy", "redundant",
    ]
    suggestion_signals = [
        "suggest", "consider", "maybe", "could", "should", "what if",
        "how about", "alternatively", "instead", "recommend", "propose",
        "add", "include", "expand", "move", "swap", "reorder",
    ]

    pos = sum(1 for s in positive_signals if s in text_lower)
    neg = sum(1 for s in negative_signals if s in text_lower)
    sug = sum(1 for s in suggestion_signals if s in text_lower)

    # When there's a tie between concern and suggestion, lean concern
    # (a suggestion to fix something is still flagging an issue)
    if neg > 0 and sug > 0 and pos == 0:
        return "concern"
    if sug > pos and sug > neg:
        return "suggestion"
    elif neg > pos:
        return "concern"
    elif pos > neg:
        return "endorsement"
    elif neg > 0:
        return "concern"
    elif sug > 0:
        return "suggestion"
    else:
        return "observation"


def _detect_alignment(cluster):
    """Determine if a cluster of comments shows alignment or divergence."""
    if len(cluster) < 2:
        return "single_reviewer"

    authors = set(c["author"] for c in cluster)
    if len(authors) < 2:
        return "single_reviewer"

    sentiments = [_classify_sentiment(c["comment_text"]) for c in cluster]
    concerns = sum(1 for s in sentiments if s == "concern")
    endorsements = sum(1 for s in sentiments if s == "endorsement")
    suggestions = sum(1 for s in sentiments if s == "suggestion")

    total = len(sentiments)
    if concerns == total:
        return "aligned_concern"
    elif endorsements == total:
        return "aligned_endorsement"
    elif concerns > 0 and endorsements > 0:
        return "divergent"
    elif suggestions == total:
        return "aligned_suggestion"
    elif concerns > 0 and suggestions > 0:
        return "mixed_concern_suggestion"
    else:
        return "mixed"


def analyze_feedback(parsed_data):
    """Analyze parsed comment data and produce a feedback report.

    Args:
        parsed_data: Output from parse_word_comments.parse_docx_comments()

    Returns:
        dict with:
            - summary: high-level stats
            - alignment: where reviewers agree
            - divergence: where reviewers disagree
            - section_analysis: per-section breakdown
            - narrative_implications: what this means for changes
            - action_items: prioritized list of suggested changes
    """
    comments = parsed_data.get("comments", [])
    stats = parsed_data.get("stats", {})
    sections_list = parsed_data.get("sections", [])

    if not comments:
        return {
            "summary": {"total_comments": 0, "verdict": "No feedback received."},
            "alignment": [],
            "divergence": [],
            "section_analysis": [],
            "narrative_implications": [],
            "action_items": [],
        }

    # Classify each comment
    for c in comments:
        c["_sentiment"] = _classify_sentiment(c["comment_text"])

    # Analyze per section
    by_section = defaultdict(list)
    for c in comments:
        by_section[c["section"]].append(c)

    section_analyses = []
    all_alignment = []
    all_divergence = []
    action_items = []

    for section_name in sections_list:
        section_comments = by_section.get(section_name, [])
        if not section_comments:
            continue

        clusters = _cluster_comments_by_topic(section_comments)
        section_result = {
            "section": section_name,
            "total_comments": len(section_comments),
            "reviewers": sorted(set(c["author"] for c in section_comments)),
            "sentiment_breakdown": {
                "endorsements": len([c for c in section_comments if c["_sentiment"] == "endorsement"]),
                "concerns": len([c for c in section_comments if c["_sentiment"] == "concern"]),
                "suggestions": len([c for c in section_comments if c["_sentiment"] == "suggestion"]),
                "observations": len([c for c in section_comments if c["_sentiment"] == "observation"]),
            },
            "clusters": [],
        }

        for cluster in clusters:
            alignment_type = _detect_alignment(cluster)
            cluster_info = {
                "referenced_text": cluster[0].get("referenced_text", ""),
                "comments": [
                    {
                        "author": c["author"],
                        "text": c["comment_text"],
                        "sentiment": c["_sentiment"],
                    }
                    for c in cluster
                ],
                "alignment": alignment_type,
                "reviewer_count": len(set(c["author"] for c in cluster)),
            }
            section_result["clusters"].append(cluster_info)

            if alignment_type in ("aligned_concern", "aligned_suggestion", "mixed_concern_suggestion"):
                all_alignment.append({
                    "section": section_name,
                    "type": alignment_type,
                    "referenced_text": cluster[0].get("referenced_text", ""),
                    "reviewers": sorted(set(c["author"] for c in cluster)),
                    "comments": [c["comment_text"] for c in cluster],
                })
                # Aligned concerns = high priority action
                priority = "high" if alignment_type == "aligned_concern" else "medium"
                action_items.append({
                    "priority": priority,
                    "section": section_name,
                    "action": f"Address aligned {'concern' if 'concern' in alignment_type else 'suggestion'}",
                    "referenced_text": cluster[0].get("referenced_text", "")[:100],
                    "feedback_summary": "; ".join(c["comment_text"][:80] for c in cluster),
                    "reviewer_count": len(set(c["author"] for c in cluster)),
                })

            elif alignment_type == "divergent":
                all_divergence.append({
                    "section": section_name,
                    "referenced_text": cluster[0].get("referenced_text", ""),
                    "positions": [
                        {"author": c["author"], "sentiment": c["_sentiment"], "text": c["comment_text"]}
                        for c in cluster
                    ],
                })
                action_items.append({
                    "priority": "high",
                    "section": section_name,
                    "action": "Resolve divergent feedback — reviewers disagree",
                    "referenced_text": cluster[0].get("referenced_text", "")[:100],
                    "feedback_summary": "; ".join(
                        f"{c['author']}: {c['comment_text'][:60]}" for c in cluster
                    ),
                    "reviewer_count": len(set(c["author"] for c in cluster)),
                })

        section_analyses.append(section_result)

    # Handle sections with comments that weren't in the sections list
    for section_name in by_section:
        if section_name not in [s["section"] for s in section_analyses]:
            section_comments = by_section[section_name]
            section_analyses.append({
                "section": section_name,
                "total_comments": len(section_comments),
                "reviewers": sorted(set(c["author"] for c in section_comments)),
                "sentiment_breakdown": {
                    "endorsements": len([c for c in section_comments if c["_sentiment"] == "endorsement"]),
                    "concerns": len([c for c in section_comments if c["_sentiment"] == "concern"]),
                    "suggestions": len([c for c in section_comments if c["_sentiment"] == "suggestion"]),
                    "observations": len([c for c in section_comments if c["_sentiment"] == "observation"]),
                },
                "clusters": [],
            })

    # Sort action items: high priority first, then by reviewer count
    action_items.sort(key=lambda x: (0 if x["priority"] == "high" else 1, -x["reviewer_count"]))

    # Narrative implications
    narrative_implications = _derive_narrative_implications(
        all_alignment, all_divergence, section_analyses, stats
    )

    # Build summary
    all_sentiments = [c["_sentiment"] for c in comments]
    summary = {
        "total_comments": len(comments),
        "reviewer_count": stats.get("reviewer_count", 0),
        "reviewers": stats.get("reviewers", []),
        "sections_with_feedback": len(section_analyses),
        "total_sections": len(sections_list),
        "endorsements": all_sentiments.count("endorsement"),
        "concerns": all_sentiments.count("concern"),
        "suggestions": all_sentiments.count("suggestion"),
        "observations": all_sentiments.count("observation"),
        "alignment_points": len(all_alignment),
        "divergence_points": len(all_divergence),
        "high_priority_actions": len([a for a in action_items if a["priority"] == "high"]),
    }

    # Clean internal fields
    for c in comments:
        c.pop("_sentiment", None)

    return {
        "summary": summary,
        "alignment": all_alignment,
        "divergence": all_divergence,
        "section_analysis": section_analyses,
        "narrative_implications": narrative_implications,
        "action_items": action_items,
    }


def _derive_narrative_implications(alignment, divergence, section_analyses, stats):
    """Synthesize what the feedback means for the narrative."""
    implications = []

    # Hot sections — most commented
    section_heat = sorted(section_analyses, key=lambda s: s["total_comments"], reverse=True)
    if section_heat:
        hottest = section_heat[0]
        if hottest["total_comments"] > 2:
            implications.append({
                "type": "attention_hotspot",
                "section": hottest["section"],
                "detail": (
                    f"Section '{hottest['section']}' received the most feedback "
                    f"({hottest['total_comments']} comments from "
                    f"{len(hottest['reviewers'])} reviewers). "
                    "This is either the most contentious or most important section — "
                    "prioritize revisions here."
                ),
            })

    # Cold sections — no feedback
    cold = [s for s in section_analyses if s["total_comments"] == 0]
    if cold and len(section_analyses) > 3:
        implications.append({
            "type": "silent_sections",
            "sections": [s["section"] for s in cold],
            "detail": (
                f"{len(cold)} sections received no comments. "
                "This could mean consensus (content is fine) or disengagement "
                "(reviewers skipped these). Worth confirming with the team."
            ),
        })

    # Aligned concerns = clear signal to change
    if alignment:
        aligned_concerns = [a for a in alignment if "concern" in a["type"]]
        if aligned_concerns:
            implications.append({
                "type": "consensus_for_change",
                "count": len(aligned_concerns),
                "detail": (
                    f"{len(aligned_concerns)} point(s) where multiple reviewers raised "
                    "the same concern. These represent clear consensus for change — "
                    "address these first."
                ),
            })

    # Divergence = needs discussion
    if divergence:
        implications.append({
            "type": "requires_discussion",
            "count": len(divergence),
            "detail": (
                f"{len(divergence)} point(s) where reviewers actively disagree. "
                "These cannot be resolved by editing alone — they need a brief "
                "alignment conversation before revisions."
            ),
        })

    # Overall sentiment
    total = stats.get("total_comments", 0) if isinstance(stats, dict) else 0
    if total > 0:
        concern_sections = [
            s for s in section_analyses
            if s["sentiment_breakdown"]["concerns"] > s["sentiment_breakdown"]["endorsements"]
        ]
        if len(concern_sections) > len(section_analyses) / 2:
            implications.append({
                "type": "overall_direction",
                "detail": (
                    "More than half the sections have more concerns than endorsements. "
                    "The narrative may need structural rethinking, not just edits."
                ),
            })
        elif not concern_sections:
            implications.append({
                "type": "overall_direction",
                "detail": (
                    "No section has more concerns than endorsements. "
                    "The narrative direction is solid — focus on refinements."
                ),
            })

    return implications


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_feedback.py <feedback.json> [--output report.json]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]

    with open(input_file) as f:
        parsed = json.load(f)

    report = analyze_feedback(parsed)

    if output_file:
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Report → {output_file}")
        print(f"  {report['summary']['total_comments']} comments from {report['summary']['reviewer_count']} reviewers")
        print(f"  {report['summary']['alignment_points']} alignment points, {report['summary']['divergence_points']} divergence points")
        print(f"  {report['summary']['high_priority_actions']} high-priority actions")
    else:
        print(json.dumps(report, indent=2))
