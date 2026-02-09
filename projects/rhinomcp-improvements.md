# RhinoMCP Improvements - Nacht-Session 28.01.2026

## Status
- **Gestartet:** 01:00
- **Letzte Iteration:** 05:30 - Finale Priorisierung & Roadmap
- **Präsentation:** 06:00 ✅ Ready

## Kontext
RhinoMCP ist ein Plugin das Rhino 3D via TCP steuert. Heute haben wir erfolgreich:
- Grasshopper Player Automation implementiert (grasshopper.py)
- Parameter aus GH-Files auslesen via SDK
- Türen mit individuellen Massen/Positionen generiert

## Zu analysieren
- [ ] RhinoMCP Repo Struktur (/home/mcmuff/rhinomcp)
- [ ] Bestehende Scripts in scripts/clawdbot/
- [ ] AGENTS.md und AUTOMATION_PLAN.md im Repo
- [ ] GitHub Issues falls vorhanden
- [ ] Vergleich mit anderen CAD-Automation Tools

## Ideen-Pool (roh)
1. **Grasshopper Integration** ✅
   - Pt → Point Alias-Mapping → Iteration 0, 3
   - Parameter-Validierung (min/max) → Iteration 3
   - Batch-Mode aus JSON/CSV → Iteration 1
   - Object-GUIDs zurückgeben → Iteration 4

2. **Workflow** ✅
   - Presets für Türtypen → Iteration 5
   - Template-System → Iteration 5

3. **Robustheit** ✅
   - Retry-Logik → Iteration 2
   - Bessere Fehlermeldungen → Iteration 2
   - Code-Qualität & Refactoring → Iteration 7

4. **Dokumentation** ✅
   - SKILL.md erweitern → Iteration 6
   - Beispiele → Iteration 6

---

## Iteration Log

### Iteration 0 (01:12) - Grasshopper Integration Analyse

**Analysiert:** `scripts/clawdbot/grasshopper.py`, `AGENTS.md`

**Gefundene Probleme:**

1. **Parameter-Aliase fehlen**
   - `--Pt` im GH-File wird zu `Point` im Player-Prompt
   - Aktuell muss man wissen dass `--Point` statt `--Pt` verwendet werden muss
   - **Fix:** Alias-Mapping in `parse_prompt()` oder Parameter-Lookup

2. **Keine Parameter-Validierung**
   - SDK liefert `min`/`max` für Number Sliders
   - Aktuell wird das ignoriert - ungültige Werte werden durchgereicht
   - **Fix:** Validierung vor `run` mit Warning/Error

3. **Object GUIDs fehlen im Output**
   - Aktuell nur `objects_created: 54` (Gesamtzahl)
   - Keine Info welche Objekte neu sind
   - **Fix:** Vor/Nach Differenz, oder via `rs.LastCreatedObjects()`

4. **Keine Batch-Unterstützung**
   - Jeder Aufruf ist einzeln
   - Für 100 Türen = 100 separate Aufrufe
   - **Fix:** `--batch input.json` oder `--csv input.csv`

**Konkrete Code-Verbesserung für Alias-Mapping:**

```python
# In grasshopper.py - Parameter-Aliase definieren
PARAM_ALIASES = {
    'Pt': 'Point',
    'Punkt': 'Point',
    # Weitere Aliase nach Bedarf
}

def normalize_param_name(name: str) -> str:
    """Map GH nicknames to Player prompt names."""
    return PARAM_ALIASES.get(name, name)

# In run_grasshopper_player():
# Beim Parsen der custom_params die Aliase auflösen
normalized_params = {normalize_param_name(k): v for k, v in params.items()}
```

**Nächste Iteration:** Batch-Processing Konzept detaillieren

---

### Iteration 1 (01:30) - Batch-Processing Konzept

**Ziel:** Mehrere Objekte aus einer Datei erstellen statt einzelner CLI-Aufrufe.

#### Vorgeschlagene Input-Formate

**1. JSON (flexibel, verschachtelt möglich):**
```json
{
  "definition": "Rahmentuer_UD4.gh",
  "defaults": {
    "Rahmendicke": 53,
    "Tuerstaerke": 58
  },
  "items": [
    {"id": "T01", "Lichthoehe": 2100, "Lichtbreite": 900, "Point": "0,0,0"},
    {"id": "T02", "Lichthoehe": 2000, "Lichtbreite": 800, "Point": "1500,0,0"},
    {"id": "T03", "Lichthoehe": 2200, "Lichtbreite": 1000, "Point": "3000,0,0"}
  ]
}
```

**2. CSV (einfach, Excel-kompatibel):**
```csv
id,Lichthoehe,Lichtbreite,Point
T01,2100,900,"0,0,0"
T02,2000,800,"1500,0,0"
T03,2200,1000,"3000,0,0"
```

#### CLI-Erweiterung

```bash
# JSON batch
python3 grasshopper.py batch doors.json

# CSV batch  
python3 grasshopper.py batch doors.csv

# Mit Options
python3 grasshopper.py batch doors.json --dry-run       # Nur validieren
python3 grasshopper.py batch doors.json --continue      # Bei Fehler weitermachen
python3 grasshopper.py batch doors.json --output result.json  # Report speichern
```

#### Implementierungs-Sketch

```python
def run_batch(input_file: str, dry_run: bool = False, continue_on_error: bool = False) -> dict:
    """Run multiple GH definitions from JSON/CSV."""
    
    # 1. Parse input file
    if input_file.endswith('.json'):
        config = json.load(open(input_file))
        items = config['items']
        defaults = config.get('defaults', {})
        gh_file = config['definition']
    else:  # CSV
        items = list(csv.DictReader(open(input_file)))
        defaults = {}
        gh_file = None  # Muss als --definition übergeben werden
    
    # 2. Validate all items first
    if dry_run:
        return validate_batch(items, gh_file)
    
    # 3. Run each item
    results = []
    for item in items:
        params = {**defaults, **item}
        item_id = params.pop('id', f'item_{len(results)}')
        
        try:
            result = run_grasshopper_player(gh_file, params)
            result['batch_id'] = item_id
            results.append(result)
        except Exception as e:
            if continue_on_error:
                results.append({'batch_id': item_id, 'status': 'error', 'message': str(e)})
            else:
                raise
    
    return {
        'status': 'success',
        'total': len(items),
        'succeeded': sum(1 for r in results if r['status'] == 'success'),
        'failed': sum(1 for r in results if r['status'] == 'error'),
        'results': results
    }
```

#### Output-Report (result.json)

```json
{
  "status": "success",
  "total": 3,
  "succeeded": 3,
  "failed": 0,
  "results": [
    {"batch_id": "T01", "status": "success", "objects_created": ["guid1", "guid2", ...]},
    {"batch_id": "T02", "status": "success", "objects_created": ["guid3", "guid4", ...]},
    {"batch_id": "T03", "status": "success", "objects_created": ["guid5", "guid6", ...]}
  ]
}
```

**Aufwand-Schätzung:** ~2-3h Implementation

---

### Iteration 2 (02:30) - Error Handling & Retry-Logik

**Analysiert:** `scripts/clawdbot/rhino_client.py`

#### Aktuelle Probleme

