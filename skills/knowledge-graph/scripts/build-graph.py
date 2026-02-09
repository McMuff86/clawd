#!/usr/bin/env python3
"""
build-graph.py — Scan markdown files and build a knowledge graph JSON.

Usage:
    python3 build-graph.py [workspace_path] [--output /tmp/graph-data.json] [--embed /path/to/template.html /tmp/output.html]

Only uses Python stdlib. Requires Python 3.10+.
"""

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

STOP_WORDS = frozenset(
    "der die das ein eine einer eines einem einen und oder aber wenn dann also "
    "nicht noch doch schon nur auch sehr viel mehr wie was wer wir sie ich du er "
    "es ist sind war hat haben wird werden kann können muss müssen soll sollte "
    "the a an and or but if then not yet also just too very much more how what "
    "who we they you he she it is are was has have will would can could must "
    "should this that these those with from for about into over after before "
    "between through during without been being had having does did do done "
    "make made use used using file files note notes todo item see section "
    "may might shall its their our your my his her".split()
)

MIN_KEYWORD_LEN = 4
MAX_KEYWORDS_PER_FILE = 15
JACCARD_THRESHOLD = 0.3
MIN_SHARED_MENTIONS = 2  # need ≥2 shared mentions to create an edge
MAX_MENTION_FREQUENCY = 0.35  # skip mentions appearing in >35% of files (too generic)

# Known project names / technologies to detect as mentions
KNOWN_PROJECTS = [
    "intelliplan", "rhinomcp", "locai", "openclaw", "sentinel",
    "fologram", "comfyui", "grasshopper", "rhino", "tailscale",
    "splashtop", "ralph", "docker", "wsl", "telegram", "discord",
    "whisper", "openai", "anthropic", "claude", "chatgpt",
]

