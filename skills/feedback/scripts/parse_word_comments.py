"""Parse inline comments from a Word (.docx) document.

Extracts comments with their author, timestamp, referenced text, and
approximate section context. Works directly with the underlying XML
since python-docx doesn't expose comments natively.

Usage:
    python parse_word_comments.py path/to/file.docx [--output feedback.json]
"""

import json
import sys
import zipfile
from collections import defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

# Word XML namespaces
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
}


def _text_of(elem):
    """Recursively extract all text from an XML element."""
    texts = []
    for node in elem.iter():
        if node.tag == f'{{{NS["w"]}}}t' and node.text:
            texts.append(node.text)
    return "".join(texts)


def _parse_comments_xml(zf):
    """Parse word/comments.xml → dict of comment_id → comment metadata."""
    comments = {}
    try:
        with zf.open("word/comments.xml") as f:
            tree = ET.parse(f)
    except KeyError:
        return comments

    root = tree.getroot()
    for comment_elem in root.findall("w:comment", NS):
        cid = comment_elem.get(f'{{{NS["w"]}}}id')
        author = comment_elem.get(f'{{{NS["w"]}}}author', "Unknown")
        date = comment_elem.get(f'{{{NS["w"]}}}date', "")
        initials = comment_elem.get(f'{{{NS["w"]}}}initials', "")
        text = _text_of(comment_elem)

        comments[cid] = {
            "id": cid,
            "author": author,
            "initials": initials,
            "date": date,
            "text": text.strip(),
        }
    return comments


def _parse_comment_replies(zf):
    """Parse word/commentsExtended.xml for reply threading (if present)."""
    replies = {}
    try:
        with zf.open("word/commentsExtended.xml") as f:
            tree = ET.parse(f)
    except KeyError:
        return replies

    root = tree.getroot()
    for info in root.findall("w15:commentEx", NS):
        cid = info.get(f'{{{NS["w15"]}}}paraId', "")
        parent = info.get(f'{{{NS["w15"]}}}paraIdParent', "")
        done = info.get(f'{{{NS["w15"]}}}done', "0")
        if parent:
            replies[cid] = {"parent": parent, "done": done == "1"}
    return replies


def _extract_sections_and_ranges(zf):
    """Walk word/document.xml to map comment ranges to their referenced text and section."""
    try:
        with zf.open("word/document.xml") as f:
            tree = ET.parse(f)
    except KeyError:
        return {}, []

    root = tree.getroot()
    body = root.find("w:body", NS)
    if body is None:
        return {}, []

    # Track current heading/section
    sections = []
    current_section = {"title": "(Introduction)", "index": 0}
    sections.append(current_section)

    # Track open comment ranges
    open_ranges = {}  # comment_id → {"texts": [], "section": ...}
    comment_contexts = {}  # comment_id → {"referenced_text": ..., "section": ...}

    # Walk all paragraphs
    for para in body.iter(f'{{{NS["w"]}}}p'):
        # Check if this paragraph is a heading
        ppr = para.find("w:pPr", NS)
        if ppr is not None:
            pstyle = ppr.find("w:pStyle", NS)
            if pstyle is not None:
                style_val = pstyle.get(f'{{{NS["w"]}}}val', "")
                if style_val.startswith("Heading"):
                    heading_text = _text_of(para)
                    if heading_text.strip():
                        current_section = {
                            "title": heading_text.strip(),
                            "index": len(sections),
                            "level": style_val,
                        }
                        sections.append(current_section)

        para_text = _text_of(para)

        # Process elements within the paragraph for comment ranges
        for elem in para.iter():
            tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag

            if tag == "commentRangeStart":
                cid = elem.get(f'{{{NS["w"]}}}id')
                if cid:
                    open_ranges[cid] = {
                        "texts": [],
                        "section": current_section["title"],
                        "section_index": current_section["index"],
                    }

            elif tag == "commentRangeEnd":
                cid = elem.get(f'{{{NS["w"]}}}id')
                if cid and cid in open_ranges:
                    rng = open_ranges.pop(cid)
                    comment_contexts[cid] = {
                        "referenced_text": " ".join(rng["texts"]).strip(),
                        "section": rng["section"],
                        "section_index": rng["section_index"],
                        "surrounding_paragraph": para_text.strip(),
                    }

            elif tag == "t" and elem.text:
                # Add text to all open ranges
                for cid in open_ranges:
                    open_ranges[cid]["texts"].append(elem.text)

        # Close any ranges still open at paragraph end — they span whole paragraph
        # (keep them open; they'll close at commentRangeEnd in a later paragraph)

    # Any ranges that never closed — use what we have
    for cid, rng in open_ranges.items():
        comment_contexts[cid] = {
            "referenced_text": " ".join(rng["texts"]).strip(),
            "section": rng["section"],
            "section_index": rng["section_index"],
            "surrounding_paragraph": "",
        }

    return comment_contexts, sections


def parse_docx_comments(docx_path):
    """Parse a .docx file and return structured comment data.

    Returns:
        dict with keys:
            - file: source filename
            - sections: list of section titles found
            - comments: list of comment objects with author, text, context
            - stats: summary counts
    """
    docx_path = Path(docx_path)
    if not docx_path.exists():
        raise FileNotFoundError(f"File not found: {docx_path}")
    if not docx_path.suffix.lower() == ".docx":
        raise ValueError(f"Expected .docx file, got: {docx_path.suffix}")

    with zipfile.ZipFile(docx_path, "r") as zf:
        comments_meta = _parse_comments_xml(zf)
        comment_contexts, sections = _extract_sections_and_ranges(zf)

    if not comments_meta:
        return {
            "file": docx_path.name,
            "sections": [s["title"] for s in sections],
            "comments": [],
            "stats": {"total_comments": 0, "reviewers": [], "sections_with_feedback": []},
        }

    # Merge comment metadata with context
    merged = []
    for cid, meta in comments_meta.items():
        ctx = comment_contexts.get(cid, {})
        merged.append({
            "id": cid,
            "author": meta["author"],
            "initials": meta.get("initials", ""),
            "date": meta["date"],
            "comment_text": meta["text"],
            "referenced_text": ctx.get("referenced_text", ""),
            "section": ctx.get("section", "(Unknown)"),
            "section_index": ctx.get("section_index", -1),
            "surrounding_paragraph": ctx.get("surrounding_paragraph", ""),
        })

    # Sort by section order, then by date
    merged.sort(key=lambda c: (c["section_index"], c["date"]))

    # Stats
    reviewers = sorted(set(c["author"] for c in merged))
    sections_with_feedback = sorted(set(c["section"] for c in merged))

    # Group by section for convenience
    by_section = defaultdict(list)
    for c in merged:
        by_section[c["section"]].append(c)

    return {
        "file": docx_path.name,
        "sections": [s["title"] for s in sections],
        "comments": merged,
        "comments_by_section": dict(by_section),
        "stats": {
            "total_comments": len(merged),
            "reviewers": reviewers,
            "reviewer_count": len(reviewers),
            "sections_with_feedback": sections_with_feedback,
            "comments_per_reviewer": {
                author: len([c for c in merged if c["author"] == author])
                for author in reviewers
            },
        },
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_word_comments.py <file.docx> [--output feedback.json]")
        sys.exit(1)

    docx_file = sys.argv[1]
    output_file = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]

    result = parse_docx_comments(docx_file)

    if output_file:
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        print(f"Parsed {result['stats']['total_comments']} comments → {output_file}")
    else:
        print(json.dumps(result, indent=2))
