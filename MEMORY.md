# MEMORY.md – Long-Term Memory

Kuratierte Erinnerungen, Entscheidungen und Learnings. Kein Raw-Log – das ist `memory/YYYY-MM-DD.md`.

---

## 🧑 Über Adi

- **Beruf:** Projektleiter Schreinerei (vorher Metallbau)
- **Expertise:** CAD → CNC → Produktion Pipeline, 14 Jahre Rhino/Grasshopper
- **Setup:** Threadripper 32-Core, 128GB RAM, RTX 3090, WSL2
- **Familie:** 3 Kids (4.5, 2.5, 2 Monate) – Zeit ist knapp
- **Ziel:** Side-Hustle aufbauen → SaaS für CAD/Fertigung → Selbstständigkeit

## 🎯 Aktuelle Prioritäten

### IntelliPlan (Hauptprojekt)
- **Produktvision:** Excel-Ablösung für Fertigungsbetriebe (Schreinerei, Metallbau, etc.)
- **Repo:** github.com/McMuff86/IntelliPlan, Branch: feature/wochenplan-phase2
- **Stack:** Node/Express + React/Vite + PostgreSQL (Docker)
- **Status:** Excel-Import funktioniert, Wochenplan-View da, Projects/Gantt existiert
- **Nächster Schritt:** Milestone 1 – Projects↔Wochenplan vereinigen (Gantt mit Phasen)
- **Docs:** `docs/product-vision.md`, `docs/unification-plan.md`
- **🔥 Beta-Lead:** Renato Buchers Cousin sucht aktiv ERP-Ablösung → Kontakt nach Milestone 2
- **Architektur-Entscheidungen:**
  - Phasen konfigurierbar pro Betrieb (phase_definitions Tabelle)
  - Ein Task = Eine Phase (simpel, mappt auf Excel)
  - KW-basierte Planung, Halbtags-Zuweisungen
  - Gantt als primäre Projektansicht (Drag&Drop mit Dependencies existiert)
  - Import = Onboarding, nicht Dauerlösung

### Side-Hustle (sekundär)
- **Rhino AR Viewer** – AR-App für Android, Rhino/GH Geometrie anzeigen
- **RhinoLeaderTool + RH_Excel_Link** – Dormante Projekte, zusammenführen
- **Grasshopper Templates** – Verkauf auf Food4Rhino/Gumroad

### Job
- Türblatt-/Zargenlisten optimieren (RhinoLeaderTool nutzen)
- CAD-Templates aufbauen (Zylinder, Zargen, OPK)

## 🔧 Tools & Accounts

- **Gmail:** sentinel.core.ai@gmail.com (gog CLI, Hooks aktiv)
- **Telegram:** Gekoppelt, gleiche Session wie Webchat
- **Memory Search:** Lokal (node-llama-cpp), keine API Keys nötig
- **Dashboard:** SPA unter `~/.npm-global/lib/node_modules/openclaw/dist/control-ui/`

## 📝 Config-Wissen

- `ui.assistant.avatar` → Nur Emoji/Text/URL (max 200 chars), kein Dateipfad
- `agents.list[].identity.avatar` → Workspace-relative Pfade OK
- Memory Search: Explizit `provider: "local"` setzen, sonst Fallback auf OpenAI/Google
- Memory Flush vor Compaction: aktiviert

## 💡 Entscheidungen & Learnings

### 2026-02-05 – RhinoAssemblyOutliner Plugin
**Neues Projekt:** SolidWorks-artiger Assembly Outliner für Rhino 8
- Repo: github.com/McMuff86/RhinoAssemblyOutliner
- Stack: C# / .NET 7.0-windows / RhinoCommon 8.0 / Eto.Forms
- Plugin GUID: 68EE26AC-D516-4F50-9DE2-46D105702323

**Rhino Plugin Learnings:**
- Panel Registration im **Command Constructor**, NICHT in Plugin.OnLoad()
- `IsLinkedDefinition` gibt es nicht → `UpdateType == Linked` prüfen
- Für .NET 7: Target `net7.0-windows`, `<NoWarn>NU1701</NoWarn>`
- Output als .rhp: `<TargetExt>.rhp</TargetExt>` in csproj
- AssemblyInfo.cs mit `[assembly: Guid("...")]` für Plugin-ID

**Feature:** Assembly Mode
- Document Mode (alle Blöcke) vs Assembly Mode (nur ein Root + Kinder)
- User wählt Root via Rechtsklick → "Set as Assembly Root"
- Session-basiert erstmal, Persistenz via UserText später

### 2026-01-28 – RhinoMCP Skill
**Grosses Update:** Der RhinoMCP Skill ist jetzt sehr komplett.

**Neue Features:**
- Boolean Ops, Selection, Solid Fillet/Chamfer, Split/Trim, Text/Annotations
- GrasshopperPlayer Automation mit custom Parametern (`grasshopper.py`)
- Screenshots direkt ins Linux-Filesystem (WSL UNC-Pfad)

**Grasshopper Integration - Zwei Wege:**
1. **SDK API** (`load_grasshopper_definition`, `set_parameter`, `solve`):
   - ✅ Gut zum Inspizieren: Parameter, Types, Defaults, Outputs sehen
   - ✅ Parameter setzen & solven funktioniert
   - ❌ Bake funktioniert NICHT mit Rhino 8 "Model Object" Komponenten
   
2. **GrasshopperPlayer** (`grasshopper.py run`):
   - ✅ Funktioniert vollständig inkl. Model Objects
   - ✅ Custom Parameter via Prompt-Monitoring & SendKeystrokes
   - ⚠️ Braucht aktives Prompt-Monitoring (nicht blockierend starten)

**Technische Learnings:**
- `Font.FromQuartetProperties()` statt Font-Konstruktor
- `Leader.Create()` erwartet `Point3d[]`, nicht `Point2d[]`
- GrasshopperPlayer via `SendKeystrokes` starten (nicht `RunScript` blocking)
- Cylinder/Cone: Default `cap=True` für Boolean-Kompatibilität

**Repo:** `github.com/McMuff86/rhinomcp` Branch `feature/clawdbot-integration`

### 2026-02-03 – UI Freeze & Session Cleanup
- **UI Freeze Root Cause:** Markdown re-parsing bei jedem Streaming-Token
- **Fix:** Sessions regelmässig cleanen (Script: `~/clawd/scripts/cleanup-sessions.sh`)
- Whisper base model für Voice Transcription (~16s, gute Qualität)
- OpenClaw TTS nutzt Edge TTS (Microsoft) - **kostenlos!**
- Qwen3-TTS: Whisper Auto-Transcript Feature hinzugefügt

### 2026-01-26
- Gmail-Integration eingerichtet (gog + Hooks)
- Heartbeat alle 30 Min aktiviert
- Workspace-Struktur: tasks/, brainstorms/, memory/, projects/, knowledge/

---

*Wird regelmässig aktualisiert basierend auf Daily Logs.*
