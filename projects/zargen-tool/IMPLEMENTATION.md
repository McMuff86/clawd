# ZargenTool - Technischer Implementierungsplan

*Für Adi - Detaillierte technische Planung*

---

## Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  React/Vue SPA                                       │   │
│  │  - Projekt-Dashboard                                 │   │
│  │  - Türen-Liste (DataGrid)                           │   │
│  │  - Eingabe-Formular (Modal)                         │   │
│  │  - Kalkulations-Übersicht                           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ REST API
┌─────────────────────────────────────────────────────────────┐
│                         Backend                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  FastAPI (Python)                                    │   │
│  │  - /api/projects                                     │   │
│  │  - /api/doors                                        │   │
│  │  - /api/calculate                                    │   │
│  │  - /api/export                                       │   │
│  │  - /api/rhino/sync                                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                              │                               │
│  ┌──────────────┐  ┌────────┴───────┐  ┌──────────────┐   │
│  │ Kalkulation  │  │   Database     │  │  RhinoMCP    │   │
│  │   Engine     │  │   (SQLite)     │  │   Client     │   │
│  └──────────────┘  └────────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
                                                │
                                                ▼ TCP
                              ┌─────────────────────────────┐
                              │  Rhino + RhinoMCP Plugin    │
                              └─────────────────────────────┘
```

---

## Datenmodell

```python
# models.py

from pydantic import BaseModel
from typing import Optional, Literal
from enum import Enum

class ZargenProfil(str, Enum):
    UDS = "UDS"
    BL = "BL"
    # weitere...

class SchlossTyp(str, Enum):
    BB = "BB"
    WC = "WC"
    RZ = "RZ"
    # weitere...

class BandTyp(str, Enum):
    HE18 = "HE18"
    M10 = "M10"
    GEFRAEST = "Gefräst"
    # weitere...

class Door(BaseModel):
    id: Optional[int] = None
    project_id: int
    
    # Identifikation
    position: str  # z.B. "EG04", "1OG103"
    element_typ: str
    anzahl: int = 1
    
    # Zarge
    zargen_profil: ZargenProfil
    zargen_falz_tiefe: float
    zargen_falz_breite: float
    zargentiefe: float
    mauerstaerke: float
    maueraufbau: str
    
    # Öffnung
    licht_breite: float  # mm
    licht_hoehe: float   # mm
    bodeneinstand: float = 0
    tb_luft_boden: float
    
    # Beschläge
    schloss_typ: SchlossTyp
    bandseite: Literal["L", "R", "SP"]
    band_typ: BandTyp
    bandmass_oben: float
    bandmass_mitte: Optional[float] = None
    bandmass_unten: float
    
    # Berechnet
    preis_zarge: Optional[float] = None
    preis_tuerblatt: Optional[float] = None
    preis_gesamt: Optional[float] = None
    
    # CAD
    rhino_guid: Optional[str] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    position_z: Optional[float] = None

class Project(BaseModel):
    id: Optional[int] = None
    name: str  # z.B. "Roggächer Haus C"
    kunde: str
    created_at: datetime
    updated_at: datetime
```

---

## API Endpoints

```python
# main.py

from fastapi import FastAPI
from typing import List

app = FastAPI(title="ZargenTool API")

# Projects
@app.get("/api/projects")
async def list_projects() -> List[Project]: ...

@app.post("/api/projects")
async def create_project(project: Project) -> Project: ...

@app.get("/api/projects/{id}")
async def get_project(id: int) -> Project: ...

# Doors
@app.get("/api/projects/{project_id}/doors")
async def list_doors(project_id: int) -> List[Door]: ...

@app.post("/api/projects/{project_id}/doors")
async def create_door(project_id: int, door: Door) -> Door: ...

@app.put("/api/doors/{id}")
async def update_door(id: int, door: Door) -> Door: ...

@app.delete("/api/doors/{id}")
async def delete_door(id: int): ...

# Calculation
@app.post("/api/calculate")
async def calculate_prices(doors: List[Door]) -> List[Door]: ...

@app.get("/api/projects/{project_id}/summary")
async def get_price_summary(project_id: int) -> PriceSummary: ...

# Export
@app.get("/api/projects/{project_id}/export/excel")
async def export_excel(project_id: int) -> FileResponse: ...

@app.get("/api/projects/{project_id}/export/pdf")
async def export_pdf(project_id: int) -> FileResponse: ...

@app.get("/api/projects/{project_id}/export/bestellung")
async def export_order(project_id: int) -> FileResponse: ...

# Rhino Integration
@app.post("/api/rhino/generate")
async def generate_in_rhino(doors: List[Door]) -> List[str]: ...

@app.post("/api/rhino/sync")
async def sync_from_rhino(project_id: int) -> List[Door]: ...

# Stammdaten
@app.get("/api/options/zargenprofile")
async def get_zargen_options() -> List[dict]: ...

@app.get("/api/options/bandtypen")
async def get_band_options() -> List[dict]: ...
```

---

## Kalkulations-Engine

```python
# calculation.py

from dataclasses import dataclass
from typing import Dict

@dataclass
class PriceTable:
    """Preistabelle aus Grunddaten-Sheet."""
    base_prices: Dict[str, float]
    lb_surcharges: Dict[str, float]  # Lichtbreite-Zuschläge
    lh_surcharges: Dict[str, float]  # Lichthöhe-Zuschläge
    zt_surcharges: Dict[str, float]  # Zargentiefe-Zuschläge
    band_prices: Dict[str, float]
    # ...

