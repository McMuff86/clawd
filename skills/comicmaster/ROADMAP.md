# ComicMaster – Roadmap

> **Stand:** 09.02.2026  
> **Hardware:** RTX 3090 (24GB), WSL2, ComfyUI  
> **Default Model:** DreamshaperXL  
> **Repo:** Teil von `github.com/McMuff86/clawd`

---

## ✅ Phase 1 – MVP (abgeschlossen)

Grundlegende Pipeline von Prompt bis PDF.

- [x] Story Planner (LLM → story_plan.json)
- [x] Panel Generator (ComfyUI, IPAdapter für Charakter-Konsistenz)
- [x] Speech Bubble System (Auto-Platzierung, mehrere Stile)
- [x] Page Layout Engine (Grid-Templates, variable Panelgrössen)
- [x] Export (PNG, PDF, CBZ)
- [x] Batch Optimizer (VRAM-effizient, mehrere Panels parallel)
- [x] Upscaling (2x via ComfyUI)

**Ergebnis:** 32-Panel Comic "Steel & Sawdust" in 9:36 min generiert ✅

---

## ✅ Phase 2 – Sequential Art Basics (abgeschlossen)

Grundlagen für sequenzielles Storytelling.

- [x] Eyeline Matching (Blickrichtung alterniert L/R)
- [x] Shot Progression Rules (Establishing → Medium → Close-Up)
- [x] Anti-Centering (Rule of Thirds, Charakter-Platzierung variiert)
- [x] Adaptive Font Sizing für Bubbles
- [x] Text-Duplikate-Erkennung

---

## ✅ Phase 3 – Quality Pipeline (abgeschlossen)

Automatische Qualitätskontrolle und Post-Processing.

- [x] Face Validation mit CLIP-Backend (funktioniert auch für Roboter/Aliens)
- [x] Per-Character Thresholds (Mensch 0.7, Non-Human 0.4)
- [x] Quality Tracker (6 Metriken: Schärfe, Kontrast, Farbe, Komposition, Konsistenz, Gesamt)
- [x] Color Grading als Pipeline-Stage (`--color-grade`, auto Style-Mapping)
- [x] Preset-Vergleich: DreamshaperXL vs JuggernautXL → Dreamshaper bleibt Default

---

## ✅ Phase 4 – Fortgeschrittenes Storytelling (abgeschlossen)

Professionelle Comic-Konventionen implementieren.

### 4.1 Lettering & Bubbles
- [x] **Z-Pattern Reading Order** – Bubble-Sortierung, First-Speaker-Priorität, Face-Avoidance
- [x] **Pro Comic Fonts** – 10 Fonts, 5 Genre-Styles, Style-Font-Map
- [x] **Balloon Tails** – Bézier-Kurven, Mund-Position, 55% Distanz (Blambot-Standard)
- [x] **Thought Bubbles** – Wolkenform + 3 Trail-Kreise
- [x] **Shout/Whisper/Narration** – Spiky, Dashed, Rectangular + passende Fonts

### 4.2 Kamera & Komposition
- [x] **180-Grad-Regel** – Character Positions pro Szene, konsistent über alle Panels
- [x] **Dynamic Angles** – Worm's Eye / Bird's Eye basierend auf Panel-Typ
- [ ] **Negative Space** – Bewusster Freiraum für emotionale Wirkung + Lettering
- [ ] **Page-Level Composition** – Splash Pages, Doppelseiten, Panel-Brüche

### 4.3 Pacing
- [x] **Panel-Grösse = Timing** – panel_importance (1-3) für Layout-Integration
- [ ] **Silent Panels** – Panels ohne Text für dramatische Beats
- [ ] **Page-Turn Reveals** – Cliffhanger am Seitenende

---

## 📋 Phase 5 – Character Consistency 2.0

Das grösste Problem bei AI-Comics: Figuren sehen nicht in jedem Panel gleich aus.

### 5.1 Kurzfristig (aktuelle Architektur)
- [x] **Costume Locking** – Outfit-Feld pro Charakter, wird in jedem Prompt wiederholt
- [x] **Face Crop + Re-inject** – Auto-Extract nach erstem Panel, als zusätzliche IPAdapter-Referenz
- [ ] **IPAdapter Weights erhöhen** – Stärkere Gewichtung für Gesichtsmerkmale

