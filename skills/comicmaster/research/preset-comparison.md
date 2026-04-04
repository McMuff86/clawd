# ComicMaster Preset Comparison Report

**Date:** 2025-02-09  
**Comic:** Steel & Sawdust  
**Panels compared:** 10 (panels 1–10)  
**GPU:** NVIDIA RTX 3090 (24GB VRAM)  
**Pipeline:** ComicMaster v1 with IPAdapter + LoRA (xl_more_art-full)

---

## Presets Tested

| Preset | Model | Steps | CFG | Sampler | Speed Class |
|--------|-------|-------|-----|---------|-------------|
| **dreamshaperXL** | dreamshaperXL_turboDPMSDE | 8 | 2.0 | dpmpp_sde / karras | Turbo |
| **juggernautXL** | juggernautXL_v9Rdphoto2Lightning | 6 | 2.0 | dpmpp_sde / karras | Lightning |
| **illustriousXL** | ❌ NOT INSTALLED | 28 | 5.5 | euler_ancestral | Standard |

### Illustrious XL Status
Model `Illustrious-XL-v0.1.safetensors` is **not yet downloaded** on the ComfyUI host.
- **Download from:** [CivitAI – Illustrious XL v0.1](https://civitai.com/models/795765/illustrious-xl) 
- **Also consider:** NoobAI-XL V-Pred (`NoobAI-XL-Vpred-v1.0.safetensors`) — fine-tuned Illustrious with v-prediction
- **File size:** ~6.5 GB each
- **Note:** Both use Danbooru-tag prompting (handled by pipeline's `build_illustrious_prompt()`)

---

## Quality Scores (Best Variant per Panel)

### Head-to-Head: Panels 1–10

| Panel | DreamshaperXL | JuggernautXL | Winner | Delta |
|-------|--------------|--------------|--------|-------|
| 01 – Workshop exterior | 53.8 | **58.9** | JG | +5.1 |
| 02 – Marco at CNC | 48.1 | **49.0** | JG | +0.9 |
| 03 – Marco at screen | 51.6 | **54.6** | JG | +3.0 |
| 04 – Elena arrives | 47.6 | **49.7** | JG | +2.1 |
| 05 – Marco meets Elena | 48.2 | **53.5** | JG | +5.3 |
| 06 – NOVA reveal | **51.2** | 46.4 | DS | +4.8 |
| 07 – NOVA in workshop | **51.4** | 45.8 | DS | +5.6 |
| 08 – NOVA + Marco + Elena | **52.5** | 51.8 | DS | +0.7 |
| 09 – NOVA at work | **48.1** | 46.9 | DS | +1.2 |
| 10 – Workshop interaction | 46.6 | **52.8** | JG | +6.2 |

**Score: DreamshaperXL 4 – JuggernautXL 6**

### Averages (Best variant per panel, panels 1–10)

| Metric | DreamshaperXL | JuggernautXL | Δ |
|--------|--------------|--------------|---|
| **Overall Score** | 49.9 | **50.9** | +1.0 |
| **Technical Score** | 48.2 | 48.1 | −0.1 |
| **Composition Score** | 51.9 | **54.4** | +2.5 |
| **Sharpness** | **436** | 380 | −56 |

### Full-Run Statistics

| Metric | DS (73 panels, 32 scenes) | JG (22 panels, 10 scenes) |
|--------|--------------------------|--------------------------|
| Mean Overall | 50.0 | 48.9 |
| Min / Max | 43.5 / 55.9 | 42.3 / 58.9 |
| Std Dev | 2.6 | 4.0 |
| Mean Sharpness | 501.4 | 387.6 |
| Mean Contrast | 63.7 | 64.9 |
| Mean Saturation | 0.214 | 0.215 |
| Mean Color Entropy | 9.08 | 8.94 |
| Mean Edge Density | 0.085 | 0.060 |
| Mean Exposure Balance | 0.703 | 0.705 |
| Mean Composition | 52.0 | 52.7 |
| Mean Harmony | 0.941 | 0.877 |
| Mean Rule of Thirds | 0.570 | 0.598 |
| Color Temp | −0.011 (neutral) | 0.085 (slightly warm) |

### Sequence Analysis

| Metric | DreamshaperXL | JuggernautXL |
|--------|--------------|--------------|
| Sequence Score | **44.4** | 39.2 |
| Flow Continuity | **0.294** | 0.067 |
| Temp Consistency | **0.765** | 0.649 |
| Shot Variety | 0.291 | **0.317** |
| Pacing | 0.521 | **0.600** |

---

## Speed Comparison

### Generation Times

| Phase | DreamshaperXL | JuggernautXL |
|-------|--------------|--------------|
| Model loading (cold start) | ~15s | ~17s |
| Character refs (3 chars) | ~60s | ~68s |
| Panel gen (avg per panel) | ~14s | ~14s |
| **Total (10 panels + refs)** | ~200s | **208s** |
| **Total (32 panels + refs)** | 9.6 min (~576s) | *est. ~7.5 min* |

Both presets use similar step counts (8 vs 6) and are comparably fast. The Lightning model's 6 steps vs Turbo's 8 steps roughly cancel out due to model loading differences.

### Per-Panel Timing Breakdown (JuggernautXL)

| Panel Type | Avg Gen Time | Notes |
|-----------|-------------|-------|
| No IPAdapter | 4.0s | Fastest — landscape/establishing shots |
| Single IPAdapter | 4–9s | Includes face validation retries |
| Multi IPAdapter | 10–15s | Highest — 2+ characters in scene |

---

## Qualitative Observations

### DreamshaperXL Strengths
- **Higher sharpness** (436 vs 380 avg) — more detail in textures, machinery
- **Better color harmony** (0.941 vs 0.877) — more cohesive palettes
- **Better sequence continuity** (0.294 vs 0.067 flow) — more consistent visual style panel-to-panel
- **Temperature consistency** (0.765 vs 0.649) — less color drift between panels
- **Higher edge density** (0.085 vs 0.060) — more defined edges and linework
- **Stronger on robot/mechanical subjects** — panels 6-9 (NOVA scenes) all won

### JuggernautXL Strengths
- **Better composition** (54.4 vs 51.9 avg) — better use of thirds, more dynamic framing
- **Higher peaks** (58.9 max vs 55.9 max) — best individual panels score higher
- **Better pacing** (0.600 vs 0.521) — more visual rhythm variation
- **More shot variety** (0.317 vs 0.291) — more diverse camera angles
- **Stronger on human subjects** — panels 1-5 (human-focused) all won
- **Slightly warmer** (0.085 vs −0.011 temp) — photorealistic warmth suits human scenes

### Both Presets
- Face validation fails constantly with PIL histogram backend (expected)
- NOVA (robot) always fails face validation — needs special handling
- Dead center composition on all panels — quality tracker flags this
- All panels in ⚠️ range (42–59) — no panel reaches "Good" (60+)

---

## Panel-by-Panel Analysis

### Where JuggernautXL excels (human/environment scenes):
- **Panel 01** (Workshop exterior): JG 58.9 vs DS 53.8 — photorealistic landscapes are JG's sweet spot
- **Panel 05** (Marco meets Elena): JG 53.5 vs DS 48.2 — human interaction, better skin tones
- **Panel 10** (Workshop interaction): JG 52.8 vs DS 46.6 — biggest single-panel advantage

### Where DreamshaperXL excels (robot/tech scenes):
- **Panel 07** (NOVA in workshop): DS 51.4 vs JG 45.8 — better at rendering metallic/sci-fi subjects
- **Panel 06** (NOVA reveal): DS 51.2 vs JG 46.4 — robot character consistency

---

## Recommendations

### For This Comic ("Steel & Sawdust")
Use **DreamshaperXL** as the primary preset:
1. Better sequence continuity is critical for comics
2. The robot character (NOVA) appears in 20+ panels — DS handles this better
3. Higher sharpness matters for comic panel detail
4. More consistent color temperature = more professional look

### For Future Comics
Consider a **hybrid approach**:
- Use **JuggernautXL** for human-only establishing shots and character introductions
- Use **DreamshaperXL** for action sequences, tech/sci-fi, and panels with mixed human+robot characters
- Pipeline could support per-panel preset override in story_plan.json

### For Illustrious XL (When Installed)
Expected advantages over both:
- **Danbooru-tag prompting** is more precise for character attributes
- **28 steps** at cfg=5.5 should produce higher detail than both Turbo/Lightning presets
- **Anime/illustration style** could be great for comics (less photorealistic, more stylized)
- **Trade-off:** ~4x slower per panel (28 steps vs 6-8 steps)
- **Best for:** Manga-style comics, character-driven stories, stylized art

### Quality Improvement Priorities
1. **Install proper face validation** (insightface or face_recognition) — PIL histogram gives ~0.4-0.6 similarity even on good matches
2. **Improve composition** — all panels score "dead center"; add composition-aware prompting
3. **Consider post-processing** — color grading pipeline already exists, could boost harmony scores
4. **Install Illustrious XL** for true 3-way comparison

---

## Files

| Run | Output Directory |
|-----|-----------------|
| DreamshaperXL (32 panels) | `~/clawd/output/comicmaster/steel_&_sawdust/` |
| JuggernautXL (10 panels) | `~/clawd/output/comicmaster/steel_sawdust_juggernaut/` |
| Quality scores (DS) | `…/steel_&_sawdust/panels/quality_scores.json` |
| Quality scores (JG) | `…/steel_sawdust_juggernaut/panels/quality_scores.json` |

---

*Report generated by ComicMaster Quality Tracker comparison pipeline*