1. **Retry-Config existiert aber wird nicht genutzt!**
   ```python
   DEFAULT_RETRIES = CONNECTION.get("max_retries", 3)      # ← Definiert
   DEFAULT_RETRY_DELAY = CONNECTION.get("retry_delay", 1.0) # ← Definiert
   # Aber nirgends verwendet!
   ```

2. **Keine spezifischen Exception-Typen**
   - Alles ist `Exception` oder `ConnectionError`
   - Keine Unterscheidung: Netzwerk vs. Rhino-Fehler vs. Timeout

3. **Keine Retry-Logik bei Verbindungsabbruch**
   - Wenn Rhino kurz nicht antwortet → sofortiger Fehler

#### Vorgeschlagene Error-Hierarchie

```python
class RhinoMCPError(Exception):
    """Base exception for RhinoMCP."""
    pass

class ConnectionError(RhinoMCPError):
    """Could not connect to Rhino."""
    pass

class TimeoutError(RhinoMCPError):
    """Operation timed out."""
    pass

class CommandError(RhinoMCPError):
    """Rhino returned an error."""
    def __init__(self, message: str, command: str, details: dict = None):
        super().__init__(message)
        self.command = command
        self.details = details or {}

class ValidationError(RhinoMCPError):
    """Invalid parameters."""
    pass
```

#### Retry-Decorator Implementation

```python
import time
from functools import wraps

def with_retry(max_retries: int = None, delay: float = None, 
               exceptions: tuple = (ConnectionError, TimeoutError)):
    """Decorator for automatic retry on transient failures."""
    max_retries = max_retries or DEFAULT_RETRIES
    delay = delay or DEFAULT_RETRY_DELAY
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        wait = delay * (2 ** attempt)  # Exponential backoff
                        print(f"Retry {attempt + 1}/{max_retries} after {wait}s: {e}")
                        time.sleep(wait)
            raise last_error
        return wrapper
    return decorator
```

#### Verbesserte send_command mit Retry

```python
@with_retry()
def send_command(self, cmd_type: str, params: Optional[Dict] = None) -> Dict:
    """Send command with automatic retry on connection issues."""
    if not self.sock:
        self.connect()  # Auto-reconnect
    
    try:
        # ... existing send logic ...
        return response
    except socket.timeout:
        raise TimeoutError(f"Command '{cmd_type}' timed out after {self.timeout}s")
    except socket.error as e:
        self.disconnect()  # Force reconnect on next call
        raise ConnectionError(f"Socket error: {e}")
```

#### Bessere Fehlermeldungen für User

```python
def format_error_for_user(error: RhinoMCPError) -> str:
    """Format error message for human consumption."""
    if isinstance(error, ConnectionError):
        return f"❌ Rhino nicht erreichbar. Läuft tcpstart? ({error})"
    elif isinstance(error, TimeoutError):
        return f"⏱️ Timeout - Rhino antwortet nicht. Evtl. beschäftigt? ({error})"
    elif isinstance(error, CommandError):
        return f"⚠️ Rhino-Fehler bei '{error.command}': {error}"
    elif isinstance(error, ValidationError):
        return f"🔧 Ungültige Parameter: {error}"
    return f"❓ Unbekannter Fehler: {error}"
```

#### Anwendung in grasshopper.py

```python
def run_grasshopper_player(...):
    try:
        result = run_with_retry(...)
        return result
    except TimeoutError:
        return {'status': 'error', 'code': 'TIMEOUT', 
                'message': 'GrasshopperPlayer hat nicht geantwortet'}
    except ConnectionError:
        return {'status': 'error', 'code': 'NO_CONNECTION',
                'message': 'Rhino nicht erreichbar - tcpstart laufen?'}
    except CommandError as e:
        return {'status': 'error', 'code': 'RHINO_ERROR',
                'message': str(e), 'details': e.details}
```

**Aufwand-Schätzung:** ~1-2h Implementation

**Benefits:**
- Automatische Reconnection bei Netzwerk-Hickups
- Exponential Backoff verhindert Überlastung
- Klare Fehlermeldungen für Debugging
- Strukturierte Error-Codes für programmatische Auswertung

---

### Iteration 3 (03:00) - Parameter-Validierung & Aliase

**Problem aus der Praxis:** Heute Abend hat `--Pt 1500,0,0` nicht funktioniert, weil GrasshopperPlayer nach "Point" fragt, nicht "Pt".

#### 1. Automatisches Alias-Mapping

**Konzept:** Beim `info`-Command die SDK-Parameter (Nicknames) mit den Player-Prompts matchen und Aliase erstellen.

```python
# Bekannte Mappings (GH Nickname → Player Prompt)
KNOWN_ALIASES = {
    'Pt': 'Point',
    'Punkt': 'Point',
    'Position': 'Point',
    # Erweitert sich durch Usage
}

def build_alias_map(gh_file: str) -> dict:
    """Build alias map from GH definition parameters."""
    params = get_gh_parameters(gh_file)
    aliases = dict(KNOWN_ALIASES)  # Start with known
    
    for nickname, info in params.items():
        param_type = info.get('type', '')
        
        # Point-Parameter automatisch erkennen
        if param_type == 'Point' or 'point' in nickname.lower():
            aliases[nickname] = 'Point'
    
    return aliases

def normalize_params(params: dict, aliases: dict) -> dict:
    """Apply alias mapping to parameters."""
    normalized = {}
    for key, value in params.items():
        mapped_key = aliases.get(key, key)
        normalized[mapped_key] = value
    return normalized
```

#### 2. Parameter-Validierung mit SDK-Info

**SDK liefert für NumberSlider:**
```json
{
  "nickname": "Lichthoehe",
  "type": "NumberSlider",
  "value": 2100.0,
  "min": 1800.0,
  "max": 2600.0
}
```

**Validierungs-Implementation:**

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ValidationResult:
    valid: bool
    errors: List[str]
    warnings: List[str]

def validate_parameters(params: dict, gh_params: dict) -> ValidationResult:
    """Validate parameters against GH definition constraints."""
    errors = []
    warnings = []
    
    for name, value in params.items():
        if name not in gh_params and name != 'Point':
            warnings.append(f"Unbekannter Parameter: '{name}'")
            continue
        
        if name == 'Point':
            # Validate point format
            if not validate_point_format(value):
                errors.append(f"Ungültiges Point-Format: '{value}' (erwartet: x,y,z)")
            continue
        
        info = gh_params.get(name, {})
        param_type = info.get('type', '')
        
        # Number validation
        if param_type in ('Number', 'NumberSlider'):
            try:
                num_value = float(value)
                min_val = info.get('min')
                max_val = info.get('max')
                
                if min_val is not None and num_value < min_val:
                    errors.append(f"{name}={value} ist unter Minimum ({min_val})")
                if max_val is not None and num_value > max_val:
                    errors.append(f"{name}={value} ist über Maximum ({max_val})")
            except ValueError:
                errors.append(f"{name}='{value}' ist keine gültige Zahl")
        
        # Boolean validation
        elif param_type == 'Boolean':
            if str(value).lower() not in ('true', 'false', '1', '0', 'yes', 'no'):
                errors.append(f"{name}='{value}' ist kein gültiger Boolean")
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )

