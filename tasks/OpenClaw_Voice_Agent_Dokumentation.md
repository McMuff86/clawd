# OpenClaw Voice Agent - Umfassende Projektdokumentation
## Open-Source AI Voice Agent mit Telefonie-Funktionalität

**Autor:** Adi  
**Datum:** Februar 2026  
**Version:** 1.0

---

## Inhaltsverzeichnis

1. [Executive Summary](#1-executive-summary)
2. [Systemübersicht](#2-systemübersicht)
3. [Komponenten im Detail](#3-komponenten-im-detail)
4. [Framework-Entscheidung: AVR vs Pipecat](#4-framework-entscheidung-avr-vs-pipecat)
5. [Telefonie-Optionen](#5-telefonie-optionen)
6. [Hardware-Anforderungen](#6-hardware-anforderungen)
7. [Implementierung Schritt für Schritt](#7-implementierung-schritt-für-schritt)
8. [Docker-Konfigurationen](#8-docker-konfigurationen)
9. [Kosten und Betrieb](#9-kosten-und-betrieb)
10. [Roadmap und Erweiterungen](#10-roadmap-und-erweiterungen)

---

## 1. Executive Summary

### Ziel des Projekts

Aufbau eines **vollständig selbst-gehosteten AI Voice Agents** für das OpenClaw-Projekt, der:

- Eingehende Telefonanrufe entgegennimmt und intelligent beantwortet
- Ausgehende Anrufe tätigen kann (z.B. Benachrichtigungen, Follow-ups)
- Komplett lokal läuft ohne Abhängigkeit von Bezahldiensten
- Auf Open-Source-Technologien basiert
- Später in IntelliPlan integriert werden kann

### Technologie-Stack (Empfohlen)

| Komponente | Technologie | Lizenz |
|------------|-------------|--------|
| **TTS (Text-to-Speech)** | Qwen3-TTS 1.7B | Apache 2.0 |
| **STT (Speech-to-Text)** | Vosk / faster-whisper | Apache 2.0 / MIT |
| **LLM (Sprachmodell)** | Ollama + Qwen3 | Apache 2.0 |
| **VAD (Voice Activity)** | Silero VAD | MIT |
| **Framework** | AVR (Agent Voice Response) | MIT |
| **Telefonie PBX** | Asterisk | GPL |
| **Container** | Docker + Docker Compose | Apache 2.0 |

### Geschätzte Kosten

| Posten | Einmalig | Monatlich |
|--------|----------|-----------|
| Hardware (wenn neuer Mini-PC) | 1'500-2'500 CHF | - |
| GSM Gateway (Dongle + SIM) | ~40 CHF | ~5-10 CHF Guthaben |
| Alternativ: SIP Trunk | - | 0-10 CHF |
| Stromkosten (~100W 24/7) | - | ~25 CHF |
| **Total (mit bestehender Hardware)** | ~40 CHF | ~30-45 CHF |

---

## 2. Systemübersicht

### Architektur-Diagramm

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        OPENCLAW VOICE AGENT SYSTEM                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      EXTERNE SCHNITTSTELLEN                          │   │
│  │                                                                       │   │
│  │   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │   │
│  │   │   TELEFON    │    │   BROWSER    │    │   MOBILE     │          │   │
│  │   │   (PSTN)     │    │   (WebRTC)   │    │    APP       │          │   │
│  │   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘          │   │
│  │          │                   │                   │                   │   │
│  └──────────┼───────────────────┼───────────────────┼───────────────────┘   │
│             │                   │                   │                       │
│             ▼                   ▼                   ▼                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      TRANSPORT LAYER                                 │   │
│  │                                                                       │   │
│  │   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐          │   │
│  │   │   ASTERISK   │    │   WebSocket  │    │   WebRTC     │          │   │
│  │   │     PBX      │    │   Server     │    │   (Daily)    │          │   │
│  │   │              │    │              │    │              │          │   │
│  │   │ • SIP Trunk  │    │ • Port 8765  │    │ • Optional   │          │   │
│  │   │ • GSM Dongle │    │              │    │              │          │   │
│  │   │ • AudioSocket│    │              │    │              │          │   │
│  │   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘          │   │
│  │          │                   │                   │                   │   │
│  └──────────┼───────────────────┼───────────────────┼───────────────────┘   │
│             │                   │                   │                       │
│             └───────────────────┼───────────────────┘                       │
│                                 │                                           │
│                                 ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      AVR / PIPECAT CORE                              │   │
│  │                      (Orchestrierung)                                │   │
│  │                                                                       │   │
│  │   • Audio-Streaming-Management                                       │   │
│  │   • Interrupt-Handling (Barge-in)                                    │   │
│  │   • Session-Management                                               │   │
│  │   • Kontext-Verwaltung                                               │   │
│  │                                                                       │   │
│  └──────────────────────────────┬──────────────────────────────────────┘   │
│                                 │                                           │
│             ┌───────────────────┼───────────────────┐                       │
│             │                   │                   │                       │
│             ▼                   ▼                   ▼                       │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                │
│  │      ASR       │  │      LLM       │  │      TTS       │                │
│  │  (Speech-to-   │  │   (Language    │  │   (Text-to-    │                │
│  │     Text)      │  │    Model)      │  │    Speech)     │                │
│  │                │  │                │  │                │                │
│  │ ┌────────────┐ │  │ ┌────────────┐ │  │ ┌────────────┐ │                │
│  │ │   VOSK     │ │  │ │  OLLAMA    │ │  │ │ QWEN3-TTS  │ │                │
│  │ │   oder     │ │  │ │    +       │ │  │ │   1.7B     │ │                │
│  │ │  WHISPER   │ │  │ │  Qwen3     │ │  │ │            │ │                │
│  │ └────────────┘ │  │ └────────────┘ │  │ └────────────┘ │                │
│  │                │  │                │  │                │                │
│  │ Deutsch: ✓     │  │ Deutsch: ✓     │  │ Deutsch: ✓     │                │
│  │ Echtzeit: ✓    │  │ Tool-Call: ✓   │  │ Streaming: ✓   │                │
│  │ Lokal: ✓       │  │ Lokal: ✓       │  │ Cloning: ✓     │                │
│  └────────────────┘  └────────────────┘  └────────────────┘                │
│                                 │                                           │
│                                 ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      SILERO VAD                                      │   │
│  │                (Voice Activity Detection)                            │   │
│  │                                                                       │   │
│  │   • Erkennt Sprechpausen                                             │   │
│  │   • Ermöglicht natürliche Unterbrechungen                            │   │
│  │   • Filtert Hintergrundgeräusche                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Datenfluss bei einem Anruf

```
1. EINGEHENDER ANRUF
   ┌─────────┐
   │ Anrufer │ ──► Mobilfunk/Festnetz ──► SIP Provider/GSM Gateway
   └─────────┘

2. ASTERISK VERARBEITUNG
   ┌──────────────────────────────────────────────────────────────┐
   │ Asterisk PBX                                                 │
   │  • Nimmt Anruf entgegen (SIP/PJSIP)                          │
   │  • Startet AudioSocket-Verbindung zu AVR Core                │
   │  • Streamt bidirektionales Audio (μ-law/A-law → PCM)         │
   └──────────────────────────────────────────────────────────────┘

3. VOICE AGENT PIPELINE
   ┌─────────────────────────────────────────────────────────────────┐
   │                                                                  │
   │  Audio Input ──► VAD ──► ASR ──► LLM ──► TTS ──► Audio Output   │
   │       │          │        │       │       │           │         │
   │       │          │        │       │       │           │         │
   │    8kHz PCM   Silero   "Hallo"  Antwort  Qwen3    Sprache      │
   │    Stream     erkennt  erkannt  generiert TTS     generiert    │
   │               Sprache                                           │
   │                                                                  │
   └─────────────────────────────────────────────────────────────────┘

4. ANTWORT ZURÜCK
   ┌─────────┐
   │ Anrufer │ ◄── Mobilfunk/Festnetz ◄── Asterisk ◄── TTS Audio
   └─────────┘
```

---

## 3. Komponenten im Detail

### 3.1 Qwen3-TTS (Text-to-Speech)

#### Was ist Qwen3-TTS?

Qwen3-TTS ist eine Open-Source TTS-Modellserie von Alibaba Cloud (Qwen Team), veröffentlicht im Januar 2026. Es bietet State-of-the-Art Sprachsynthese mit Features, die bisher nur in kommerziellen Systemen verfügbar waren.

#### Technische Spezifikationen

| Eigenschaft | Wert |
|-------------|------|
| **Modellgrößen** | 0.6B Parameter / 1.7B Parameter |
| **Architektur** | Discrete Multi-Codebook LM |
| **Tokenizer** | Qwen3-TTS-Tokenizer-12Hz |
| **Sprachen** | 10 (DE, EN, FR, ES, IT, PT, RU, ZH, JA, KO) |
| **Streaming-Latenz** | ~97ms (First Token) |
| **Lizenz** | Apache 2.0 |

#### Modellvarianten

| Modell | Beschreibung | Use Case |
|--------|--------------|----------|
| **Base** | Standard TTS + Voice Cloning | Allgemein, Voice Clone |
| **CustomVoice** | 9 vortrainierte Premium-Stimmen | Konsistente Qualität |
| **VoiceDesign** | Stimme per Text-Beschreibung erstellen | Kreative Anwendungen |

#### Voice Cloning Funktionalität

```python
# Nur 3-15 Sekunden Referenz-Audio benötigt!
from qwen_tts import QwenTTS

tts = QwenTTS(model_name="Qwen/Qwen3-TTS-12Hz-1.7B-Base")

# Voice Clone
audio = tts.clone_voice(
    reference_audio="meine_stimme_sample.wav",  # 3-15 Sekunden
    reference_text="Der gesprochene Text im Sample",  # Optional, verbessert Qualität
    target_text="Neuer Text der gesprochen werden soll",
    language="de"
)
```

#### VRAM-Anforderungen

| Modell | Minimum VRAM | Empfohlen | RTX 3090 (24GB) |
|--------|--------------|-----------|-----------------|
| 0.6B | ~4 GB | 6 GB | ✅ Sehr gut |
| 1.7B | ~8 GB | 12 GB | ✅ Gut |
| 1.7B + LLM parallel | ~18 GB | 20 GB | ✅ Machbar |

#### Installation

```bash
# Conda Environment
conda create -n qwen3-tts python=3.12 -y
conda activate qwen3-tts

# Installation
pip install qwen-tts

# Optional: FlashAttention 2 für bessere Performance
pip install flash-attn --no-build-isolation

# Modell wird automatisch bei erster Nutzung geladen
# Oder manueller Download:
huggingface-cli download Qwen/Qwen3-TTS-12Hz-1.7B-Base --local-dir ./models/qwen3-tts
huggingface-cli download Qwen/Qwen3-TTS-Tokenizer-12Hz --local-dir ./models/tokenizer
```

---

### 3.2 Speech-to-Text (ASR)

#### Option A: Vosk (Empfohlen für Echtzeit)

| Eigenschaft | Wert |
|-------------|------|
| **Typ** | Offline Speech Recognition |
| **Latenz** | Sehr niedrig (<100ms) |
| **Deutsch-Modell** | vosk-model-de-0.21 (~1.5GB) |
| **VRAM** | CPU-basiert, kein GPU nötig |
| **Lizenz** | Apache 2.0 |

```bash
# Installation
pip install vosk

# Deutsches Modell herunterladen
wget https://alphacephei.com/vosk/models/vosk-model-de-0.21.zip
unzip vosk-model-de-0.21.zip
```

#### Option B: Faster-Whisper (Höhere Genauigkeit)

| Eigenschaft | Wert |
|-------------|------|
| **Typ** | CTranslate2 optimiertes Whisper |
| **Latenz** | Mittel (200-500ms je nach Modell) |
| **Modelle** | tiny, base, small, medium, large-v3 |
| **VRAM** | 1-10 GB je nach Modell |
| **Lizenz** | MIT |

```bash
pip install faster-whisper

# Nutzung
from faster_whisper import WhisperModel
model = WhisperModel("base", device="cuda", compute_type="float16")
```

#### Vergleich

| Aspekt | Vosk | Faster-Whisper |
|--------|------|----------------|
| Geschwindigkeit | ⭐⭐⭐ Sehr schnell | ⭐⭐ Schnell |
| Genauigkeit | ⭐⭐ Gut | ⭐⭐⭐ Sehr gut |
| Ressourcen | ⭐⭐⭐ CPU only | ⭐⭐ GPU empfohlen |
| Streaming | ✅ Nativ | ⚠️ Chunked |

**Empfehlung:** Starte mit **Vosk** für niedrige Latenz, wechsle zu **Whisper** wenn Genauigkeit wichtiger wird.

---

### 3.3 Large Language Model (LLM)

#### Ollama als LLM-Server

Ollama ist ein lokaler LLM-Server, der verschiedene Modelle hosten kann und eine OpenAI-kompatible API bereitstellt.

```bash
# Installation
curl -fsSL https://ollama.ai/install.sh | sh

# Modell herunterladen
ollama pull qwen3:14b      # Empfohlen für RTX 3090
ollama pull qwen3:7b       # Leichtere Alternative
ollama pull llama3.2:7b    # Alternative mit guter Tool-Unterstützung

# Server starten (läuft automatisch nach Installation)
ollama serve

# API-Endpunkt: http://localhost:11434
```

#### Empfohlene Modelle

| Modell | Parameter | VRAM | Deutsch | Tool-Calling |
|--------|-----------|------|---------|--------------|
| qwen3:14b | 14B | ~10GB | ⭐⭐⭐ | ✅ |
| qwen3:7b | 7B | ~5GB | ⭐⭐⭐ | ✅ |
| llama3.2:7b | 7B | ~5GB | ⭐⭐ | ✅ |
| mistral:7b | 7B | ~5GB | ⭐⭐ | ✅ |

#### System Prompt für OpenClaw

```python
SYSTEM_PROMPT = """Du bist OpenClaw, ein intelligenter KI-Assistent für 
Projektplanung und Automatisierung.

PERSÖNLICHKEIT:
- Freundlich und professionell
- Antworte präzise und kurz (max. 2-3 Sätze für Telefonate)
- Sprich natürlich, wie in einem echten Gespräch

FÄHIGKEITEN:
- Projektplanung und -verwaltung
- Terminkoordination
- Informationsabfragen
- Erinnerungen setzen

KONTEXT:
- Du sprichst mit Adi, dem Entwickler von IntelliPlan
- Aktuelle Zeit: {current_time}
- Anruftyp: {call_type}

Antworte immer auf Deutsch, es sei denn, der Anrufer spricht eine andere Sprache."""
```

---

### 3.4 Voice Activity Detection (VAD)

#### Silero VAD

Silero VAD ist ein kompaktes, schnelles Modell zur Erkennung von Sprachaktivität.

| Eigenschaft | Wert |
|-------------|------|
| **Modellgröße** | ~2MB |
| **Latenz** | <1ms pro Frame |
| **Plattform** | CPU (PyTorch) |
| **Lizenz** | MIT |

**Funktionen:**
- Erkennt Start/Ende von Sprechphasen
- Ermöglicht natürliche Unterbrechungen (Barge-in)
- Filtert Hintergrundgeräusche

```python
import torch
model, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad'
)
```

---

## 4. Framework-Entscheidung: AVR vs Pipecat

### 4.1 AVR (Agent Voice Response)

#### Überblick

AVR ist eine Open-Source-Plattform, die speziell für Telefonie-basierte AI Voice Agents entwickelt wurde. Sie ist eng mit Asterisk integriert und bietet eine modulare Architektur.

#### Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                        AVR STACK                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐                                            │
│  │  Asterisk   │ ◄──── SIP Trunk / GSM Gateway              │
│  │    PBX      │                                            │
│  └──────┬──────┘                                            │
│         │ AudioSocket (TCP 5001)                            │
│         ▼                                                   │
│  ┌─────────────┐                                            │
│  │  AVR Core   │ ◄──── Orchestrierung                       │
│  └──────┬──────┘                                            │
│         │                                                   │
│    ┌────┴────┬────────────┐                                 │
│    ▼         ▼            ▼                                 │
│  ┌─────┐  ┌─────┐     ┌─────┐                               │
│  │ ASR │  │ LLM │     │ TTS │                               │
│  │Vosk │  │Ollama│    │Qwen3│                               │
│  └─────┘  └─────┘     └─────┘                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Vorteile

- ✅ **Telefonie-fokussiert:** Asterisk-Integration out-of-the-box
- ✅ **Docker-ready:** Fertige Images verfügbar
- ✅ **Modularer Aufbau:** Einfacher Austausch von Komponenten
- ✅ **Gut dokumentiert:** Wiki mit Beispielen
- ✅ **100% lokal möglich:** Vosk + Ollama + Kokoro/Qwen3

#### Nachteile

- ❌ Kleinere Community als Pipecat
- ❌ Weniger Flexibilität für Non-Telefonie Use Cases
- ❌ Kein natives WebRTC

#### Offizielle Docker Images

| Image | Funktion |
|-------|----------|
| `agentvoiceresponse/avr-core` | Orchestrierung |
| `agentvoiceresponse/avr-asterisk` | Telefonie PBX |
| `agentvoiceresponse/avr-asr-vosk` | Speech-to-Text |
| `agentvoiceresponse/avr-llm-openai` | LLM Adapter |
| `agentvoiceresponse/avr-tts-kokoro` | Text-to-Speech |

---

### 4.2 Pipecat

#### Überblick

Pipecat ist ein universelles Open-Source-Framework für Echtzeit-Voice-und-Video AI Anwendungen. Es wurde von Daily.co entwickelt und ist transport-agnostisch.

#### Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                      PIPECAT STACK                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 TRANSPORT LAYER                      │   │
│  │  WebSocket │ WebRTC │ SIP │ Daily │ Twilio          │   │
│  └─────────────────────────┬───────────────────────────┘   │
│                            │                               │
│                            ▼                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    PIPELINE                          │   │
│  │                                                       │   │
│  │   Input → VAD → STT → LLM → TTS → Output             │   │
│  │                                                       │   │
│  │   + Custom Processors                                │   │
│  │   + Filter/Transformation                            │   │
│  │   + Tool Calling                                     │   │
│  │   + MCP Integration                                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              50+ PROVIDER INTEGRATIONS               │   │
│  │  OpenAI, Anthropic, Deepgram, ElevenLabs, ...       │   │
│  │  + Lokale: Whisper, Ollama, Piper, ...              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Vorteile

- ✅ **Sehr flexibel:** Jede Komponente austauschbar
- ✅ **Multi-Transport:** WebRTC, WebSocket, SIP, etc.
- ✅ **Große Community:** Aktive Entwicklung, viele Beispiele
- ✅ **Multimodal:** Auch Video/Bilder möglich
- ✅ **Gute Dokumentation:** Umfangreiche Docs und Tutorials
- ✅ **Python-native:** Einfach erweiterbar

#### Nachteile

- ❌ Telefonie erfordert zusätzliches Setup
- ❌ Steilere Lernkurve
- ❌ Mehr Code nötig für Basissetup
- ❌ Kein fertiges Docker-Compose für Self-Hosting

#### Code-Beispiel

```python
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.transports.websocket import WebSocketServerTransport
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.services.whisper import WhisperSTTService
from pipecat.services.ollama import OllamaLLMService

async def main():
    transport = WebSocketServerTransport(host="0.0.0.0", port=8765)
    
    pipeline = Pipeline([
        transport.input(),
        SileroVADAnalyzer(),
        WhisperSTTService(model="base", language="de"),
        OllamaLLMService(model="qwen3:14b"),
        Qwen3TTSService(language="de"),  # Custom
        transport.output()
    ])
    
    task = PipelineTask(pipeline, params=PipelineParams(allow_interruptions=True))
    await PipelineRunner().run(task)
```

---

### 4.3 Entscheidungsmatrix

| Kriterium | AVR | Pipecat | Gewichtung |
|-----------|-----|---------|------------|
| Telefonie out-of-the-box | ⭐⭐⭐ | ⭐ | Hoch |
| Setup-Geschwindigkeit | ⭐⭐⭐ | ⭐⭐ | Mittel |
| Flexibilität | ⭐⭐ | ⭐⭐⭐ | Mittel |
| WebRTC/Browser Support | ⭐ | ⭐⭐⭐ | Niedrig |
| Community/Dokumentation | ⭐⭐ | ⭐⭐⭐ | Mittel |
| Lokale AI-Integration | ⭐⭐⭐ | ⭐⭐⭐ | Hoch |
| Docker-Support | ⭐⭐⭐ | ⭐⭐ | Hoch |

### 4.4 Empfehlung

**Für das OpenClaw-Projekt empfehle ich: AVR**

Begründung:
1. **Telefonie ist das Hauptziel** → AVR ist darauf spezialisiert
2. **Schnellerer Start** → Fertige Docker Images
3. **Asterisk-Integration** → Bewährt für Produktionsumgebungen
4. **Erweiterbar** → Später kann Pipecat für Web-Interface hinzugefügt werden

**Hybrid-Ansatz (später):**
```
Telefonie → AVR + Asterisk
Web/Browser → Pipecat + WebRTC
Shared → Ollama LLM, Qwen3-TTS
```

---

## 5. Telefonie-Optionen

### 5.1 Das Problem

Ein SIP Trunk ist die Brücke zwischen dem Internet (VoIP) und dem öffentlichen Telefonnetz (PSTN). Das Telefonnetz selbst ist nicht "Open Source" - es gehört den Telekommunikationsanbietern.

### 5.2 Optionen im Überblick

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        TELEFONIE-OPTIONEN                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  OPTION 1: GSM GATEWAY (Empfohlen)                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                   │   │
│  │   ┌──────────┐    ┌──────────────┐    ┌──────────┐              │   │
│  │   │ Anrufer  │───►│ Mobilfunknetz│───►│USB Dongle│              │   │
│  │   │ (Handy)  │    │ (Swisscom,   │    │+ SIM     │              │   │
│  │   └──────────┘    │  Sunrise)    │    └────┬─────┘              │   │
│  │                   └──────────────┘         │                     │   │
│  │                                            ▼                     │   │
│  │                                    ┌──────────────┐              │   │
│  │                                    │  Asterisk    │              │   │
│  │                                    │ chan_dongle  │              │   │
│  │                                    └──────────────┘              │   │
│  │                                                                   │   │
│  │   Kosten: ~40 CHF einmalig + Prepaid-Guthaben                    │   │
│  │   Vorteile: Eigene Handynummer, keine Fixkosten                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  OPTION 2: SIP TRUNK                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                   │   │
│  │   ┌──────────┐    ┌──────────────┐    ┌──────────┐              │   │
│  │   │ Anrufer  │───►│ Telefonnetz  │───►│SIP       │              │   │
│  │   │ (Festnetz│    │ (PSTN)       │    │Provider  │              │   │
│  │   │  /Handy) │    │              │    │(sipgate, │              │   │
│  │   └──────────┘    └──────────────┘    │ VoIP.ms) │              │   │
│  │                                       └────┬─────┘              │   │
│  │                                            │ Internet           │   │
│  │                                            ▼                     │   │
│  │                                    ┌──────────────┐              │   │
│  │                                    │  Asterisk    │              │   │
│  │                                    │   PJSIP      │              │   │
│  │                                    └──────────────┘              │   │
│  │                                                                   │   │
│  │   Kosten: 0-10 CHF/Monat                                         │   │
│  │   Vorteile: Festnetznummer möglich, professioneller              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  OPTION 3: NUR VoIP (Kostenlos)                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                   │   │
│  │   ┌──────────┐                        ┌──────────┐              │   │
│  │   │ Softphone│────── Internet ───────►│ Asterisk │              │   │
│  │   │ (Linphone│                        │          │              │   │
│  │   │  Zoiper) │                        └──────────┘              │   │
│  │   └──────────┘                                                   │   │
│  │                                                                   │   │
│  │   Kosten: 0 CHF                                                  │   │
│  │   Einschränkung: Nur über Internet erreichbar                    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Option 1: GSM Gateway (Detailliert)

#### Hardware

| Gerät | Preis | Kompatibilität |
|-------|-------|----------------|
| Huawei E1550 | ~10-15 CHF (gebraucht) | ⭐⭐⭐ Sehr gut |
| Huawei E173 | ~15-20 CHF | ⭐⭐⭐ Sehr gut |
| Huawei E3372 | ~30 CHF | ⭐⭐ Gut |
| ZTE MF180 | ~20 CHF | ⭐⭐ Gut |

#### Software: chan_dongle

```bash
# Abhängigkeiten
apt install asterisk asterisk-dev usb-modeswitch libusb-1.0-0-dev

# chan_dongle kompilieren
git clone https://github.com/wdoekes/asterisk-chan-dongle
cd asterisk-chan-dongle
./configure --with-astversion=18  # Asterisk Version anpassen
make
make install

# Konfiguration kopieren
cp etc/dongle.conf /etc/asterisk/
```

#### Konfiguration

```ini
# /etc/asterisk/dongle.conf
[general]
interval=15

[dongle0]
context=from-dongle           ; Dialplan context für eingehende Anrufe
audio=/dev/ttyUSB1            ; Audio device
data=/dev/ttyUSB2             ; Data/AT command device
imei=YOUR_DONGLE_IMEI         ; IMEI des Dongles
imsi=YOUR_SIM_IMSI            ; IMSI der SIM-Karte
```

```ini
# /etc/asterisk/extensions.conf
[from-dongle]
; Eingehende Anrufe vom GSM Dongle
exten => s,1,NoOp(Incoming GSM call from ${CALLERID(num)})
 same => n,Answer()
 same => n,Wait(1)
 same => n,AudioSocket(127.0.0.1:5001,${UNIQUEID})
 same => n,Hangup()

[to-dongle]
; Ausgehende Anrufe über GSM
exten => _X.,1,NoOp(Outgoing GSM call to ${EXTEN})
 same => n,Dial(Dongle/dongle0/${EXTEN},60)
 same => n,Hangup()
```

### 5.4 Option 2: SIP Trunk (Detailliert)

#### Empfohlene Provider (Schweiz/Deutschland)

| Provider | Eingehend | Ausgehend | Monatlich |
|----------|-----------|-----------|-----------|
| sipgate (DE) | Gratis | ~1ct/Min | 0€ Basis |
| peoplefone (CH) | ~2 CHF/Monat | ~3ct/Min | ab 2 CHF |
| VoIP.ms | ~1$/Monat | ~1ct/Min | Pay-as-you-go |
| Zadarma | 100 Min gratis | ~2ct/Min | 0€ Basis |

#### Asterisk PJSIP Konfiguration

```ini
# /etc/asterisk/pjsip.conf

; Transport
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060

; SIP Trunk Registration
[sipgate]
type=registration
transport=transport-udp
outbound_auth=sipgate-auth
server_uri=sip:sipgate.de
client_uri=sip:DEIN_USERNAME@sipgate.de
retry_interval=60

; Authentication
[sipgate-auth]
type=auth
auth_type=userpass
username=DEIN_SIP_USERNAME
password=DEIN_SIP_PASSWORT

; Endpoint
[sipgate-endpoint]
type=endpoint
transport=transport-udp
context=from-sipgate
disallow=all
allow=ulaw
allow=alaw
outbound_auth=sipgate-auth
aors=sipgate

; AOR (Address of Record)
[sipgate]
type=aor
contact=sip:sipgate.de
```

```ini
# /etc/asterisk/extensions.conf

[from-sipgate]
; Eingehende Anrufe vom SIP Trunk
exten => _X.,1,NoOp(Incoming SIP call to ${EXTEN})
 same => n,Answer()
 same => n,AudioSocket(127.0.0.1:5001,${UNIQUEID})
 same => n,Hangup()

[to-sipgate]
; Ausgehende Anrufe über SIP Trunk
exten => _X.,1,NoOp(Outgoing SIP call to ${EXTEN})
 same => n,Dial(PJSIP/${EXTEN}@sipgate-endpoint,60)
 same => n,Hangup()
```

### 5.5 Empfohlene Strategie

```
PHASE 1: Entwicklung & Test
├── Nur VoIP (Softphone)
├── Kostenlos
└── Schneller Start

PHASE 2: Erste Telefonie
├── GSM Dongle (~40 CHF)
├── Prepaid SIM
└── Echte Handynummer

PHASE 3: Produktiv (Optional)
├── SIP Trunk für Festnetznummer
├── Oder: Zweiter GSM Dongle für Redundanz
└── Professionelleres Setup
```

---

## 6. Hardware-Anforderungen

### 6.1 Aktuelle Hardware (RTX 3090 Workstation)

| Komponente | Spezifikation | Für Voice Agent |
|------------|---------------|-----------------|
| CPU | AMD Threadripper 32-Core | ✅ Mehr als ausreichend |
| RAM | 128 GB | ✅ Mehr als ausreichend |
| GPU | RTX 3090 24GB | ✅ Ideal für 1.7B TTS + 14B LLM |
| Storage | NVMe | ✅ Schnell genug |

**Fazit:** Deine Workstation ist perfekt für Entwicklung und Test.

### 6.2 VRAM-Verteilung (RTX 3090)

```
┌─────────────────────────────────────────────────────────────┐
│                    RTX 3090 - 24 GB VRAM                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Qwen3-TTS 1.7B                         ~10 GB      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Ollama Qwen3:14b (quantisiert)         ~10 GB      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Silero VAD + Overhead                   ~2 GB      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Reserve / Whisper (optional)            ~2 GB      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Total: ~24 GB (voll ausgelastet, aber machbar)            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 Dedizierter Mini-PC (24/7 Betrieb)

#### Empfohlene Konfiguration

| Komponente | Minimum | Empfohlen | Premium |
|------------|---------|-----------|---------|
| **GPU** | RTX 4060 8GB | RTX 4070 12GB | RTX 4080 16GB |
| **CPU** | Intel i5-13400 | Intel i7-13700 | Intel i9-13900 |
| **RAM** | 32 GB DDR5 | 64 GB DDR5 | 128 GB DDR5 |
| **Storage** | 500 GB NVMe | 1 TB NVMe | 2 TB NVMe |
| **Preis ca.** | ~1'200 CHF | ~1'800 CHF | ~2'500 CHF |

#### Alternative: NVIDIA Jetson

| Modell | VRAM | Preis | Use Case |
|--------|------|-------|----------|
| Jetson Orin Nano | 8 GB | ~500 CHF | Nur 0.6B Modelle |
| Jetson AGX Orin | 32/64 GB | ~1'500-2'500 CHF | Volle Power, kompakt |

### 6.4 Strom und Wärme

| Setup | Leistung | Strom/Monat | Wärme |
|-------|----------|-------------|-------|
| RTX 3090 Workstation | ~300-450W | ~80-100 CHF | Hoch |
| Mini-PC RTX 4070 | ~150-200W | ~40-50 CHF | Mittel |
| Jetson AGX Orin | ~30-60W | ~10-15 CHF | Niedrig |

---

## 7. Implementierung Schritt für Schritt

### Phase 1: Basis-Setup (Tag 1-2)

#### Schritt 1.1: Docker & NVIDIA Setup

```bash
# Docker installieren (falls nicht vorhanden)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker

# Test
docker run --rm --gpus all nvidia/cuda:12.1-base nvidia-smi
```

#### Schritt 1.2: Projektstruktur erstellen

```bash
mkdir -p ~/openclaw-voice-agent/{config,models,logs}
cd ~/openclaw-voice-agent

# Struktur:
# openclaw-voice-agent/
# ├── docker-compose.yml
# ├── config/
# │   ├── asterisk/
# │   │   ├── pjsip.conf
# │   │   ├── extensions.conf
# │   │   └── dongle.conf
# │   └── avr/
# │       └── .env
# ├── models/
# │   ├── vosk-model-de/
# │   └── qwen3-tts/
# ├── qwen3-tts-service/
# │   ├── Dockerfile
# │   ├── requirements.txt
# │   └── server.py
# └── logs/
```

#### Schritt 1.3: Vosk Modell herunterladen

```bash
cd ~/openclaw-voice-agent/models
wget https://alphacephei.com/vosk/models/vosk-model-de-0.21.zip
unzip vosk-model-de-0.21.zip
mv vosk-model-de-0.21 vosk-model-de
rm vosk-model-de-0.21.zip
```

#### Schritt 1.4: Ollama Setup

```bash
# Ollama installieren
curl -fsSL https://ollama.ai/install.sh | sh

# Modell herunterladen
ollama pull qwen3:14b

# Test
ollama run qwen3:14b "Hallo, wie geht es dir?"
```

### Phase 2: Voice Agent Core (Tag 3-5)

#### Schritt 2.1: Qwen3-TTS Service erstellen

```dockerfile
# qwen3-tts-service/Dockerfile
FROM nvidia/cuda:12.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY server.py .

EXPOSE 6012

CMD ["python3", "server.py"]
```

```text
# qwen3-tts-service/requirements.txt
fastapi>=0.100.0
uvicorn>=0.23.0
qwen-tts
torch>=2.0.0
numpy
scipy
```

```python
# qwen3-tts-service/server.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io
import os

app = FastAPI(title="Qwen3-TTS Service")

# Lazy loading für GPU-Speicher
tts_model = None

def get_tts():
    global tts_model
    if tts_model is None:
        from qwen_tts import QwenTTS
        model_size = os.getenv("MODEL_SIZE", "1.7B")
        model_name = f"Qwen/Qwen3-TTS-12Hz-{model_size}-Base"
        print(f"Loading {model_name}...")
        tts_model = QwenTTS(model_name=model_name)
        print("Model loaded!")
    return tts_model

class TTSRequest(BaseModel):
    text: str
    language: str = "de"

@app.post("/text-to-speech-stream")
async def text_to_speech_stream(request: TTSRequest):
    """AVR-kompatibler TTS Streaming Endpoint"""
    tts = get_tts()
    
    async def generate():
        try:
            for chunk in tts.generate_stream(
                text=request.text, 
                language=request.language
            ):
                yield chunk
        except Exception as e:
            print(f"TTS Error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return StreamingResponse(
        generate(),
        media_type="audio/wav",
        headers={"Transfer-Encoding": "chunked"}
    )

@app.post("/text-to-speech")
async def text_to_speech(request: TTSRequest):
    """Non-streaming TTS Endpoint"""
    tts = get_tts()
    
    try:
        audio = tts.generate(text=request.text, language=request.language)
        buffer = io.BytesIO()
        audio.save(buffer, format="wav")
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model_loaded": tts_model is not None,
        "model_size": os.getenv("MODEL_SIZE", "1.7B")
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 6012))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

#### Schritt 2.2: Docker Compose erstellen

```yaml
# docker-compose.yml
version: '3.8'

services:
  # ============================================
  # ASTERISK PBX - Telefonie Server
  # ============================================
  asterisk:
    image: andrius/asterisk:18
    container_name: openclaw-asterisk
    restart: unless-stopped
    ports:
      - "5060:5060/udp"      # SIP UDP
      - "5060:5060/tcp"      # SIP TCP
      - "5061:5061/tcp"      # SIP TLS
      - "10000-10100:10000-10100/udp"  # RTP Media
    volumes:
      - ./config/asterisk:/etc/asterisk:ro
      - ./logs/asterisk:/var/log/asterisk
    networks:
      - openclaw-network
    # Für GSM Dongle:
    # devices:
    #   - /dev/ttyUSB0:/dev/ttyUSB0
    #   - /dev/ttyUSB1:/dev/ttyUSB1
    #   - /dev/ttyUSB2:/dev/ttyUSB2

  # ============================================
  # AVR CORE - Voice Agent Orchestrierung
  # ============================================
  avr-core:
    image: agentvoiceresponse/avr-core
    container_name: openclaw-avr-core
    restart: unless-stopped
    environment:
      - PORT=5001
      - ASR_URL=http://avr-asr:6010/speech-to-text-stream
      - LLM_URL=http://avr-llm:6002/prompt-stream
      - TTS_URL=http://qwen3-tts:6012/text-to-speech-stream
      - INTERRUPT_LISTENING=true
      - SYSTEM_MESSAGE=Hallo, hier ist OpenClaw. Wie kann ich dir helfen?
    ports:
      - "5001:5001"
    networks:
      - openclaw-network
    depends_on:
      - avr-asr
      - avr-llm
      - qwen3-tts

  # ============================================
  # ASR - Speech-to-Text (Vosk)
  # ============================================
  avr-asr:
    image: agentvoiceresponse/avr-asr-vosk
    container_name: openclaw-asr
    restart: unless-stopped
    environment:
      - PORT=6010
      - MODEL_PATH=model
    volumes:
      - ./models/vosk-model-de:/usr/src/app/model:ro
    networks:
      - openclaw-network

  # ============================================
  # OLLAMA - LLM Server
  # ============================================
  ollama:
    image: ollama/ollama:latest
    container_name: openclaw-ollama
    restart: unless-stopped
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    networks:
      - openclaw-network
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # ============================================
  # AVR LLM Adapter - OpenAI-kompatibler Wrapper
  # ============================================
  avr-llm:
    image: agentvoiceresponse/avr-llm-openai
    container_name: openclaw-llm-adapter
    restart: unless-stopped
    environment:
      - PORT=6002
      - OPENAI_BASEURL=http://ollama:11434/v1
      - OPENAI_API_KEY=sk-local-dummy
      - OPENAI_MODEL=qwen3:14b
      - OPENAI_MAX_TOKENS=150
      - OPENAI_TEMPERATURE=0.7
      - SYSTEM_PROMPT=Du bist OpenClaw, ein intelligenter KI-Assistent. Antworte kurz und präzise auf Deutsch. Maximal 2-3 Sätze.
    networks:
      - openclaw-network
    depends_on:
      - ollama

  # ============================================
  # QWEN3-TTS - Text-to-Speech
  # ============================================
  qwen3-tts:
    build:
      context: ./qwen3-tts-service
      dockerfile: Dockerfile
    container_name: openclaw-tts
    restart: unless-stopped
    environment:
      - PORT=6012
      - MODEL_SIZE=1.7B
    ports:
      - "6012:6012"
    volumes:
      - huggingface-cache:/root/.cache/huggingface
    networks:
      - openclaw-network
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

networks:
  openclaw-network:
    driver: bridge

volumes:
  ollama-data:
  huggingface-cache:
```

#### Schritt 2.3: Asterisk Konfiguration

```ini
# config/asterisk/pjsip.conf
[global]
type=global
user_agent=OpenClaw-Asterisk

[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0:5060

; Lokaler Test-Endpoint (Softphone)
[softphone-auth]
type=auth
auth_type=userpass
username=1000
password=openclaw123

[softphone-aor]
type=aor
max_contacts=1

[softphone]
type=endpoint
context=from-internal
disallow=all
allow=ulaw
allow=alaw
auth=softphone-auth
aors=softphone-aor
```

```ini
# config/asterisk/extensions.conf
[general]
static=yes
writeprotect=no

[globals]
AVR_HOST=avr-core
AVR_PORT=5001

[from-internal]
; Eingehende Anrufe von lokalem Softphone
exten => 100,1,NoOp(Test call to Voice Agent)
 same => n,Answer()
 same => n,Wait(1)
 same => n,AudioSocket(${AVR_HOST}:${AVR_PORT},${UNIQUEID})
 same => n,Hangup()

[from-external]
; Eingehende Anrufe von SIP Trunk / GSM
exten => _X.,1,NoOp(External call from ${CALLERID(num)})
 same => n,Answer()
 same => n,Wait(1)
 same => n,AudioSocket(${AVR_HOST}:${AVR_PORT},${UNIQUEID})
 same => n,Hangup()

[from-dongle]
; Eingehende Anrufe vom GSM Dongle
exten => s,1,NoOp(GSM call from ${CALLERID(num)})
 same => n,Answer()
 same => n,Wait(1)
 same => n,AudioSocket(${AVR_HOST}:${AVR_PORT},${UNIQUEID})
 same => n,Hangup()

[outbound]
; Ausgehende Anrufe
exten => _0X.,1,NoOp(Outbound call to ${EXTEN})
 same => n,Dial(PJSIP/${EXTEN}@siptrunk,60)
 same => n,Hangup()
```

### Phase 3: Test & Integration (Tag 6-7)

#### Schritt 3.1: System starten

```bash
cd ~/openclaw-voice-agent

# Qwen3-TTS Image bauen
docker compose build qwen3-tts

# Ollama Modell vorbereiten (einmalig)
docker compose up -d ollama
sleep 10
docker exec openclaw-ollama ollama pull qwen3:14b

# Alle Services starten
docker compose up -d

# Logs überprüfen
docker compose logs -f
```

#### Schritt 3.2: Health Checks

```bash
# AVR Core
curl http://localhost:5001/health

# Qwen3-TTS
curl http://localhost:6012/health

# Ollama
curl http://localhost:11434/api/tags

# Asterisk
docker exec openclaw-asterisk asterisk -rx "pjsip show endpoints"
```

#### Schritt 3.3: Test mit Softphone

1. **Softphone installieren** (Linphone, Zoiper, oder MicroSIP)
2. **SIP Account konfigurieren:**
   - Server: `localhost:5060` (oder IP des Servers)
   - Username: `1000`
   - Password: `openclaw123`
3. **Nummer wählen:** `100`
4. **Sprechen und testen!**

### Phase 4: Telefonie Setup (Tag 8-10)

#### Option A: GSM Dongle

```bash
# USB Dongle einstecken und prüfen
lsusb  # Sollte Huawei o.ä. zeigen

# Device-Dateien prüfen
ls -la /dev/ttyUSB*

# In docker-compose.yml die devices einkommentieren
# und neu starten
docker compose down
docker compose up -d
```

#### Option B: SIP Trunk

```ini
# Zu config/asterisk/pjsip.conf hinzufügen:

[siptrunk]
type=registration
transport=transport-udp
outbound_auth=siptrunk-auth
server_uri=sip:sipgate.de
client_uri=sip:DEIN_USERNAME@sipgate.de
retry_interval=60

[siptrunk-auth]
type=auth
auth_type=userpass
username=DEIN_USERNAME
password=DEIN_PASSWORT

[siptrunk-endpoint]
type=endpoint
transport=transport-udp
context=from-external
disallow=all
allow=ulaw
allow=alaw
outbound_auth=siptrunk-auth
aors=siptrunk

[siptrunk]
type=aor
contact=sip:sipgate.de
```

---

## 8. Docker-Konfigurationen

### 8.1 Vollständiges Docker Compose (Produktiv)

Siehe Abschnitt 7, Schritt 2.2 für die vollständige `docker-compose.yml`.

### 8.2 Ressourcen-Limits (Optional)

```yaml
# Zusatz für docker-compose.yml
services:
  qwen3-tts:
    # ... bestehende Konfiguration ...
    deploy:
      resources:
        limits:
          memory: 16G
        reservations:
          memory: 8G
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  ollama:
    # ... bestehende Konfiguration ...
    deploy:
      resources:
        limits:
          memory: 20G
        reservations:
          memory: 12G
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 8.3 Nützliche Docker Befehle

```bash
# Alle Logs
docker compose logs -f

# Nur einen Service
docker compose logs -f qwen3-tts

# Neustart einzelner Service
docker compose restart avr-core

# In Container shell
docker exec -it openclaw-asterisk bash
docker exec -it openclaw-ollama bash

# Asterisk CLI
docker exec -it openclaw-asterisk asterisk -rvvv

# Ressourcenverbrauch
docker stats
```

---

## 9. Kosten und Betrieb

### 9.1 Einmalige Kosten

| Posten | Option A (Minimal) | Option B (Empfohlen) |
|--------|-------------------|---------------------|
| GSM Dongle | 20 CHF | 30 CHF |
| Prepaid SIM | 10 CHF | 10 CHF |
| **Total** | **30 CHF** | **40 CHF** |

*Bestehende Hardware (RTX 3090 Workstation) vorausgesetzt.*

### 9.2 Laufende Kosten

| Posten | Monatlich |
|--------|-----------|
| Prepaid Guthaben | ~5-20 CHF (je nach Nutzung) |
| SIP Trunk (optional) | 0-10 CHF |
| Strom (24/7, ~150W avg) | ~25-35 CHF |
| **Total** | **30-65 CHF** |

### 9.3 Vergleich mit Cloud-Alternativen

| Lösung | Kosten/Monat | Kontrolle | Datenschutz |
|--------|--------------|-----------|-------------|
| **OpenClaw (Self-Hosted)** | ~30-65 CHF | ⭐⭐⭐ | ⭐⭐⭐ |
| Twilio + OpenAI + ElevenLabs | ~100-500 CHF | ⭐⭐ | ⭐ |
| Vapi.ai | ~100-300 CHF | ⭐ | ⭐ |
| Retell.ai | ~150-400 CHF | ⭐ | ⭐ |

---

## 10. Roadmap und Erweiterungen

### 10.1 Kurzfristig (1-2 Monate)

- [ ] Basis-System lauffähig
- [ ] Telefonie (GSM oder SIP)
- [ ] Erste Tests mit echten Anrufen
- [ ] Voice Cloning mit eigener Stimme

### 10.2 Mittelfristig (3-6 Monate)

- [ ] **IntelliPlan Integration**
  - Projektdaten per Sprache abrufen
  - Termine erstellen/ändern
  - Status-Updates

- [ ] **Tool Calling**
  - Kalender-Integration
  - E-Mail senden
  - Erinnerungen setzen

- [ ] **Multi-Sprachen**
  - Automatische Spracherkennung
  - Antwort in gleicher Sprache

### 10.3 Langfristig (6-12 Monate)

- [ ] **Web-Interface**
  - Pipecat für WebRTC
  - Browser-basierter Assistent

- [ ] **Mobile App**
  - Direkte SIP-Verbindung
  - Push-Benachrichtigungen

- [ ] **Multi-Agent**
  - Verschiedene Personas
  - Weiterleitung an Spezialisten

- [ ] **Analytics**
  - Anruf-Statistiken
  - Sentiment-Analyse
  - Gesprächstranskripte

### 10.4 Mögliche Erweiterungen

```
┌─────────────────────────────────────────────────────────────┐
│                 OPENCLAW ERWEITERUNGEN                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   IntelliPlan   │    │   Home          │                │
│  │   Integration   │    │   Assistant     │                │
│  │                 │    │                 │                │
│  │ • Projekte      │    │ • Licht         │                │
│  │ • Aufgaben      │    │ • Heizung       │                │
│  │ • Termine       │    │ • Geräte        │                │
│  └────────┬────────┘    └────────┬────────┘                │
│           │                      │                          │
│           └──────────┬───────────┘                          │
│                      │                                      │
│                      ▼                                      │
│           ┌─────────────────────┐                           │
│           │   OPENCLAW CORE     │                           │
│           │                     │                           │
│           │   • Voice Agent     │                           │
│           │   • Tool Calling    │                           │
│           │   • MCP Server      │                           │
│           └─────────────────────┘                           │
│                      │                                      │
│           ┌──────────┴───────────┐                          │
│           │                      │                          │
│           ▼                      ▼                          │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   Kalender      │    │   E-Mail        │                │
│  │   Integration   │    │   Integration   │                │
│  │                 │    │                 │                │
│  │ • Google Cal    │    │ • Gmail         │                │
│  │ • Outlook       │    │ • IMAP/SMTP     │                │
│  └─────────────────┘    └─────────────────┘                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Anhang A: Troubleshooting

### Problem: Qwen3-TTS lädt nicht

```bash
# VRAM prüfen
nvidia-smi

# Kleineres Modell versuchen
# In docker-compose.yml:
environment:
  - MODEL_SIZE=0.6B
```

### Problem: Asterisk verbindet nicht mit AVR

```bash
# Netzwerk prüfen
docker network inspect openclaw-network

# Ports prüfen
docker exec openclaw-asterisk netstat -tlnp

# AVR Core Logs
docker compose logs avr-core
```

### Problem: Keine Audiowiedergabe

```bash
# Codec-Unterstützung prüfen
docker exec openclaw-asterisk asterisk -rx "core show codecs"

# RTP Ports prüfen
docker exec openclaw-asterisk asterisk -rx "rtp set debug on"
```

---

## Anhang B: Referenzen

- **Qwen3-TTS:** https://github.com/QwenLM/Qwen3-TTS
- **AVR:** https://github.com/agentvoiceresponse
- **Pipecat:** https://github.com/pipecat-ai/pipecat
- **Asterisk:** https://www.asterisk.org/
- **Ollama:** https://ollama.ai/
- **Vosk:** https://alphacephei.com/vosk/
- **chan_dongle:** https://github.com/wdoekes/asterisk-chan-dongle

---

*Dokument erstellt für das OpenClaw Voice Agent Projekt*
*Letzte Aktualisierung: Februar 2026*
