# OpenClaw Memory System – Vollständiger Guide

> Stand: Februar 2026 | OpenClaw 2026.2.3-1

---

## Übersicht

OpenClaw speichert Erinnerungen als **plain Markdown** im Workspace. Das Modell "erinnert" sich nur an das, was auf die Festplatte geschrieben wird. Zusätzlich gibt es eine **Vektor-Suche** die semantische Abfragen über alle Memory-Files ermöglicht.

---

## Die 3 Memory-Schichten

### 1. Memory Files (Markdown)

| File | Zweck | Wann geladen |
|------|-------|--------------|
| `MEMORY.md` | Kuratiertes Langzeitgedächtnis | Session-Start (nur Main-Session) |
| `memory/YYYY-MM-DD.md` | Tagesnotizen, Raw-Logs | Session-Start (heute + gestern) |

- **Speicherort:** `~/clawd/` (konfigurierbar via `agents.defaults.workspace`)
- **Format:** Markdown (nur .md wird indexiert)
- **Wer schreibt:** Das Modell selbst, auf Anweisung oder proaktiv

### 2. Vector Memory Search

Baut einen Vektor-Index über alle Memory-Files für semantische Suche.

**Tools:**
- `memory_search` – Semantische Suche, liefert Snippets mit Datei + Zeilennummern
- `memory_get` – Liest spezifische Memory-Files (Pfad + optionale Zeilen)

**Hybrid Search (BM25 + Vector):**
- **Vector:** Findet semantisch ähnliche Inhalte ("gleiche Bedeutung, andere Worte")
- **BM25:** Findet exakte Tokens (IDs, Code-Symbole, Fehlermeldungen)
- Kombination: `finalScore = vectorWeight × vectorScore + textWeight × textScore`
- Default-Gewichtung: 70% Vector / 30% BM25

**Embedding-Provider (wählbar):**

| Provider | Beschreibung | API Key nötig? |
|----------|-------------|----------------|
| `local` | node-llama-cpp, ~0.6GB GGUF Model | ❌ Nein |
| `openai` | OpenAI text-embedding-3-small | ✅ Ja |
| `gemini` | Google Gemini embeddings | ✅ Ja |

### 3. Automatic Memory Flush (Pre-Compaction)

Wenn der Context fast voll ist, triggert OpenClaw automatisch einen stillen Turn:
1. Das Modell wird aufgefordert, wichtige Infos in Memory-Files zu schreiben
2. Danach wird der Context kompaktiert (zusammengefasst)
3. So gehen keine wichtigen Informationen verloren

**Konfiguration:**
```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "memoryFlush": {
          "enabled": true,
          "softThresholdTokens": 4000
        }
      }
    }
  }
}
```

---

## NEU: QMD Backend (ab OpenClaw 2026.2.2)

### Was ist QMD?

QMD ist ein **lokaler Such-Sidecar** der das eingebaute SQLite-Indexing durch ein mächtigeres System ersetzt:

- **BM25** (Keyword-Suche)
- **Vektor-Suche** (Semantik)
- **Reranking** (Ergebnis-Qualität verbessern)
- Alles **lokal** – keine Cloud-API nötig

### Voraussetzungen für QMD

| Komponente | Beschreibung | Installation |
|------------|-------------|-------------|
| **QMD CLI** | Der Such-Sidecar selbst | `bun install -g github.com/tobi/qmd` |
| **Bun Runtime** | JavaScript-Runtime für QMD | `curl -fsSL https://bun.sh/install \| bash` |
| **SQLite mit Extensions** | Für Vektor-Tabellen | `sudo apt install sqlite3` (WSL2) |
| **GGUF Models** | Embedding + Reranking | Werden automatisch heruntergeladen (~1-2 GB) |

### Aktivierung

```json
{
  "memory": {
    "backend": "qmd",
    "citations": "auto",
    "qmd": {
      "includeDefaultMemory": true,
      "update": {
        "interval": "5m",
        "debounceMs": 15000,
        "onBoot": true
      },
      "limits": {
        "maxResults": 6,
        "maxSnippetChars": 700,
        "timeoutMs": 4000
      },
      "scope": {
        "default": "deny",
        "rules": [
          { "action": "allow", "match": { "chatType": "direct" } }
        ]
      }
    }
  }
}
```

### QMD Konfigurationsoptionen

