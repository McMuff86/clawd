# Quality Tracker Phase 1

**Datum:** 2026-02-09
**Agent:** night-agent-d-quality
**Projekt:** ComicMaster
**Dauer:** 7m 25s

## Zusammenfassung
Quality Tracker erweitert mit 7 neuen Metriken (Komposition + Kolorimetrie), Panel-Sequenz-Analyse und Composition Score. Alles PIL/numpy-only, keine externen Dependencies.

## Neue Kompositions-Metriken (4)

### Center Bias Score
- Berechnet "Center of Visual Mass" via helligkeitsgewichteten Centroid
- Score 0 = dead center (schlecht), 1 = off-center (gut)
- Flaggt Panels < 0.2 als "dead center composition"

### Rule of Thirds
- Teilt Bild in 3×3 Grid, misst Zonen-Varianz + Hotspot-Alignment an Schnittpunkten
- Handhabt uniforme Bilder korrekt (Score 0)

### Visual Flow Direction
- Sobel-Gradienten-Analyse für dominante Flussrichtung
- Output: Winkel in Grad + human-readable Label
- Nützlich für Panel-zu-Panel Flow-Analyse

### Quadrant Balance
- Kombiniertes visuelles Gewicht (Helligkeit + Kontrast + Edge Density) pro Quadrant
- Score 0 = uniform, 1 = alles in einem Quadranten
- Gute Comics: 0.3–0.7

## Neue Kolorimetrie-Metriken (3)

### Color Temperature
- Warm/Cool Bias via Red vs Blue Channel Vergleich
- Returns -1.0 (cool) bis 1.0 (warm) + Label

### Palette Size
- Custom K-Means Implementation (kein sklearn, ~25 Zeilen)
- Clustert downgesampeltes Bild in k=8, zählt Cluster >5% der Pixel
- Reportet dominante Farben als RGB

### Color Harmony
- Prüft dominante Hues auf Farbrad-Harmonie:
  - Complementary (~180°)
  - Analogous (~60° Span)
  - Triadic (~120°)
  - Split-Complementary (~150°)

## Panel-Sequenz-Analyse (neu)
`analyze_sequence()` analysiert geordnete Panel-Listen:
- **Flow Continuity:** Stimmt der Flow-Vektor mit LTR-Leserichtung überein?
- **Color Temperature Consistency:** Flaggt Outlier-Panels (>2σ vom Mean)
- **Shot Variety:** Diversität von Edge Density, Contrast, Saturation
- **Pacing:** Vorzeichenwechsel-Frequenz in Edge Density (Alternation = guter Rhythmus)
- Combined Sequence Score (0–100)

## Scoring System
- **Composition Score** (0–100): Gewichtetes Composite aus Center Bias, Thirds, Balance, Harmony, Palette Richness
- **Overall Score:** 55% Technical + 45% Composition (wenn `--composition` aktiviert)
- Labels: **good** (≥65), **ok** (≥40), **poor** (<40)

## CLI-Erweiterungen
- `--composition` — Aktiviert Kompositions- + Kolorimetrie-Metriken
- `--sequence` — Aktiviert Panel-Sequenz-Analyse (erwartet Directory)
- `--report` — Detaillierter Text-Report mit Per-Panel Breakdown

## Tests
- **96/96 Tests bestanden** in `test_quality_tracker.py`
- Generiert Test-Bilder mit PIL (Gradienten, Kreise, Farbblöcke)
- Testet jede Metrik einzeln + Integration für score_panel, score_batch, analyze_sequence

## Offene Punkte
- CLIP-basierte Metriken (Phase 2) noch nicht implementiert
- Face Consistency Check braucht InsightFace (Phase 3)
- Benchmark auf echten Comic-Panels steht aus
