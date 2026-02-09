# ComicMaster – Nächste Session Kontext

## Status: Phase 3+4 komplett, Quality Research done

### Was existiert
- **Skill:** `~/clawd/skills/comicmaster/`
- **Scripts:** comic_pipeline.py, panel_generator.py, speech_bubbles.py, page_layout.py, export.py, story_planner.py, batch_optimizer.py, upscale.py, color_grading.py, utils.py
- **Workflows:** 5 JSON-Dateien in `workflows/`
- **Research Reports (LIES DIESE ZUERST):**
  - `research/aaa-comic-analysis.md` — Profi-Standards vs unser Output
  - `research/sota-models-and-training.md` — SOTA Modelle & LoRA Training
  - `research/quality-tracking.md` — ML Quality Metrics Design
- **Learnings:** `memory/learnings.md`
- **PDFs:** `skills/comicmaster/output/` (4 PDFs)
- **30-Panel Test:** `output/comicmaster/test_30panel/` (7 Seiten)

### Verbesserungen umsetzen (nach Priorität)

**P0 — Lettering Fix ✅ DONE:**
- ~~Text wird abgeschnitten in Bubbles~~ → Adaptive Font Sizing + bessere Margins
- ~~Duplikate (gleicher Text doppelt)~~ → Deduplication-Check in comic_pipeline.py
- Pro Comic Fonts evaluieren (Blambot-Standard) → noch offen
- Reading Order sicherstellen (Z-Pattern) → noch offen

**P0 — Sequential Composition ✅ DONE:**
- ~~Eyeline Matching~~ → Alternating look left/right basierend auf Panel-Sequence
- ~~Shot Progression Rules~~ → Hinweise basierend auf vorherigem Panel
- 180-Grad-Regel für Dialoge → noch offen (benötigt erweiterte Story-Plan Felder)
- ~~Anti-Centering~~ → Rule of thirds + alternating character placement

**P1 — Character Consistency stärken:**
- IPAdapter weights erhöhen für Gesichter
- Face Validation nach Generation (CLIP-Similarity Check)
- Costume Locking (Kleidung konsistenter)

**P2 — Illustrious XL testen:**
- Modell herunterladen (CivitAI)
- Als neues Preset in presets.json
- Vergleichstest: gleicher Comic mit DreamShaperXL vs Illustrious XL

**P2 — Quality Tracker Phase 1 ✅ DONE:**
- ~~PIL-basierte Metriken implementieren~~ → quality_tracker.py (6 Metriken)
- ~~Automatisch nach jedem Comic-Run ausführen~~ → CLI: `python quality_tracker.py <panels_dir>`
- ~~Scores in JSON speichern~~ → quality_scores.json mit per-panel + aggregate

**P3 — LoRA Training:**
- Kohya-ss auf WSL2 installieren
- 50-100 Comic-Panels als Training Dataset sammeln
- Eigenes Comic-Style LoRA trainieren

### Technische Details
- ComfyUI: `host.docker.internal:8188`
- Presets: `skills/comfyui/presets.json`
- 90 LoRAs verfügbar, 7 Styles gemappt
- IPAdapter + CLIP Vision installiert
- RTX 3090 (24GB VRAM)
- Illustrious XL, NoobAI-XL = beste Comic-Modelle laut Research
