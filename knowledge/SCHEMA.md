# Knowledge Schema

Referenzwissen – Dinge die ich mir merken soll für später.

## Wann Knowledge?

- Recherche-Ergebnisse die wiederverwendbar sind
- How-Tos, Anleitungen, Best Practices
- Technische Referenzen (APIs, Specs)
- Nicht projekt-spezifisch (sonst → `projects/slug/docs/`)

## Struktur

```
knowledge/
├── SCHEMA.md           # Diese Datei
├── topic/              # Themen-Ordner
│   ├── README.md       # Übersicht zum Thema
│   └── specific.md     # Spezifische Artikel
└── standalone.md       # Einzelne Artikel ohne Ordner
```

## Beispiele

```
knowledge/
├── rhino/
│   ├── README.md           # Rhino-Ecosystem Übersicht
│   ├── grasshopper-ai.md   # AI-Tools für GH
│   └── food4rhino.md       # Marketplace Notes
├── ar-mr/
│   ├── README.md           # AR/MR Technologie-Übersicht
│   └── fologram.md         # Fologram Research
└── dev/
    ├── wsl-setup.md        # WSL2 Config Notes
    └── cursor-tips.md      # Cursor IDE Tricks
```

## Format

```markdown
# Titel

> Kurze Zusammenfassung (1-2 Sätze)

## Inhalt

...

## Quellen

- [Link](url)
- Dokument XY

---
*Erstellt: YYYY-MM-DD | Aktualisiert: YYYY-MM-DD*
```

## Tagging

Im Dateinamen oder als YAML-Frontmatter:
```yaml
---
tags: [rhino, grasshopper, ai]
---
```
