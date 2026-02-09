#!/bin/bash
# OpenClaw Session Cleanup Script
# Archiviert alte und verwaiste Sessions um die Performance zu erhalten
#
# Usage: ./cleanup-sessions.sh [--dry-run]

set -e

DRY_RUN=false
if [ "$1" = "--dry-run" ]; then
    DRY_RUN=true
    echo "🔍 DRY RUN - keine Änderungen werden gemacht"
fi

SESSIONS_DIR="$HOME/.openclaw/agents/main/sessions"
SESSIONS_FILE="$SESSIONS_DIR/sessions.json"
ARCHIVE_BASE="$HOME/clawd/archives/sessions"
DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)

echo "═══════════════════════════════════════════"
echo "🧹 OpenClaw Session Cleanup"
echo "   $(date)"
echo "═══════════════════════════════════════════"
echo ""

# Prüfen ob Sessions-Verzeichnis existiert
if [ ! -d "$SESSIONS_DIR" ]; then
    echo "❌ Sessions-Verzeichnis nicht gefunden: $SESSIONS_DIR"
    exit 1
fi

# Aktuellen Stand anzeigen
echo "📊 Aktueller Stand:"
echo "   Pfad: $SESSIONS_DIR"
du -sh "$SESSIONS_DIR" | awk '{print "   Grösse: " $1}'
echo ""

# 1. Soft-deleted Dateien archivieren (.deleted.*)
DELETED_FILES=$(ls "$SESSIONS_DIR"/*.deleted.* 2>/dev/null || true)
DELETED_COUNT=$(echo "$DELETED_FILES" | grep -c . || echo 0)

if [ -n "$DELETED_FILES" ] && [ "$DELETED_COUNT" -gt 0 ]; then
    echo "📦 $DELETED_COUNT soft-deleted Dateien gefunden"
    DELETED_ARCHIVE="$ARCHIVE_BASE/deleted-$DATE"
    
    if [ "$DRY_RUN" = true ]; then
        echo "   → Würde verschieben nach: $DELETED_ARCHIVE"
    else
        mkdir -p "$DELETED_ARCHIVE"
        mv "$SESSIONS_DIR"/*.deleted.* "$DELETED_ARCHIVE/"
        echo "   ✓ Verschoben nach: $DELETED_ARCHIVE"
    fi
else
    echo "✓ Keine soft-deleted Dateien"
fi
echo ""

# 2. Aktive Session-IDs aus dem Index holen
echo "🔍 Prüfe verwaiste JSONL-Dateien..."
ACTIVE_IDS=$(cat "$SESSIONS_FILE" 2>/dev/null | grep -o '"sessionId": "[^"]*"' | cut -d'"' -f4 | sort -u || echo "")

ORPHANED_COUNT=0
ORPHANED_LIST=""

for f in "$SESSIONS_DIR"/*.jsonl; do
    [ -f "$f" ] || continue
    
    BASENAME=$(basename "$f" .jsonl)
    
    # Skip lock files
    case "$BASENAME" in
        *.lock) continue ;;
    esac
    
    # Prüfen ob diese ID im Index ist
    if ! echo "$ACTIVE_IDS" | grep -q "^$BASENAME$"; then
        ORPHANED_COUNT=$((ORPHANED_COUNT + 1))
        ORPHANED_LIST="$ORPHANED_LIST$f
"
        SIZE=$(du -h "$f" | cut -f1)
        echo "   Verwaist: $BASENAME ($SIZE)"
    fi
done

if [ "$ORPHANED_COUNT" -gt 0 ]; then
    ORPHANED_ARCHIVE="$ARCHIVE_BASE/orphaned-$DATE"
    
    if [ "$DRY_RUN" = true ]; then
        echo "   → Würde $ORPHANED_COUNT Dateien verschieben nach: $ORPHANED_ARCHIVE"
    else
        mkdir -p "$ORPHANED_ARCHIVE"
        echo "$ORPHANED_LIST" | while read f; do
            [ -n "$f" ] && mv "$f" "$ORPHANED_ARCHIVE/"
        done
        echo "   ✓ $ORPHANED_COUNT Dateien verschoben nach: $ORPHANED_ARCHIVE"
    fi
else
    echo "✓ Keine verwaisten JSONL-Dateien"
fi
echo ""

# 3. Alte Sessions aus dem Index entfernen (älter als 7 Tage, außer main)
echo "🔍 Prüfe alte Sessions im Index..."
DAYS_OLD=7

node -e "
const fs = require('fs');
const sessionsFile = process.argv[1];
const archiveBase = process.argv[2];
const timestamp = process.argv[3];
const dryRun = process.argv[4] === 'true';
const daysOld = 7;

const data = JSON.parse(fs.readFileSync(sessionsFile, 'utf8'));
const cutoffMs = Date.now() - (daysOld * 24 * 60 * 60 * 1000);

const archived = {};
const kept = {};
let oldCount = 0;

for (const [key, session] of Object.entries(data)) {
    if (key === 'agent:main:main') {
        kept[key] = session;
        continue;
    }
    
    const updatedAt = session.updatedAt || 0;
    if (updatedAt < cutoffMs) {
        archived[key] = session;
        oldCount++;
        console.log('   Alt: ' + key);
    } else {
        kept[key] = session;
    }
}

if (oldCount === 0) {
    console.log('✓ Keine alten Sessions im Index');
} else if (dryRun) {
    console.log('   → Würde ' + oldCount + ' Sessions aus Index entfernen');
} else {
    const archiveFile = archiveBase + '/index-' + timestamp + '.json';
    fs.mkdirSync(archiveBase, { recursive: true });
    fs.writeFileSync(archiveFile, JSON.stringify(archived, null, 2));
    fs.writeFileSync(sessionsFile, JSON.stringify(kept, null, 2));
    console.log('   ✓ ' + oldCount + ' Sessions archiviert nach: ' + archiveFile);
}
" "$SESSIONS_FILE" "$ARCHIVE_BASE" "$TIMESTAMP" "$DRY_RUN"

echo ""

# Finaler Stand
echo "═══════════════════════════════════════════"
echo "📊 Nach Cleanup:"
du -sh "$SESSIONS_DIR" | awk '{print "   Sessions: " $1}'
du -sh "$ARCHIVE_BASE" 2>/dev/null | awk '{print "   Archive:  " $1}' || echo "   Archive:  (leer)"
echo "═══════════════════════════════════════════"
echo "✅ Cleanup abgeschlossen!"
