# Aktiver Sprint

**Sprint:** 4 (07.02 - 13.02.2026)
**Ziel:** RBAC Integration + Pendenzen-Frontend + DB-Hardening

---

## 🔴 Prio 1: IntelliPlan

### Backend
- [x] RBAC Backend implementiert (Permissions, Service, Middleware, Tests) ✅ 06.02
- [x] Pendenzen-Modul Backend ✅ 04.02
- [x] RBAC in alle Routes einbauen (requirePermission statt requireRole) ✅ 07.02
- [x] DB-Fixes: ON DELETE Constraints (reminders, working_time_templates) ✅ 07.02
- [x] DB-Fixes: Auth-Tokens hashen statt Klartext ✅ (war schon SHA-256)
- [x] DB-Fixes: Soft-Delete Pattern vereinheitlichen (deleted_at überall) ✅ 07.02
- [x] DB-Fixes: updated_at Trigger auf alle Tabellen ✅ 07.02

### Frontend
- [x] Pendenzen-Liste (Tabelle + Filter) ✅ 07.02
- [x] Pendenzen-Detail (Create/Edit Form) ✅ 07.02
- [x] Pendenzen-Status Workflow (offen → in_arbeit → erledigt → archiviert) ✅ 07.02
- [x] RBAC-aware UI (Buttons/Actions basierend auf User-Rolle ausblenden) ✅ 07.02
- [x] Frontend node_modules installieren + lauffähig machen ✅ 07.02

## 🟡 Prio 2: RhinoAssemblyOutliner

- [ ] Phase 1: Dual-Property Datenmodell (IsLightBulbOn + IsEffectivelyVisible)
- [ ] Phase 4: Debug-Logging aus TreeBuilder entfernen
- [ ] Phase 2: Conduit Channels erweitern (wenn Phase 1 stabil)

## 🟢 Prio 3: Maintenance

- [x] LocAI: Security Fix SEC-1 (Auth auf API Routes) ✅ 07.02
- [x] LocAI: Security Fix SEC-2 (Path Traversal) ✅ 07.02
- [x] LocAI: Security Fix SEC-3 (Command Injection) ✅ 07.02
- [ ] Dependency Updates (minor/patch) über alle Projekte

---

## 📊 Sprint Stats

| Metrik | Wert |
|--------|------|
| Tasks gesamt | 18 |
| Erledigt | 15 |
| In Progress | 0 |
| Fortschritt | 83% |

## 📝 Sprint Notes

- RBAC: Code-Agent hat DB-basierte Permissions implementiert, Research-Agent empfiehlt Hybrid (Code-Konstanten). Entscheidung: DB-Ansatz erstmal beibehalten, bei Performance-Problemen auf Hybrid wechseln.
- DB-Improvement-Plan liegt in `~/projects/intelliplan/docs/db-improvement-plan.md`
- Technische Doku in `~/projects/intelliplan/docs/technical-overview.md`
