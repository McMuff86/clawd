# Sequential Composition Rules

**Datum:** 2026-02-09
**Agent:** night-agent-b-composition
**Projekt:** ComicMaster
**Dauer:** 4m 54s

## Zusammenfassung
Sequentielle Kompositionsregeln in `story_planner.py` und `panel_generator.py` implementiert. 5 neue Panel-Felder, Auto-Enrichment, Shot Progression Validator und 17 Composition Templates sorgen dafür, dass Panels wie echte Comic-Sequenzen wirken statt wie Portfolio-Bilder.

## Änderungen in story_planner.py

### Neue Konstanten
- `VALID_GAZE_DIRECTIONS`: `{left, right, center, up, down}`
- `VALID_SUBJECT_POSITIONS`: `{left_third, center, right_third}`
- `VALID_SPATIAL_RELATIONS`: `{same_location, cut_to, time_skip, flashback, parallel}`
- `VALID_FOCAL_POINTS`: `{upper_left, upper_right, lower_left, lower_right, center}`
- `ESTABLISHING_SHOTS`: Shot-Types die als Scene-Opener gelten

### Validation
Validiert alle 5 neuen optionalen Panel-Felder gegen erlaubte Werte. Cross-validiert `connects_to` Referenzen.

### Auto-Enrichment
`_enrich_sequential_fields()` füllt fehlende Felder automatisch:
- **gaze_direction:** Speaker-Hash für Dialogue, Sequenz-Alternation sonst
- **subject_position:** Alterniert links/rechts; Splash-Panels bekommen Center
- **connects_to:** Automatisch nächstes Panel in Sequenz
- **spatial_relation:** Erkennt `same_location` via Scene-Text-Overlap
- **focal_point:** Abgeleitet aus subject_position + gaze_direction

`_enrich_dialogue_positions()` setzt `position_hint` basierend auf Leserichtung (top_left → top_right → bottom_left → bottom_right).

### Shot Progression Validator
`validate_shot_progression()` mit 3 Checks + Auto-Fix:
1. Warnung bei >3 aufeinanderfolgenden identischen Shot-Types
2. Warnung wenn neue Szene nicht mit Establishing Shot beginnt
3. Warnung wenn Dialogue-Sprecherwechsel gleichen Shot-Type nutzt

Alle Warnungen in `plan["_enrichment_warnings"]`.

## Änderungen in panel_generator.py

### COMPOSITION_TEMPLATES (17 Templates)
Vorgefertigte Composition-Strings für:
- Dialogue (speaker_a, speaker_b)
- Scene Openers (establishing, establishing_dramatic)
- Reactions (reaction, reaction_wide)
- Action (action_peak, action_buildup, action_aftermath)
- Transitions (transition, time_skip, flashback)
- Drama (reveal, confrontation, climax, climax_splash)
- Quiet (contemplation, parallel)

### Lookup-Dicts
`FOCAL_POINT_TAGS`, `SUBJECT_POSITION_TAGS`, `GAZE_DIRECTION_TAGS`

### Neugeschriebenes `_get_sequential_composition_tags()`
11 Kompositionsregeln:
1. **Scene Opening Rules** — Establishing/Flashback/Time-Skip Templates
2. **Anti-Centering mit Kontext** — Off-Center Default; zentriert NUR für Splash, Konfrontation, Two-Speaker Dialogue
3. **Focal Point** — Nutzt `focal_point` aus Story Plan
4. **Gaze Direction** — Nutzt Plan oder fällt auf Alternation zurück
5. **Eyeline Matching** — Vorheriges Panel beeinflusst aktuelles Subject-Placement
6. **Dialogue Templates** — Speaker A/B basierend auf Character-Hash
7. **Action-Reaction Choreografie** — Post-Action Panels bekommen Reaction-Komposition
8. **Spatial Continuity** — `same_location` fügt Environment-Konsistenz-Tags hinzu
9. **Climax Build-up** — high → dramatisch, splash → volle Splash-Behandlung
10. **Shot Progression Hints** — Kontextuelle Tags für wide→tight oder close→wide
11. **Reveal Detection** — Panels mit "reveal" in Action bekommen Reveal-Komposition

## Tests
- **109/109 Tests bestanden** in `test_composition.py`
- Deckt ab: Validation, Backward Compatibility, Auto-Enrichment, Shot Progression, Dialogue Order, alle Template-Types, Anti-Centering, Eyeline Matching, Full Pipeline

## Offene Punkte
- story_planner Enrichment noch nicht automatisch in comic_pipeline.py integriert (manueller Aufruf nötig)
