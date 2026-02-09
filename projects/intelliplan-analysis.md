# IntelliPlan – Schonungslos ehrliche Deep Analysis

**Datum:** 2025-07-17 (Erstanalyse) | **Update:** 2026-01-29  
**Analysiert:** Kompletter Source-Code (Backend + Frontend + Migrations)  
**Autor:** Automatische Code-Analyse

---

## ✅ Fixes seit Erstanalyse (2026-01-29)

Die folgenden kritischen Issues aus der Erstanalyse wurden auf `feature/security-foundation` gefixt und nach `main` gemerged (PR #2):

| # | Issue | Status | Commit/Detail |
|---|-------|--------|---------------|
| 1 | JWT Secret Fallback `'dev-insecure-secret'` | ✅ GEFIXT | Throws at startup wenn nicht gesetzt |
| 2 | x-user-id Header Bypass | ✅ GEFIXT | Nur Bearer Token Auth |
| 3 | Kein Rate Limiting | ✅ GEFIXT | Global 100/15min + Auth 5/15min |
| 4 | Logout No-Op | ✅ GEFIXT | In-Memory Token Blacklist |
| 5 | 0% Test Coverage | ✅ GEFIXT | 71 Tests (Vitest), 5 Test-Files |
| 6 | AI Suggestions nicht im Frontend | ✅ GEFIXT | OverlapWarningDialog zeigt Vorschläge |
| 7 | Soft Delete fehlte | ✅ GEFIXT | Migration 017, Projects + Tasks |

---

## Teil 8: Executive Summary (Top 10) – AKTUALISIERT

1. **Solides technisches Fundament** – Saubere Architektur (Controller/Service/Model), konsistente API-Responses, parameterisierte SQL-Queries. Kein Amateur-Projekt.
2. ~~Null Tests~~ → **71 Tests** mit Vitest (Auth, AI-Conflict, Appointments, Tasks, Validators). Integration Tests in Arbeit.
3. ~~Kein Rate Limiting~~ → **Rate Limiting aktiv** (Global + Auth-spezifisch)
4. ~~JWT Secret Fallback~~ → **Gefixt** – Startup-Error wenn nicht konfiguriert
5. **Nur ~20% eines Schreinerei-ERPs gebaut** – Terminverwaltung & Projektplanung existieren. Kalkulation, Offerten, Material, Rechnungen, BOM, Zeiterfassung: alles fehlt.
6. **AI Conflict Resolution ist regelbasiert**, nicht AI – Der Name oversellt. Gute Heuristiken, aber kein ML/LLM. Trotzdem ein valides Feature. **Jetzt auch im Frontend sichtbar.**
7. **Frontend ist überraschend poliert** – MUI-basiert, responsive, Breadcrumbs, Empty States, Keyboard Shortcuts, Dark Mode, Gantt-View. Professioneller als erwartet.
8. ~~Logout ist ein No-Op~~ → **Token Blacklist implementiert**
9. **Markt-Lücke ist real** – Kein modernes, API-first Schreinerei-ERP für CH-KMU. IntelliPlan kann diese Nische besetzen, wenn es die fehlenden Module baut.
10. **Geschätzter Aufwand bis MVP "Schreinerei-ERP Light": 6-9 Monate** mit 1-2 Entwicklern. Aktuell ~20% des Weges geschafft.

---

## Teil 1: Backend Code-Review

### Error Handling Konsistenz
**Bewertung: ✅ Gut**

Alle Controller verwenden konsistent `try/catch` mit `next(error)`. Es gibt ein zentrales `errorHandler` Middleware:

```typescript
// middleware/errorHandler.ts
export const errorHandler = (err: AppError, _req: Request, res: Response, _next: NextFunction): void => {
  const statusCode = err.statusCode || 500;
  const message = err.message || 'Internal Server Error';
  res.status(statusCode).json({
    success: false,
    error: { message: ... }
  });
};
```

**Positiv:** Production-Mode versteckt Stack Traces. 404-Handler vorhanden.  
**Negativ:** Kein custom Error-Klasse System. Errors werden als generische Strings geworfen, nicht als typisierte Fehler.

### SQL Injection Risiken
**Bewertung: ✅ Sicher**

Alle Queries verwenden parameterisierte Statements (`$1, $2, ...`). Kein einziger Fall von String-Concatenation in SQL gefunden. Beispiel:

```typescript
// Korrekt überall:
const result = await pool.query<Appointment>(
  `SELECT * FROM appointments WHERE user_id = $1 AND deleted_at IS NULL`,
  [userId]
);
```

Dynamische WHERE-Clauses (appointmentService, taskService) bauen den SQL-String zusammen, aber Parameter werden immer korrekt indexiert. **Kein SQL-Injection-Risiko.**

### TypeScript Qualität
**Bewertung: ⚠️ Ordentlich mit Mängeln**

- **Kein `any`-Missbrauch** in Services und Models – saubere Interfaces überall
- **Ein `any`-Cast im authController:** `const userId = (req as any).userId;` – Obwohl in `roleMiddleware.ts` korrekt ein `declare module` existiert. Inkonsistenz.
- **DTOs sind sauber definiert** (CreateTaskDTO, UpdateTaskDTO etc.)
- **Typen für DB-Rows korrekt** – `pool.query<Task>(...)` überall

### API Response Format Konsistenz
**Bewertung: ✅ Gut**

Einheitliches Format:
```json
{ "success": true, "data": {...} }
{ "success": false, "error": "..." }
{ "success": false, "errors": [...] }  // Validierungsfehler
```

Pagination bei Appointments vorhanden:
```json
{ "success": true, "data": [...], "pagination": { "total": 42, "limit": 50, "offset": 0 } }
```

**Problem:** Pagination nur bei Appointments. Projects und Tasks geben alles ohne Pagination zurück. Bei 100+ Tasks pro Projekt wird das zum Problem.

### Auth Security
**Bewertung: ⚠️ Funktional aber lückenhaft**

**Positiv:**
- bcryptjs mit Salt-Rounds 10 ✅
- JWT mit konfigurierbarem Expiry ✅
- Email-Verification mit gehashten Tokens (SHA-256) ✅
- Password-Reset mit Expiry ✅
- Verification-Token wird gehashed in der DB gespeichert ✅

**Kritisch:**
- 🔴 **JWT Secret Fallback:** `const JWT_SECRET = process.env.JWT_SECRET || 'dev-insecure-secret';` – Wenn ENV nicht gesetzt, ist JEDER Token vorhersagbar
- 🔴 **Kein Rate Limiting** auf Login/Register/Password-Reset Endpoints
- 🔴 **Logout ist ein No-Op:** Token bleibt bis Expiry gültig. Kein Blacklisting.
- 🟡 **x-user-id Header Fallback:** `roleMiddleware.ts` akzeptiert sowohl Bearer Token ALS AUCH `x-user-id` Header. Das bedeutet: Wenn jemand die User-ID kennt, kann er ohne Passwort agieren. Legacy-Code der entfernt werden muss.
- 🟡 **Kein Password-Complexity-Check** beyond min 8 Zeichen
- 🟡 **Bcrypt Salt Rounds 10** – Akzeptabel aber nicht optimal (12+ empfohlen für 2025)

### Input Validation Vollständigkeit
**Bewertung: ✅ Gut**

express-validator wird konsistent eingesetzt:
- Appointments: title (required, max 255), description (max 5000), startTime/endTime (ISO 8601, endTime > startTime), timezone
- Tasks: title, status (enum), schedulingMode (enum), durationMinutes (int > 0), dates (ISO 8601), resourceId (UUID)
- Auth: email (isEmail), password (min 8), name (max 255)
- Resources: name, resourceType (enum), booleans

**Lücke:** `req.params.id` wird nie auf UUID-Format validiert (ausser in roleMiddleware für userId). Ein `GET /tasks/not-a-uuid` könnte unerwartete DB-Fehler werfen.

### Test Coverage
**Bewertung: 🔴 0%**

- Kein Test-Framework installiert (kein jest, mocha, vitest)
- Keine `*.test.ts`, `*.spec.ts` Dateien
- Zwei manuelle Test-Scripts (`test_auth_wave1.js`, `test_ai_conflict.js`) – plain JS, nicht automatisiert
- **Kein CI/CD konfiguriert**

### Security Basics
**Bewertung: ⚠️ Teilweise**

| Feature | Status |
|---------|--------|
| Helmet | ✅ Aktiv |
| CORS | ✅ Konfigurierbar via ENV |
| Rate Limiting | 🔴 Fehlt komplett |
| CSRF | 🟡 N/A (API-only, kein Cookie-Auth) |
| Input Sanitization | ✅ Via express-validator `.trim()` |
| SQL Injection | ✅ Parameterisiert |
| XSS | ⚠️ Kein Output-Encoding (Frontend-Verantwortung) |

### Pagination
**Bewertung: ⚠️ Unvollständig**

- ✅ Appointments: `limit`, `offset`, `total` – korrekt implementiert
- 🔴 Projects: Kein Pagination – `listProjects()` liefert ALLE
- 🔴 Tasks: Kein Pagination – `listTasksByProject()` liefert ALLE
- 🔴 Resources: Kein Pagination
- 🔴 Activity: Kein Pagination – Könnte bei aktiven Projekten hunderte Einträge haben

---

## Teil 2: Frontend Code-Review

### Komponenten-Struktur
**Bewertung: ⚠️ Mischqualität**

**Gut strukturiert (wiederverwendbar):**
- `EmptyState` – Generisch, mit Icon, Title, Description, Action
- `ConfirmDialog` – Generisch mit destructive Option
- `Breadcrumbs` – Clean, wiederverwendbar
- `OverlapWarningDialog` – Spezifisch aber sauber
- `ProtectedRoute` – Sauberer Auth-Guard

**Problematisch:**
- `ProjectDetail.tsx` – **~650 Zeilen Monster-Komponente**. Enthält Task-Erstellung, Resource-Management, Activity-Log, Layout-Drag&Drop, Template-System. Sollte in 5-6 Sub-Komponenten aufgeteilt werden.
- `Projects.tsx` – **~900+ Zeilen**. Grid-View, Calendar-View, Gantt-View, Holiday-Management, Project-Creation Dialog, Drag-Shifting. Mindestens 4 Komponenten.
- `CalendarView.tsx` – **~700+ Zeilen**. Calendar, Reverse Planning Dialog, Overlap Dialog, Task Overlay. Mindestens 3 Komponenten.
- `TaskDetail.tsx` – **~500+ Zeilen**. Dependencies, Work Slots, Reminders, Shift Schedule, Resource Assignment. Mindestens 3 Komponenten.

### State Management
**Bewertung: ✅ Angemessen für Projektgrösse**

- `AuthContext` ist sauber implementiert mit localStorage-Persistenz
- Custom Hooks (`useTimezone`, `useThemePreference`, `useLayoutPreference`) verwenden `useSyncExternalStore` korrekt
- Kein globaler State-Store nötig bei aktueller Komplexität
- **Problem:** Viel lokaler State in Pages (ProjectDetail hat ~25 `useState` Calls). Bei wachsender Komplexität wird das unmanageable.

### API Error Handling + Loading States
**Bewertung: ✅ Gut**

- Loading States: `CircularProgress` überall vorhanden, Skeleton-Loading bei Listen
- Error States: `Alert`-Komponenten mit error Messages
- Axios Error Handling konsistent:
```typescript
if (axios.isAxiosError(err)) {
  const message = typeof data?.error === 'string' ? data.error : data?.error?.message;
  setError(message || 'Failed to ...');
}
```
- **Gut:** 401-Response entfernt automatisch den Token (api.ts Interceptor)

### Form Validierung client-seitig
**Bewertung: ⚠️ Inkonsistent**

- `AppointmentForm`: react-hook-form mit Controller-Pattern ✅ Sauber
- `Auth.tsx`: Manuelle Validierung (if-Statements) ⚠️ Funktional aber nicht elegant
- `ProjectDetail` (Task-Creation): Minimale Validierung (nur title.trim()) 🔴
- Kein Debouncing bei Form-Inputs

### Mobile Responsiveness
**Bewertung: ✅ Gut**

- MUI's `useMediaQuery` + responsive `sx` Props überall
- Hamburger-Menu auf Mobile via Drawer
- `flexDirection: { xs: 'column', sm: 'row' }` konsistent verwendet
- Container `maxWidth` konfigurierbar (standard/wide)
- **Problem:** Gantt-Chart und Timeline sind auf Mobile nur eingeschränkt brauchbar (horizontal scroll)

### TypeScript Qualität
**Bewertung: ✅ Gut**

- Typen in `types/index.ts` zentral definiert
- Service-Layer korrekt typisiert mit `ApiResponse<T>`
- Kein `any`-Missbrauch im Frontend
- **Kleine Lücke:** Einige Event-Handler nutzen `event.target.value` ohne expliziten Cast

### Empty States
**Bewertung: ✅ Vorhanden**

- Generische `EmptyState`-Komponente mit Icon, Text, Action Button
- Verwendet bei: Appointments, Projects, Tasks, Dependencies, Work Slots, Activity, Timeline
- **Positiv:** Empty States haben CTAs ("Create your first...") – gute UX

---

## Teil 3: UX/Usability

### Onboarding nach erstem Login
**Bewertung: 🔴 Nicht vorhanden**

Nach Registration/Login landet der User auf dem Dashboard (`Home.tsx`). Es gibt:
- ❌ Kein Welcome-Wizard
- ❌ Keine Tooltips/Guided Tour
- ❌ Kein "Create your first project" Prompt auf dem Dashboard (nur generische Stats und Quick Actions)
- ❌ Keine Beispieldaten

Das Dashboard zeigt "0 Today, 0 This Week, 0 Total" und "No upcoming appointments". **Frustrierendes Erstnutzer-Erlebnis.**

### Klick-Analyse für häufige Aktionen

| Aktion | Klicks | Bewertung |
|--------|--------|-----------|
| Neuen Termin erstellen | 2 (Quick Action → Form) | ✅ Gut |
| Neues Projekt erstellen | 2 (Projects → Dialog) | ✅ Gut |
| Task zu Projekt hinzufügen | 3 (Projects → Detail → Scroll zu Form) | ⚠️ OK |
| Work Slot zu Task | 4 (Projects → Detail → Task → Scroll zu Slots) | 🔴 Zu viel |
| Dependency hinzufügen | 4 (wie oben) | 🔴 Zu viel |
| Timeline ansehen | 3 (Projects → Detail → Timeline Button) | ✅ OK |
| Keyboard Shortcut "N" | 1 Tastendruck | ✅ Excellent |

### AI Conflict Resolution – User-Präsentation
**Bewertung: ⚠️ Funktional aber versteckt**

Die AI-Suggestions werden im Conflict-Response mitgeliefert (`aiSuggestions`, `conflictPattern`, `historicalContext`), aber **das Frontend zeigt sie NICHT an**. Der `OverlapWarningDialog` zeigt nur die Konflikte und bietet "Cancel" oder "Create Anyway".

```typescript
// appointmentController.ts sendet:
res.status(409).json({
  success: false,
  error: 'Scheduling conflict detected',
  conflicts: overlapResult.conflicts,
  aiSuggestions: aiSuggestions.suggestions,  // <-- Frontend ignoriert das!
  conflictPattern: aiSuggestions.conflictPattern,
  historicalContext: aiSuggestions.historicalContext,
});
```

Das **beste Feature des Backends wird im Frontend komplett ignoriert**.

### Navigation, Breadcrumbs, Shortcuts
**Bewertung: ✅ Gut**

- Breadcrumbs auf allen Detail-Seiten ✅
- Hauptnavigation: Home, Appointments, Projects, Settings ✅
- Keyboard Shortcuts: `N` (New Appointment), `Shift+?` (Help), `Escape` (Close) ✅
- Footer mit Links ✅
- **Fehlt:** Globale Suche, Breadcrumb-Trail für Tasks (zeigt nur "Projects → Task Title", nicht den Projektnamen dazwischen)

### Feedback-States Übersicht

| State | Implementiert? |
|-------|---------------|
| Loading (Spinner) | ✅ Ja, überall |
| Loading (Skeleton) | ✅ Ja, bei Listen |
| Success (Snackbar) | ✅ Bei Calendar-Drag, Settings |
| Error (Alert) | ✅ Ja, inline |
| Empty State | ✅ Ja, mit CTAs |
| Confirm Dialog | ✅ Für destructive Actions |
| Overlap Warning | ✅ Spezifischer Dialog |

---

## Teil 4: Datenbank-Schema

### Schema-Überblick

```
teams
  ├── id (UUID PK)
  ├── name
  └── created_at

users
  ├── id (UUID PK)
  ├── email (UNIQUE)
  ├── name
  ├── role (admin|single|team)
  ├── team_id → teams
  ├── timezone
  ├── password_hash
  ├── email_verified_at
  ├── email_verification_token
  ├── email_verification_expires_at
  ├── password_reset_token
  ├── password_reset_expires_at
  └── timestamps

appointments
  ├── id (UUID PK)
  ├── title, description
  ├── start_time, end_time (TIMESTAMPTZ)
  ├── timezone
  ├── user_id → users (CASCADE)
  ├── deleted_at (Soft Delete)
  └── timestamps
  └── CHECK (end_time > start_time)

projects
  ├── id (UUID PK)
  ├── name, description
  ├── owner_id → users (CASCADE)
  ├── include_weekends
  ├── workday_start, workday_end (TIME)
  ├── work_template
  └── timestamps

tasks
  ├── id (UUID PK)
  ├── project_id → projects (CASCADE)
  ├── owner_id → users (CASCADE)
  ├── title, description
  ├── status (planned|in_progress|blocked|done)
  ├── scheduling_mode (manual|auto)
  ├── duration_minutes
  ├── resource_label
  ├── resource_id → resources (SET NULL)
  ├── start_date, due_date (DATE)
  ├── reminder_enabled
  └── timestamps

task_dependencies
  ├── id (UUID PK)
  ├── task_id → tasks (CASCADE)
  ├── depends_on_task_id → tasks (CASCADE)
  ├── dependency_type (finish_start|start_start|finish_finish)
  ├── CHECK (task_id ≠ depends_on_task_id)
  └── UNIQUE (task_id, depends_on_task_id, dependency_type)

task_work_slots
  ├── id (UUID PK)
  ├── task_id → tasks (CASCADE)
  ├── start_time, end_time (TIMESTAMPTZ)
  ├── is_fixed, is_all_day
  ├── reminder_enabled
  └── CHECK (end_time > start_time)

resources
  ├── id (UUID PK)
  ├── owner_id → users (CASCADE)
  ├── name
  ├── resource_type (person|machine|vehicle)
  ├── description
  ├── is_active, availability_enabled
  └── timestamps

project_activity
  ├── id (UUID PK)
  ├── project_id → projects (CASCADE)
  ├── actor_user_id → users (SET NULL)
  ├── entity_type, action, summary
  ├── metadata (JSONB)
  └── created_at

migrations (System-Tabelle)
```

### Was FEHLT für ein Schreinerei-ERP

| Modul | Status | Wichtigkeit |
|-------|--------|-------------|
| **Kunden/Adressen** | 🔴 Fehlt komplett | Kritisch |
| **Angebote/Offerten** | 🔴 Fehlt komplett | Kritisch |
| **Material/Lager** | 🔴 Fehlt komplett | Kritisch |
| **Stücklisten (BOM)** | 🔴 Fehlt komplett | Wichtig |
| **Kalkulation** | 🔴 Fehlt komplett | Kritisch |
| **Rechnungen/Faktura** | 🔴 Fehlt komplett | Kritisch |
| **Zeiterfassung (detailliert)** | 🔴 Fehlt – nur Task-Duration vorhanden, keine SOLL/IST-Erfassung | Kritisch |
| **Maschinenbelegung** | 🟡 Rudimentär – Resources existieren aber ohne Kapazitätsplanung | Wichtig |
| **Dokumente/Pläne** | 🔴 Fehlt komplett – kein File Upload | Wichtig |
| **Lieferanten** | 🔴 Fehlt komplett | Wichtig |
| **MWST/Buchhaltung** | 🔴 Fehlt komplett | Kritisch für CH |
| **Einkauf/Bestellung** | 🔴 Fehlt komplett | Wichtig |
| **Auftragsstatus/Workflow** | 🟡 Tasks haben Status, aber kein Auftrags-Workflow | Wichtig |
| **Kontakthistorie** | 🔴 Fehlt | Nice-to-have |
| **Reporting/Dashboard** | 🟡 Nur Appointment-Stats auf Home | Wichtig |

---

## Teil 5: Feature Bewertung

| Feature | Sterne | Kommentar |
|---------|--------|-----------|
| **Terminverwaltung** | ⭐⭐⭐⭐ | CRUD, Overlap-Detection, Soft Delete, Timezone Support, Calendar/List Views, Drag-Reschedule |
| **Projektverwaltung** | ⭐⭐⭐ | CRUD, Work Templates, Activity History, Schedule Shift. Fehlt: Status, Deadline, Team-Zuordnung |
| **Task Management** | ⭐⭐⭐⭐ | Status-Flow, Dependencies (3 Typen!), Work Slots, Reminders, Resource Assignment, Blocked-Detection |
| **AI Conflict Resolution** | ⭐⭐ | Regelbasiert (5 Heuristiken), Backend solide, aber Frontend zeigt Suggestions NICHT an. Kein echtes ML. |
| **Auth System** | ⭐⭐⭐ | JWT, bcrypt, Email Verification, Password Reset. Aber: Kein Rate Limiting, Logout No-Op, x-user-id Fallback |
| **Ressourcen-Management** | ⭐⭐ | CRUD für person/machine/vehicle. Availability Flag existiert, wird aber nicht für Scheduling genutzt |
| **Kalender-Ansichten** | ⭐⭐⭐⭐ | Month/Week/Day, FullCalendar-Integration, Drag&Drop, Task-Overlay, Holiday Management, Year View |
| **Reverse Planning** | ⭐⭐⭐ | Rückwärtsplanung von Deadline, respektiert Arbeitszeiten/Wochenenden, Overlap-Vermeidung. Gutes Konzept. |

---

## Teil 6: Problem-Liste

### 🔴 Kritisch (Security, Data Loss)

1. **Kein Rate Limiting** – Login Brute-Force, Password Reset Flooding, API Abuse trivial möglich
2. **JWT Secret Fallback `'dev-insecure-secret'`** – Wenn ENV fehlt, kann jeder Tokens fälschen
3. **`x-user-id` Header Fallback** – Bypass der Auth. Jeder der eine User-UUID kennt, hat vollen Zugriff
4. **Logout invalidiert Token nicht** – Gestohlene Tokens bleiben bis Expiry (7 Tage!) gültig
5. **Keine Tests** – Jedes Deployment ist Russisches Roulette
6. **Projects werden hart gelöscht** (`DELETE FROM projects`) – Kein Soft Delete wie bei Appointments. Kein Undo.
7. **Tasks werden hart gelöscht** – Cascade Delete auf Dependencies und Work Slots ohne Warnung
8. **Kein HTTPS-Enforcement** – Tokens im Klartext über HTTP möglich

### 🟡 Wichtig (Bugs, schlechte UX)

9. **AI Suggestions werden im Frontend nicht angezeigt** – Bestes Backend-Feature wird ignoriert
10. **ProjectDetail.tsx ist 650+ Zeilen** – Unmaintainable, muss refactored werden
11. **Projects.tsx ist 900+ Zeilen** – Drei Views in einer Datei
12. **Keine Pagination bei Projects, Tasks, Resources, Activity** – Performance-Problem bei Wachstum
13. **Kein Onboarding** – Neue User sehen leeres Dashboard ohne Guidance
14. **`req.params.id` nicht als UUID validiert** – Kann zu unhandled DB-Errors führen
15. **Breadcrumb bei TaskDetail zeigt nicht den Projekt-Namen** – Navigation broken
16. **Appointment Timezone vs. Display Timezone** kann verwirrend sein – keine klare Erklärung für User
17. **Keine Undo-Funktion** bei Löschungen (ausser Project-Shift hat Undo-Snackbar)
18. **Auto-Scheduling Mode existiert im Schema, wird aber nirgends implementiert** – Toter Code
19. **Holiday-Management nur in localStorage** – Nicht server-persistent, nicht geteilt zwischen Devices

### 🟢 Nice-to-fix (Code Quality)

20. **`(req as any).userId`** im authController statt korrektem typing
21. **Unused import** in aiConflictService: `import { join } from 'path';` wird verwendet, aber `path` auch separat importiert im appointmentService
22. **`beads` Conflict Learning** schreibt auf Filesystem – Nicht skalierbar (sollte in DB)
23. **Kein ESLint in CI** – Config existiert aber wird nicht enforced
24. **CSS-Variablen (`--ip-surface-elevated`)** werden verwendet aber nicht definiert in Analyse-zugänglichem Code (vermutlich in index.css)
25. **`date-fns` wird in beiden Packages doppelt installiert** – Bundle-Optimierung möglich
26. **Migrations nicht transaktional** – Ein Fehler mitten in einer Migration kann partiellen State hinterlassen
27. **Appointments: Soft Delete, Tasks/Projects: Hard Delete** – Inkonsistente Strategie
28. **Resource Availability wird im Schema gespeichert aber nie bei Scheduling berücksichtigt**

---

## Teil 7: Markt-Kontext & Strategie

### Strategische Positionierung

Die Markt-Analyse bestätigt: **Die Lücke ist real.** Borm und Swiss-Holz dominieren den CH-Markt, sind aber:
- Teuer (Enterprise-Pricing, 200-500 CHF/User/Monat)
- Technisch veraltet (On-Premise, keine REST API, keine Cloud-native Architektur)
- Komplex (Schulung nötig, "fummelig")

IntelliPlan kann sich als **"Das Anti-Borm"** positionieren: Modern, einfach, API-first, Cloud-native.

### Build vs. Buy Empfehlung

| Modul | Empfehlung | Begründung |
|-------|-----------|------------|
| **Kalkulation** | 🏗️ Build | Kern-Differenzierung, branchenspezifisch |
| **Offerten/Angebote** | 🏗️ Build | Eng mit Kalkulation verknüpft |
| **Kunden/CRM** | 🏗️ Build (simpel) | Einfache Kontaktverwaltung reicht initial |
| **Rechnungen** | 🛒 Buy/Integrate | bexio, Abacus, oder QR-Rechnung Library |
| **Buchhaltung** | 🛒 Buy/Integrate | Niemals selbst bauen. bexio/Abacus-API |
| **Zeiterfassung** | 🏗️ Build | Direkt an Tasks/Projekte gekoppelt |
| **Material/Lager** | 🏗️ Build (simpel) | Einfache Bestandsführung |
| **BOM/Stücklisten** | 🏗️ Build | Kern-Feature für Schreinerei |
| **Dokumente** | 🛒 Buy | S3/MinIO + simple Upload-UI |
| **Email/Notifications** | ✅ Exists | Nodemailer vorhanden, ausbaufähig |
| **CAD-Integration** | ❌ Skip (Phase 3+) | Zu komplex, kein MVP-Feature |

### MVP-Definition: "Schreinerei-ERP Light"

**Phase 1: Fundament (Monate 1-3)**
1. ✅ Auth System (vorhanden, Security-Fixes nötig)
2. ✅ Terminverwaltung (vorhanden)
3. ✅ Projektverwaltung (vorhanden)
4. ✅ Task Management (vorhanden)
5. 🆕 **Kundenverwaltung** (Firma, Kontaktperson, Adresse, Telefon, Email)
6. 🆕 **Einfache Zeiterfassung** (SOLL/IST pro Task, Stundensatz)
7. 🔧 Security Fixes (Rate Limiting, JWT Secret, x-user-id entfernen)
8. 🔧 Tests (mindestens Services + kritische Flows)

**Phase 2: Kalkulation (Monate 3-5)**
9. 🆕 **Material-Stammdaten** (Artikel, Preise, Einheiten)
10. 🆕 **Einfache BOM** (Material + Arbeitszeit pro Projekt)
11. 🆕 **Kalkulation** (Materialkosten + Arbeit × Stundensatz + Marge)
12. 🆕 **Offerte/Angebot** (PDF-Export, basierend auf Kalkulation)

**Phase 3: Fakturierung (Monate 5-7)**
13. 🆕 **Rechnung aus Projekt** (QR-Rechnung CH, MWST)
14. 🆕 **Zahlungsstatus** (Offen, Bezahlt, Überfällig)
15. 🔗 **bexio Integration** (Optional, für Buchhaltung)

**Phase 4: Optimierung (Monate 7-9)**
16. 🆕 **Maschinenbelegungsplan** (Resource Scheduling)
17. 🔧 **AI Suggestions im Frontend** anzeigen
18. 🆕 **Reporting Dashboard** (Umsatz, Auslastung, Projektstatus)
19. 🆕 **Multi-User/Team** (Team-Zuordnung, Rollen)

### Tech-Entscheidung: Bleiben bei Node/React?

**Empfehlung: JA, bei Node/React bleiben.**

Begründung:
- **Stack ist modern und passend:** Express + React + PostgreSQL ist battle-tested für SaaS
- **Kein Performance-Problem absehbar:** Für 5-30 User pro Schreinerei reicht Node.js locker
- **Talent-Pool:** Node.js/React-Entwickler sind einfacher zu finden als Rust/Go/Elixir
- **Bestehender Code ist solide:** Die Architektur (Controller/Service/Model) ist sauber
- **Einzige Überlegung:** TypeORM oder Prisma statt Raw SQL für neue Module (Schema-Migrations, Type Safety)

**Optionale Verbesserungen:**
- Vite + React ist korrekt ✅
- MUI v7 als UI-Framework ✅
- PostgreSQL als DB ✅
- **Hinzufügen:** Prisma ORM (für neue Module), Redis (für Rate Limiting + Cache), Vitest (für Tests)

---

## Priorisierte Roadmap mit Aufwandsschätzung

| # | Aufgabe | Aufwand | Priorität | Begründung |
|---|---------|---------|-----------|------------|
| 1 | 🔴 Security Fixes (Rate Limiting, JWT Secret enforcement, x-user-id entfernen) | 2-3 Tage | SOFORT | Production-Blocker |
| 2 | 🔴 Test-Framework aufsetzen + kritische Service-Tests | 1 Woche | SOFORT | Ohne Tests kein sicheres Deployment |
| 3 | 🟡 AI Suggestions im Frontend anzeigen | 2-3 Tage | Hoch | Niedrig-hängend, grosser UX-Impact |
| 4 | 🟡 Pagination für alle Listen | 2-3 Tage | Hoch | Skalierbarkeit |
| 5 | 🆕 Kundenverwaltung (DB + API + UI) | 1-2 Wochen | Hoch | Basis für Offerten/Rechnungen |
| 6 | 🆕 Zeiterfassung (SOLL/IST pro Task) | 1-2 Wochen | Hoch | Kern-Feature für Schreinerei |
| 7 | 🟡 Onboarding Flow | 3-5 Tage | Mittel | Erste Eindrücke zählen |
| 8 | 🟡 Refactoring: ProjectDetail, Projects, CalendarView aufteilen | 1 Woche | Mittel | Maintainability |
| 9 | 🆕 Material-Stammdaten | 1-2 Wochen | Mittel | Basis für Kalkulation |
| 10 | 🆕 Einfache BOM | 1-2 Wochen | Mittel | Kern-Schreinerei-Feature |
| 11 | 🆕 Kalkulation | 2-3 Wochen | Mittel | USP vs. Borm |
| 12 | 🆕 Offerten (PDF-Export) | 1-2 Wochen | Mittel | Erster Umsatz-relevanter Flow |
| 13 | 🆕 QR-Rechnung CH | 2-3 Wochen | Mittel | CH-Compliance |
| 14 | 🆕 File Upload (Pläne, Dokumente) | 1 Woche | Niedrig | S3-basiert |
| 15 | 🆕 Resource Scheduling (Kapazität) | 2-3 Wochen | Niedrig | Availability-Flags schon vorhanden |
| 16 | 🆕 Reporting Dashboard | 2-3 Wochen | Niedrig | Erst mit Daten sinnvoll |
| 17 | 🔗 bexio Integration | 2-3 Wochen | Niedrig | Optional, für Buchhaltungs-Export |

**Geschätzter Gesamtaufwand bis MVP "Schreinerei-ERP Light":**
- Security + Tests + Quick Wins: **3-4 Wochen**
- Phase 1 (Kunden + Zeit): **3-4 Wochen**
- Phase 2 (Kalkulation + Offerten): **6-8 Wochen**
- Phase 3 (Rechnungen): **4-6 Wochen**
- **Total: ~4-6 Monate** mit einem Vollzeit-Entwickler, **6-9 Monate** realistisch mit Feedback-Loops und Korrekturen

---

*Diese Analyse basiert auf dem vollständigen Quellcode-Review aller 80+ Dateien im IntelliPlan Repository.*
