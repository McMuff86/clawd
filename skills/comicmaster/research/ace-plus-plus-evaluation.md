# ACE++ Evaluation for ComicMaster

> **Datum:** 09.02.2026  
> **Kontext:** ComicMaster Phase 5 – Character Consistency 2.0  
> **Hardware:** RTX 3090 (24GB VRAM), WSL2, ComfyUI

---

## 1. Was ist ACE++?

**ACE++** (Instruction-Based Image Creation and Editing via Context-Aware Content Filling) ist ein von **Alibaba Tongyi Lab** entwickeltes Open-Source-Modell zur character-konsistenten Bildgenerierung und Bildbearbeitung.

**Kernversprechen:** Aus einem einzigen Referenzbild können neue Bilder mit hochkonsistenten Charakter-Features generiert werden — **ohne Training, ohne LoRA, ohne Fine-Tuning**.

- **Paper:** [arxiv.org/abs/2501.02487](https://arxiv.org/abs/2501.02487)
- **GitHub:** [github.com/ali-vilab/ACE_plus](https://github.com/ali-vilab/ACE_plus)
- **Models:** [huggingface.co/ali-vilab/ACE_Plus](https://huggingface.co/ali-vilab/ACE_Plus/tree/main)
- **Entwickler:** Alibaba Group (Tongyi Lab)
- **Release:** Januar 2025 (Code + Modelle), März 2025 (Unified FFT Model)

---

## 2. Wie funktioniert ACE++?

### Architektur

ACE++ baut auf **FLUX.1-Fill-dev** als Basismodell auf und nutzt eine innovative **Context-Aware Content Filling** Architektur:

1. **Long Context Unit (LCU):** Verarbeitet gleichzeitig Bildinhalte, Textanweisungen und Bearbeitungsbereiche in einem einzigen Kontext
2. **Dynamic Attention Mechanism:** Erreicht 92.3% Feature-Retentionsrate bei 512×512
3. **Two-Stage Optimization:** Schrittweises Training mit Basis-Restaurierung + spezialisierter Bearbeitung

### Funktionsprinzip

Das Modell arbeitet als **Inpainting/Outpainting-System**: 
- Man gibt ein Referenzbild und ein Zielbild (leer oder mit Maske) ein
- Dazu eine Textanweisung wie "Maintain the facial features. A girl wearing a police uniform..."
- ACE++ füllt das Zielbild so, dass die Charakter-Features des Referenzbilds beibehalten werden

### Modell-Varianten

| Variante | Typ | Stärke | Empfehlung |
|----------|-----|--------|------------|
| **Portrait LoRA** | LoRA auf FLUX-Fill | Gesichtskonsistenz, Portraitgeneration | ⭐ Empfohlen für ComicMaster |
| **Subject LoRA** | LoRA auf FLUX-Fill | Objektkonsistenz (Logos, Gegenstände) | Nützlich für Props |
| **LocalEditing LoRA** | LoRA auf FLUX-Fill | Lokale Bildbearbeitung mit Maske | Nützlich für Korrekturen |
| **Unified FFT Model** | Vollständig fine-getuntes Modell | Alle Tasks in einem Modell | ⚠️ Schwächer als LoRA-Varianten |

**Wichtig:** Das Alibaba-Team hat kommuniziert, dass ACE++ die **letzte Iteration** auf FLUX-Basis sein wird. Weitere Entwicklung wird auf dem WAN-Modell basieren (Reason: Hohe Heterogenität zwischen Training-Data und FLUX-Modell macht Training instabil).

---

## 3. ComfyUI Integration

### Status: ✅ Vorhanden

ACE++ hat eine **offizielle ComfyUI-Integration** direkt vom Entwicklerteam:

- **Custom Node Package:** `workflow/ComfyUI-ACE_Plus/` im offiziellen GitHub-Repo
- **Installation:** Ordner `ComfyUI-ACE_Plus` in `ComfyUI/custom_nodes/` kopieren
- **Workflows vorhanden:**
  - `workflow_no_preprocess.json` — Preprocessed Images als Input
  - `workflow_controlpreprocess.json` — Kontrollierte Image-to-Image Transformationen
  - `workflow_reference_generation.json` — Referenz-basierte Bildgeneration (Portraits/Objekte)
  - `workflow_referenceediting_generation.json` — Referenz-basierte Bildbearbeitung
  - Weitere FFT-Workflows im `workflow_example_fft/` Ordner

### Benötigte Modelle

| Modell | Grösse (ca.) | Pfad |
|--------|-------------|------|
| FLUX.1-Fill-dev (FP8) | ~12GB | `ComfyUI/models/diffusion_models/` |
| ACE++ Portrait LoRA | ~300MB | `ComfyUI/models/loras/` |
| ACE++ Subject LoRA | ~300MB | `ComfyUI/models/loras/` |
| ACE++ LocalEditing LoRA | ~300MB | `ComfyUI/models/loras/` |
| ACE++ FFT Model (optional) | ~24GB | `ComfyUI/models/diffusion_models/` |

### Community Workflows

- RunComfy hat fertige Workflows für Character Consistency und Face Swap
- Mehrere YouTube-Tutorials verfügbar (Sebastian Kamph u.a.)
- Reddit r/comfyui: Aktive Community mit Workflow-Sharing

---

## 4. VRAM Requirements

### Passt es auf RTX 3090 (24GB)?

| Konfiguration | VRAM Bedarf | RTX 3090? | Anmerkung |
|---------------|-------------|-----------|-----------|
| **Portrait LoRA + FLUX-Fill FP8** | ~16-20GB | ✅ Ja | Empfohlene Konfiguration |
| **Subject LoRA + FLUX-Fill FP8** | ~16-20GB | ✅ Ja | Gleiche Basis |
| **FFT Model (full)** | ~24GB+ | ⚠️ Knapp | Braucht max_seq_length Tuning |
| **Portrait LoRA + FLUX-Fill FP16** | ~24GB+ | ❌ Zu viel | FP8 nutzen |

**Empfehlung für RTX 3090:**
- FLUX.1-Fill-dev als **FP8-Quantisierung** laden (~12GB statt ~24GB)
- Portrait LoRA verwenden (nicht FFT Unified)
- `max_seq_length` auf 1024-2048 setzen (statt 5120) → reduziert VRAM weiter
- Bei Bedarf: NF4/GGUF Quantisierung möglich (ComfyUI unterstützt das)

**Fazit: ✅ Ja, RTX 3090 reicht für ACE++ mit FP8-Quantisierung.**

---

## 5. Stärken & Schwächen für Comics

### Stärken

- **Zero-Training:** Keine LoRA pro Charakter nötig — eine Referenz reicht
- **Gesichtskonsistenz:** Speziell der Portrait LoRA ist sehr gut bei Gesichtsmerkmalen
- **Outfit-Change möglich:** Kann Kleidung ändern während Gesicht konsistent bleibt
- **Szenen-Variation:** Gleicher Charakter in verschiedenen Szenen/Posen/Beleuchtungen
- **ComfyUI-ready:** Offizielle Nodes, einfache Integration

### Schwächen

- **FLUX-basiert:** Langsamer als SDXL (~60s vs ~15s pro Bild auf 3090)
- **Entwicklung eingestellt:** Team wechselt zu WAN — keine Updates mehr für FLUX-Version
- **Inpainting-Ansatz:** Generiert durch Ausfüllen → kann bei Ganzkörper-Shots problematisch sein
- **Hand-Qualität:** Nur 62.3% Genauigkeit bei Handdetails (bekanntes Problem)
- **Nicht für Multi-Character optimiert:** Primär für Single-Character-Consistency
- **Heterogenitäts-Problem:** Training auf FLUX war instabil, was sich in der Qualität des FFT-Modells zeigt

### Vergleich mit aktuellem IPAdapter-Ansatz

| Aspekt | IPAdapter (aktuell) | ACE++ |
|--------|-------------------|-------|
| Geschwindigkeit | ~15s/Panel (SDXL) | ~60s/Panel (FLUX) |
| Gesichtskonsistenz | ★★★ (gut mit Face-Crop) | ★★★★ (sehr gut) |
| Setup-Komplexität | Niedrig (bereits integriert) | Mittel (neue Nodes + FLUX-Modell) |
| Multi-Character | ✅ (chained IPAdapter) | ⚠️ (sequenziell, nicht parallel) |
| Outfit-Kontrolle | ★★★ (prompt-basiert + locking) | ★★★★ (kann explizit ändern) |
| Modell-Ökosystem | SDXL (riesig, stabil) | FLUX-Fill (kleiner, Entwicklung gestoppt) |
| VRAM | ~8GB | ~16-20GB |

---

## 6. Konkreter Integrationsplan für ComicMaster

### Phase A: Evaluation (1-2 Tage)

1. **FLUX.1-Fill-dev FP8 runterladen** → `ComfyUI/models/diffusion_models/`
2. **ACE++ Portrait LoRA** runterladen → `ComfyUI/models/loras/`
3. **ComfyUI-ACE_Plus Nodes** installieren → `ComfyUI/custom_nodes/`
4. **Manuelle Tests:**
   - Charakter-Referenz → 5 verschiedene Szenen generieren
   - Vergleich: IPAdapter vs. ACE++ (gleicher Charakter, gleiche Szenen)
   - Face Similarity messen mit unserem FaceValidator

### Phase B: Pipeline-Integration (2-3 Tage)

Falls Evaluation positiv:

1. **Neuer Generator-Mode:** `panel_generator.py` bekommt einen `ace_plus` Mode neben dem bisherigen `ipadapter` Mode
2. **Workflow-Builder:** `build_ace_plus_workflow()` Funktion erstellen:
   ```python
   def build_ace_plus_workflow(
       prompt: str,
       ref_image_filename: str,  # Character Reference
       preset_config: dict,
       width: int = 768,
       height: int = 768,
       seed: int = -1,
   ) -> dict:
       """Build ACE++ character-consistent workflow.
       
       Uses FLUX-Fill-dev + Portrait LoRA for character consistency.
       The ref image is placed in the context area, the target area
       is filled based on the text prompt.
       """
   ```
3. **Character Ref Pipeline anpassen:**
   - Bestehende Multi-Angle-Refs können als Input für ACE++ dienen
   - Front-View wird bevorzugt (beste Gesichtsinformation)
4. **Hybrid-Ansatz:** 
   - **Close-Up/Portrait Panels:** ACE++ (beste Gesichtskonsistenz)
   - **Wide/Action Panels:** IPAdapter (schneller, Multi-Character)

### Phase C: Optimierung (fortlaufend)

1. **Geschwindigkeits-Optimierung:**
   - FLUX-Fill-Dev mit fp8 + `--lowvram` Flag
   - max_seq_length auf 2048 begrenzen
   - Nur für Close-Up Panels einsetzen (nicht für alle)
2. **Quality-Gating:**
   - FaceValidator Score vergleichen: IPAdapter vs. ACE++
   - Automatisch den besseren Output wählen
3. **WAN-Migration planen:**
   - Alibaba's nächste ACE-Version wird auf WAN basieren
   - Wenn WAN-Version erscheint: evaluieren und ggf. migrieren

### Empfohlener Ansatz: Hybride Pipeline

```
Story Plan
  │
  ├── Character Ref Generation (Multi-Angle, SDXL, wie bisher)
  │
  ├── Panel Generation
  │     ├── Close-Up / Portrait Panels → ACE++ (FLUX-Fill + Portrait LoRA)
  │     ├── Medium / Wide Panels → IPAdapter (SDXL, wie bisher)
  │     └── Multi-Character Panels → Chained IPAdapter (SDXL)
  │
  ├── Face Crop Re-injection (NEU, Phase 5.1)
  │
  └── Face Validation → Bester Output gewinnt
```

---

## 7. Risiken & Empfehlung

### Risiken

- **Entwicklung gestoppt:** Keine Bug-Fixes oder Verbesserungen mehr für FLUX-Version
- **Geschwindigkeits-Einbusse:** 4x langsamer als aktuelle SDXL-Pipeline
- **Kompatibilität:** FLUX-basiert = anderes Ökosystem als unser SDXL-Setup
- **VRAM-Druck:** 16-20GB lässt wenig Spielraum für andere Aufgaben

### Empfehlung

**Kurzfristig (jetzt):** Die in Phase 5.1 umgesetzten Verbesserungen (Costume Locking + Face Crop Re-injection) zuerst nutzen und evaluieren. Diese laufen auf der bestehenden SDXL-Pipeline und sind sofort einsatzbereit.

**Mittelfristig (nach Evaluation):** ACE++ als **optionaler Qualitäts-Boost** für Close-Up Panels integrieren. Nicht als Ersatz für IPAdapter, sondern als Ergänzung. Der Hybrid-Ansatz gibt das Beste aus beiden Welten.

**Langfristig:** ACE auf WAN-Basis abwarten (vermutlich H2 2025 / H1 2026). Wenn die WAN-Version stabiler und schneller ist, könnte sie IPAdapter für Character-Consistency komplett ablösen.

---

## Quellen

- [ACE++ GitHub Repository](https://github.com/ali-vilab/ACE_plus)
- [ACE++ Paper (arxiv)](https://arxiv.org/abs/2501.02487)
- [ACE++ HuggingFace Models](https://huggingface.co/ali-vilab/ACE_Plus/tree/main)
- [ComfyUI Wiki: ACE++ Evaluation](https://comfyui-wiki.com/en/news/2025-02-10-alibaba-ace-plus-zero-training-image-generation)
- [ACE++ FFT Unified Model (ComfyUI.org)](https://comfyui.org/en/ace-unified-fft-model-for-image-generation)
- [Reddit r/comfyui: ACE++ Workflow Discussion](https://www.reddit.com/r/comfyui/comments/1ieg4th/ace_character_consistency_from_1_image_no/)
- [RunComfy ACE++ Workflows](https://www.runcomfy.com/comfyui-workflows/ace-plus-plus-character-consistency)
