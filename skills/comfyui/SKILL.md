---
name: comfyui
description: Generate images with ComfyUI running on Windows. Use when asked to create, generate, or render images, artwork, photos, illustrations, or any visual content. Requires ComfyUI running on Windows with --listen 0.0.0.0.
---

# ComfyUI Skill

Generate images via the ComfyUI API running on Windows, accessible from WSL2.

## Prerequisites

1. **ComfyUI** running on Windows with `--listen 0.0.0.0`
2. Accessible via `host.docker.internal:8188` from WSL2

## Quick Check

```bash
python3 skills/comfyui/scripts/comfy_client.py status
```

## Generate Images

### Simple generation (uses dreamshaperXL Turbo preset by default)
```bash
python3 skills/comfyui/scripts/generate.py "a robot sentinel guarding a castle at sunset"
```

### With specific preset
```bash
python3 skills/comfyui/scripts/generate.py "prompt" -m juggernautXL
python3 skills/comfyui/scripts/generate.py "prompt" -m flux
python3 skills/comfyui/scripts/generate.py "prompt" -m flux2
python3 skills/comfyui/scripts/generate.py "prompt" -m cyberrealistic
python3 skills/comfyui/scripts/generate.py "prompt" -m architecture
```

### Full control
```bash
python3 skills/comfyui/scripts/generate.py "prompt" \
    -m dreamshaperXL \
    -W 1024 -H 768 \
    -s 12 -c 2.5 \
    --seed 42 \
    -o /path/to/output
```

### List presets
```bash
python3 skills/comfyui/scripts/generate.py "" --list-presets
```

## Available Presets

| Preset | Model | Type | Resolution | Steps | Speed |
|--------|-------|------|-----------|-------|-------|
| `dreamshaperXL` | DreamShaper XL Turbo | SDXL | 1024x1024 | 8 | ⚡ Fast |
| `juggernautXL` | Juggernaut XL Lightning | SDXL | 1024x1024 | 6 | ⚡ Fast |
| `cyberrealisticXL` | CyberRealistic XL | SDXL | 1024x1024 | 25 | Normal |
| `zavychroma` | ZavyChroma XL | SDXL | 1024x1024 | 25 | Normal |
| `sdxl` | SD XL Base | SDXL | 1024x1024 | 25 | Normal |
| `flux` | Flux.1 Dev FP8 | Flux | 1024x1024 | 20 | 🎨 Hochwertig |
| `fluxFast` | Flux.1 Dev Small | Flux | 1024x1024 | 20 | ⚡ Schneller |
| `flux2` | Flux 2 Dev FP8 Mixed | Flux | 1024x1024 | 20 | 🆕 Neueste |
| `cyberrealistic` | CyberRealistic v6 | SD1.5 | 512x512 | 30 | Normal |
| `dreamshaper` | DreamShaper 8 | SD1.5 | 512x512 | 30 | Normal |
| `realisticVision` | Realistic Vision 6 | SD1.5 | 512x768 | 30 | Normal |
| `architecture` | Architecture RealMix | SD1.5 | 512x512 | 30 | 🏠 Architektur |

## Model Selection Guide

- **Best Quality:** `flux`, `flux2` (Flux-Architektur, beste Prompt-Adherence)
- **Photorealism:** `juggernautXL`, `cyberrealisticXL`, `cyberrealistic`
- **Creative/Artistic:** `dreamshaperXL`, `zavychroma`
- **Architecture:** `architecture`
- **Speed priority:** `dreamshaperXL` (8 steps), `juggernautXL` (6 steps)
- **Flux (schneller):** `fluxFast` (weniger VRAM)

## Custom Workflows

Place workflow JSON files in `skills/comfyui/workflows/` and run:
```bash
python3 skills/comfyui/scripts/comfy_client.py generate workflows/my_workflow.json
```

## Output

Generated images are saved to `/home/mcmuff/clawd/output/comfyui/` by default.

## Workflow

1. Check if ComfyUI is running: `comfy_client.py status`
2. If not reachable, ask user to start ComfyUI with `--listen 0.0.0.0`
3. Generate image with appropriate preset for the request
4. Show the generated image to the user using the `image` tool

## Scripts

| Script | Purpose |
|--------|---------|
| `comfy_client.py` | Low-level API client (status, queue, generate from JSON) |
| `generate.py` | High-level generator with presets and CLI args |
