# Finding Reports

Strukturierte Agent-Reports aus Nacht-Sessions und Sub-Agent-Runs.

## Struktur

```
reports/
├── {projekt}/                    # Projektname (lowercase, kebab-case)
│   └── YYYY-MM-DD_{thema}.md    # Datum + Thema
└── maintenance/                  # Cross-Projekt (Deps, Security, Infra)
```

## Namenskonvention

- **Dateiname:** `YYYY-MM-DD_{thema-kebab-case}.md`
- **Projekt-Ordner:** Lowercase, kebab-case (z.B. `comicmaster`, `intelliplan`, `rhino-assembly-outliner`)
- **maintenance/** für projektübergreifende Reports (Dependency Updates, Security Audits, etc.)

## Template

```markdown
# {Titel}

**Datum:** YYYY-MM-DD
**Agent:** {Agent-Name/Label}
**Projekt:** {Projektname}
**Dauer:** {Xm Ys}

## Zusammenfassung
{1-3 Sätze}

## Änderungen
{Details}

## Tests
{Ergebnisse}

## Offene Punkte
{Was noch zu tun ist}
```
