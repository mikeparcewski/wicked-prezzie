#!/usr/bin/env python3
"""
slide-learn — Source document indexing for wicked-prezzie.

Two-pass pipeline:
  Pass 1: Per-document extraction → chunks with YAML frontmatter
  Pass 2: Cross-document synthesis → _tags/, _relationships/, _insights/

Design decision (strategy gate C1): Pure coordinator. Claude extracts content
via vision; this script writes indexes and manages file structure. No PyPDF2,
pdfplumber, or python-docx dependency.

Usage:
    python slide-learn/scripts/slide_learn.py --source-dir /path/to/docs
    python slide-learn/scripts/slide_learn.py --doc /path/to/file.pdf
    python slide-learn/scripts/slide_learn.py --source-dir . --output-dir ./index
"""

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Cross-skill import pattern
_root = Path(__file__).parent.parent.parent  # skills/ directory
sys.path.insert(0, str(_root / "shared"))
from paths import output_path, ensure_output_dir

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

SUPPORTED_TYPES = {"pdf", "pptx", "docx", "html", "image"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tiff", ".tif"}

SCHEMA_VERSION = 1


def learn(source_dir: str, output_dir: str = None, single_doc: str = None) -> dict:
    """Main entry point for the slide-learn pipeline.

    Args:
        source_dir: Directory containing source documents. Used as the base
                    for relative paths in the index. Required even when
                    single_doc is provided (sets the index root context).
        output_dir: Directory where the index is written. Defaults to
                    {source_dir}/index if not provided.
        single_doc: Path to a single document to index. When set, only that
                    document is processed in pass 1 (pass 2 still runs over
                    the full index).

    Returns:
        Summary dict: {documents_processed, chunks_created, pass2_complete}
    """
    source_dir = Path(source_dir).resolve()
    if output_dir is None:
        output_dir = source_dir / "index"
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    documents_processed = 0
    chunks_created = 0

    # Collect documents to process
    if single_doc:
        docs = [Path(single_doc).resolve()]
    else:
        docs = _collect_documents(source_dir)

    # Pass 1: per-document extraction
    for doc_path in docs:
        doc_type = _detect_type(doc_path)
        if doc_type is None:
            continue

        source_name = _safe_source_name(doc_path)
        doc_output_dir = output_dir / source_name
        doc_output_dir.mkdir(parents=True, exist_ok=True)

        # Skip if unchanged (hash check)
        if _is_unchanged(doc_path, output_dir):
            # Count existing chunks toward total
            existing = list(doc_output_dir.glob("chunk-*.md"))
            chunks_created += len(existing)
            documents_processed += 1
            continue

        chunks = _chunk_document(doc_path, doc_type)
        _write_chunks(chunks, source_name, output_dir)
        _update_cache(doc_path, output_dir)

        chunks_created += len(chunks)
        documents_processed += 1

    # Pass 2: cross-document synthesis
    pass2_complete = _run_pass2(output_dir)

    stats = {
        "documents_processed": documents_processed,
        "chunks_created": chunks_created,
        "pass2_complete": pass2_complete,
    }
    _write_manifest(output_dir, stats)

    return stats


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _detect_type(path: Path) -> str | None:
    """Detect document type from file extension.

    Returns:
        One of: pdf | pptx | docx | html | image
        None if the extension is not supported.
    """
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return "pdf"
    if suffix in {".pptx", ".ppt"}:
        return "pptx"
    if suffix in {".docx", ".doc"}:
        return "docx"
    if suffix in {".html", ".htm"}:
        return "html"
    if suffix in IMAGE_EXTENSIONS:
        return "image"
    return None


def _chunk_document(path: Path, doc_type: str) -> list[dict]:
    """Return a list of chunk dicts for a document.

    Each chunk dict contains:
        frontmatter: dict — YAML frontmatter fields (see index-schema.md)
        content: str — Markdown body text for the chunk file

    For binary formats (pdf, pptx, image), content is a structured placeholder
    describing what Claude should fill in via vision. The calling agent reads
    the document and replaces placeholder content before writing.

    Args:
        path: Absolute path to the document.
        doc_type: One of pdf | pptx | docx | html | image

    Returns:
        List of chunk dicts. Never empty — at minimum one chunk per document.
    """
    now = datetime.now(timezone.utc).isoformat()
    source_name = _safe_source_name(path)

    chunks: list[dict] = []

    if doc_type == "pdf":
        chunks = _chunk_pdf(path, source_name, now)
    elif doc_type == "pptx":
        chunks = _chunk_pptx(path, source_name, now)
    elif doc_type == "docx":
        chunks = _chunk_docx(path, source_name, now)
    elif doc_type == "html":
        chunks = _chunk_html(path, source_name, now)
    elif doc_type == "image":
        chunks = _chunk_image(path, source_name, now)

    # Ensure every chunk has a sequential chunk_id
    for i, chunk in enumerate(chunks):
        chunk["frontmatter"].setdefault("chunk_id", f"{source_name}/chunk-{i + 1:03d}")

    return chunks


def _chunk_pdf(path: Path, source_name: str, now: str) -> list[dict]:
    """PDF: page-based chunking, 3-6 pages per chunk.

    Returns placeholder chunks. The agent reads the PDF visually and fills
    content. Page count is estimated from file size for placeholder generation;
    the agent adjusts chunk boundaries at extraction time.
    """
    # Estimate page count from file size (rough heuristic: ~50 KB per page)
    size_kb = path.stat().st_size / 1024
    estimated_pages = max(1, int(size_kb / 50))
    chunk_size = 4  # default pages per chunk

    chunks = []
    page = 1
    chunk_num = 1
    while page <= estimated_pages:
        end_page = min(page + chunk_size - 1, estimated_pages)
        fm = _base_frontmatter(source_name, "pdf", chunk_num, now)
        fm["pages"] = f"{page}-{end_page}"
        chunks.append({
            "frontmatter": fm,
            "content": (
                f"<!-- EXTRACT: Read pages {page}–{end_page} of {path.name} "
                f"and replace this block with extracted content. "
                f"Use vision-templates.md for charts and diagrams. -->\n\n"
                f"_Content pending extraction by agent._"
            ),
        })
        page = end_page + 1
        chunk_num += 1

    return chunks


def _chunk_pptx(path: Path, source_name: str, now: str) -> list[dict]:
    """PPTX: one chunk per slide plus an optional section summary.

    Returns placeholder chunks; agent fills vision descriptions.
    """
    # Estimate slide count (very rough: pptx is a zip, ~20–80 KB per slide)
    size_kb = path.stat().st_size / 1024
    estimated_slides = max(1, int(size_kb / 40))

    chunks = []
    for slide_num in range(1, estimated_slides + 1):
        fm = _base_frontmatter(source_name, "pptx", slide_num, now)
        fm["slide_number"] = slide_num
        chunks.append({
            "frontmatter": fm,
            "content": (
                f"<!-- EXTRACT: Read slide {slide_num} of {path.name} and replace "
                f"this block with a vision description. "
                f"Use vision-templates.md for charts and diagrams. -->\n\n"
                f"_Content pending extraction by agent._"
            ),
        })

    return chunks


def _chunk_docx(path: Path, source_name: str, now: str) -> list[dict]:
    """DOCX: section-heading chunking, target 400-800 words per chunk.

    Returns a single placeholder chunk since we cannot read DOCX natively.
    Agent reads the file and splits at H1/H2 boundaries.
    """
    fm = _base_frontmatter(source_name, "docx", 1, now)
    return [{
        "frontmatter": fm,
        "content": (
            f"<!-- EXTRACT: Read {path.name} and split at H1/H2 section headings. "
            f"Target 400-800 words per chunk. Replace this file with the first section "
            f"and create additional chunk files for each subsequent section. -->\n\n"
            f"_Content pending extraction by agent._"
        ),
    }]


def _chunk_html(path: Path, source_name: str, now: str) -> list[dict]:
    """HTML: per-slide div chunking.

    Parses slide divs from the HTML file directly (no external dependency).
    Each top-level div with class containing 'slide' is one chunk.
    """
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        raw = ""

    # Simple regex split on slide divs
    slide_pattern = re.compile(
        r'<div[^>]+class=["\'][^"\']*slide[^"\']*["\'][^>]*>(.*?)</div>',
        re.DOTALL | re.IGNORECASE,
    )
    matches = slide_pattern.findall(raw)

    if not matches:
        # Treat the whole file as one chunk
        fm = _base_frontmatter(source_name, "html", 1, now)
        return [{
            "frontmatter": fm,
            "content": f"<!-- Source: {path.name} -->\n\n{raw[:2000]}",
        }]

    chunks = []
    for i, slide_html in enumerate(matches, start=1):
        fm = _base_frontmatter(source_name, "html", i, now)
        fm["slide_number"] = i
        # Strip tags for a plain-text content preview
        text = re.sub(r"<[^>]+>", " ", slide_html)
        text = re.sub(r"\s+", " ", text).strip()
        chunks.append({
            "frontmatter": fm,
            "content": f"<!-- Slide {i} from {path.name} -->\n\n{text[:1500]}",
        })

    return chunks


def _chunk_image(path: Path, source_name: str, now: str) -> list[dict]:
    """Image: single chunk per file, vision description is the content."""
    fm = _base_frontmatter(source_name, "image", 1, now)
    fm["content_type"] = ["visual"]
    return [{
        "frontmatter": fm,
        "content": (
            f"<!-- EXTRACT: Describe {path.name} using the appropriate template "
            f"from vision-templates.md. Replace this block with the description. -->\n\n"
            f"_Content pending vision description by agent._"
        ),
    }]


def _base_frontmatter(source_name: str, doc_type: str, chunk_num: int, now: str) -> dict:
    """Return a base frontmatter dict with required fields pre-populated."""
    return {
        "schema_version": SCHEMA_VERSION,
        "source": source_name,
        "source_type": doc_type,
        "chunk_id": f"{source_name}/chunk-{chunk_num:03d}",
        "content_type": [],
        "contains": [],
        "entities": {"systems": [], "people": [], "programs": [], "metrics": []},
        "figures": [],
        "narrative_theme": "",
        "slide_relevance": [],
        "confidence": 0.0,
        "indexed_at": now,
    }


def _write_chunks(chunks: list[dict], source_name: str, output_dir: Path) -> None:
    """Write per-doc chunk files with YAML frontmatter.

    Each chunk is written to:
        {output_dir}/{source_name}/chunk-{NNN}.md

    File format:
        ---
        <YAML frontmatter>
        ---

        <Markdown content>
    """
    doc_dir = output_dir / source_name
    doc_dir.mkdir(parents=True, exist_ok=True)

    for i, chunk in enumerate(chunks, start=1):
        chunk_path = doc_dir / f"chunk-{i:03d}.md"
        fm = chunk["frontmatter"]
        content = chunk.get("content", "")

        yaml_lines = ["---"]
        for key, value in fm.items():
            yaml_lines.append(_yaml_field(key, value))
        yaml_lines.append("---")
        yaml_lines.append("")

        chunk_path.write_text("\n".join(yaml_lines) + "\n" + content + "\n",
                              encoding="utf-8")


def _yaml_field(key: str, value) -> str:
    """Serialize a single YAML frontmatter field to a string line."""
    if isinstance(value, list):
        if not value:
            return f"{key}: []"
        items = "\n".join(f"  - {_yaml_scalar(v)}" for v in value)
        return f"{key}:\n{items}"
    if isinstance(value, dict):
        if not value:
            return f"{key}: {{}}"
        lines = [f"{key}:"]
        for k, v in value.items():
            if isinstance(v, list):
                if not v:
                    lines.append(f"  {k}: []")
                else:
                    lines.append(f"  {k}:")
                    for item in v:
                        lines.append(f"    - {_yaml_scalar(item)}")
            else:
                lines.append(f"  {k}: {_yaml_scalar(v)}")
        return "\n".join(lines)
    if isinstance(value, bool):
        return f"{key}: {'true' if value else 'false'}"
    if isinstance(value, (int, float)):
        return f"{key}: {value}"
    return f"{key}: {_yaml_scalar(str(value))}"


def _yaml_scalar(value) -> str:
    """Quote a scalar value if it contains special YAML characters."""
    s = str(value)
    if any(c in s for c in (':', '#', '[', ']', '{', '}', ',', '&', '*', '?',
                             '|', '-', '<', '>', '=', '!', '%', '@', '`', '"', "'")):
        escaped = s.replace('"', '\\"')
        return f'"{escaped}"'
    if not s:
        return '""'
    return s


def _write_manifest(output_dir: Path, stats: dict) -> None:
    """Write _manifest.json with freshness record and run statistics."""
    manifest_path = output_dir / "_manifest.json"

    existing = {}
    if manifest_path.exists():
        try:
            existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    manifest = {
        "schemaVersion": SCHEMA_VERSION,
        "lastIndexed": datetime.now(timezone.utc).isoformat(),
        "documentsProcessed": stats.get("documents_processed", 0),
        "chunksCreated": stats.get("chunks_created", 0),
        "pass2Complete": stats.get("pass2_complete", False),
        "runs": existing.get("runs", []) + [{
            "at": datetime.now(timezone.utc).isoformat(),
            "documents": stats.get("documents_processed", 0),
            "chunks": stats.get("chunks_created", 0),
        }],
    }

    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def _run_pass2(output_dir: Path) -> bool:
    """Read all chunk frontmatter and synthesize _tags/, _relationships/, _insights/.

    Pass 2 aggregates across all chunk files in the index. Each synthesis
    artifact is written as a Markdown file. Returns True if synthesis completed
    without errors.
    """
    try:
        all_chunks = _load_all_chunks(output_dir)

        if not all_chunks:
            return False

        _synthesize_tags(all_chunks, output_dir)
        _synthesize_relationships(all_chunks, output_dir)
        _synthesize_insights(all_chunks, output_dir)

        return True
    except Exception as exc:  # noqa: BLE001
        # Non-fatal: log and continue; pass 1 output is still usable
        print(f"[slide-learn] Pass 2 synthesis warning: {exc}", file=sys.stderr)
        return False


def _load_all_chunks(output_dir: Path) -> list[dict]:
    """Load frontmatter from all chunk files in the index.

    Returns a list of dicts, each with 'frontmatter' and 'path' keys.
    """
    chunks = []
    for chunk_path in sorted(output_dir.rglob("chunk-*.md")):
        # Skip anything inside _tags, _relationships, _insights
        parts = chunk_path.relative_to(output_dir).parts
        if parts[0].startswith("_"):
            continue
        try:
            fm = _parse_frontmatter(chunk_path.read_text(encoding="utf-8"))
            chunks.append({"frontmatter": fm, "path": chunk_path})
        except Exception:  # noqa: BLE001
            continue
    return chunks


def _parse_frontmatter(text: str) -> dict:
    """Very simple YAML frontmatter parser (no PyYAML dependency).

    Reads key: value lines between --- delimiters. Handles scalar, list, and
    shallow nested dict fields sufficient for the index schema.

    Container type disambiguation: when a top-level key has no inline value,
    look ahead at the next non-empty line to decide whether to create a list
    (next line starts with `  - `) or a dict (next line matches `  word:`).
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    fm_lines = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        fm_lines.append(line)

    fm: dict = {}
    current_key = None
    current_list = None
    current_dict = None
    current_dict_key = None

    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]
        stripped = line.strip()
        i += 1

        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        # Sub-list item (4-space indent under a dict key)
        if indent >= 4 and current_dict is not None and current_dict_key is not None:
            if stripped.startswith("- "):
                sub = current_dict.setdefault(current_dict_key, [])
                if not isinstance(sub, list):
                    current_dict[current_dict_key] = []
                    sub = current_dict[current_dict_key]
                sub.append(stripped[2:].strip().strip('"'))
            continue

        # List item (2-space indent) — only if we are in list mode
        if indent == 2 and stripped.startswith("- ") and current_list is not None:
            current_list.append(stripped[2:].strip().strip('"'))
            continue

        # Dict sub-key (2-space indent, key: pattern) — only if in dict mode
        if indent == 2 and ":" in stripped and not stripped.startswith("- "):
            if current_dict is not None:
                k, _, v = stripped.partition(":")
                raw_v = v.strip()
                dk = k.strip()
                if raw_v == "[]":
                    current_dict[dk] = []
                    current_dict_key = dk
                elif raw_v.startswith("[") and raw_v.endswith("]"):
                    current_dict[dk] = _parse_inline_array(raw_v)
                    current_dict_key = dk
                elif raw_v:
                    current_dict[dk] = _coerce(raw_v.strip('"').strip("'"))
                    current_dict_key = dk
                else:
                    # Empty sub-value — will be filled by 4-indent list items
                    current_dict[dk] = []
                    current_dict_key = dk
            continue

        # Top-level key: value
        if ":" in stripped and indent == 0:
            k, _, v = stripped.partition(":")
            key = k.strip()
            raw_val = v.strip()
            # Detect explicit quoted empty string: "" or ''
            is_quoted_empty = raw_val in ('""', "''")
            val = raw_val.strip('"').strip("'")
            current_list = None
            current_dict = None
            current_dict_key = None
            current_key = key

            if val == "[]":
                fm[key] = []
                current_list = fm[key]
            elif val == "{}":
                fm[key] = {}
                current_dict = fm[key]
            elif raw_val.startswith("[") and raw_val.endswith("]"):
                # Inline YAML array: [item1, item2, ...]
                fm[key] = _parse_inline_array(raw_val)
            elif val or is_quoted_empty:
                # Non-empty scalar, OR explicit quoted empty string → scalar
                fm[key] = _coerce(val) if not is_quoted_empty else ""
            else:
                # Truly empty value (no quotes) — look ahead to determine container type
                next_content = _next_nonempty(fm_lines, i)
                if next_content is not None:
                    next_indent = len(next_content) - len(next_content.lstrip())
                    next_strip = next_content.strip()
                    if next_indent == 2 and ":" in next_strip and not next_strip.startswith("- "):
                        # Sub-key pattern → dict
                        fm[key] = {}
                        current_dict = fm[key]
                    else:
                        # List item pattern (or anything else) → list
                        fm[key] = []
                        current_list = fm[key]
                else:
                    fm[key] = []
                    current_list = fm[key]

    return fm


def _next_nonempty(lines: list[str], start: int) -> str | None:
    """Return the first non-empty, non-comment line at or after `start`."""
    for line in lines[start:]:
        s = line.strip()
        if s and not s.startswith("#"):
            return line
    return None


def _coerce(value: str):
    """Coerce a YAML scalar string to an appropriate Python type."""
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def _parse_inline_array(raw: str) -> list:
    """Parse an inline YAML array like [item1, "item 2", item3].

    Handles quoted strings with commas inside them.
    """
    inner = raw[1:-1].strip()
    if not inner:
        return []

    items = []
    current = []
    in_quotes = False
    quote_char = None

    for ch in inner:
        if ch in ('"', "'") and not in_quotes:
            in_quotes = True
            quote_char = ch
        elif ch == quote_char and in_quotes:
            in_quotes = False
            quote_char = None
        elif ch == "," and not in_quotes:
            items.append("".join(current).strip().strip('"').strip("'"))
            current = []
            continue
        else:
            current.append(ch)

    # Last item
    if current:
        items.append("".join(current).strip().strip('"').strip("'"))

    return [_coerce(item) for item in items if item]


def _synthesize_tags(chunks: list[dict], output_dir: Path) -> None:
    """Aggregate chunks by tag and write _tags/{tag}.md files."""
    tags_dir = output_dir / "_tags"
    tags_dir.mkdir(exist_ok=True)

    tag_map: dict[str, list[dict]] = {}
    for chunk in chunks:
        fm = chunk["frontmatter"]
        for tag in fm.get("contains", []):
            tag_map.setdefault(tag, []).append(chunk)
        for ct in fm.get("content_type", []):
            tag_map.setdefault(ct, []).append(chunk)

    for tag, tag_chunks in sorted(tag_map.items()):
        safe_tag = re.sub(r"[^\w-]", "-", tag.lower())
        tag_file = tags_dir / f"{safe_tag}.md"
        lines = [f"# Tag: {tag}", "", f"Chunks carrying this tag ({len(tag_chunks)} total):", ""]
        for c in tag_chunks:
            fm = c["frontmatter"]
            source = fm.get("source", "?")
            chunk_id = fm.get("chunk_id", "?")
            theme = fm.get("narrative_theme", "")
            lines.append(f"- **{chunk_id}** ({source})" + (f" — {theme}" if theme else ""))
        tag_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _synthesize_relationships(chunks: list[dict], output_dir: Path) -> None:
    """Build cross-document relationship files under _relationships/."""
    rel_dir = output_dir / "_relationships"
    rel_dir.mkdir(exist_ok=True)

    systems: dict[str, list[str]] = {}
    people: dict[str, list[str]] = {}

    for chunk in chunks:
        fm = chunk["frontmatter"]
        chunk_id = fm.get("chunk_id", "?")
        entities = fm.get("entities", {})

        for system in entities.get("systems", []):
            systems.setdefault(system, []).append(chunk_id)
        for person in entities.get("people", []):
            people.setdefault(person, []).append(chunk_id)

    # Write systems.md
    _write_relationship_file(rel_dir / "systems.md", "Systems", systems)
    _write_relationship_file(rel_dir / "people.md", "People & Roles", people)


def _write_relationship_file(path: Path, title: str, entity_map: dict[str, list[str]]) -> None:
    """Write a relationship file listing entities and the chunks that mention them."""
    if not entity_map:
        return
    lines = [f"# {title}", "", f"Cross-document references ({len(entity_map)} unique entities):", ""]
    for entity, chunk_ids in sorted(entity_map.items()):
        lines.append(f"## {entity}")
        lines.append(f"Mentioned in {len(chunk_ids)} chunk(s):")
        for cid in sorted(set(chunk_ids)):
            lines.append(f"- {cid}")
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _synthesize_insights(chunks: list[dict], output_dir: Path) -> None:
    """Surface key-facts, narrative-themes, and gaps into _insights/."""
    insights_dir = output_dir / "_insights"
    insights_dir.mkdir(exist_ok=True)

    themes: dict[str, list[str]] = {}
    slide_relevance_map: dict[str, list[str]] = {}
    all_metrics: list[tuple[str, str]] = []  # (metric, chunk_id)

    for chunk in chunks:
        fm = chunk["frontmatter"]
        chunk_id = fm.get("chunk_id", "?")
        theme = fm.get("narrative_theme", "").strip()
        if theme:
            themes.setdefault(theme, []).append(chunk_id)
        for rel in fm.get("slide_relevance", []):
            slide_relevance_map.setdefault(rel, []).append(chunk_id)
        for metric in fm.get("entities", {}).get("metrics", []):
            all_metrics.append((metric, chunk_id))

    # key-facts.md
    facts_path = insights_dir / "key-facts.md"
    lines = ["# Key Facts", "",
             "Top metrics and figures extracted from indexed documents.", ""]
    if all_metrics:
        for metric, chunk_id in all_metrics[:50]:  # top 50
            lines.append(f"- {metric}  _(source: {chunk_id})_")
    else:
        lines.append("_No metrics extracted yet. Run pass 1 with agent extraction._")
    facts_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # narrative-themes.md
    themes_path = insights_dir / "narrative-themes.md"
    lines = ["# Narrative Themes", "",
             "Recurring themes suitable for slide narratives.", ""]
    if themes:
        for theme, chunk_ids in sorted(themes.items()):
            lines.append(f"## {theme}")
            lines.append(f"Appears in {len(chunk_ids)} chunk(s): "
                         + ", ".join(sorted(set(chunk_ids))[:5]))
            lines.append("")
    else:
        lines.append("_No themes extracted yet. Run pass 1 with agent extraction._")
    themes_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # gaps.md
    gaps_path = insights_dir / "gaps.md"
    lines = ["# Coverage Gaps", "",
             "Topics or slide types with low source coverage.", ""]
    all_relevance = set(slide_relevance_map.keys())
    expected = {"title", "agenda", "stats", "chart", "diagram", "cta", "section"}
    missing = expected - all_relevance
    if missing:
        for m in sorted(missing):
            lines.append(f"- No chunks tagged `slide_relevance: {m}`")
    else:
        lines.append("_All common slide types have source coverage._")
    gaps_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# File system utilities
# ---------------------------------------------------------------------------

def _collect_documents(source_dir: Path) -> list[Path]:
    """Return all indexable documents under source_dir (non-recursive)."""
    docs = []
    for entry in sorted(source_dir.iterdir()):
        if entry.is_file() and _detect_type(entry) is not None:
            docs.append(entry)
    return docs


def _safe_source_name(path: Path) -> str:
    """Convert a file path to a safe directory name for the index."""
    name = path.name  # e.g. "Q3 Review.pdf"
    # Replace spaces and special chars with hyphens
    safe = re.sub(r"[^\w.-]", "-", name)
    # Collapse multiple hyphens
    safe = re.sub(r"-{2,}", "-", safe)
    return safe.strip("-")


def _content_hash(path: Path) -> str:
    """Return a short SHA-256 hash of file contents."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()[:16]


def _is_unchanged(path: Path, output_dir: Path) -> bool:
    """Return True if the document has not changed since last index run."""
    cache_dir = output_dir / ".cache"
    cache_dir.mkdir(exist_ok=True)
    cache_file = cache_dir / f"{_safe_source_name(path)}.hash"
    if not cache_file.exists():
        return False
    current_hash = _content_hash(path)
    return cache_file.read_text(encoding="utf-8").strip() == current_hash


def _update_cache(path: Path, output_dir: Path) -> None:
    """Write the current content hash to .cache/{source-name}.hash."""
    cache_dir = output_dir / ".cache"
    cache_dir.mkdir(exist_ok=True)
    cache_file = cache_dir / f"{_safe_source_name(path)}.hash"
    cache_file.write_text(_content_hash(path), encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="slide-learn: index source documents for wicked-prezzie"
    )
    parser.add_argument(
        "--source-dir",
        default=".",
        help="Directory containing source documents (default: current directory)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for the index (default: {source-dir}/index)",
    )
    parser.add_argument(
        "--doc",
        default=None,
        metavar="PATH",
        help="Index a single document instead of the whole source directory",
    )

    args = parser.parse_args()

    result = learn(
        source_dir=args.source_dir,
        output_dir=args.output_dir,
        single_doc=args.doc,
    )

    print(f"[slide-learn] Done.")
    print(f"  Documents processed : {result['documents_processed']}")
    print(f"  Chunks created      : {result['chunks_created']}")
    print(f"  Pass 2 synthesis    : {'complete' if result['pass2_complete'] else 'skipped/failed'}")


if __name__ == "__main__":
    main()
