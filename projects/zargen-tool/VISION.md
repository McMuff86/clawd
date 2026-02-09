# ZargenTool - Vision & Projektplan

**Digitalisierung der Zargen-/Türblatt-Kalkulation**

*Stand: 28. Januar 2026*

---

## 🎯 Executive Summary

Transformation der Excel-basierten Zargen-/Türblattliste in ein modernes, integriertes System:

- **Web-Oberfläche** für einfache Dateneingabe
- **Automatische Kalkulation** (Python-basiert, wartbar)
- **CAD-Integration** (Rhino/Grasshopper) für 3D-Generierung
- **Bidirektionale Synchronisation** zwischen Web-UI und CAD
- **Automatisierte Exports** für Produktion und Bestellung

**Ziel:** Fehlerreduktion, Zeitersparnis, durchgängiger digitaler Workflow

---

## 📊 Ist-Zustand (Probleme)

| Problem | Auswirkung |
|---------|------------|
| Excel mit VBA-Makros | Schwer wartbar, fehleranfällig |
| Manuelle Dateneingabe | Tippfehler, Inkonsistenzen |
| Keine CAD-Verbindung | Doppelte Datenpflege |
| PDF-Export manuell | Zeitaufwändig |
| Keine Validierung | Ungültige Kombinationen möglich |
| Wissen in Excel versteckt | Abhängigkeit von Einzelpersonen |

---

## 🚀 Soll-Zustand (Vision)