def validate_point_format(value) -> bool:
    """Check if value is valid point format."""
    if isinstance(value, (list, tuple)) and len(value) == 3:
        return all(isinstance(v, (int, float)) for v in value)
    if isinstance(value, str):
        parts = value.replace(' ', '').split(',')
        if len(parts) == 3:
            try:
                [float(p) for p in parts]
                return True
            except ValueError:
                pass
    return False
```

#### 3. Integrierte Validierung im Workflow

```bash
# Validierung vor Run
python3 grasshopper.py run file.gh --Lichthoehe 3000 --validate
# Output:
# ❌ Validierung fehlgeschlagen:
#    - Lichthoehe=3000 ist über Maximum (2600)
# Run abgebrochen.

# Warnung aber trotzdem ausführen
python3 grasshopper.py run file.gh --Lichthoehe 3000 --force
# Output:
# ⚠️ Warnung: Lichthoehe=3000 ist über Maximum (2600)
# Fahre trotzdem fort...

# Dry-run zum Prüfen
python3 grasshopper.py run file.gh --Lichthoehe 2100 --dry-run
# Output:
# ✅ Validierung OK
# Parameter:
#   Lichthoehe: 2100 (im Bereich 1800-2600)
#   Lichtbreite: 900 (default)
#   Point: 0,0,0 (default)
```

#### 4. Info-Command erweitern

```bash
python3 grasshopper.py info file.gh --verbose
# Output:
# Rahmentuer_UD4.gh
# ================
# 
# Parameter (26):
#   --Lichthoehe     Number  [1800 - 2600]  default: 2100
#   --Lichtbreite    Number  [600 - 1400]   default: 900
#   --Pt             Point   → Alias: --Point
#   --DichtNut_Rahmen Boolean              default: true
#   ...
#
# Aliase:
#   --Pt → --Point
```

**Aufwand-Schätzung:** ~2h Implementation

**Quick Win:** Das Alias-Mapping allein (30 Min) würde das Pt→Point Problem sofort lösen!

---

### Iteration 4 (03:30) - Output-Tracking (Object GUIDs)

**Problem:** Aktuell gibt `run` nur `objects_created: 54` zurück - die Gesamtzahl im Dokument. Keine Info welche Objekte gerade erstellt wurden.

#### Warum GUIDs wichtig sind

1. **Nachbearbeitung:** Erstellte Türen nachträglich verschieben, gruppieren, löschen
2. **Batch-Zuordnung:** Welche 6 Objekte gehören zu Tür T01?
3. **Fehler-Recovery:** Bei Batch-Abbruch wissen welche Türen fertig sind
4. **Reporting:** Export-Liste mit Objekt-IDs für Dokumentation

#### Lösungsansätze

**Ansatz 1: Vorher/Nachher Differenz**
```python
def run_grasshopper_player_with_tracking(file_path: str, params: dict) -> dict:
    """Run GH and track which objects were created."""
    
    # 1. Snapshot vor Run
    before_ids = get_all_object_ids()
    
    # 2. Run GrasshopperPlayer
    result = run_grasshopper_player(file_path, params)
    
    # 3. Snapshot nach Run
    after_ids = get_all_object_ids()
    
    # 4. Differenz = neue Objekte
    new_ids = after_ids - before_ids
    
    result['created_guids'] = list(new_ids)
    return result

def get_all_object_ids() -> set:
    """Get all object GUIDs in current document."""
    with RhinoClient() as client:
        code = '''
import rhinoscriptsyntax as rs
ids = rs.AllObjects()
print(",".join(str(id) for id in ids) if ids else "")
'''
        result = client.send_command('execute_rhinoscript_python_code', {'code': code})
        output = result.get('result', {}).get('result', '')
        if output:
            return set(output.strip().split(','))
        return set()
```

**Ansatz 2: rs.LastCreatedObjects() (Rhino 8)**
```python
def get_last_created_objects() -> list:
    """Get GUIDs of last created objects (Rhino 8+)."""
    with RhinoClient() as client:
        code = '''
import rhinoscriptsyntax as rs
# Nur in Rhino 8 verfügbar
try:
    ids = rs.LastCreatedObjects()
    print(",".join(str(id) for id in ids) if ids else "")
except:
    print("NOT_SUPPORTED")
'''
        result = client.send_command('execute_rhinoscript_python_code', {'code': code})
        output = result.get('result', {}).get('result', '').strip()
        
        if output == "NOT_SUPPORTED":
            return None  # Fallback zu Ansatz 1
        return output.split(',') if output else []
