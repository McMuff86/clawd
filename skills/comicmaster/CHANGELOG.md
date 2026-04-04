# ComicMaster – Changelog

Alle wesentlichen Änderungen am ComicMaster Skill.

---

## [0.5.0] – 2026-02-09 (Nacht-Session)

### Phase 5 – Character Consistency 2.0 (teilweise)
- **Costume Locking** – Outfit-Feld pro Charakter, wird in jedem Panel-Prompt wiederholt
- **Face Crop + Re-inject** – Auto-Extract nach erstem Panel, als zusätzliche IPAdapter-Referenz
- **ACE++ Evaluation** – Getestet, passt auf RTX 3090 (FP8), aber Entwicklung gestoppt → bleibt Ergänzung

### Phase 4 – Fortgeschrittenes Storytelling
- **Z-Pattern Reading Order** – Bubble-Sortierung nach natürlichem Lesefluss, First-Speaker-Priorität, Face-Avoidance
- **Pro Comic Fonts** – 10 Fonts installiert, 5 Genre-Styles, automatische Style-Font-Map
- **Balloon Tails** – Bézier-Kurven, Mund-Position, 55% Distanz (Blambot-Standard)
- **Thought Bubbles** – Wolkenform + 3 Trail-Kreise
- **Shout/Whisper/Narration Styles** – Spiky, Dashed, Rectangular + passende Fonts
- **180-Grad-Regel** – Character Positions pro Szene, konsistent über alle Panels
- **Dynamic Angles** – Worm's Eye / Bird's Eye basierend auf Panel-Typ
- **Panel-Grösse = Timing** – panel_importance (1-3) steuert Layout-Gewichtung

### Verbesserungen (P1+P2 Nacht-Fabrik, 5 Agents)
- Character Consistency: IPAdapter, Face Validation, Costume Locking, Multi-Angle Refs
- Page Layout Redesign: Variable Gutters, Non-Rect Panels, Spread-Aware, Splash Rules
- Prompt Engineering: Anti-Centering, Pose Descriptions, Env Interaction, Lighting
- Quality Gates: Hand/Finger Detection, Face Embedding, Auto-Regen, Inpainting Workflow
- Color Storytelling + SFX Integration

---

## [0.4.0] – 2026-02-09

### Phase 3 – Quality Pipeline
- **Face Validation** mit CLIP-Backend (funktioniert auch für Roboter/Aliens)
- **Per-Character Thresholds** – Mensch 0.7, Non-Human 0.4
- **Quality Tracker** – 6 Metriken: Schärfe, Kontrast, Farbe, Komposition, Konsistenz, Gesamt
- **Color Grading** als Pipeline-Stage (`--color-grade`, auto Style-Mapping)
- **Preset-Vergleich:** DreamshaperXL vs JuggernautXL → Dreamshaper bleibt Default

---

## [0.3.0] – 2026-02-08 (Nacht-Session 23:34)

### Phase 2 – Sequential Art Basics
- **Eyeline Matching** – Blickrichtung alterniert L/R
- **Shot Progression Rules** – Establishing → Medium → Close-Up
- **Anti-Centering** – Rule of Thirds, Charakter-Platzierung variiert
- **Adaptive Font Sizing** für Bubbles
- **Text-Duplikate-Erkennung**

### Test: "Steel & Sawdust"
- 32-Panel Comic generiert in 9:36 min
- Output: `output/comicmaster/steel_&_sawdust/`

---

## [0.2.0] – 2026-02-08 (abends ~20:30)

### Phase 1 – MVP (Character Consistency)
- **IPAdapter Integration** – PLUS + PLUS FACE Auto-Switch
- **Character Ref Generation** + automatischer Upload zu ComfyUI
- Test: "Night Shift" – 4 Panels mit konsistentem Charakter, 45.6s

### Fixes
- Bubble-Clipping behoben
- Panel-Overlay Fehler korrigiert

---

## [0.1.0] – 2026-02-08

### Phase 1 – MVP Pipeline
- **story_planner.py** – LLM → story_plan.json (Validation, Enrichment, Auto-Layout)
- **panel_generator.py** – SDXL via ComfyUI, Retry-Logic
- **speech_bubbles.py** – 6 Bubble-Stile, Auto-Platzierung
- **page_layout.py** – 7 Grid-Templates, variable Panelgrössen
- **export.py** – PNG, PDF, CBZ Export
- **batch_optimizer.py** – VRAM-effiziente Batch-Generierung
- **upscale.py** – 2x Upscaling via ComfyUI
- **color_grading.py** – Post-Processing Farbanpassung
- **comic_pipeline.py** – Full Orchestrator
- **utils.py** – Shared Utilities

### Workflows
- `panel_sdxl.json` – Standard SDXL Generierung
- `panel_ipadapter.json` – IPAdapter Character Consistency
- `character_ref.json` – Character Reference Generierung

### Erster Test
- "The Tired Detective" – 4 Panels, 64.5s

---

## Offen

### Phase 5 (Rest) – Character Consistency 2.0
- IPAdapter Weights für Gesichter erhöhen
- ACE++ Integration (Hybrid: Close-Ups ACE++, Wide Shots IPAdapter)
- InstantID / IP-Adapter FaceID
- Character Sheet Generator (Turnaround Front/Side/Back)
- LoRA pro Charakter (On-the-fly Training)

### Phase 6 – Modell-Upgrades
- Illustrious XL, NoobAI-XL, FLUX.1/2 testen

### Phase 7 – Custom Style Training
- Kohya-ss Setup, Style LoRA Training

### Phase 8 – Produktisierung
- Web UI, Templates, Multi-Language, Print-Ready, API

---

*Letzte Aktualisierung: 10.02.2026*