# Known person names (add names relevant to your workspace)
KNOWN_PERSONS = [
    "adi", "renato",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def classify_file(rel_path: str) -> str:
    """Classify a markdown file into a type based on its path."""
    p = rel_path.lower()
    if re.match(r"memory/\d{4}-\d{2}-\d{2}", p):
        return "daily-note"
    if p.startswith("memory/"):
        return "memory"
    if p.startswith("tasks/") or p.startswith("sprints/"):
        return "task"
    if p.startswith("projects/"):
        return "project"
    if p.startswith("knowledge/") or p.startswith("brainstorms/") or p.startswith("docs/"):
        return "knowledge"
    if p.startswith("skills/"):
        return "skill"
    # Top-level config files
    if p in ("agents.md", "memory.md", "soul.md", "user.md", "tools.md",
             "identity.md", "heartbeat.md"):
        return "config"
    return "other"


def extract_title(content: str, filename: str) -> str:
    """Extract first H1 heading or fall back to filename."""
    m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return Path(filename).stem


def extract_wiki_links(content: str) -> list[str]:
    """Extract [[wiki-link]] references."""
    return re.findall(r"\[\[([^\]]+)\]\]", content)


def extract_at_mentions(content: str) -> list[str]:
    """Extract @mentions."""
    return [m.lower() for m in re.findall(r"@(\w{2,})", content)]


def extract_bold_terms(content: str) -> list[str]:
    """Extract **bold** and __bold__ terms as potential keywords."""
    terms = re.findall(r"\*\*([^*]+)\*\*", content)
    terms += re.findall(r"__([^_]+)__", content)
    return [t.strip().lower() for t in terms if 2 < len(t.strip()) < 50]


def extract_headings(content: str) -> list[str]:
    """Extract heading text (## and ###)."""
    headings = re.findall(r"^#{1,4}\s+(.+)$", content, re.MULTILINE)
    return [h.strip().lower() for h in headings]


def extract_keywords(content: str) -> list[str]:
    """Extract keywords from content using frequency analysis + headings + bold."""
    # Combine heading words, bold terms, and frequent words
    heading_words = []
    for h in extract_headings(content):
        heading_words.extend(tokenize(h))

    bold_words = []
    for b in extract_bold_terms(content):
        bold_words.extend(tokenize(b))

    # Frequency analysis of all words
    all_words = tokenize(content.lower())
    freq = Counter(all_words)

    # Boost heading and bold words
    for w in heading_words:
        freq[w] = freq.get(w, 0) + 5
    for w in bold_words:
        freq[w] = freq.get(w, 0) + 3

    # Filter
    keywords = [
        w for w, c in freq.most_common(MAX_KEYWORDS_PER_FILE * 3)
        if len(w) >= MIN_KEYWORD_LEN and w not in STOP_WORDS and not w.isdigit()
    ]
    return keywords[:MAX_KEYWORDS_PER_FILE]


def extract_project_mentions(content: str) -> list[str]:
    """Find known project/technology names in content."""
    lower = content.lower()
    found = []
    for proj in KNOWN_PROJECTS:
        if proj in lower:
            found.append(proj)
    return found


def extract_person_mentions(content: str) -> list[str]:
    """Extract person names — only @mentions and known persons."""
    at_mentions = extract_at_mentions(content)
    lower = content.lower()
    found = [p for p in KNOWN_PERSONS if p in lower]
    return list(set(at_mentions + found))


def tokenize(text: str) -> list[str]:
    """Simple word tokenizer."""
    return re.findall(r"[a-zäöüéèêß]{2,}", text.lower())


def jaccard_similarity(set_a: set, set_b: set) -> float:
    """Compute Jaccard similarity between two sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


def resolve_wiki_link(link: str, all_paths: dict[str, str]) -> str | None:
    """Try to resolve a wiki-link to an actual file path."""
    link_lower = link.lower().strip()

    # Direct match on filename (without extension)
    for rel_path, _ in all_paths.items():
        stem = Path(rel_path).stem.lower()
        if stem == link_lower:
            return rel_path

    # Partial match
    for rel_path, _ in all_paths.items():
        if link_lower in rel_path.lower():
            return rel_path

    return None


# ---------------------------------------------------------------------------
# Main graph builder
# ---------------------------------------------------------------------------

def scan_workspace(workspace: Path) -> dict:
    """Scan workspace and build the knowledge graph."""

    # Collect all markdown files
    md_files: dict[str, str] = {}  # rel_path -> content
    for md_path in sorted(workspace.rglob("*.md")):
        # Skip hidden dirs, node_modules, .git, etc.
        parts = md_path.relative_to(workspace).parts
        if any(p.startswith(".") or p == "node_modules" or p == "__pycache__" for p in parts):
            continue
        # Skip the skill itself
        if "skills/knowledge-graph" in str(md_path):
            continue

        rel = str(md_path.relative_to(workspace))
        try:
            content = md_path.read_text(encoding="utf-8", errors="replace")
            md_files[rel] = content
        except (PermissionError, OSError):
            continue

    # Build nodes
    nodes = []
    file_data: dict[str, dict] = {}  # rel_path -> extracted data

    for rel_path, content in md_files.items():
        full_path = workspace / rel_path
        stat = full_path.stat()

        title = extract_title(content, rel_path)
        file_type = classify_file(rel_path)
        keywords = extract_keywords(content)
        wiki_links = extract_wiki_links(content)
        person_mentions = extract_person_mentions(content)
        project_mentions = extract_project_mentions(content)
        all_mentions = sorted(set(person_mentions + project_mentions))

        node = {
            "id": rel_path,
            "label": title,
            "type": file_type,
            "size": stat.st_size,
            "keywords": keywords,
            "mentions": all_mentions,
            "lastModified": datetime.fromtimestamp(
                stat.st_mtime, tz=timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        nodes.append(node)

        file_data[rel_path] = {
            "keywords": set(keywords),
            "mentions": set(all_mentions),
            "wiki_links": wiki_links,
        }

    # Build edges
    edges = []
    edge_set = set()  # avoid duplicates

    def add_edge(source: str, target: str, etype: str, weight: float):
        key = (min(source, target), max(source, target), etype)
        if key not in edge_set:
            edge_set.add(key)
            edges.append({
                "source": source,
                "target": target,
                "type": etype,
                "weight": round(weight, 3),
            })

    paths_all = {k: v for k, v in md_files.items()}

    # Pre-filter: compute mention frequency across files, skip overly common ones
    mention_file_count: dict[str, int] = Counter()
    for data in file_data.values():
        for m in data["mentions"]:
            mention_file_count[m] += 1
    total_files = len(file_data)
    rare_enough = {
        m for m, c in mention_file_count.items()
        if c / total_files <= MAX_MENTION_FREQUENCY and c >= 2
    }

    for rel_path, data in file_data.items():
        # 1. Wiki-link edges
        for link in data["wiki_links"]:
            target = resolve_wiki_link(link, paths_all)
            if target and target != rel_path:
                add_edge(rel_path, target, "wiki-link", 1.0)

        # 2. Keyword similarity edges
        for other_path, other_data in file_data.items():
            if other_path <= rel_path:
                continue
            sim = jaccard_similarity(data["keywords"], other_data["keywords"])
            if sim >= JACCARD_THRESHOLD:
                add_edge(rel_path, other_path, "keyword", sim)

        # 3. Shared mention edges (only rare-enough mentions, need ≥ MIN_SHARED_MENTIONS)
        filtered_mentions = data["mentions"] & rare_enough
        for other_path, other_data in file_data.items():
            if other_path <= rel_path:
                continue
            other_filtered = other_data["mentions"] & rare_enough
            shared = filtered_mentions & other_filtered
            if len(shared) >= MIN_SHARED_MENTIONS:
                weight = len(shared) / max(
                    len(filtered_mentions | other_filtered), 1
                )
                add_edge(rel_path, other_path, "mention", max(weight, 0.3))

    graph = {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "totalNodes": len(nodes),
            "totalEdges": len(edges),
            "scannedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    }

    return graph


def main():
    parser = argparse.ArgumentParser(description="Build knowledge graph from markdown files")
    parser.add_argument("workspace", nargs="?", default=os.path.expanduser("~/clawd"),
                        help="Workspace root path (default: ~/clawd)")
    parser.add_argument("--output", "-o", default="/tmp/graph-data.json",
                        help="Output JSON file path")
    parser.add_argument("--embed", nargs=2, metavar=("TEMPLATE_HTML", "OUTPUT_HTML"),
                        help="Embed data into HTML template and write to output")

    args = parser.parse_args()
    workspace = Path(args.workspace).resolve()

    if not workspace.is_dir():
        print(f"Error: {workspace} is not a directory", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning {workspace} ...", file=sys.stderr)
    graph = scan_workspace(workspace)
    print(
        f"Found {graph['stats']['totalNodes']} files, "
        f"{graph['stats']['totalEdges']} connections",
        file=sys.stderr,
    )

    # Write JSON
    json_str = json.dumps(graph, indent=2, ensure_ascii=False)
    Path(args.output).write_text(json_str, encoding="utf-8")
    print(f"Graph JSON written to {args.output}", file=sys.stderr)

    # Optionally embed into HTML
    if args.embed:
        template_path, output_path = args.embed
        template = Path(template_path).read_text(encoding="utf-8")
        # Replace the INJECT_DATA placeholder
        embedded = template.replace("/* INJECT_DATA */", json_str)
        embedded = embedded.replace("/*INJECT_DATA*/", json_str)
        Path(output_path).write_text(embedded, encoding="utf-8")
        print(f"Embedded HTML written to {output_path}", file=sys.stderr)

    # Also print JSON to stdout
    print(json_str)


if __name__ == "__main__":
    main()
