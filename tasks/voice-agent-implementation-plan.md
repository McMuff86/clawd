# OpenClaw Voice Agent – Analyse & Implementierungsplan

Erstellt: 02.02.2026  
Basierend auf: `tasks/OpenClaw_Voice_Agent_Dokumentation.md`

---

## 📊 Stärken/Schwächen-Analyse

### ✅ Stärken des vorgeschlagenen Stacks

| Bereich | Stärke | Bewertung |
|---------|--------|-----------|
| **100% Self-Hosted** | Keine Cloud-Dependencies, keine laufenden API-Kosten | ⭐⭐⭐ |
| **Datenschutz** | Alle Daten lokal, DSGVO/DSG-konform by design | ⭐⭐⭐ |
| **Hardware vorhanden** | RTX 3090 + Threadripper = ideale Entwicklungsplattform | ⭐⭐⭐ |
| **Qwen3-TTS** | State-of-the-art, Voice Cloning, 10 Sprachen, Apache 2.0 | ⭐⭐⭐ |
| **Qwen3-TTS Expertise** | Adi hat bereits Erfahrung (Repo, Gradio App, Modelle geladen) | ⭐⭐⭐ |
| **Kosten** | ~30-65 CHF/Monat vs. 100-500 CHF Cloud-Lösungen | ⭐⭐⭐ |
| **AVR Framework** | Telefonie-ready, Docker-basiert, modulare Services | ⭐⭐ |
| **Ollama** | Bewährt, einfach, OpenAI-kompatible API | ⭐⭐⭐ |
| **Erweiterbarkeit** | IntelliPlan-Integration, Tool-Calling, Multi-Agent | ⭐⭐ |

### ❌ Schwächen & Risiken

| Bereich | Risiko | Schwere | Mitigation |
|---------|--------|---------|------------|
| **VRAM-Knappheit** | TTS 1.7B (~10GB) + LLM 14B (~10GB) + Overhead = 24GB knapp | 🔴 Hoch | 0.6B TTS oder 7B LLM verwenden; Model-Offloading |
| **Latenz** | Pipeline ASR→LLM→TTS könnte >2s End-to-End sein | 🟡 Mittel | Streaming, Vosk statt Whisper, Token-Level TTS |
| **AVR Maturity** | Kleinere Community, weniger Battle-tested als Pipecat | 🟡 Mittel | AVR für Telefonie, Pipecat als Backup |
| **Qwen3-TTS Streaming** | Streaming-API Stabilität unklar für Produktions-Telefonie | 🟡 Mittel | Fallback auf Non-Streaming mit Buffer |
| **Asterisk Komplexität** | PBX-Konfiguration ist komplex, schwer zu debuggen | 🟡 Mittel | Schritt-für-Schritt, erst Softphone |
| **GSM Dongle** | chan_dongle ist ein Community-Projekt, Kompatibilität variiert | 🟡 Mittel | SIP Trunk als Alternative bereithalten |
| **24/7 Betrieb** | Workstation ist nicht für Dauerbetrieb gedacht (Strom, Lärm) | 🟡 Mittel | Erst Workstation, später Mini-PC |
| **Deutsch ASR** | Vosk Deutsch-Modell ist akzeptabel, nicht perfekt | 🟡 Mittel | Whisper als Fallback, Fine-Tuning |
| **Interrupt Handling** | Natürliches Unterbrechen (Barge-in) ist komplex | 🟡 Mittel | AVR hat Barge-in Support |
| **Single Point of Failure** | Alles auf einer Maschine | 🟢 Niedrig | Für MVP akzeptabel |

### ⚠️ Fehlende Aspekte in der Dokumentation

1. **Monitoring & Alerting** – Was passiert wenn ein Service crasht?
2. **Logging & Analytics** – Gesprächstranskripte, Qualitätsmetriken
3. **Graceful Degradation** – Was wenn GPU out-of-memory?
4. **Security** – SIP-Sicherheit, Asterisk Hardening
5. **Testing** – Wie testet man Voice-Qualität automatisiert?
6. **Update-Strategie** – Wie werden Modelle/Container aktualisiert?
7. **Concurrent Calls** – Was bei 2+ gleichzeitigen Anrufen?
8. **Kontext-Persistenz** – Wie merkt sich der Agent vorherige Gespräche?
9. **Fallback-Verhalten** – Was wenn der Agent nicht versteht?
10. **Warm-up Zeit** – Model-Loading bei erstem Anruf (~10-20s)

