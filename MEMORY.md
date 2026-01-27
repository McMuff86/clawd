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

### Side-Hustle
- **Rhino AR Viewer** – AR-App für Android, Rhino/GH Geometrie anzeigen
- **RhinoLeaderTool + RH_Excel_Link** – Dormante Projekte, zusammenführen
- **Grasshopper Templates** – Verkauf auf Food4Rhino/Gumroad

### Job
- Türblatt-/Zargenlisten optimieren (RhinoLeaderTool nutzen)
- CAD-Templates aufbauen (Zylinder, Zargen, OPK)

## 🔧 Tools & Accounts

- **Gmail:** sentinel.core.ai@gmail.com (gog CLI, Hooks aktiv)
- **Telegram:** Gekoppelt, gleiche Session wie Webchat

## 💡 Entscheidungen & Learnings

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

### 2026-01-26
- Gmail-Integration eingerichtet (gog + Hooks)
- Heartbeat alle 30 Min aktiviert
- Workspace-Struktur: tasks/, brainstorms/, memory/, projects/, knowledge/

---

*Wird regelmässig aktualisiert basierend auf Daily Logs.*
