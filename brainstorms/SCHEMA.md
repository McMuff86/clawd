# Brainstorm Schema

## Struktur

Jedes Brainstorm ist ein Markdown-File mit YAML-Frontmatter.

```
brainstorms/
├── SCHEMA.md           # Diese Datei
├── index.json          # Schnell-Index für Queries
└── YYYY-MM-DD_slug.md  # Einzelne Brainstorms
```

## Frontmatter Schema

```yaml
---
id: string              # Unique ID (UUID oder slug)
title: string           # Kurztitel
date: string            # ISO 8601 (YYYY-MM-DD)
tags: string[]          # Kategorien/Tags
status: string          # idea | exploring | actionable | archived
priority: number        # 1 (hoch) - 5 (niedrig)
source: string          # Woher kam die Idee? (agent, manual, meeting, etc.)
related: string[]       # IDs von verwandten Brainstorms
actions: Action[]       # Nächste Schritte (siehe unten)
---
```

## Action Schema

```yaml
actions:
  - task: string        # Was tun?
    effort: string      # low | medium | high
    impact: string      # low | medium | high
    status: string      # todo | in-progress | done | dropped
    due: string         # Optional: Deadline (YYYY-MM-DD)
    notes: string       # Optional: Notizen
```

## Body

Nach dem Frontmatter: Freiform-Markdown.

Empfohlene Sections:
- `## Kontext` - Hintergrund, warum dieses Brainstorm
- `## Ideen` - Die eigentlichen Ideen
- `## Research` - Gefundene Infos, Links
- `## Fazit` - Zusammenfassung, Entscheidungen
- `## Log` - Chronologische Updates

## Index (index.json)

```json
{
  "version": 1,
  "entries": [
    {
      "id": "2026-01-25_rhino-research",
      "title": "Rhino Community & Side-Hustle Brainstorm",
      "date": "2026-01-25",
      "tags": ["rhino", "side-hustle", "research"],
      "status": "actionable",
      "priority": 2,
      "file": "2026-01-25_rhino-research.md"
    }
  ]
}
```

## Nutzung

**Neues Brainstorm erstellen:**
1. File anlegen: `YYYY-MM-DD_slug.md`
2. Frontmatter ausfüllen
3. Index updaten

**Suchen/Filtern:**
- Nach Tags: `jq '.entries[] | select(.tags[] == "rhino")' index.json`
- Nach Status: `jq '.entries[] | select(.status == "actionable")' index.json`
- Nach Priorität: `jq '.entries | sort_by(.priority)' index.json`

**Archivieren:**
- Status auf `archived` setzen
- Optional: In `brainstorms/archive/` verschieben
