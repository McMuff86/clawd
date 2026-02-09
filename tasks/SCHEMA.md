# Tasks Schema

Einfaches Task-Tracking, file-basiert.

## Struktur

```
tasks/
├── SCHEMA.md       # Diese Datei
├── inbox.md        # Schnelle Notizen, unsortiert
├── work.md         # Job-bezogene Tasks
├── side-hustle.md  # Side-Hustle Tasks
└── archive.md      # Erledigte Tasks
```

## Task Format

```markdown
- [ ] Task Beschreibung
  - Details, Notizen
  - Due: YYYY-MM-DD
  - Priority: 1-3 (1=hoch)
  - Source: brainstorms/YYYY-MM-DD_slug.md
  - Tags: #tag1 #tag2
```

### Minimales Format (für schnelle Captures)
```markdown
- [ ] Task Beschreibung
```

### Vollständiges Format (für wichtige Tasks)
```markdown
- [ ] Task Beschreibung
  - Context: Warum ist das wichtig?
  - Due: 2026-02-01
  - Priority: 1
  - Source: brainstorms/2026-01-25_rhino-research.md
  - Effort: low | medium | high
  - Impact: low | medium | high
  - Tags: #rhino #side-hustle
```

## Status

- `[ ]` = offen
- `[x]` = erledigt
- `[-]` = gestrichen/dropped
- `[~]` = in Arbeit

## Priority

- **1** = Dringend/Wichtig – diese Woche
- **2** = Wichtig – diesen Monat
- **3** = Nice-to-have – irgendwann

## Workflow

1. **Capture:** Schnelle Notiz → `inbox.md`
2. **Sortieren:** Bei Zeit in `work.md` oder `side-hustle.md` verschieben
3. **Erledigt:** Nach `archive.md` verschieben (Datum notieren)
4. **Review:** Weekly Review – Inbox leeren, Priorities checken

## Verlinkung

Tasks können auf ihren Ursprung verweisen:
- `Source: brainstorms/2026-01-25_rhino-research.md` → Idee aus Brainstorm
- `Source: meeting` → aus einem Meeting
- `Source: heartbeat` → Sentinel hat's gefunden

Brainstorms können auf Tasks verweisen:
- Im `actions:` Block des Frontmatters
- Oder inline: `→ tasks/side-hustle.md#rhino-ar-viewer`