---

## 🏗️ Implementierungsplan in Phasen

### Phase 0: Vorbereitung (1-2 Tage) 🟢
**Ziel:** Umgebung ready, alle Abhängigkeiten geklärt

- [ ] NVIDIA Container Toolkit in WSL2 verifizieren
- [ ] Docker Compose Basis aufsetzen (`~/projects/openclaw-voice-agent/`)
- [ ] Projektstruktur erstellen (config/, models/, logs/, src/)
- [ ] Vosk Deutsch-Modell herunterladen (~1.5GB)
- [ ] Ollama installieren + qwen3:7b laden (erst 7B, sicherer für VRAM)
- [ ] Git Repo initialisieren

**Deliverable:** Leere aber funktionale Docker-Umgebung

---

### Phase 1: TTS-Service (2-3 Tage) 🟡
**Ziel:** Qwen3-TTS als eigenständiger HTTP-Service

- [ ] FastAPI Service für Qwen3-TTS bauen (basierend auf `src/engine.py` vom TTS-Repo!)
- [ ] Dockerfile mit CUDA Support
- [ ] Endpoints: `/health`, `/text-to-speech`, `/text-to-speech-stream`
- [ ] AVR-kompatibles Audio-Format (PCM 16-bit, 8kHz für Telefonie)
- [ ] Resampling von 24kHz TTS-Output auf 8kHz Telefonie
- [ ] Model warm-up bei Container-Start
- [ ] VRAM-Monitoring Endpoint
- [ ] Testen: curl → Audio-File → Abspielen

**Deliverable:** Standalone TTS-Service, aufrufbar via HTTP

**Synergie mit Qwen3-TTS Repo:** 
- `src/engine.py` → Basis für den TTS-Server
- `src/config.py` → Config-Pattern wiederverwenden
- `src/audio_utils.py` → Resampling-Funktionen

---

### Phase 2: ASR + LLM Services (2-3 Tage) 🟡
**Ziel:** Speech-to-Text und LLM funktional

- [ ] Vosk ASR Container aufsetzen (AVR Docker Image)
- [ ] Ollama Container mit GPU-Zugriff
- [ ] LLM Adapter (AVR avr-llm-openai Image)
- [ ] System Prompt definieren und testen
- [ ] End-to-End Test: Audio-File → Text → LLM-Antwort → TTS-Audio
- [ ] Latenz messen und dokumentieren

**Deliverable:** Funktionierende ASR→LLM→TTS Pipeline (ohne Telefonie)

---

### Phase 3: AVR Core + WebSocket (2-3 Tage) 🟡
**Ziel:** Voice Agent funktioniert über WebSocket

- [ ] AVR Core Container einrichten
- [ ] WebSocket-Transport konfigurieren
- [ ] Silero VAD integrieren
- [ ] Interrupt-Handling (Barge-in) testen
- [ ] Test mit Browser-basiertem Audio-Client
- [ ] Latenz-Optimierung: Streaming Pipeline tunen

**Deliverable:** Funktionierender Voice Agent über WebSocket (Browser)

---

### Phase 4: Asterisk + Softphone (3-4 Tage) 🟠
**Ziel:** Telefonie-Grundlage steht

- [ ] Asterisk Container aufsetzen
- [ ] PJSIP Basis-Konfiguration
- [ ] AudioSocket Verbindung zu AVR Core
- [ ] Lokaler Softphone-Test (Linphone/Zoiper)
- [ ] Anruf annehmen → Voice Agent antwortet
- [ ] Audio-Qualität prüfen (Codec-Konfiguration)
- [ ] Dialplan für ein- und ausgehende Anrufe

**Deliverable:** Funktionierende Telefonie über lokales Softphone

---

### Phase 5: Echte Telefonie (2-3 Tage) 🟠
**Ziel:** Erreichbar über echte Telefonnummer

- [ ] Option A: GSM Dongle + chan_dongle ODER
- [ ] Option B: SIP Trunk (sipgate/peoplefone)
- [ ] Konfiguration in Asterisk
- [ ] Test mit echtem Telefonanruf
- [ ] Audio-Qualität über Mobilfunk prüfen
- [ ] Robustheit: Was bei schlechter Verbindung?