```

**Ansatz 3: Hybrid (am robustesten)**
```python
def track_created_objects(func):
    """Decorator to track objects created during a function call."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        before = get_all_object_ids()
        result = func(*args, **kwargs)
        after = get_all_object_ids()
        
        new_ids = list(after - before)
        
        if isinstance(result, dict):
            result['created_guids'] = new_ids
            result['created_count'] = len(new_ids)
        
        return result
    return wrapper

@track_created_objects
def run_grasshopper_player(file_path: str, params: dict) -> dict:
    # ... existing implementation ...
```

#### Erweitertes Output-Format

```json
{
  "status": "success",
  "file": "Rahmentuer_UD4.gh",
  "params_used": {
    "Lichthoehe": 2100,
    "Lichtbreite": 900,
    "Point": "0,0,0"
  },
  "created_count": 6,
  "created_guids": [
    "a1b2c3d4-...",
    "e5f6g7h8-...",
    "..."
  ],
  "created_by_layer": {
    "Tuerblatt": ["a1b2c3d4-..."],
    "Tuerrahmen": ["e5f6g7h8-...", "..."],
    "Intumex_Rahmen": ["..."]
  }
}
```

#### Layer-basierte Gruppierung

```python
def get_objects_by_layer(guids: list) -> dict:
    """Group GUIDs by their layer."""
    with RhinoClient() as client:
        code = f'''
import rhinoscriptsyntax as rs
import json

guids = {guids}
by_layer = {{}}

for guid in guids:
    layer = rs.ObjectLayer(guid)
    if layer not in by_layer:
        by_layer[layer] = []
    by_layer[layer].append(str(guid))

print(json.dumps(by_layer))
'''
        result = client.send_command('execute_rhinoscript_python_code', {'code': code})
        output = result.get('result', {}).get('result', '{}')
        return json.loads(output)
```

#### Anwendungsbeispiel

```python
# Nach Batch-Run
result = run_batch("doors.json")

# Alle Türen mit ihren Objekten
for door in result['results']:
    print(f"Tür {door['batch_id']}:")
    print(f"  Rahmen: {door['created_by_layer'].get('Tuerrahmen', [])}")
    print(f"  Blatt:  {door['created_by_layer'].get('Tuerblatt', [])}")

# Nachträgliche Gruppierung
for door in result['results']:
    group_name = f"Door_{door['batch_id']}"
    create_group(group_name, door['created_guids'])
```

**Aufwand-Schätzung:** ~1.5h Implementation

**Empfehlung:** Ansatz 3 (Hybrid mit Decorator) - sauber, wiederverwendbar, robust.

---

### Iteration 5 (04:00) - Presets & Templates für Türtypen

**Kontext:** Es existieren bereits mehrere GH-Definitionen:
- `Rahmentuer_UD3.gh`
- `Rahmentuer_UD4.gh` 
- `Rahmentuer_UD5.gh`
- `Rahmentuer_Schwelle.gh`
- `HausB_Detail_Türen_WHG_Nebenraum.gh`

**Problem:** Aktuell muss man bei jedem Aufruf:
1. Den vollen Windows-Pfad zur GH-Datei kennen
2. Alle Parameternamen auswendig wissen
3. Sinnvolle Werte selbst bestimmen

#### Konzept: Preset-System

**Presets** = Benannte Konfigurationen für häufige Anwendungsfälle

```yaml
# presets/doors.yaml
presets:
  # === STANDARD INNENTÜREN ===
  standard_900:
    description: "Standard Innentür 900mm"
    template: rahmentuer_ud4
    params:
      Lichtbreite: 900
      Lichthoehe: 2100
      
  standard_800:
    description: "Standard Innentür 800mm"  
    template: rahmentuer_ud4
    params:
      Lichtbreite: 800
      Lichthoehe: 2100

  # === BRANDSCHUTZTÜREN ===
  brandschutz_t30:
    description: "Brandschutztür T30 (EI30)"
    template: rahmentuer_ud5
    params:
      Lichtbreite: 900
      Lichthoehe: 2100
      Brandschutz: true
      Tuerstaerke: 68

  # === NASSZELLEN ===
  nasszelle_750:
    description: "Nasszelltür 750mm (WC/Bad)"
    template: rahmentuer_ud4
    params:
      Lichtbreite: 750
      Lichthoehe: 2000
      Schwelle: false
      
  # === MIT SCHWELLE ===
  aussentuer_schwelle:
    description: "Aussentür mit Schwelle"
    template: rahmentuer_schwelle
    params:
      Lichtbreite: 1000
      Lichthoehe: 2100
      Schwellenhoehe: 20
```

#### Konzept: Template-System

**Templates** = GH-Definitionen mit Metadaten

```yaml
# templates/doors.yaml
templates:
  rahmentuer_ud3:
    file: "C:/Users/Adi.Muff/Documents/Rhino/GH/Rahmentuer_UD3.gh"
    description: "Rahmentür Basis (UD3)"
    category: doors
    defaults:
      Lichtbreite: 900
      Lichthoehe: 2100
      Rahmendicke: 53
    validation:
      Lichtbreite: { min: 600, max: 1400 }
      Lichthoehe: { min: 1800, max: 2600 }
    aliases:
      Pt: Point
      Breite: Lichtbreite
      Hoehe: Lichthoehe

  rahmentuer_ud4:
    file: "C:/Users/Adi.Muff/Documents/Rhino/GH/Rahmentuer_UD4.gh"
    description: "Rahmentür Standard (UD4)"
    category: doors
    inherits: rahmentuer_ud3  # Erbt defaults/validation
    defaults:
      Tuerstaerke: 58
      DichtNut_Rahmen: true
    
  rahmentuer_ud5:
    file: "C:/Users/Adi.Muff/Documents/Rhino/GH/Rahmentuer_UD5.gh"
    description: "Rahmentür Brandschutz (UD5)"
    category: doors
    inherits: rahmentuer_ud4
    defaults:
      Tuerstaerke: 68
      Brandschutz: true
      Intumex: true

  rahmentuer_schwelle:
    file: "C:/Users/Adi.Muff/Documents/Rhino/GH/Rahmentuer_Schwelle.gh"
    description: "Rahmentür mit Bodenschwelle"
    category: doors
    inherits: rahmentuer_ud4
    defaults:
      Schwellenhoehe: 20
```

#### CLI-Erweiterung

```bash
# === PRESETS ===

# Liste alle Presets
python3 grasshopper.py presets
# Output:
# Verfügbare Presets:
#   standard_900      Standard Innentür 900mm
#   standard_800      Standard Innentür 800mm
#   brandschutz_t30   Brandschutztür T30 (EI30)
#   nasszelle_750     Nasszelltür 750mm (WC/Bad)
#   aussentuer_schwelle  Aussentür mit Schwelle

# Preset verwenden
python3 grasshopper.py preset standard_900 --Point 0,0,0

# Preset mit Überschreibung
python3 grasshopper.py preset standard_900 --Lichthoehe 2200 --Point 1500,0,0

# Preset Info
python3 grasshopper.py preset standard_900 --info
# Output:
# Preset: standard_900
# Template: rahmentuer_ud4
# Beschreibung: Standard Innentür 900mm
# Parameter:
#   Lichtbreite: 900
#   Lichthoehe: 2100
#   (inherited from template)
#   Rahmendicke: 53
#   Tuerstaerke: 58
#   DichtNut_Rahmen: true

# === TEMPLATES ===

# Liste alle Templates
python3 grasshopper.py templates
# Output:
# Verfügbare Templates:
#   rahmentuer_ud3    Rahmentür Basis (UD3)
#   rahmentuer_ud4    Rahmentür Standard (UD4)
#   rahmentuer_ud5    Rahmentür Brandschutz (UD5)
#   rahmentuer_schwelle  Rahmentür mit Bodenschwelle

# Template direkt verwenden (mit Alias!)
python3 grasshopper.py template rahmentuer_ud4 --Breite 1000 --Hoehe 2200 --Point 0,0,0
```

#### Implementation: PresetManager

```python
# presets.py
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class PresetManager:
    """Manage door presets and templates."""
    
    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path(__file__).parent / 'config'
        self.templates = self._load_yaml('templates/doors.yaml').get('templates', {})
        self.presets = self._load_yaml('presets/doors.yaml').get('presets', {})
    
    def _load_yaml(self, filename: str) -> dict:
        path = self.config_dir / filename
        if path.exists():
            return yaml.safe_load(path.read_text())
        return {}
    
    def get_template(self, name: str) -> dict:
        """Get template by name, resolving inheritance."""
        if name not in self.templates:
            raise ValueError(f"Unknown template: {name}")
        
        template = dict(self.templates[name])
        
        # Resolve inheritance chain
        if 'inherits' in template:
            parent = self.get_template(template['inherits'])
            # Merge: parent defaults + child defaults
            merged_defaults = {**parent.get('defaults', {}), **template.get('defaults', {})}
            merged_validation = {**parent.get('validation', {}), **template.get('validation', {})}
            merged_aliases = {**parent.get('aliases', {}), **template.get('aliases', {})}
            
            template['defaults'] = merged_defaults
            template['validation'] = merged_validation
            template['aliases'] = merged_aliases
            template['file'] = template.get('file', parent.get('file'))
        
        return template
    
    def get_preset(self, name: str) -> dict:
        """Get preset by name, resolving template reference."""
        if name not in self.presets:
            raise ValueError(f"Unknown preset: {name}")
        
        preset = dict(self.presets[name])
        template = self.get_template(preset['template'])
        
        # Merge template defaults with preset params
        params = {**template.get('defaults', {}), **preset.get('params', {})}
        
        return {
            'name': name,
            'description': preset.get('description', ''),
            'template_name': preset['template'],
            'file': template['file'],
            'params': params,
            'validation': template.get('validation', {}),
            'aliases': template.get('aliases', {})
        }
    
    def list_presets(self) -> list:
        """List all available presets."""
        return [
            {'name': k, 'description': v.get('description', '')}
            for k, v in self.presets.items()
        ]
    
    def list_templates(self) -> list:
        """List all available templates."""
        return [
            {'name': k, 'description': v.get('description', '')}
            for k, v in self.templates.items()
        ]
    
    def resolve_aliases(self, params: dict, aliases: dict) -> dict:
        """Apply alias mapping to parameters."""
        return {aliases.get(k, k): v for k, v in params.items()}


def run_preset(preset_name: str, overrides: dict = None, point: str = None) -> dict:
    """Run a preset with optional parameter overrides."""
    from grasshopper import run_grasshopper_player
    
    manager = PresetManager()
    preset = manager.get_preset(preset_name)
    
    # Merge preset params with overrides
    params = dict(preset['params'])
    if overrides:
        # Resolve aliases first
        resolved_overrides = manager.resolve_aliases(overrides, preset['aliases'])
        params.update(resolved_overrides)
    
    if point:
        params['Point'] = point
    
    # Run with resolved parameters
    return run_grasshopper_player(preset['file'], params)
```

#### Verzeichnisstruktur

```
scripts/clawdbot/
├── grasshopper.py          # Hauptscript (erweitert)
├── presets.py              # PresetManager
├── config/
│   ├── templates/
│   │   └── doors.yaml      # Tür-Templates
│   └── presets/
│       └── doors.yaml      # Tür-Presets
```

#### Erweiterung: Kategorien & Filterung

```bash
# Nur Brandschutztüren
python3 grasshopper.py presets --category brandschutz

# Suche in Presets
python3 grasshopper.py presets --search "nasszelle"
```

#### Integration mit Batch-Processing (Iteration 1)

```json
// doors_batch.json - Batch mit Presets
{
  "items": [
    {"preset": "standard_900", "Point": "0,0,0"},
    {"preset": "standard_800", "Point": "1500,0,0"},
    {"preset": "brandschutz_t30", "Point": "3000,0,0"},
    {"preset": "nasszelle_750", "Point": "4500,0,0", "Lichthoehe": 1900}
  ]
}
```

```bash
python3 grasshopper.py batch doors_batch.json
```

#### Quick Wins (30 Min Implementation)

1. **Einfache JSON-Config** statt YAML für den Start
2. **Hardcoded Presets** erstmal inline in Python
3. **`preset` Subcommand** mit Basis-Funktionalität

```python
# Minimal viable implementation
QUICK_PRESETS = {
    'standard_900': {
        'file': 'C:/Users/Adi.Muff/Documents/Rhino/GH/Rahmentuer_UD4.gh',
        'params': {'Lichtbreite': 900, 'Lichthoehe': 2100}
    },
    'standard_800': {
        'file': 'C:/Users/Adi.Muff/Documents/Rhino/GH/Rahmentuer_UD4.gh', 
        'params': {'Lichtbreite': 800, 'Lichthoehe': 2100}
    },
    'brandschutz': {
        'file': 'C:/Users/Adi.Muff/Documents/Rhino/GH/Rahmentuer_UD5.gh',
        'params': {'Lichtbreite': 900, 'Lichthoehe': 2100, 'Tuerstaerke': 68}
    }
}
```

**Aufwand-Schätzung:**
- Quick Win (hardcoded): 30 Min
- Basis-System (YAML-Config): 2h
- Vollständig (mit Vererbung, Kategorien, Batch-Integration): 4-5h

**Benefits:**
- Drastisch reduzierte Tipparbeit bei repetitiven Aufgaben
- Standardisierte Konfigurationen = weniger Fehler
- Selbstdokumentierend (presets --info)
- Basis für weitere Automatisierung (z.B. Türlisten aus Excel → Batch)

---

### Iteration 6 (04:30) - SKILL.md Dokumentation erweitern

**Problem:** Die aktuelle SKILL.md dokumentiert `grasshopper.py` NICHT - obwohl es heute Nacht implementiert wurde und funktioniert!

#### Fehlende Dokumentation

1. **Grasshopper Player Section** - Komplett fehlend
2. **Architektur-Übersicht** - Wie funktioniert das TCP-Protokoll?
3. **End-to-End Workflows** - Mehr praktische Beispiele
4. **Bekannte Limitationen** - Was geht nicht?
5. **Troubleshooting erweitern** - Mehr Fälle

#### Neue Section: 🌿 Grasshopper Player

```markdown
## 🌿 Grasshopper Player Automation

Run Grasshopper definitions with custom parameters directly from CLI.

### Basic Usage

```bash
# Show available parameters in a GH file
python3 grasshopper.py info "C:/path/to/definition.gh"

# Run with default parameters
python3 grasshopper.py run "C:/path/to/definition.gh"

# Run with custom parameters
python3 grasshopper.py run "C:/path/to/definition.gh" --Lichthoehe 2200 --Lichtbreite 1000

# Set insertion point
python3 grasshopper.py run "C:/path/to/definition.gh" --Point 100,200,0
```

### Parameter Discovery

```bash
python3 grasshopper.py info "C:/Users/.../Rahmentuer_UD4.gh"
# Output:
# Available Parameters (26):
# ----------------------------------------------------------
#   --Lichthoehe = 2100.0 [1800.0 - 2600.0]  (Number)
#   --Lichtbreite = 900.0 [600.0 - 1400.0]  (Number)
#   --Rahmendicke = 53.0  (Number)
#   --Tuerstaerke = 58.0  (Number)
#   --DichtNut_Rahmen = True  (Boolean)
#   ...
```

### Example: Create Multiple Doors

```bash
# Door 1: Standard at origin
python3 grasshopper.py run "C:/path/to/Rahmentuer_UD4.gh" \
  --Lichthoehe 2100 --Lichtbreite 900 --Point 0,0,0

# Door 2: Wider door offset 1500mm
python3 grasshopper.py run "C:/path/to/Rahmentuer_UD4.gh" \
  --Lichthoehe 2100 --Lichtbreite 1000 --Point 1500,0,0

# Door 3: Taller door offset 3000mm  
python3 grasshopper.py run "C:/path/to/Rahmentuer_UD4.gh" \
  --Lichthoehe 2300 --Lichtbreite 900 --Point 3000,0,0
```

### How It Works

1. `info` loads the GH file via SDK to extract parameter metadata
2. `run` starts Rhino's GrasshopperPlayer command
3. Script monitors command prompts and sends parameter values
4. Prompts like "Lichthoehe <2100>" get the custom or default value
5. "Get Point" prompts receive the --Point coordinate or 0,0,0

### Known Parameter Aliases

| GH Nickname | Player Prompt |
|-------------|---------------|
| Pt | Point |
| Punkt | Point |

> **Tip:** Use `info` first to see exact parameter names expected by the Player.

### Output Format

```json
{
  "status": "success",
  "file": "C:/path/to/definition.gh",
  "prompts_handled": [
    {"name": "Lichthoehe", "value": "2200", "was_custom": true},
    {"name": "Lichtbreite", "value": "1000", "was_custom": true},
    {"name": "Point", "value": "0,0,0", "was_custom": false}
  ],
  "objects_created": 54,
  "layers": ["Tuerblatt", "Tuerrahmen", "Intumex_Rahmen", ...]
}
```
```

#### Neue Section: 🏗️ Architecture Overview

```markdown
## 🏗️ Architecture

### Communication Flow

```
┌─────────────┐     TCP/1999      ┌─────────────┐
│  Clawdbot   │ ◄───────────────► │  RhinoMCP   │
│   (WSL)     │    JSON-RPC       │  (Windows)  │
└─────────────┘                   └──────┬──────┘
                                         │
                                         ▼
                                  ┌─────────────┐
                                  │   Rhino 8   │
                                  │ + Grasshop. │
                                  └─────────────┘
```

### Protocol

- **Transport:** TCP socket, default port 1999
- **Format:** JSON-RPC style messages
- **Request:** `{"type": "command_name", "params": {...}}`
- **Response:** `{"status": "success|error", "result": {...}}`

### Commands (partial list)

| Command | Description |
|---------|-------------|
| `ping` | Connection test |
| `get_document_info` | Object count, layers, etc. |
| `create_geometry` | Create primitives |
| `execute_rhinoscript_python_code` | Run arbitrary Python |
| `load_grasshopper_definition` | Load GH for parameter inspection |
| `capture_viewport` | Screenshot to file |
```

#### Neue Section: ⚠️ Known Limitations

```markdown
## ⚠️ Known Limitations

### General
- **Single Document:** Only one Rhino document at a time
- **No Undo Batching:** Each command is a separate undo step
- **Windows Only:** RhinoMCP plugin requires Windows Rhino

### Grasshopper Player
- **Sequential Prompts:** Parameters are set one-by-one (not instant)
- **No Mid-Run Cancel:** Once started, Player runs to completion
- **Alias Mismatch:** GH nicknames may differ from Player prompts (use `info` first)
- **Point Prompt Detection:** Relies on "Point" appearing in prompt text

### Geometry
- **Boolean Prerequisites:** Objects must be valid closed solids
- **Large Meshes:** May timeout on complex operations
- **Block Editing:** Limited support for in-place block editing

### Screenshots
- **WSL Path Required:** Screenshots save via UNC path to Linux filesystem
- **Active Viewport:** Captures the currently active viewport only
```

#### Erweitertes Troubleshooting

```markdown
## Troubleshooting (Extended)

| Problem | Symptom | Solution |
|---------|---------|----------|
| Connection refused | `ConnectionRefusedError` | Run `tcpstart` in Rhino |
| Timeout | Command hangs | Increase `timeout` in config.json |
| Boolean failed | "Objects must be solid" | Check objects with `analysis.py properties` |
| Screenshot black | Empty image | Ensure geometry is in view, run `viewport.py zoom` first |
| GH Player stuck | Prompts not advancing | Check Rhino command line for unexpected prompt |
| Wrong parameter | Value ignored | Use `grasshopper.py info` to verify exact parameter names |
| Path not found | Windows path error | Use forward slashes or escaped backslashes |
| WSL network issue | Can't reach Windows | Check WSL IP with `ip route \| grep default` |

### Debug Mode

```bash
# Enable verbose logging
export RHINOMCP_DEBUG=1
python3 rhino_client.py ping

# Watch Rhino-side log
tail -f "/mnt/c/Users/Adi.Muff/AppData/Local/Temp/rhinomcp.log"
```

### Common Fixes

**WSL IP changed after reboot:**
```bash
# Get current Windows host IP
WIN_IP=$(ip route | grep default | awk '{print $3}')
# Update config.json host field
```

**Rhino not responding:**
1. Check if Rhino is busy (progress bar?)
2. Run `tcpstop` then `tcpstart` to reset listener
3. Restart Rhino if plugin crashed
```

#### Neue Section: 📚 End-to-End Workflows

```markdown
## 📚 Complete Workflows

### Workflow 1: Batch Door Creation

```bash
# 1. Verify GH file parameters
python3 grasshopper.py info "C:/path/to/Rahmentuer_UD4.gh"

# 2. Create doors at specific positions
for i in 0 1 2 3 4; do
  X=$((i * 1500))
  python3 grasshopper.py run "C:/path/to/Rahmentuer_UD4.gh" \
    --Lichthoehe 2100 --Lichtbreite 900 --Point "$X,0,0"
done

# 3. Take screenshot of result
python3 viewport.py zoom
python3 viewport.py screenshot --width 1920 --height 1080
```

### Workflow 2: Parametric Facade Panel

```bash
# 1. Create base geometry
python3 geometry.py box --width 1000 --length 50 --height 2000 --name "Panel_Base"
# Note the returned ID

# 2. Create cutting pattern
python3 geometry.py cylinder --radius 100 --height 100 --position 500,0,500
python3 transforms.py polar <cylinder_id> --center 500,0,1000 --axis 0,1,0 --count 5

# 3. Boolean subtract all cylinders
python3 booleans.py difference <panel_id> <cyl1> <cyl2> <cyl3> <cyl4> <cyl5>

# 4. Apply material and render
python3 materials.py preset aluminum
python3 materials.py assign "Default" <material_id>
python3 render.py render --output facade_panel.png
```

### Workflow 3: From CSV to 3D

```bash
# Given: points.csv with columns x,y,z,radius
# Create spheres at each point

python3 -c "
import csv
from geometry import create_sphere

with open('points.csv') as f:
    for row in csv.DictReader(f):
        create_sphere(
            float(row['radius']),
            [float(row['x']), float(row['y']), float(row['z'])]
        )
"
```

#### Update Scripts Reference Table

Add to existing table:

```markdown
| Script | Purpose |
|--------|---------|
| `grasshopper.py` | **NEW:** Run GH definitions with custom parameters |
```

**Aufwand-Schätzung:** 
- Grasshopper Section: 30 Min (Copy/Adapt)
- Architecture + Limitations: 30 Min
- Workflows + Troubleshooting: 45 Min
- **Total: ~2h**

**Priorität:**
1. ⭐ Grasshopper Section (fehlt komplett, wird aktiv genutzt)
2. Architecture (hilft beim Debugging)
3. Workflows (nice-to-have)
4. Limitations (verhindert Frust)

---

### Iteration 7 (05:00) - Code-Qualität & Refactoring

**Analyse:** 3086 Zeilen Python über 20+ Scripts. Code-Review durchgeführt.

#### Gefundene Issues

##### 1. Massive Code-Duplikation

**Problem:** `with RhinoClient()` erscheint **84 Mal** in den Scripts!

```python
# Aktuell in JEDER Funktion:
def some_operation(...):
    with RhinoClient() as client:
        return client.send_command(...)

def another_operation(...):
    with RhinoClient() as client:
        return client.send_command(...)
```

**Lösung:** Decorator oder gemeinsame Base-Klasse

```python
# Option A: Decorator
from functools import wraps

def with_rhino(func):
    """Inject RhinoClient as first argument."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with RhinoClient() as client:
            return func(client, *args, **kwargs)
    return wrapper

