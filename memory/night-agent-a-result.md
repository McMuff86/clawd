# Night Agent A Result — Character Consistency Improvements

**Date:** 2026-02-09  
**Task:** Character Consistency im ComicMaster Skill  
**Status:** ✅ Alle 4 Aufgaben umgesetzt

---

## 1. IPAdapter Weight Tuning ✅

**File:** `scripts/panel_generator.py`

**Änderungen:**
- `IPADAPTER_WEIGHTS` aktualisiert:
  - `extreme_wide`: 0.40 → **0.50**
  - `wide`: 0.50 → **0.55**
  - `medium`: 0.65 → **0.75**
  - `medium_close`: 0.70 → **0.85**
  - `close_up`: 0.80 → **0.92**
  - `extreme_close`: 0.50 → **0.95**
- Neuer `FACE_WEIGHT_BOOST = 0.05` Konstante hinzugefügt
- Face-Shots (close_up, extreme_close, medium_close) bekommen automatisch +0.05 Weight Boost
- Default fallback weight von 0.65 auf 0.75 erhöht

## 2. Multi-Angle Reference Sheets ✅

**Files:** `scripts/panel_generator.py`, `workflows/character_ref_multi.json`

**Änderungen:**
- `CHARACTER_REF_VIEW_PROMPTS` Dict mit 4 View-spezifischen Prompts: front, three_quarter, profile, back
- `CAMERA_ANGLE_TO_REF_VIEW` Mapping: camera_angle → bevorzugte Ref-View
  - eye_level/low_angle/worms_eye → front
  - high_angle/dutch_angle → three_quarter
  - birds_eye/over_the_shoulder → back
- `generate_character_ref()` erweitert mit `multi_angle=True` Parameter:
  - Generiert 4 separate 1024x1024 Views
  - Assembliert 2x2 Grid (2048x2048)
  - Jede View wird separat zu ComfyUI hochgeladen
  - Return-Dict enthält `views` Dict mit per-View Pfaden und ComfyUI Filenames
  - Backwards-kompatibel: `multi_angle=False` für altes Verhalten
- `generate_panel()` wählt automatisch die beste View basierend auf `camera_angle`
- Neuer Workflow `character_ref_multi.json` als Dokumentation

## 3. Costume Locking ✅

**Files:** `scripts/story_planner.py`, `scripts/panel_generator.py`

**Änderungen in story_planner.py:**
- `_extract_costume_from_description()` Funktion hinzugefügt
  - Heuristische Extraktion von Top/Bottom/Shoes/Accessories aus visual_description
  - Keyword-Listen für jede Kategorie (_TOP_KEYWORDS, _BOTTOM_KEYWORDS, etc.)
- `enrich_story_plan()` setzt automatisch `costume_details` auf Characters wenn nicht vorhanden

**Änderungen in panel_generator.py:**
- `_build_costume_string()` Helper: generiert "wearing [top], [bottom], [shoes], with [accessories]"
- Costume-String wird in JEDEN Panel-Prompt injiziert:
  - Standard SDXL: als natürlicher Satz im Character-Teil
  - Illustrious XL: als konvertierte Danbooru-Tags
- Wenn `costume_details` explizit im Story Plan gesetzt → wird direkt verwendet
- Wenn nicht gesetzt → automatische Extraktion aus visual_description (via Enrichment)

## 4. Face Validation ✅

**Neues File:** `scripts/face_validator.py`

**Features:**
- `FaceValidator` Klasse mit 3 Backends (automatischer Fallback):
  1. **InsightFace** (ArcFace) — höchste Qualität
  2. **face_recognition** (dlib) — einfacher aber effektiv
  3. **PIL Histogram Fallback** — kein ML nötig, Farbhistogramm der Gesichtsregion
- `validate_panel()`: Einzelpanel gegen Referenz prüfen
- `validate_panel_batch()`: Alle Characters in einem Panel prüfen
- `generate_quality_report()`: Menschenlesbarer Quality Report
- Similarity Threshold: 0.7 (Cosine Similarity)
- Automatische Retry-Logik (max 2 Retries) in `generate_panel()` integriert:
  - Nach Panel-Generation → Face Embedding extrahieren → mit Reference vergleichen
  - Unter Threshold → neuer Seed → Retry
  - Bestes Ergebnis (höchste Similarity) wird behalten
- Face Similarity Scores werden im Panel-Result als `face_validation` Array gespeichert

**Installation:**
- InsightFace/face_recognition brauchen gcc (nicht auf diesem System verfügbar)
- PIL-Fallback funktioniert out-of-box
- Auf ComfyUI-Maschinen (mit Build-Tools) wird InsightFace automatisch bevorzugt

---

## Syntax Check
Alle 3 geänderten/neuen Files kompilieren erfolgreich:
- ✅ `scripts/panel_generator.py`
- ✅ `scripts/story_planner.py`
- ✅ `scripts/face_validator.py`

## Nicht geändert
- `workflows/panel_ipadapter.json` — wird programmatisch generiert, kein Änderungsbedarf
- `workflows/panel_ipadapter_multi.json` — wird programmatisch generiert, kein Änderungsbedarf
- `workflows/character_ref.json` — Original bleibt als Fallback, neues `character_ref_multi.json` hinzugefügt