### 5.2 Mittelfristig (neue Technologie)
- [x] **ACE++ evaluiert** – Passt auf RTX 3090 (FP8), aber Entwicklung gestoppt → Ergänzung, nicht Ersatz
- [ ] **ACE++ Integration** – Hybrid: ACE++ für Close-Ups, IPAdapter für Wide Shots
- [ ] **InstantID / IP-Adapter FaceID** – Spezialisierte Face-Consistency Modelle
- [ ] **Character Sheet Generator** – Automatisch Turnaround-Sheet (Front/Side/Back) generieren

### 5.3 Langfristig
- [ ] **LoRA pro Charakter** – On-the-fly LoRA Training für Haupt-Charaktere (5-10 min)
- [ ] **Persistent Character Library** – Einmal erstellt, immer wiederverwendbar

---

## 📋 Phase 6 – Modell-Upgrades

Bessere Basismodelle = bessere Ergebnisse bei gleichem Workflow.

### 6.1 SDXL-basiert (6-8GB VRAM, schnell)
- [ ] **Illustrious XL** runterladen + testen (bestes Anime/Comic SDXL-Modell)
- [ ] **NoobAI-XL** testen (Illustrious-Finetune, noch besser für Comics)
- [ ] Preset-System erweitern: Auto-Auswahl basierend auf Comic-Style

### 6.2 FLUX-basiert (12-24GB VRAM, langsamer, höhere Qualität)
- [ ] **FLUX.1 dev** testen (FP8/GGUF für RTX 3090)
- [ ] **FLUX.2 dev** evaluieren (beste Bildqualität 2026, Multi-Reference built-in)
- [ ] Workflow-Anpassung für DiT-Architektur (andere Nodes als SDXL)

### 6.3 Entscheidungsmatrix
| Modell | Qualität | Speed | VRAM | Comic-LoRAs | Empfehlung |
|--------|----------|-------|------|-------------|------------|
| DreamshaperXL | ★★★ | ~15s | 6-8GB | ✅ viele | **Aktueller Default** |
| Illustrious XL | ★★★★ | ~15s | 6-8GB | ✅ viele | **Nächster Test** |
| NoobAI-XL | ★★★★ | ~15s | 6-8GB | ✅ viele | Nach Illustrious |
| FLUX.1 dev | ★★★★☆ | ~60s | 12-16GB | ✅ wachsend | Qualitäts-Upgrade |
| FLUX.2 dev | ★★★★★ | ~60s | 14-24GB | 🔄 neu | Zukunft |

---

## 📋 Phase 7 – Custom Style Training

Eigener, wiedererkennbarer Comic-Style via LoRA.

- [ ] **Kohya-ss** auf WSL2 installieren + konfigurieren
- [ ] **Training Dataset** sammeln: 50-100 kuratierte Comic-Panels
- [ ] **Style LoRA trainieren** (SDXL-basiert, ~2-4h auf RTX 3090)
- [ ] **A/B Test**: Generic Style vs. Custom LoRA
- [ ] Style-Bibliothek aufbauen: Manga, Western, Cartoon, Noir, etc.

---

## 📋 Phase 8 – Produktisierung (Vision)

ComicMaster als eigenständiges Tool/Service.

- [ ] **Web UI** – Prompt eingeben → Comic generiert → Download
- [ ] **Template Library** – Vorgefertigte Story-Templates (Action, Romance, Sci-Fi, etc.)
- [ ] **Multi-Language** – Automatische Übersetzung der Dialoge
- [ ] **Print-Ready Export** – CMYK, Bleed, Seitenzahlen, Cover
- [ ] **Collaboration** – Story editieren, Panels austauschen, Feedback
- [ ] **API** – Comic-Generation als Service (SaaS Potential?)

---

## Metriken & Ziele

| Metrik | Aktuell | Ziel Phase 4-5 | Ziel Phase 6-7 |
|--------|---------|-----------------|-----------------|
| Panels pro Comic | 32 | 50+ | 100+ |
| Generierungszeit | ~18s/Panel | ~15s/Panel | ~10s/Panel |
| Character Consistency | ~70% | ~85% | ~95% |
| Lettering-Qualität | Basic | Pro-Level | Print-Ready |
| Unterstützte Styles | 7 | 10+ | 20+ (inkl. Custom) |

---

## Abhängigkeiten

- **ComfyUI** auf Windows mit `--listen 0.0.0.0`
- **RTX 3090** (24GB) – reicht für alles bis FLUX.2
- **IPAdapter + CLIP Vision** installiert
- **90+ LoRAs** verfügbar in ComfyUI
- **Python 3.x** in WSL2

---

*Letzte Aktualisierung: 09.02.2026 | Nächstes Review: Sprint 5*