@with_rhino
def create_layer(client, name: str, color: list = None) -> dict:
    params = {"name": name}
    if color:
        params["color"] = color
    return client.send_command("create_layer", params)
```

```python
# Option B: Command-Klassen (sauberer für komplexe Ops)
class RhinoCommand:
    """Base class for Rhino commands."""
    
    def __init__(self, client: RhinoClient = None):
        self._client = client
        self._owns_client = False
    
    @property
    def client(self) -> RhinoClient:
        if self._client is None:
            self._client = RhinoClient()
            self._client.connect()
            self._owns_client = True
        return self._client
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        if self._owns_client and self._client:
            self._client.disconnect()

class LayerCommands(RhinoCommand):
    def create(self, name: str, color: list = None) -> dict:
        return self.client.send_command("create_layer", {"name": name, "color": color})
    
    def delete(self, name: str) -> dict:
        return self.client.send_command("delete_layer", {"name": name})

# Usage
with LayerCommands() as layers:
    layers.create("MyLayer", [255, 0, 0])
    layers.create("Another")  # Same connection!
```

##### 2. Utility-Funktionen dupliziert

**Problem:** `parse_coords()` ist nur in geometry.py, aber überall nötig.

```python
# Sollte in utils.py sein:
def parse_coords(s: str) -> list[float] | None:
    """Parse 'x,y,z' string to [x, y, z] list."""
    if not s:
        return None
    return [float(x.strip()) for x in s.split(',')]

