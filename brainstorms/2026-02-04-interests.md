# Brainstorm: Was könnte Adi interessieren?
*Erstellt: 4. Februar 2026, 01:30 Uhr*

---

## 1. SaaS-Ideen für die Fertigungsbranche

### 1.1 🏆 Leichtgewicht-ERP für Schweizer Schreinereien
**Was:** Ein schlankes, Cloud-basiertes Projektmanagement-/ERP-Tool speziell für kleine Schreinereien (5-30 Mitarbeiter). Fokus auf: Auftragserfassung → Stücklisten → CNC-Übergabe → Montageplanung.

**Warum relevant:** Die Schreinerzeitung Schweiz listet zwar ERP-Systeme auf, aber die meisten (SWOOD, Imos, CADmatic) sind schwerfällig und teuer. Schweizer KMU-Schreinereien arbeiten oft noch mit Excel + Papier. IntelliPlan könnte genau diese Lücke füllen – ein "Stripe for Schreinereien": simpel, modern, bezahlbar.

**Marktgrösse:** ~5'000 Schreinereien in der Schweiz, ~100'000 in DACH. Selbst mit 50-100 CHF/Monat pro Betrieb massiv skalierbar.

**Links:**
- [Schreinerzeitung Digitalisierung](https://www.schreinerzeitung.ch/de/themen/digitalisierung)
- [topsoft ERP-Marktübersicht CH](https://topsoft.ch/themen/marktuebersicht-erp-fuer-kmu/)

---

### 1.2 📐 CAD-to-CNC Bridge (Nesting + Schnittoptimierung)
**Was:** SaaS-Tool das 3D-Modelle (Rhino, STEP, DXF) nimmt und automatisch optimierte CNC-Programme + Nestings erstellt. Für Holz- und Metallbaubetriebe die keinen dedizierten Programmierer haben.

**Warum relevant:** Adi kennt die komplette Pipeline CAD → CNC aus 14 Jahren Erfahrung. Viele kleine Betriebe haben CNC-Maschinen, aber der Engpass ist die Programmierung. Ein Tool das "Modell rein → G-Code raus" kann, wäre Gold wert.

**Differenzierung:** Bestehende Lösungen (Mozaik, CabinetVision) sind monolithisch und teuer. Ein modularer, API-first Ansatz wäre neu.

**Links:**
- [Mozaik Software](https://www.mozaiksoftware.com/) – Etablierter Wettbewerber (Cabinet-fokussiert)
- [Fulcrum Pro](https://fulcrumpro.com/workflows/cnc-machine-shop) – Interessanter neuer Ansatz

---

### 1.3 📊 CNC-Maschinenüberwachung (Lightweight Digital Twin)
**Was:** IoT-basierte Überwachung für CNC-Maschinen in Schreinereien/Metallbau. Einfache Sensoren → Dashboard mit Maschinenstatus, Auslastung, Wartungsvorhersage. Kein Full-Enterprise-IoT, sondern "Plug & Play für KMU".

**Warum relevant:** Digital Twins und IIoT sind 2026 der grosse Trend in der Fertigung, aber NUR für Grossbetriebe zugänglich. Kleine Shops haben keine IT-Abteilung. Ein einfaches System (Raspberry Pi + Sensoren + Web-Dashboard) könnte hier einsteigen.

**Links:**
- [CNC Automation 2026](https://cnccode.com/2025/12/03/cnc-automation-2026-beyond-ai-driven-machine-shops-lights-out-production-and-smart-robotics-revolution/)

---

### 1.4 📝 Intelligente Stücklisten-Automatisierung
**Was:** Tool das aus 3D-CAD-Modellen automatisch Stücklisten, Bestelllisten und Produktionsdokumente generiert. Speziell für Schreinerei: Plattenzuschnitt, Beschläge, Kanten, Oberflächen.

**Warum relevant:** Das ist exakt Adis Schmerz im Alltag (Türblatt-/Zargenlisten). Wenn er das für sich löst, kann er es als Produkt verkaufen. Direkte Verbindung zu IntelliPlan.

---

### 1.5 🤝 Offerttool mit AI-Kalkulation
**Was:** Offerten erstellen mit AI-basierter Preiskalkulation. Input: Grundriss/Raum + gewünschte Einrichtung → Output: Detaillierte Offerte mit Material, Arbeitsstunden, Preis.

**Warum relevant:** Offerten sind in Schreinereien extrem zeitaufwändig und ungenau. Ein Tool das aus historischen Daten lernt und Kalkulationen automatisiert, spart Stunden pro Woche.

---

## 2. AI + CAD/Manufacturing Trends

### 2.1 🧠 Raven – AI-Copilot für Grasshopper
**Was:** Raven ist ein conversational AI Plugin für Grasshopper das direkt GH-Definitionen aus Text-Prompts erstellt. Kein Python/C# – echte GH-Komponenten. Zugriff auf 928+ Community Plugins.

**Warum relevant:** Das ist die direkte Konkurrenz/Ergänzung zu Adis RhinoMCP-Arbeit. Raven zeigt den Markt: AI + Grasshopper ist heiss. Adi könnte:
- Seinen RhinoMCP-Ansatz differenzieren (MCP-Protocol vs. Chat-basiert)
- Raven als Benchmark/Inspiration nutzen
- Eigene Nische finden (Manufacturing-fokussiert vs. Ravens Architektur-Fokus)

**Links:**
- [Raven Website](https://www.raven.build/)
- [Food4Rhino Webinar Jan 2026](https://blog.rhino3d.com/2026/01/food4rhino-webinar-raven-unlock.html)
- [McNeel Forum Thread](https://discourse.mcneel.com/t/raven-can-now-use-plugins-grasshopper-ai-interface/208628)

---

### 2.2 🔄 Backflip AI – 3D Scan-to-CAD
**Was:** Startup (Gründer von Markforged) das AI nutzt um 3D-Scans automatisch in editierbare CAD-Modelle umzuwandeln. Auch generatives 3D-Design aus Text/Bildern.

**Warum relevant:** Scan-to-CAD ist ein riesiger Pain Point in der Fertigung (Reverse Engineering, Ersatzteile). Mit Adis RTX 3090 könnte er ähnliche Modelle lokal laufen lassen. Potenzielle Inspiration für eigene Tools.

**Links:**
- [Backflip AI](https://www.backflip.ai/)
- [Forbes Artikel](https://www.forbes.com/sites/michaelmolitch-hou/2025/02/20/how-backflips-ai-aids-amateur-and-veteran-3d-designers-alike/)

---

### 2.3 🏗️ AR in der Werkstatt/Baustelle
**Was:** AR-Overlays direkt aus CAD-Daten generieren – für Montage, Qualitätskontrolle, Kundenvisualisierung. 2025/2026 Trends: Hardware-agnostisch (nicht mehr an eine Brille gebunden), automatische AR-Anleitung aus CAD-Modellen.

**Warum relevant:** Adi arbeitet bereits am Rhino AR Viewer! Der Trend bestätigt: AR aus CAD-Daten für die Fertigung ist der richtige Weg. Besonders die Idee, AR-Anleitungen automatisch aus Modellen zu generieren, passt perfekt.

**Links:**
- [Dassault AR Trends 2025](https://blog.3ds.com/brands/delmia/2025-trends-for-augmented-reality-in-manufacturing/)
- [AR in Manufacturing 2026](https://pluto-men.com/nine-uses-of-augmented-reality-in-manufacturing/)

---

### 2.4 ⚡ Self-Optimizing Toolpaths (AI + CNC)
**Was:** AI die CNC-Toolpaths in Echtzeit optimiert basierend auf Material, Werkzeugverschleiss, Maschinenvibrationen. Edge-AI direkt an der Maschine.

**Warum relevant:** 2026 grosser Trend. Kombination aus Adis CNC-Wissen + AI-Skills. Könnte als Grasshopper-Plugin starten (Toolpath-Optimierung) und zu einem eigenständigen Produkt wachsen.

---

### 2.5 🤖 MecAgent – AI CAD Copilot
**Was:** AI-Copilot der direkt in CAD-Software integriert ist und mechanische Design-Workflows unterstützt (Constraints, Thermal/Mechanical Optimierung).

**Warum relevant:** Zeigt die Richtung: AI als Assistent im CAD-Workflow, nicht als Ersatz. Adis RhinoMCP geht genau in diese Richtung.

**Links:**
- [MecAgent](https://mecagent.com/blog/ai-in-cad-how-2025-is-reshaping-mechanical-design-workflows)

---

## 3. Grasshopper/Rhino Marketplace

### 3.1 📦 Schreinerei-Template-Pack für Grasshopper
**Was:** Parametrische Templates für typische Schreinereiprodukte: Küchenschränke, Einbauschränke, Türen/Zargen, Treppen. Input: Masse → Output: 3D-Modell + Stückliste + CNC-Dateien.

**Warum relevant:** Es gibt kaum GH-Templates für Holzbau/Schreinerei – der Markt auf Food4Rhino ist komplett architekturlastig. Adi ist einer der wenigen der sowohl GH als auch Schreinerei aus dem Effeff kennt. **Massive Lücke.**

**Preismodell:** CHF 49-149 pro Template-Pack auf Gumroad/Food4Rhino.

---

### 3.2 🔗 Rhino-to-ERP/Excel Connector
**Was:** Grasshopper-Plugin das Modell-Daten (Masse, Material, Stücklisten) direkt in Excel/CSV/ERP exportiert. Bidirektional: Excel-Daten → Grasshopper Parameter.

**Warum relevant:** Adi hat bereits RH_Excel_Link als dormantes Projekt! Das wäre ein Revival mit klarem Marktbedarf. Architekten und Ingenieure brauchen das ständig.

---

### 3.3 🏷️ Automatische Beschriftung & Bemasung (Leaders + Annotations)
**Was:** GH-Plugin für automatische technische Zeichnungen: Leader-Linien, Bemassungen, Stücklisten-Labels direkt aus dem 3D-Modell.

**Warum relevant:** Adi hat RhinoLeaderTool bereits! Der RhinoMCP-Skill hat Leader-Funktionalität eingebaut. Das als eigenständiges, poliertes Food4Rhino Plugin wäre sofort verkaufbar.

---

### 3.4 🌐 Rhino-to-Web Viewer (glTF/WebXR Export)
**Was:** Plugin das Rhino-Modelle als interaktive Web-3D-Viewer exportiert (glTF + einbettbare HTML-Seite). Für Kundenfreigaben, Portfolio, AR-Preview.

**Warum relevant:** Direkte Verbindung zum Rhino AR Viewer Projekt. Könnte als "Light-Version" davon verkauft werden.

---

### 3.5 🏭 CNC Post-Processor für Grasshopper
**Was:** GH-Komponenten die direkt G-Code/NC-Code für gängige CNC-Maschinen (HOMAG, Biesse, SCM) generieren. Parametrisch: Modell ändern → Code ändert sich automatisch.

**Warum relevant:** Die Brücke CAD → CNC ist Adis Kernkompetenz. Bestehende Post-Prozessoren sind standalone und nicht parametrisch. In Grasshopper wäre das ein Game-Changer.

---

## 4. Monetarisierungs-Möglichkeiten

### 4.1 💰 Sofort machbar: Grasshopper-Templates verkaufen
**Aufwand:** Niedrig (existierende Definitionen aufpolieren)
**Einnahmen:** CHF 30-150 pro Template auf Gumroad
**Warum:** Adi hat 14 Jahre GH-Erfahrung und bestehende Definitionen. Clean-up, Dokumentation, Screenshot → verkaufen. Passive Income.

**Konkrete erste Produkte:**
- Parametrischer Küchenschrank-Konfigurator
- Türblatt + Zarge Generator (aus aktuellem Arbeitsprojekt)
- CNC-Nesting-Optimierer für Plattenware

---

### 4.2 📹 YouTube/Tutorial-Kanal: "Rhino für Schreiner"
**Aufwand:** Mittel (1-2 Videos/Monat)
**Einnahmen:** Indirekt (Audience → Plugin-Verkäufe, Consulting)
**Warum:** Es gibt fast KEINE Rhino/GH-Tutorials für Holzbearbeitung. Die Nische ist komplett frei. Deutsche Sprache = noch weniger Konkurrenz.

---

### 4.3 🎓 Consulting: CAD-Automatisierung für Betriebe
**Aufwand:** Pro Projekt (10-40h)
**Einnahmen:** CHF 150-200/h
**Warum:** Kleine Schreinereien/Metallbauer wollen automatisieren, haben aber kein Know-how. Adi könnte Grasshopper-Definitionen + Schulung als Paket anbieten. 2-3 Kunden → guter Nebenverdienst.

**Zielgruppe:** Schweizer Schreinereien die gerade eine CNC-Maschine gekauft haben und nicht wissen wie sie das Potenzial ausschöpfen.

---

### 4.4 🔌 RhinoMCP als Commercial Plugin
**Aufwand:** Mittel (Polishing, Docs, Support)
**Einnahmen:** Subscription (CHF 10-30/Monat) oder einmalig (CHF 99-249)
**Warum:** MCP-basierter Zugriff auf Rhino ist einzigartig. Wenn Raven zeigt dass AI+GH ein Markt ist, ist RhinoMCP die "API-first" Alternative für Entwickler und Power-User.

---

### 4.5 📊 IntelliPlan als fokussiertes MVP
**Aufwand:** Hoch, aber bereits in Arbeit
**Einnahmen:** SaaS CHF 49-99/Monat/Betrieb
**Warum:** Wenn IntelliPlan auf EIN Problem fokussiert (z.B. nur Stücklisten + CNC-Übergabe), kann es schneller am Markt sein als ein Full-ERP.

---

## 5. Coole Tech-Projekte

### 5.1 👶 CNC-Holzpuzzle-Generator für die Kids
**Was:** Grasshopper-Definition die parametrische Holzpuzzles erstellt → CNC-Fräsen → zusammenbauen mit den Kids. Tiere, Zahlen, Buchstaben als Themes.

**Warum relevant:** Perfekte Kombination: Papa-Zeit + Maker-Projekt + GH-Skills. Die Kleinen (4.5 + 2.5) sind im richtigen Alter. Bonus: Fotogener Content für Social Media / YouTube.

**Aufwand:** 2-3 Abende für die Definition, dann unbegrenzt Varianten.

---

### 5.2 🤖 Mini-Roboterarm (3D-Druck + Arduino)
**Was:** Kleiner Roboterarm aus 3D-gedruckten Teilen (designed in Rhino), gesteuert via Arduino/Python. Kann kleine Objekte greifen, sortieren, zeichnen.

**Warum relevant:** RTX 3090 für Computer Vision (Objekterkennung), Rhino für Design, Python für Steuerung. Alle Skills kommen zusammen. Kids finden Roboter cool.

**Links:**
- [All3DP 3D Printed Robots](https://all3dp.com/2/3d-printed-robot-print-robots/)

---

### 5.3 🪵 Parametrische CNC-Möbel (Steckverbindung, kein Leim)
**Was:** Möbel die nur aus CNC-gefrästen Platten bestehen und per Steckverbindung zusammengebaut werden. Parametrisch: Masse ändern → neues Design.

**Warum relevant:** Portfolio-Stück, Social-Media-Content, potenzielles Produkt (Open-Source Pläne verkaufen). Rhino → Grasshopper → CNC → fertiges Möbel in einem Tag.

---

### 5.4 🎮 Interactive Tangram für Kids (CNC + LED)
**Was:** Holz-Tangram-Set mit CNC gefräst, mit eingelassenen LEDs die aufleuchten wenn die Teile richtig platziert werden (Arduino + Reed-Sensoren).

**Warum relevant:** Lernspielzeug + Maker-Projekt + Elektronik. Perfekt für die Altersgruppe. Könnte auch als Produkt verkauft werden.

---

### 5.5 🖥️ Local AI Image Generation Pipeline (ComfyUI + Rhino)
**Was:** Workflow: Rhino 3D-Modell → Render → ComfyUI ControlNet → fotorealistische Visualisierung. Alles lokal auf der RTX 3090.

**Warum relevant:** Adi hat ComfyUI bereits eingerichtet. Die Kombination Rhino-Render + AI-Enhancement für Kundenvisualisierungen ist ein konkreter Business-Use-Case. Statt teurem V-Ray: schnelle, überzeugende Visualisierungen per AI.

---

## Zusammenfassung: Top 5 "Do This Next" Empfehlungen

| Priorität | Idee | Aufwand | Potenzial | Nächster Schritt |
|-----------|------|---------|-----------|------------------|
| 🥇 | GH-Templates für Schreiner verkaufen | Niedrig | Mittel | 1 Template aufpolieren, auf Gumroad stellen |
| 🥈 | RhinoMCP kommerzialisieren | Mittel | Hoch | Raven analysieren, Differenzierung definieren |
| 🥉 | CNC-Puzzle-Generator mit Kids | Niedrig | Fun + Content | Wochenend-Projekt starten |
| 4️⃣ | IntelliPlan MVP auf Stücklisten fokussieren | Hoch | Sehr hoch | MVP-Scope definieren (nur 1 Feature) |
| 5️⃣ | Consulting-Paket schnüren | Niedrig | Mittel | LinkedIn-Profil updaten, 1 Referenzprojekt |

---

*Recherche-Basis: Web-Suchen vom 04.02.2026. Fokus auf Schweizer Markt und Adis bestehendes Skillset.*
