# Projects Schema

Aktive Projekte mit eigener Struktur.

## Wann ein Projekt?

Ein Projekt bekommt einen eigenen Ordner wenn:
- Mehr als 2-3 Tasks daran hängen
- Eigene Dateien entstehen (Code, Docs, Assets)
- Es länger als eine Woche läuft

Sonst: Tasks in `tasks/side-hustle.md` oder `tasks/work.md` tracken.

## Struktur

```
projects/
├── SCHEMA.md                 # Diese Datei
└── project-slug/
    ├── README.md             # Projekt-Übersicht (Pflicht)
    ├── BUILD_PLAN.md         # Technischer Plan (optional)
    ├── DECISIONS.md          # Wichtige Entscheidungen (optional)
    ├── docs/                 # Dokumentation
    ├── src/                  # Code (wenn hier, nicht in separatem Repo)
    └── assets/               # Bilder, Referenzen, etc.
```

## README.md Template

```markdown
# Projekt Name

Kurzbeschreibung in 1-2 Sätzen.

## Status

`planning` | `active` | `paused` | `done` | `abandoned`

## Ziel

Was soll am Ende rauskommen?

## Stack

- Tech 1
- Tech 2

## Timeline

- **Start:** YYYY-MM-DD
- **Target:** YYYY-MM-DD (optional)

## Links

- Brainstorm: `brainstorms/YYYY-MM-DD_slug.md`
- Tasks: `tasks/side-hustle.md#section`
- Repo: `github.com/user/repo` (wenn extern)

## Log

### YYYY-MM-DD
- Was wurde gemacht
```

## Lifecycle

1. **Idee** → `brainstorms/` (noch kein Projekt-Ordner)
2. **Commitment** → `projects/slug/` anlegen, README.md schreiben
3. **Aktiv** → BUILD_PLAN.md, Code, Docs
4. **Done/Paused** → Status updaten, optional nach `projects/_archive/` verschieben

## Naming

- Lowercase, kebab-case: `rhino-ar-viewer`, `intelliplan-mvp`
- Kurz aber verständlich