def parse_color(s: str) -> list[int] | None:
    """Parse 'r,g,b' string to [r, g, b] list."""
    if not s:
        return None
    return [int(x.strip()) for x in s.split(',')]

def format_point(pt: list) -> str:
    """Format point for display."""
    return f"({pt[0]:.2f}, {pt[1]:.2f}, {pt[2]:.2f})"
```

##### 3. Inkonsistente Type Hints

**Aktuell:** Mischung aus typed/untyped

```python
# geometry.py - teilweise typed
def create_object(obj_type: str, params: dict, name: str = None, ...

# layers.py - teilweise typed  
def create_layer(name: str, color: list = None, parent: str = None) -> dict:

# Andere Files - kaum typed
def do_something(x, y):
```

**Lösung:** Durchgängig Type Hints + `py.typed` marker

```python
from typing import Optional, List, Dict, Any, Union

Point3D = List[float]  # Type alias
Color = List[int]
ObjectId = str

def create_object(
    obj_type: str,
    params: Dict[str, Any],
    name: Optional[str] = None,
    color: Optional[Color] = None,
    layer: Optional[str] = None,
    translation: Optional[Point3D] = None
) -> Dict[str, Any]:
    ...
```

##### 4. Kein strukturiertes Logging

**Aktuell:** `print()` überall

```python
print(f"Connection failed: {e}", file=sys.stderr)
print(f"Starting GrasshopperPlayer: {file_path}")
```

**Lösung:** Python logging module

```python
# In rhino_client.py oder __init__.py
import logging

logger = logging.getLogger("rhinomcp")

# Konfigurierbar via Umgebungsvariable
if os.getenv("RHINOMCP_DEBUG"):
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.WARNING)

