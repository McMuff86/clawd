---
name: knowledge-graph
description: Build and visualize a knowledge graph from workspace files (markdown, memory, notes). Use when the user asks to see connections between their files, visualize their knowledge base, show a knowledge graph, or explore relationships in their workspace.
---

# Knowledge Graph Skill

Builds an interactive 3D knowledge graph from all markdown files in the workspace and displays it via Canvas.

## How to Use

When the user asks to see a knowledge graph, visualize connections, or explore file relationships:

### Step 1: Build the graph data

```bash
python3 ~/clawd/skills/knowledge-graph/scripts/build-graph.py ~/clawd/ --output /tmp/graph-data.json
```

This scans all `.md` files recursively and extracts:
- Wiki-links (`[[...]]` references)
- Shared keywords (Jaccard similarity)
- Shared mentions (people, projects, technologies)

### Step 2: Build the combined HTML with embedded data

```bash
python3 ~/clawd/skills/knowledge-graph/scripts/build-graph.py ~/clawd/ \
  --output /tmp/graph-data.json \
  --embed ~/clawd/skills/knowledge-graph/assets/graph-viewer.html /tmp/knowledge-graph.html
```

The `--embed` flag takes the HTML template and injects the JSON data into it, producing a self-contained HTML file.

### Step 3: Present via Canvas

```
canvas action=navigate url=file:///tmp/knowledge-graph.html
```

### All-in-One Command

```bash
python3 ~/clawd/skills/knowledge-graph/scripts/build-graph.py ~/clawd/ \
  --output /tmp/graph-data.json \
  --embed ~/clawd/skills/knowledge-graph/assets/graph-viewer.html /tmp/knowledge-graph.html
```

Then present:
```
canvas action=navigate url=file:///tmp/knowledge-graph.html
```

## Alternative: Scan a Subdirectory

To graph only a specific project:

```bash
python3 ~/clawd/skills/knowledge-graph/scripts/build-graph.py ~/clawd/projects/rhinomcp-dev/ \
  --output /tmp/graph-data.json \
  --embed ~/clawd/skills/knowledge-graph/assets/graph-viewer.html /tmp/knowledge-graph.html
```

## Graph Features

- **3D force-directed layout** — nodes cluster by connections
- **Color-coded by type**: daily-note (blue), memory (green), task (orange), project (purple), knowledge (blue), config (grey), skill (red)
- **Node size** reflects file size + connection count
- **Edge types**: wiki-link (bright, particles), keyword (green, subtle), mention (orange, subtle)
- **Search** (top bar, or press `/`): filters by filename, keywords, mentions
- **Type filters**: click chips to show/hide types
- **Click a node**: opens detail panel with keywords, mentions, connected files
- **Click connections** in detail panel to navigate to that node
- **Escape**: close panel, clear search

## Output Schema

The JSON output follows this schema:

```json
{
  "nodes": [{ "id", "label", "type", "size", "keywords", "mentions", "lastModified" }],
  "edges": [{ "source", "target", "type", "weight" }],
  "stats": { "totalNodes", "totalEdges", "scannedAt" }
}
```

## Requirements

- Python 3.10+ (stdlib only, no pip dependencies)
- Browser with WebGL for 3D visualization
- Internet connection for CDN (3d-force-graph library)