class Calculator:
    def __init__(self, price_table: PriceTable):
        self.prices = price_table
    
    def calculate_zarge(self, door: Door) -> float:
        """Berechne Zargenpreis."""
        base = self.prices.base_prices[door.zargen_profil]
        
        # Zuschläge
        lb_surcharge = self._get_lb_surcharge(door.licht_breite)
        lh_surcharge = self._get_lh_surcharge(door.licht_hoehe)
        zt_surcharge = self._get_zt_surcharge(door.zargentiefe)
        
        return (base + lb_surcharge + lh_surcharge + zt_surcharge) * door.anzahl
    
    def calculate_tuerblatt(self, door: Door) -> float:
        """Berechne Türblattpreis."""
        # Logik aus Excel extrahieren
        ...
    
    def calculate_total(self, door: Door) -> float:
        """Gesamtpreis inkl. Beschläge."""
        return (
            self.calculate_zarge(door) + 
            self.calculate_tuerblatt(door) +
            self.calculate_beschlaege(door)
        )
    
    def _get_lb_surcharge(self, licht_breite: float) -> float:
        """Zuschlag basierend auf Lichtbreite."""
        if licht_breite <= 800:
            return 0
        elif licht_breite <= 900:
            return self.prices.lb_surcharges["80_90"]
        elif licht_breite <= 1000:
            return self.prices.lb_surcharges["90_100"]
        # etc.
```

---

## RhinoMCP Integration

```python
# rhino_integration.py

from rhino_client import RhinoClient
from typing import List
import json

class RhinoSync:
    def __init__(self):
        self.client = RhinoClient()
    
    def generate_door(self, door: Door) -> str:
        """Generiere Tür in Rhino, return GUID."""
        # Option A: Grasshopper Player
        params = {
            "Lichtbreite": door.licht_breite,
            "Lichthoehe": door.licht_hoehe,
            "Point": f"{door.position_x},{door.position_y},{door.position_z}"
        }
        result = run_grasshopper_player(
            "Rahmentuer_UD4.gh",  # oder basierend auf door.zargen_profil
            params
        )
        return result.get("created_guids", [])
    
    def generate_all(self, doors: List[Door]) -> Dict[int, List[str]]:
        """Batch-Generierung aller Türen."""
        results = {}
        for door in doors:
            guids = self.generate_door(door)
            results[door.id] = guids
            door.rhino_guid = guids[0] if guids else None
        return results
    
    def sync_positions_from_cad(self, project_id: int) -> List[Door]:
        """Lese Türpositionen aus Rhino und update Datenbank."""
        # Alle Objekte auf Layer "Türen" finden
        # Positionen extrahieren
        # Mit existierenden Doors matchen
        ...
```

---

## Verzeichnisstruktur

```
zargen-tool/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI app
│   │   ├── models.py         # Pydantic models
│   │   ├── database.py       # SQLite/SQLAlchemy
│   │   ├── calculation.py    # Preisberechnung
│   │   ├── rhino_sync.py     # RhinoMCP integration
│   │   └── export/
│   │       ├── excel.py
│   │       ├── pdf.py
│   │       └── order.py
│   ├── data/
│   │   ├── price_tables.json # Aus Excel extrahiert
│   │   └── options.json      # Dropdowns
│   ├── tests/
│   │   └── test_calculation.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DoorForm.vue
│   │   │   ├── DoorTable.vue
│   │   │   └── ProjectDashboard.vue
│   │   ├── api/
│   │   │   └── client.ts
│   │   └── App.vue
│   └── package.json
│
├── VISION.md
├── IMPLEMENTATION.md
└── README.md
```

---

## Sprint 1: MVP (Woche 1-2)

### Tasks

- [ ] **Backend Setup**
  - [ ] FastAPI Projekt aufsetzen
  - [ ] SQLite + SQLAlchemy
  - [ ] Door/Project Models
  - [ ] CRUD Endpoints

- [ ] **Excel Import**
  - [ ] Parser für bestehendes Excel
  - [ ] Daten in DB importieren
  - [ ] Grunddaten/Preistabellen extrahieren

- [ ] **Frontend Minimal**
  - [ ] Vue/React Setup
  - [ ] Projekt-Liste
  - [ ] Türen-Tabelle (read-only)

### Deliverable
Web-UI zeigt bestehende Excel-Daten an

---

## Sprint 2: CRUD + Kalkulation (Woche 3-4)

### Tasks

- [ ] **Eingabe-Formular**
  - [ ] Door erstellen/bearbeiten Modal
  - [ ] Validierung
  - [ ] Dropdown-Optionen aus API

- [ ] **Kalkulation**
  - [ ] Preislogik implementieren
  - [ ] Unit Tests
  - [ ] Preisanzeige in UI

### Deliverable
Türen können bearbeitet werden, Preise werden berechnet

---

## Sprint 3: CAD Integration (Woche 5-7)

### Tasks

- [ ] **RhinoMCP Anbindung**
  - [ ] Tür-Generierung via Grasshopper
  - [ ] Position Sync
  - [ ] Batch-Generierung

- [ ] **UI Integration**
  - [ ] "In Rhino anzeigen" Button
  - [ ] "Aus CAD importieren" Button

### Deliverable
Türen erscheinen im Rhino Grundriss

---

## Sprint 4: Export + Polish (Woche 8-10)

### Tasks

- [ ] **Exports**
  - [ ] Excel-Export (bisheriges Format)
  - [ ] PDF Bestellliste
  - [ ] Produktionsliste

- [ ] **Polish**
  - [ ] Error Handling
  - [ ] Loading States
  - [ ] Dokumentation

### Deliverable
Produktionsreifes System

---

## Quick Start (für später)

```bash
# Backend starten
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend starten
cd frontend
npm install
npm run dev

# Rhino vorbereiten
# In Rhino: tcpstart
```

---

*Technische Fragen? → Sentinel fragen*