# Usage
logger.debug(f"Sending command: {cmd_type}")
logger.info(f"Created object: {result.get('id')}")
logger.warning(f"Timeout on command {cmd_type}, retrying...")
logger.error(f"Connection failed: {e}")
```

##### 5. Keine Tests

**Problem:** Null Unit-Tests gefunden.

**Quick Win:** Zumindest für Core-Funktionen

```python
# tests/test_utils.py
import pytest
from utils import parse_coords, parse_color

def test_parse_coords_basic():
    assert parse_coords("1,2,3") == [1.0, 2.0, 3.0]

def test_parse_coords_with_spaces():
    assert parse_coords("1, 2, 3") == [1.0, 2.0, 3.0]

def test_parse_coords_none():
    assert parse_coords(None) is None
    assert parse_coords("") is None

def test_parse_color():
    assert parse_color("255,128,0") == [255, 128, 0]

# tests/test_client.py (mit Mock)
from unittest.mock import Mock, patch

def test_ping():
    with patch('rhino_client.socket.socket') as mock_socket:
        mock_socket.return_value.recv.return_value = b'{"status":"success"}'
        client = RhinoClient()
        # ...
```

##### 6. Config-Loading redundant

**Problem:** Config wird in jeder Datei neu geladen

**Lösung:** Singleton-Pattern oder zentrale Config-Klasse

```python
# config.py
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import json

@dataclass
class ConnectionConfig:
    host: str = "172.31.96.1"
    port: int = 1999
    timeout: float = 15.0
    max_retries: int = 3
    retry_delay: float = 1.0

@dataclass  
class ScreenshotConfig:
    linux_dir: str = ""
    windows_dir: str = ""

class Config:
    _instance: Optional['Config'] = None
    
    def __init__(self):
        self.connection = ConnectionConfig()
        self.screenshots = ScreenshotConfig()
        self._load()
    
    @classmethod
    def get(cls) -> 'Config':
        if cls._instance is None:
            cls._instance = Config()
        return cls._instance
    
    def _load(self):
        config_path = Path(__file__).parent / "config.json"
        if config_path.exists():
            data = json.loads(config_path.read_text())
            conn = data.get("connection", {})
            self.connection = ConnectionConfig(**conn)
            # ...

# Usage überall:
from config import Config
cfg = Config.get()
client = RhinoClient(cfg.connection.host, cfg.connection.port)
```

#### Vorgeschlagene Verzeichnisstruktur (Refactored)

```
scripts/clawdbot/
├── __init__.py
├── config.py              # Zentrale Config (Singleton)
├── utils.py               # parse_coords, parse_color, etc.
├── logging_config.py      # Logger setup
├── exceptions.py          # Custom exceptions
├── client/
│   ├── __init__.py
│   ├── base.py            # RhinoClient
│   └── commands.py        # RhinoCommand base class
├── commands/
│   ├── __init__.py
│   ├── geometry.py        # Geometry commands
│   ├── layers.py          # Layer commands
│   ├── transforms.py      # Transform commands
│   └── ...
├── cli/
│   ├── __init__.py
│   ├── main.py            # Unified CLI entrypoint
│   └── parsers.py         # Shared argument parsers
├── grasshopper/
│   ├── __init__.py
│   ├── player.py          # GH Player automation
│   ├── presets.py         # Preset manager
│   └── config/
│       ├── templates/
│       └── presets/
└── tests/
    ├── __init__.py
    ├── test_utils.py
    ├── test_client.py
    └── conftest.py        # pytest fixtures
```

#### Refactoring-Prioritäten

| Prio | Task | Aufwand | Impact |
|------|------|---------|--------|
| 1 | utils.py extrahieren | 30 Min | Sofort weniger Duplikation |
| 2 | Logging einführen | 1h | Besseres Debugging |
| 3 | Config-Singleton | 1h | Saubere Konfiguration |
| 4 | @with_rhino Decorator | 1h | 84→20 Client-Instanzen |
| 5 | Type Hints komplettieren | 2h | IDE-Support, weniger Bugs |
| 6 | Tests für Core | 3h | Regressionssicherheit |
| 7 | CLI unifizieren | 4h | `rhino geometry sphere` statt `python3 geometry.py sphere` |

#### Quick Win: utils.py sofort erstellen

```python
# utils.py - Kann sofort erstellt werden
"""Common utilities for RhinoMCP scripts."""

from typing import List, Optional

def parse_coords(s: str) -> Optional[List[float]]:
    """Parse 'x,y,z' string to [x, y, z] float list."""
    if not s:
        return None
    return [float(x.strip()) for x in s.split(',')]

def parse_color(s: str) -> Optional[List[int]]:
    """Parse 'r,g,b' string to [r, g, b] int list."""
    if not s:
        return None
    return [int(x.strip()) for x in s.split(',')]

