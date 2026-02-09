# ComfyUI – Empfohlene Downloads & Workflows

Recherche vom 01.02.2026. Sortiert nach Priorität.

---

## ⚡ Schnelle Modelle (1-8 Steps)

### 1. Hyper-SDXL LoRA ⭐ (Top-Empfehlung)
- **Was:** LoRA die jedes SDXL-Modell auf 1-4 Steps beschleunigt
- **Download:** https://huggingface.co/ByteDance/Hyper-SD
- **Files:** `Hyper-SDXL-1step-lora.safetensors` (1 Step) / `Hyper-SDXL-4steps-lora.safetensors` (4 Steps, besser)
- **Wohin:** `ComfyUI/models/loras/`
- **Warum:** Macht ALLE deine bestehenden SDXL-Modelle schneller, kein neues Checkpoint nötig
- **Settings:** CFG 0-1, Sampler: Euler/DPM++ SDE

### 2. SDXL Turbo
- **Was:** Standalone Turbo-Checkpoint, 1-4 Steps
- **Download:** https://huggingface.co/stabilityai/sdxl-turbo
- **File:** `sd_xl_turbo_1.0.safetensors`
- **Wohin:** `ComfyUI/models/checkpoints/`
- **Settings:** 1-4 Steps, CFG 1.0, 512x512 nativ (upscale für grösser)

### 3. Flux Schnell GGUF ⭐
- **Was:** Flux-Qualität in 4 Steps, quantisiert für weniger VRAM
- **Download:** https://huggingface.co/city96/FLUX.1-schnell-gguf
- **File:** `flux1-schnell-Q8_0.gguf` (~12GB) oder `flux1-schnell-Q5_K_S.gguf` (~8GB)
- **Wohin:** `ComfyUI/models/diffusion_models/` (NICHT checkpoints!)
- **Custom Node nötig:** `ComfyUI-GGUF` von city96 → https://github.com/city96/ComfyUI-GGUF
- **Node:** "Unet Loader (GGUF)" statt "Load Checkpoint"

### 4. Flux Dev GGUF (für maximale Qualität)
- **Was:** Beste Textdarstellung, Photorealismus, 20-30 Steps
- **Download:** https://huggingface.co/city96/FLUX.1-dev-gguf
- **File:** `flux1-dev-Q5_K_S.gguf` (~8GB)
- **Wohin:** `ComfyUI/models/diffusion_models/`
- **Custom Node:** Gleich wie oben (ComfyUI-GGUF)

---

## 🎨 Fortgeschrittene Workflows

### 5. IPAdapter FaceID Plus V2 (Face Consistency)
- **Was:** Gesicht aus Referenzbild konsistent in neue Bilder übernehmen
- **Download Models:**
  - IPAdapter: https://huggingface.co/h94/IP-Adapter-FaceID → `ip-adapter-faceid-plusv2_sdxl.bin`
  - LoRA: `ip-adapter-faceid-plusv2_sdxl_lora.safetensors`
- **Custom Node:** https://github.com/cubiq/ComfyUI_IPAdapter_plus
- **Zusätzlich nötig:** InsightFace (`pip install insightface onnxruntime-gpu`)
- **Wohin:** `ComfyUI/models/ipadapter/`

### 6. InstantID (Gesichtsbasierte Generierung)
- **Was:** Ein Foto → generiere beliebige Szenen mit diesem Gesicht
- **Custom Node:** https://github.com/cubiq/ComfyUI_InstantID
- **Models:** InstantID SDXL + ControlNet
- **Nur SDXL kompatibel**

### 7. ControlNet SDXL (Pose/Depth/Canny)
- **Was:** Struktur/Pose aus Bild vorgeben, neuen Style generieren
- **Download:** https://huggingface.co/diffusers/controlnet-canny-sdxl-1.0
- **Wohin:** `ComfyUI/models/controlnet/`

---

## 🔧 Upscaler

### 8. 4x-UltraSharp
- **Was:** Bester Allround-Upscaler
- **Download:** https://civitai.com/models/116225/4x-ultrasharp (oder openmodeldb)
- **File:** `4x-UltraSharp.pth`
- **Wohin:** `ComfyUI/models/upscale_models/`

### 9. 4x-NMKD-Siax (Alternative)
- **Was:** Guter Upscaler für realistische Bilder
- **Wohin:** `ComfyUI/models/upscale_models/`

---

## 🔌 Custom Nodes (empfohlen)

| Node | Zweck | URL |
|------|-------|-----|
| ComfyUI-GGUF | GGUF-Modelle laden (Flux etc.) | https://github.com/city96/ComfyUI-GGUF |
| ComfyUI_IPAdapter_plus | Face/Style Transfer | https://github.com/cubiq/ComfyUI_IPAdapter_plus |
| ComfyUI_InstantID | Gesichtsbasierte Generation | https://github.com/cubiq/ComfyUI_InstantID |
| ComfyUI-Manager | Node-Management UI | https://github.com/ltdrdata/ComfyUI-Manager |
| rgthree-comfy | Workflow-Optimierung | https://github.com/rgthree/rgthree-comfy |

---

## ⚡ Performance-Tipps

1. **xFormers installieren** → 15-25% schneller (in ComfyUI portable: `pip install xformers`)
2. **DPM++ 2M Karras** als Standard-Sampler → schnellster bei gleicher Qualität
3. **Hyper-SD LoRA** statt neue Checkpoints → beschleunigt bestehende Modelle
4. **GGUF statt volle Modelle** → weniger VRAM, kaum Qualitätsverlust bei Q8

---

## Reihenfolge zum Installieren

1. ✅ Lightning Checkpoints (hast du schon)
2. → **Hyper-SDXL LoRA** (Quick Win, beschleunigt alles)
3. → **ComfyUI-GGUF Node** + **Flux Schnell GGUF**
4. → **4x-UltraSharp Upscaler**
5. → **IPAdapter** (wenn Face Consistency gebraucht wird)
6. → **xFormers** (einmal installieren, immer profitieren)