```
┌─────────────────────────────────────────────────────────────────┐
│                        ZargenTool                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │   Web-UI     │◄───►│   Backend    │◄───►│   Rhino/GH   │    │
│  │  (Eingabe)   │     │  (Python)    │     │   (3D/CAD)   │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│         │                    │                    │             │
│         ▼                    ▼                    ▼             │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │  Validierung │     │  Kalkulation │     │ 3D-Elemente  │    │
│  │  & Eingabe   │     │  & Preise    │     │ im Grundriss │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│                              │                                  │
│                              ▼                                  │
│                       ┌──────────────┐                         │
│                       │    Export    │                         │
│                       │ PDF/Excel/   │                         │
│                       │ Bestellung   │                         │
│                       └──────────────┘                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💡 Kernfunktionen

### 1. Web-Oberfläche
- Übersichtliche Eingabemaske für Türpositionen
- Dropdown-Menüs für Standardwerte (Zargenprofile, Bandtypen, etc.)
- Echtzeit-Validierung (Plausibilitätsprüfung)
- Projektübersicht mit Filterfunktionen
- Mobile-friendly (Tablet auf Baustelle)

### 2. Intelligente Kalkulation
- Python-basiert (testbar, versionierbar, wartbar)
- Regelbasierte Preisberechnung
- Automatische Zuschläge (Sondermasse, Ausführungen)
- Transparente Berechnungslogik

### 3. CAD-Integration (RhinoMCP)
- Türelemente im Grundriss generieren
- Position aus CAD übernehmen → Web-UI
- Änderungen in Web-UI → CAD aktualisieren
- Massabgleich Planung ↔ Kalkulation

### 4. Automatisierte Exports
- **Bestellliste Zargen** (Lieferant-Format)
- **Bestellliste Türblätter** (Lieferant-Format)
- **Produktionsliste** (interne Fertigung)
- **Preiszusammenstellung** (Kunde)
- **PDF-Dokumentation** (Projektordner)

---

## 📈 Nutzen / ROI

### Zeitersparnis
| Tätigkeit | Heute | Mit Tool | Ersparnis |
|-----------|-------|----------|-----------|
| Dateneingabe pro Projekt | 4h | 1h | 75% |
| Fehlerkorrektur | 2h | 0.25h | 87% |
| Export/Formatierung | 1h | 5min | 92% |
| CAD-Abgleich | 2h | 0h (automatisch) | 100% |
| **Pro Projekt** | **9h** | **1.5h** | **83%** |

### Qualitätsverbesserung
- ✅ Keine Tippfehler durch Dropdown-Auswahl
- ✅ Automatische Plausibilitätsprüfung
- ✅ Konsistente Daten CAD ↔ Kalkulation
- ✅ Nachvollziehbare Berechnungen
- ✅ Versionierung / Änderungshistorie

### Strategischer Wert
- 🔧 Unabhängigkeit von Excel-Experten
- 📚 Wissen im System dokumentiert
- 🔄 Skalierbar für mehr Projekte
- 🚀 Grundlage für weitere Automatisierung

---

## 🗓️ Implementierungsplan

### Phase 1: Foundation (2-3 Wochen)
**Ziel:** Lauffähiger Prototyp mit Basisfunktionen

- [ ] Datenmodell definieren (Türen, Zargen, Optionen)
- [ ] Backend-API (Python/FastAPI)
- [ ] Einfache Web-UI (Eingabe + Liste)
- [ ] Import bestehender Excel-Daten
- [ ] Export: Excel-Liste

**Lieferobjekt:** Web-UI die Excel ersetzen kann

### Phase 2: Kalkulation (2 Wochen)
**Ziel:** Automatische Preisberechnung

- [ ] Preislogik aus Excel extrahieren
- [ ] Kalkulationsmodul implementieren
- [ ] Zuschlagsberechnung (Masse, Sonderausführungen)
- [ ] Preiszusammenstellung generieren

**Lieferobjekt:** Automatische Kalkulation wie bisher

### Phase 3: CAD-Integration (2-3 Wochen)
**Ziel:** Bidirektionale Sync mit Rhino

- [ ] RhinoMCP-Anbindung
- [ ] Türelemente aus Daten generieren
- [ ] Positionen aus CAD importieren
- [ ] Änderungen synchronisieren

**Lieferobjekt:** Türen erscheinen automatisch im Grundriss

### Phase 4: Export & Polish (1-2 Wochen)
**Ziel:** Produktionsreife

- [ ] Bestelllisten-Export (Lieferanten-Format)
- [ ] PDF-Generierung
- [ ] Benutzerrollen (Projektleiter, Sachbearbeiter)
- [ ] Dokumentation & Schulung

**Lieferobjekt:** Vollständig einsatzbereites System

---

## ⏱️ Zeitaufwand Gesamt

| Phase | Aufwand | Zeitraum |
|-------|---------|----------|
| Phase 1: Foundation | 40-50h | 2-3 Wochen |
| Phase 2: Kalkulation | 25-35h | 2 Wochen |
| Phase 3: CAD-Integration | 35-45h | 2-3 Wochen |
| Phase 4: Export & Polish | 15-25h | 1-2 Wochen |
| **Gesamt** | **~120-150h** | **7-10 Wochen** |

*Bei 8h/Woche Projektzeit: ~4-5 Monate bis produktiv*
*Bei 16h/Woche: ~2-3 Monate*

---

## 🛠️ Technologie-Stack

| Komponente | Technologie | Grund |
|------------|-------------|-------|
| Backend | Python + FastAPI | Schnell, modern, gut für Berechnungen |
| Frontend | React oder Vue | Interaktive UI, weit verbreitet |
| Datenbank | SQLite → PostgreSQL | Einfacher Start, skalierbar |
| CAD | Rhino + RhinoMCP | Bestehende Infrastruktur |
| Hosting | Lokal / Intranet | Datenschutz, kein Cloud-Zwang |

---

## 🚦 Nächste Schritte

### Sofort (diese Woche)
1. ✅ Excel-Struktur analysiert
2. ⏳ Vision mit Chef besprechen
3. ⏳ Zeitbudget klären

### Bei Freigabe
1. Datenmodell finalisieren
2. Erster Prototyp (Web-UI mit Eingabe)
3. Pilotprojekt identifizieren

---

## 💬 Diskussionspunkte für Chef-Gespräch

1. **Priorität vs. Tagesgeschäft** - Wie viel Zeit pro Woche?
2. **Pilotprojekt** - Welches Projekt als Testlauf?
3. **Rollout** - Schrittweise oder Big Bang?
4. **Schulung** - Wer soll das Tool nutzen?
5. **Wartung** - Langfristige Betreuung

---

*Erstellt von: Sentinel (AI-Assistent)*
*Kontakt: Adrian Muff*