def parse_ids(s: str) -> List[str]:
    """Parse comma-separated IDs."""
    if not s:
        return []
    return [x.strip() for x in s.split(',') if x.strip()]

def format_point(pt: List[float], decimals: int = 2) -> str:
    """Format point for human-readable display."""
    return f"({pt[0]:.{decimals}f}, {pt[1]:.{decimals}f}, {pt[2]:.{decimals}f})"

def format_result(result: dict, verbose: bool = False) -> str:
    """Format command result for CLI output."""
    if result.get('status') == 'success':
        if verbose:
            import json
            return json.dumps(result, indent=2)
        obj_id = result.get('result', {}).get('id', result.get('result', {}).get('guid'))
        if obj_id:
            return f"✓ Created: {obj_id}"
        return "✓ Success"
    else:
        return f"✗ Error: {result.get('message', 'Unknown error')}"
```

**Gesamtaufwand Refactoring:** ~12-15h für vollständiges Cleanup

**Empfehlung:** Schrittweise vorgehen, mit utils.py + logging starten. Nicht alles auf einmal!

---

### Iteration 8 (05:30) - Finale Priorisierung & Roadmap

**Ziel:** Alle Erkenntnisse der Nacht-Session zusammenfassen und priorisierte Roadmap erstellen.

---

## 📊 Executive Summary

### Was wurde analysiert (8 Iterationen, 01:00-05:30)

| Iteration | Fokus | Kern-Erkenntnis |
|-----------|-------|-----------------|
| 0 | GH Integration | 4 Probleme: Aliase, Validierung, GUIDs, Batch |
| 1 | Batch-Processing | JSON/CSV Input-Format + CLI designed |
| 2 | Error Handling | Retry-Decorator + Exception-Hierarchie |
| 3 | Validierung | SDK-basierte min/max Validierung |
| 4 | Output-Tracking | Vor/Nach-Differenz für Object GUIDs |
| 5 | Presets & Templates | YAML-Config für Türtypen |
| 6 | SKILL.md Doku | Grasshopper Section fehlt komplett! |
| 7 | Code-Qualität | 84x Duplikation, keine Tests, kein Logging |

### Geschätzter Gesamtaufwand

| Kategorie | Aufwand | Beschreibung |
|-----------|---------|--------------|
| Quick Wins | 2-3h | utils.py, Logging, Alias-Mapping |
| Core Features | 6-8h | Batch, Validierung, GUIDs |
| Presets/Templates | 4-5h | Config-System, CLI-Erweiterung |
| Dokumentation | 2h | SKILL.md erweitern |
| Refactoring | 12-15h | Tests, Types, Struktur |
| **TOTAL** | **~30h** | Vollständige Implementation |

---

## 🎯 Priorisierte Roadmap

### Phase 1: Quick Wins (Weekend Sprint, 3h)
*Sofort umsetzbar, hoher Impact*

1. **utils.py erstellen** (30 Min)
   - parse_coords, parse_color, format_result
   - Sofort in allen Scripts nutzbar

2. **Alias-Mapping in grasshopper.py** (30 Min)
   - PARAM_ALIASES dict
   - Pt → Point etc.
   - Löst das häufigste User-Problem

3. **SKILL.md Grasshopper Section** (1h)
   - Dokumentiert was bereits funktioniert
   - Copy/Paste aus Iteration 6

4. **Logging statt print()** (1h)
   - RHINOMCP_DEBUG Umgebungsvariable
   - Besseres Debugging

**Deliverable:** Sofort bessere DX, weniger Frust bei Nutzung

---

### Phase 2: Core Improvements (1 Woche, 8h)
*Macht das Tool wirklich produktiv*

1. **Object GUID Tracking** (2h)
   - Vor/Nach-Differenz implementieren
   - created_guids im Output
   - Basis für alle Nachbearbeitung

2. **Parameter-Validierung** (2h)
   - SDK min/max auslesen
   - --validate und --dry-run Flags
   - Verhindert stille Fehler

3. **Batch-Processing Basis** (3h)
   - JSON-Input mit items[]
   - --batch Subcommand
   - Ergebnis-Report

4. **Error Handling verbessern** (1h)
   - @with_retry Decorator
   - Custom Exceptions
   - Klare Fehlermeldungen

**Deliverable:** 100 Türen aus JSON statt 100 CLI-Aufrufe

---

### Phase 3: Preset-System (2 Wochen, 5h)
*Workflow-Beschleunigung für repetitive Aufgaben*

1. **Hardcoded Presets** (1h)
   - QUICK_PRESETS dict in grasshopper.py
   - standard_900, brandschutz_t30, etc.
   - Sofort nutzbar ohne Config-Files

2. **YAML Config** (2h)
   - templates/doors.yaml
   - presets/doors.yaml
   - Vererbung (UD5 → UD4 → UD3)

3. **CLI Integration** (2h)
   - `grasshopper.py preset standard_900`
   - `grasshopper.py presets --list`
   - `grasshopper.py preset X --info`

**Deliverable:** `preset standard_900 --Point 0,0,0` statt voller Parameterliste

---

### Phase 4: Polish & Refactoring (Ongoing, 15h)
*Langfristige Code-Gesundheit*

1. **Unit Tests für Core** (3h)
   - pytest Setup
   - utils, client, validation Tests
   - CI-ready

2. **Type Hints vervollständigen** (2h)
   - Alle public APIs
   - py.typed marker

3. **@with_rhino Decorator** (1h)
   - Reduziert 84 → ~20 Client-Instanzen

4. **Unified CLI** (4h)
   - `rhino geometry sphere` statt `python3 geometry.py sphere`
   - Click oder Typer

5. **Config Singleton** (1h)
   - Zentrale Konfiguration

6. **Directory Restructure** (3h)
   - client/, commands/, cli/, tests/

**Deliverable:** Maintainable, testable, documented codebase

---

## 🏁 Empfohlener Start

### Diese Woche (2h)
```bash
# 1. utils.py erstellen und committen
# 2. Alias-Mapping in grasshopper.py
# 3. SKILL.md Grasshopper Section
```

### Nächstes Weekend (4h)
```bash
# 4. Object GUID Tracking
# 5. Validierung mit --dry-run
```

### Danach nach Bedarf
- Batch-Processing wenn >10 Objekte nötig
- Presets wenn gleiche Türen oft wiederholt
- Refactoring wenn Code-Änderungen anstehen

---

## 📋 Checkliste für Präsentation (06:00)

- [x] Problem-Analyse komplett (8 Iterationen)
- [x] Konkrete Code-Vorschläge dokumentiert
- [x] Aufwand geschätzt
- [x] Roadmap priorisiert
- [x] Quick Wins identifiziert
- [ ] Optional: utils.py live erstellen als Demo

---

## 🔑 Key Takeaways

1. **grasshopper.py funktioniert** - aber Doku fehlt und kleine Pain Points (Aliase)
2. **Batch ist der größte Hebel** - 100 Türen = 100 Aufrufe ist nicht praktikabel
3. **Code ist okay, aber dupliziert** - 84x with RhinoClient() ist zu viel
4. **Quick Wins sind schnell** - 3h für spürbare Verbesserung
5. **Vollständig = ~30h** - aber iterativ umsetzbar

**Bottom Line:** Phase 1 (Quick Wins) diese Woche, dann nach Bedarf erweitern.

