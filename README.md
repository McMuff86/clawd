# 🤖 Sentinel Workspace

Persönlicher AI-Workspace von [Sentinel](https://github.com/McMuff86/clawd) — powered by [OpenClaw](https://github.com/openclaw/openclaw).

## Was ist das?

Dieses Repo enthält die Skills, Konfigurationen, Memory-Files und Automatisierungen meines AI-Assistenten **Sentinel**. Er läuft auf einer WSL2-Workstation und unterstützt bei:

- 🏗️ CAD/CNC-Automatisierung (Rhino, Grasshopper)
- 🎨 Bildgenerierung (ComfyUI / Stable Diffusion)
- 📊 Projektmanagement & Dokumentation
- 🔧 DevOps & Tooling

## Skills

| Skill | Beschreibung |
|-------|-------------|
| **comfyui** | Bildgenerierung mit ComfyUI (SDXL, LoRA) |
| **comicmaster** | Comic-Pipeline: Story → Panels → Bubbles → Layout → PDF |
| **rhinomcp** | Rhino 3D Steuerung via MCP (Geometrie, Grasshopper, Screenshots) |
| **openai-whisper** | Lokale Spracherkennung |

## Struktur

```
clawd/
├── skills/          # AI Skills (ComfyUI, RhinoMCP, ComicMaster, ...)
├── memory/          # Tagesnotizen & Session-Logs
├── projects/        # Aktive Projekte
├── templates/       # Dokumentvorlagen
├── sprints/         # Sprint-Backlogs
├── docs/            # OpenClaw Dokumentation
├── SOUL.md          # Persönlichkeit
├── AGENTS.md        # Arbeitsregeln
├── MEMORY.md        # Langzeitgedächtnis
└── USER.md          # Kontext über den User
```

## Setup

Läuft auf:
- AMD Threadripper 32-Core, 128GB RAM, RTX 3090
- Windows + WSL2 (Ubuntu)
- ComfyUI auf Windows, erreichbar via `host.docker.internal:8188`

## Lizenz

Privater Workspace. Skills können als Referenz dienen.
