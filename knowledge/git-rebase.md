# Git Rebase – Erklärt

## Was ist Rebase?

Rebase nimmt deine Commits von einem Branch, **pflückt sie ab**, und setzt sie **oben auf** einen anderen Stand (z.B. den aktuellen Remote-Branch).

## Typisches Szenario: Diverged Branches

Du und jemand anderes (oder ein Agent) habt ab dem gleichen Commit weitergearbeitet:

```
                 deine-1 → deine-2        (dein lokaler Branch)
                /
basis-commit ───
                \
                 remote-1 → remote-2      (auf GitHub)
```

Zwei parallele Linien – **diverged**. Push wird rejected.

### Rebase löst das auf

```bash
git fetch origin
git rebase origin/feature-branch
```

Ergebnis – deine Commits sitzen obendrauf:

```
basis-commit → remote-1 → remote-2 → deine-1' → deine-2'
```

Deine Commits bekommen **neue Hashes** (darum `'`), weil sich ihr Eltern-Commit geändert hat. Der Inhalt bleibt gleich.

## Rebase vs Merge

**Merge** erzeugt einen extra Merge-Commit:
```
basis → remote → remote ─────────┐
    \                              → Merge-Commit
     → deine → deine ────────────┘
```

**Rebase** ergibt eine saubere gerade Linie:
```
basis → remote → remote → deine → deine
```

→ Rebase = sauberere History, kein unnötiger Merge-Commit.

## Praxis-Workflow

### Standard: Aufholen auf Remote

```bash
git fetch origin
git rebase origin/branch-name
git push
```

### Mit uncommitted Changes

```bash
git stash                                    # Änderungen zur Seite legen
git rebase origin/branch-name                # Rebase ausführen
git stash pop                                # Änderungen zurückholen
git push
```

### Bei Konflikten während Rebase

```bash
# Git zeigt betroffene Files an
# → Konflikte manuell lösen
git add <file>
git rebase --continue

# Oder: Abbrechen und zurück zum Ausgangszustand
git rebase --abort
```

## Wann Rebase, wann Merge?

| Situation | Empfehlung |
|-----------|------------|
| Eigener Feature-Branch aufholen | **Rebase** |
| Feature-Branch → Main zusammenführen | **Merge** (oder Squash-Merge) |
| Shared Branch den andere auch nutzen | **Merge** (Rebase ändert Hashes = Chaos) |

## Goldene Regel

> **Nie einen Branch rebasen den andere Leute aktiv nutzen.** Rebase ändert Commit-Hashes – das bringt andere aus dem Tritt. Für eigene Feature-Branches: kein Problem.

## Feature-Branch zu Main machen

### Option A: Merge (Standard)
```bash
git checkout main
git merge feature-branch
git push origin main
```

### Option B: Hard Reset (Main komplett ersetzen)
```bash
git checkout main
git reset --hard feature-branch
git push --force origin main
```

→ Option B nur wenn Main keine eigenen Commits hat die du behalten willst.
