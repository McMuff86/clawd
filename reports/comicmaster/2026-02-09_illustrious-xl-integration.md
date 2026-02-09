# Illustrious XL Integration

**Datum:** 2026-02-09
**Agent:** night-agent-c-illustrious
**Projekt:** ComicMaster
**Dauer:** 5m 22s

## Zusammenfassung
Illustrious XL und NoobAI-XL als alternative Modelle in den ComicMaster Skill integriert. Neue Presets, Danbooru-Tag Prompt Builder, eigener Workflow mit clip_skip und v_prediction Support.

## Neue Dateien

### `references/illustrious-xl-guide.md`
Komplett-Guide mit:
- Download-Links (HuggingFace + CivitAI)
- Exakte Dateinamen: `Illustrious-XL-v0.1.safetensors`, `NoobAI-XL-Vpred-v1.0.safetensors`
- Empfohlene Settings aus Community:
  - **Illustrious XL:** euler_ancestral, 28 Steps, CFG 5.5, clip_skip 2
  - **NoobAI-XL:** euler, 28 Steps, CFG 5.0, v_prediction
- Danbooru-Tag Mapping-Tabellen (Shot Types, Angles, Emotions, Lighting)
- Negative Prompt Templates
- "When to use which" Vergleichstabelle

### `workflows/panel_illustrious.json`
Standard SDXL-Workflow angepasst für Illustrious:
- CLIPSetLastLayer (clip_skip=2)
- 1024×1024 (statt 768×768)
- Illustrious-spezifische Negative Prompts
- Beispiel-Danbooru-Tags

## Änderungen

### `presets.json` — 2 neue Presets
```json
"illustriousXL": {
  "model": "Illustrious-XL-v0.1.safetensors",
  "steps": 28, "cfg": 5.5,
  "sampler": "euler_ancestral", "scheduler": "normal",
  "clip_skip": 2, "prompt_style": "danbooru"
}
"noobaiXL": {
  "model": "NoobAI-XL-Vpred-v1.0.safetensors",
  "steps": 28, "cfg": 5.0,
  "sampler": "euler", "scheduler": "normal",
  "v_prediction": true, "prompt_style": "danbooru"
}
```

### `panel_generator.py` — Neue Funktionen (backward-compatible)
- **`build_illustrious_prompt()`** — Konvertiert Panel-Daten zu Danbooru-Tag-Format
- **`_convert_description_to_tags()`** — Hilfsfunktion Natural Language → Tags
- **`get_negative_prompt_for_preset()`** — Modell-spezifische Negative Prompts
- **`ILLUSTRIOUS_NEGATIVE_PROMPT`** + **`NOOBAI_NEGATIVE_PROMPT`** Konstanten
- Tag-Mappings für: Shot Types, Angles, Styles, Emotions, Lighting
- `build_panel_prompt()` delegiert automatisch bei `preset_name in ILLUSTRIOUS_PRESETS`
- `build_sdxl_workflow()` unterstützt `clip_skip` (CLIPSetLastLayer Node) und `v_prediction` (ModelSamplingDiscrete Node)

### `SKILL.md` aktualisiert
- Presets-Tabelle mit Illustrious XL + NoobAI-XL
- "Illustrious XL / NoobAI-XL Notes" Section
- Empfehlungstabelle wann welches Modell nutzen
- Workflow-Tabelle mit `panel_illustrious.json`

## Tests
- Python-Syntax validiert ✅
- Keine Breaking Changes (bestehende Presets/Workflows unverändert)
- `build_panel_prompt()` mit optionalem `preset_name` Parameter — ohne Argument identisches Verhalten

## Offene Punkte
- **Live-Test mit ComfyUI** steht noch aus (Modell muss erst heruntergeladen werden)
- NoobAI-XL v_prediction Workflow nicht separat als JSON exportiert
- LoRA-Kompatibilität mit Illustrious noch nicht getestet