| Option | Default | Beschreibung |
|--------|---------|-------------|
| `command` | `qmd` | Pfad zur QMD Binary |
| `includeDefaultMemory` | `true` | MEMORY.md + memory/**/*.md automatisch indexieren |
| `paths[]` | `[]` | Extra-Verzeichnisse indexieren (z.B. Projekt-Docs) |
| `sessions.enabled` | `false` | Session-Transcripts indexieren |
| `sessions.retentionDays` | unlimited | Wie lange exportierte Sessions behalten werden |
| `update.interval` | `5m` | Wie oft der Index aktualisiert wird |
| `update.onBoot` | `true` | Index beim Gateway-Start aktualisieren |
| `update.embedInterval` | `60m` | Wie oft Embeddings aktualisiert werden |
| `limits.maxResults` | `6` | Max. Ergebnisse pro Suche |
| `limits.timeoutMs` | `4000` | Timeout pro Suche |

### Extra Pfade indexieren (Beispiel)

```json
{
  "memory": {
    "qmd": {
      "paths": [
        { "name": "notes", "path": "~/notes", "pattern": "**/*.md" },
        { "name": "project-docs", "path": "~/projects/intelliplan/docs" }
      ]
    }
  }
}
```

---

## Vergleich: Builtin vs. QMD

| Feature | Builtin (aktuell) | QMD (neu) |
|---------|-------------------|-----------|
| **Suche** | Hybrid (BM25 + Vector) | BM25 + Vector + Reranking |
| **Qualität** | Gut | Besser (durch Reranking) |
| **Speed** | Schnell | Erster Start langsam (Model-Download) |
| **Setup** | Automatisch | Manuell (Bun + QMD installieren) |
| **Lokale Ausführung** | ✅ (node-llama-cpp) | ✅ (Bun + GGUF) |
| **Cloud-API nötig?** | Optional | ❌ Nein |
| **Extra Pfade** | Via `extraPaths` | Via `qmd.paths[]` (flexibler) |
| **Session-Indexing** | Experimentell | Unterstützt |
| **Speicher (~RAM)** | ~0.6 GB | ~1-2 GB |
| **Fallback** | — | Automatisch auf Builtin |
| **Zitations-Support** | ✅ | ✅ |

---

## Vorteile QMD

✅ **Bessere Suchqualität** durch Reranking (Query Expansion + Cross-Encoder)
✅ **Komplett lokal** – kein API Key, keine Cloud-Abhängigkeit
✅ **Flexible Extra-Pfade** – Projekt-Docs, Notizen, etc. durchsuchbar
✅ **Session-Transcripts** indexierbar (vergangene Gespräche durchsuchen)
✅ **Automatischer Fallback** auf Builtin wenn QMD ausfällt

## Nachteile QMD

❌ **Zusätzliche Abhängigkeiten** (Bun + QMD CLI installieren)
❌ **Erster Start langsam** (~1-2 GB GGUF Models werden heruntergeladen)
❌ **Mehr RAM-Verbrauch** (~1-2 GB für Reranking-Models)
❌ **Experimentell** – noch nicht so lange getestet wie Builtin
❌ **Kein Windows-Native** – braucht WSL2 (kein Problem bei dir)

---

## Empfehlung

### Jetzt beibehalten (Builtin)

Dein aktuelles Setup ist solide:
- Lokale Embeddings via node-llama-cpp ✅
- Hybrid Search (BM25 + Vector) ✅
- Memory Flush vor Compaction ✅
- Kein API Key nötig ✅

### Wann auf QMD wechseln?

- Wenn du **viele Memory-Files** hast (50+) und die Suche präziser sein soll
- Wenn du **Projekt-Dokumentation** durchsuchbar machen willst
- Wenn du **alte Gespräche** wieder finden willst (Session-Indexing)
- Wenn du mit der Suchqualität des Builtin-Systems nicht zufrieden bist

### Quick-Migration (wenn du wechseln willst)

```bash
# 1. Bun installieren
curl -fsSL https://bun.sh/install | bash

# 2. QMD installieren
bun install -g github.com/tobi/qmd

# 3. Testen
qmd --version

# 4. Config patchen (OpenClaw)
# memory.backend = "qmd" setzen (siehe Aktivierung oben)

# 5. Gateway restarten
openclaw gateway restart
```

---

## Aktuelle Config (dein Setup)

```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "enabled": true,
        "sources": ["memory", "sessions"],
        "provider": "local",
        "fallback": "none"
      },
      "compaction": {
        "mode": "safeguard",
        "memoryFlush": { "enabled": true }
      }
    }
  }
}
```

---

*Erstellt von Sentinel – 06.02.2026*