**Deliverable:** Voice Agent über echte Telefonnummer erreichbar

---

### Phase 6: Intelligence & Integration (ongoing) 🔵
**Ziel:** Nützliche Features, IntelliPlan-Anbindung

- [ ] Tool-Calling für Ollama konfigurieren
- [ ] Kalender-Abfrage (Google Calendar via gog)
- [ ] Erinnerungen setzen per Sprachbefehl
- [ ] IntelliPlan API-Anbindung (Projekte, Tasks)
- [ ] Gesprächstranskripte speichern
- [ ] Kontext-Persistenz über Anrufe hinweg
- [ ] Voice Cloning mit Adis Stimme

---

## 📐 Technische Entscheidungen

### VRAM-Strategie (kritisch!)

**Option A: Shared GPU (RTX 3090)**
```
Qwen3-TTS 0.6B  →  ~4 GB
Ollama qwen3:7b  → ~5 GB
Vosk             →  CPU (0 GB GPU)
Silero VAD       →  CPU (<1 MB)
Reserve          →  ~15 GB frei
─────────────────────────────
Total: ~9 GB / 24 GB ✅ Komfortabel
```

**Option B: Maximale Qualität**
```
Qwen3-TTS 1.7B  → ~10 GB
Ollama qwen3:14b → ~10 GB
─────────────────────────────
Total: ~20 GB / 24 GB ⚠️ Knapp
```

**Empfehlung:** Start mit Option A (0.6B + 7B), upgrade wenn stabil.

### Latenz-Budget

| Schritt | Ziel | Worst Case |
|---------|------|------------|
| VAD → Sprache erkannt | <100ms | 200ms |
| ASR (Vosk) | <200ms | 500ms |
| LLM (7B, 2-3 Sätze) | <500ms | 1500ms |
| TTS (0.6B, Streaming) | <200ms first token | 500ms |
| **Total** | **<1000ms** | **<2700ms** |

Ziel: <1.5 Sekunden End-to-End für natürliche Konversation.

### Audio-Format Konvertierung

```
Telefon (8kHz μ-law) → Asterisk → PCM 16-bit → Vosk (16kHz)
                                                     ↓
Telefon (8kHz μ-law) ← Asterisk ← PCM 16-bit ← TTS (24kHz → resample)
```

---

## 🗓️ Zeitschätzung

| Phase | Dauer | Abhängigkeit |
|-------|-------|-------------|
| Phase 0: Vorbereitung | 1-2 Tage | - |
| Phase 1: TTS-Service | 2-3 Tage | Phase 0 |
| Phase 2: ASR + LLM | 2-3 Tage | Phase 0 |
| Phase 3: AVR Core | 2-3 Tage | Phase 1 + 2 |
| Phase 4: Asterisk | 3-4 Tage | Phase 3 |
| Phase 5: Telefonie | 2-3 Tage | Phase 4 |
| Phase 6: Integration | Ongoing | Phase 5 |
| **Total bis MVP** | **~12-18 Tage** | |

*Bei ~2h/Abend Arbeitszeit = ~6-9 Wochen realistisch.*

---

## 🔄 Beziehung zu anderen Projekten

### Qwen3-TTS Voice Clone Repo
- `src/engine.py` → Direkte Wiederverwendung für TTS-Service
- `src/config.py` → Config-Pattern
- `src/audio_utils.py` → Resampling-Funktionen
- Voice Cloning Feature → Adis Stimme für den Agent

### IntelliPlan
- REST-API als Tool für den Voice Agent
- Projekte/Tasks per Sprache abrufen/erstellen
- Termine per Sprachbefehl planen

### OpenClaw (Sentinel)
- Sentinel als "Gehirn" hinter dem Voice Agent?
- Oder separater Agent mit eigenem LLM?
- → Entscheidung in Phase 6

---

## ✅ Nächste konkrete Schritte

1. **NVIDIA Container Toolkit testen** (`docker run --gpus all nvidia/cuda:12.1-base nvidia-smi`)
2. **Projektstruktur erstellen** (`~/projects/openclaw-voice-agent/`)
3. **Vosk-Modell downloaden**
4. **TTS-Service Dockerfile schreiben** (basierend auf Qwen3-TTS engine.py)
5. **Docker Compose v1** (TTS + Vosk + Ollama)

---

*Dieses Dokument wird aktualisiert sobald Phasen abgeschlossen werden.*
