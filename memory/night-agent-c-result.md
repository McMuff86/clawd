# Night Factory – Agent C Result: Prompt Engineering

**Datum:** 2026-02-09  
**Agent:** C (Prompt Engineering)  
**Status:** ✅ Alle 5 Aufgaben abgeschlossen

---

## Aufgabe 1: Anti-Centering System ✅

### Änderungen:
- **`panel_generator.py`**: NEGATIVE_PROMPT aktualisiert mit vollständigen Anti-Centering Terms: "centered composition, symmetrical framing, passport photo, static pose, fashion photography, straight-on camera, centered subject"
- **`panel_generator.py`**: Neues `ANTI_CENTERING_POSITIVE` Constant: "dynamic composition, off-center framing, rule of thirds"
- **`panel_generator.py`**: `_get_sequential_composition_tags()` erweitert – respektiert `composition_override`:
  - `"symmetric"` → Erzwingt "balanced symmetrical composition, centered framing, deliberate symmetry"
  - `"dynamic"` → Erzwingt Off-Center auch wenn Heuristik Centering erlauben würde
  - `None` → Automatische Heuristik (wie vorher, aber mit stärkeren Tags)
- **`panel_generator.py`**: `get_negative_prompt_for_preset()` akzeptiert jetzt optionalen `panel` Parameter:
  - Bei `composition_override == "symmetric"` werden Anti-Centering Terms aus dem Negative Prompt entfernt
  - Illustrious/NoobAI Presets bekommen Anti-Centering auch im Negative Prompt (vorher fehlte es dort)
- **`story_planner.py`**: Neues Feld `composition_override` in Validation (akzeptiert "symmetric", "dynamic", null)
- **`story_planner.py`**: Default `composition_override: None` wird bei Enrichment gesetzt

### Exception-Logik:
- `camera_angle == "eye_level"` + `composition_override == "symmetric"` → Anti-Centering wird komplett übersprungen (Positive UND Negative)

---

## Aufgabe 2: Biomechanische Pose-Beschreibungen ✅

### Neue Datei: `references/pose-library.md`
- 30 detaillierte Pose-Beschreibungen in Kategorien:
  - **Action:** Running, Fighting (Punch/Kick/Block), Jumping, Falling, Sneaking, Climbing, Crawling, Dodging
  - **Stance:** Standing Confident/Casual/Alert/Menacing
  - **Seated:** Sitting Thoughtful/Casual/Defeated
  - **Movement:** Walking Casual/Determined/Injured
  - **Communication:** Talking Animated, Shouting, Whispering
  - **Emotional:** Looking Up in Awe, Exhausted, Celebrating, Shocked, Grieving, Surrendering
  - **Interaction:** Helping Someone Up, Pointing, Holding/Carrying

### Änderungen in `story_planner.py`:
- Neues `POSE_LIBRARY` Dictionary mit allen 30 Poses + Keywords für Fuzzy Matching
- Neue Funktion `_match_pose_from_action(action_text)`: Scannt Action-Text nach Keywords, gibt beste Pose zurück
- In `enrich_story_plan()`: Auto-Enrichment von `character_poses` falls leer – matched Action gegen Pose Library

### Fuzzy Matching Beispiele:
- "Hero runs across rooftop" → Running pose ✅
- "Hero jumps to next building" → Jumping pose ✅
- "Hero sneaks along wall" → Sneaking pose ✅
- "Hero sits thinking" → Sitting thoughtful pose ✅

---

## Aufgabe 3: Environment-Interaction Prompts ✅

### Änderungen in `panel_generator.py`:
- Neues `ENVIRONMENT_INTERACTION_MAP` Dictionary: 50+ Scene-Keywords → Interaction-Hints
  - Indoor: room, office, bedroom, kitchen, hallway, bar, hospital, prison, church, library, warehouse
  - Elevated: rooftop, balcony, tower
  - Urban: street, alley, city, market, park, bridge, subway, train
  - Lab/Tech: lab, tech, computer, server, cockpit
  - Nature: forest, mountain, desert, beach, ocean, river, cave, jungle, field, garden
  - Vehicles: car, motorcycle, spaceship
  - Danger: battlefield, ruins, fire, rain, snow, storm
- Neue Funktion `_get_environment_interaction(scene, action, shot_type)`:
  - Deterministischer Selection basierend auf Hash (reproduzierbare Ergebnisse)
  - Gibt `None` zurück für `extreme_close` Shots (kein Environment sichtbar)
  - Matcht Scene-Keywords gegen Dictionary, wählt passenden Hint
- Integriert in `build_panel_prompt()` (Standard SDXL) UND `build_illustrious_prompt()` (Danbooru-Tags)

---

## Aufgabe 4: Lighting als Storytelling-Tool ✅

### Neue Sektion in `references/style-guides.md`:
- Komplette "Lighting as Storytelling Tool" Dokumentation
- Mood → Lighting Directive Tabelle
- Lighting Consistency Rules (5 Regeln)
- Lighting + Shot Type Interaction Guide

### Änderungen in `panel_generator.py`:
- Neues `MOOD_LIGHTING_DIRECTIVES` Dictionary: 14 Moods → Lighting Directives
- Neue Funktion `_get_mood_lighting_directive(mood)`:
  - Direkte und Fuzzy-Matching (Substring) Suche
  - Gibt `None` für neutral/unbekannte Moods
- In `build_panel_prompt()`: Mood-Lighting wird VOR explizitem Lighting injiziert (beide können koexistieren)
- In `build_illustrious_prompt()`: Gleiche Logik, mit Tag-Konvertierung

### Lighting Consistency:
- Gleiche Szene → `spatial_relation: same_location` → Sequential Composition Tags erzwingen "consistent background elements"
- Mood-Lighting + explizites Lighting = komplementäre Effekte (z.B. "tense" mood lighting + "moonlight" = dramatische Nachtszene)

---

## Aufgabe 5: Sequential Storytelling Prompt Boost ✅

### Änderungen in `panel_generator.py`:
- JEDES Panel bekommt: `"sequential comic book art, storytelling panel, narrative composition"` (statt generischem "comic book style")
- **Dialogue-Panels** zusätzlich: `"comic dialogue scene, expressive character interaction"`
- **Action-Panels** zusätzlich: `"dynamic comic action, motion lines, impact frame"`
- Action-Detection via Keyword-Scan in `action` und `mood` Feldern
- Implementiert für BEIDE Prompt-Paths: Standard SDXL + Illustrious/NoobAI

---

## Technische Details

### Files geändert:
1. `scripts/panel_generator.py` – Anti-Centering, Environment Interaction, Mood Lighting, Sequential Storytelling
2. `scripts/story_planner.py` – Pose Library, composition_override Validation, Pose Auto-Enrichment
3. `references/style-guides.md` – Lighting Storytelling Sektion
4. `references/pose-library.md` – **NEU** – 30 Biomechanische Pose-Beschreibungen

### Syntax-Check: ✅ Beide Python-Files kompilieren fehlerfrei
### Funktionstest: ✅ story_planner.py CLI-Test läuft durch, Enrichment funktioniert
### Prompt-Test: ✅ Alle Features in generierten Prompts sichtbar (Standard + Illustrious)

### Keine Breaking Changes:
- Alle neuen Features sind additiv
- Bestehende Prompt-Bau-Logik wurde erweitert, nicht gebrochen
- Neue Story-Plan Felder sind optional (defaults zu None/auto)
- `get_negative_prompt_for_preset()` ist backward-compatible (panel parameter ist optional)
