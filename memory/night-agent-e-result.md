# Night Agent E — Color Storytelling + SFX Integration
**Date:** 2026-02-09  
**Status:** ✅ All 6 tasks completed, all tests pass, backward-compatible

---

## Changes Summary

### 1. Scene-based Color Palettes (`color_grading.py`) ✅
- Added `MOOD_PALETTES` dict: 11 moods mapped to full color palettes (tense, calm, mysterious, cheerful, noir, dark, hopeful, dramatic, neutral, happy, sad)
- `get_auto_palette(mood)` — auto-generates palette from mood if no explicit scene palette defined
- `apply_scene_palette(image, palette)` — applies palette via color temp shift + primary color tint + saturation/contrast adjustment
- `interpolate_palettes(pal_a, pal_b, t)` — linear interpolation for smooth scene transitions
- `grade_panels_with_scenes(...)` — batch grading with scene awareness, automatic 2-panel transition blending when scenes change
- `grade_panel_for_pipeline(...)` — single-panel convenience function for pipeline integration
- Scene palette schema: `{"primary": "#hex", "secondary": "#hex", "accent": "#hex", "mood_tone": "warm|cool|neutral"}`
- Panels reference scenes via `panel.scene_id`; fallback to mood-based auto-palette

### 2. Color Temperature Shifting (`color_grading.py` + `story_planner.py`) ✅
- `compute_temp_sequence(num_panels, start_temp, end_temp)` — generates smoothstep-eased temperature curve for action arcs
- New panel field: `color_temp_override` (float -1.0 to 1.0, maps to ±30 shift)
- `_enrich_color_temperature()` in story_planner.py — auto-detects action sequences (moods: tense, dramatic, dark) and applies warm→cool shift (0.6 → -0.6) across consecutive action panels using smoothstep interpolation
- Non-action panels left untouched

### 3. Focal Point Color Boost (`color_grading.py`) ✅
- `apply_focal_boost(image, strength=0.15, center=(0.5, 0.45))` 
- Center-weighted saturation mask: +boost at focal point, slight desaturation at edges
- Also applies subtle contrast boost at center
- Configurable: `focal_boost: 0.0–0.5` (default 0.15)
- Applied automatically in `grade_panels_with_scenes` and `grade_panel_for_pipeline`

### 4. SFX Perspective Matching (`speech_bubbles.py`) ✅
- Four perspective modes: `flat` (legacy), `radial`, `curved`, `impact`
- `_render_sfx_flat()` — classic centered text (unchanged behavior)
- `_render_sfx_radial()` — characters radiate from impact point along arc (for explosions: CRASH, ZAP, SPLASH)
- `_render_sfx_curved()` — text follows sweeping Bézier arc (for movement: WHOOSH, SWOOSH, SWISH)
- `_render_sfx_impact()` — characters grow larger away from center, shockwave effect (for BOOM, BANG, KABOOM)
- Auto-detection: `_auto_detect_sfx_style(text)` — maps 30+ SFX keywords to appropriate styles
- Story plan field: `dialogue[].sfx_style: "flat"|"radial"|"curved"|"impact"`
- `_enrich_sfx_styles()` in story_planner.py auto-enriches SFX dialogue entries

### 5. Art-Integrated SFX (`speech_bubbles.py`) ✅
- **Semi-transparency:** SFX rendered at alpha 0.85 (not opaque floating text)
- **Drop shadow:** Automatic offset shadow (40% opacity, Gaussian-blurred, down-right offset simulating upper-left light)
- **Color matching:** `_get_sfx_color(bubble, scene_mood_tone)` — complementary color selection:
  - Cool/blue scene → Orange SFX
  - Warm scene → Cyan SFX
  - Dark scene → Gold SFX
  - Explicit text_color always takes priority
- **Partial occlusion:** Bottom 20% of SFX text fades progressively (60% reduction at bottom edge), simulating ground-level occlusion
- **Narrative weight scaling:** `_SFX_WEIGHT_SCALE` — low: 0.6×, medium: 1.0×, high: 1.5×, splash: 2.2× font size
- `scene_mood_tone` field auto-enriched by story planner based on panel mood

### 6. Color Holds (`color_grading.py`) ✅
- `apply_color_holds(image, hold_color, threshold=40, edge_width=0)` 
- Replaces near-black pixels (<40 brightness) in border region with scene's primary color
- Fade gradient: stronger at image edge, fading toward interior (max 85% replacement)
- Auto edge width: 8% of shorter image dimension
- Activated via panel field: `panel.color_holds: true`
- Automatically uses scene palette's primary color

---

## Files Modified
| File | Lines Before | Lines After | Changes |
|------|-------------|-------------|---------|
| `scripts/color_grading.py` | 317 | ~530 | +MOOD_PALETTES, +apply_scene_palette, +interpolate_palettes, +grade_panels_with_scenes, +compute_temp_sequence, +apply_focal_boost, +apply_color_holds, +grade_panel_for_pipeline, +CLI flags |
| `scripts/speech_bubbles.py` | 1558 | ~1780 | +SFX perspectives (radial/curved/impact), +art integration (shadow/transparency/occlusion/color-match), +auto-detect, +weight scaling |
| `scripts/story_planner.py` | 1152 | ~1240 | +_enrich_color_temperature, +_enrich_sfx_styles |

## Backward Compatibility
- ✅ All existing functions retain their signatures and behavior
- ✅ New parameters use sensible defaults (no breakage if not provided)
- ✅ Old-style SFX calls (`text_color="#CC0000"`, no sfx_style) still work identically
- ✅ `apply_color_grade()` / `grade_all_panels()` unchanged
- ✅ Story plans without `scenes`, `scene_id`, `color_temp_override`, `sfx_style` etc. work fine

## Tests Run
- Python syntax validation: ✅ all 3 files
- Import tests: ✅ all new functions importable
- Unit tests: ✅ mood palettes, temp sequences, interpolation, hex utils, SFX detection, SFX colors
- Visual rendering: ✅ all 4 SFX styles, scene palette, focal boost, color holds
- Backward compat: ✅ old-style calls work unchanged
- Story planner enrichment: ✅ auto color_temp_override on action sequences, auto sfx_style on SFX dialogue
