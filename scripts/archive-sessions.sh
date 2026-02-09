#!/bin/bash
# Archive old OpenClaw sessions to keep the main file small
# Usage: ./archive-sessions.sh [days_old] (default: 3)

DAYS_OLD=${1:-3}
SESSIONS_FILE="$HOME/.openclaw/agents/main/sessions/sessions.json"
ARCHIVE_DIR="$HOME/clawd/archives/sessions"
TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)

mkdir -p "$ARCHIVE_DIR"

if [ ! -f "$SESSIONS_FILE" ]; then
    echo "Sessions file not found: $SESSIONS_FILE"
    exit 1
fi

echo "Archiving sessions older than $DAYS_OLD days..."

node -e "
const fs = require('fs');
const path = require('path');

const sessionsFile = '$SESSIONS_FILE';
const archiveDir = '$ARCHIVE_DIR';
const timestamp = '$TIMESTAMP';
const daysOld = $DAYS_OLD;
const cutoffMs = Date.now() - (daysOld * 24 * 60 * 60 * 1000);

const data = JSON.parse(fs.readFileSync(sessionsFile, 'utf8'));
const archived = {};
const kept = {};
let archivedCount = 0;
let keptCount = 0;

for (const [key, session] of Object.entries(data)) {
    const updatedAt = session.updatedAt || 0;
    
    // Always keep main session
    if (key === 'agent:main:main') {
        kept[key] = session;
        keptCount++;
        console.log('Keeping: agent:main:main (always kept)');
        continue;
    }
    
    if (updatedAt < cutoffMs) {
        archived[key] = session;
        archivedCount++;
    } else {
        kept[key] = session;
        keptCount++;
    }
}

if (archivedCount > 0) {
    const archiveFile = path.join(archiveDir, 'sessions-' + timestamp + '.json');
    fs.writeFileSync(archiveFile, JSON.stringify(archived, null, 2));
    console.log('Archived ' + archivedCount + ' sessions to: ' + archiveFile);
    
    fs.writeFileSync(sessionsFile, JSON.stringify(kept, null, 2));
    console.log('Kept ' + keptCount + ' sessions in main file');
    
    // Show archive size
    const stats = fs.statSync(archiveFile);
    console.log('Archive size: ' + (stats.size / 1024).toFixed(1) + ' KB');
} else {
    console.log('No sessions old enough to archive');
    console.log('Current sessions: ' + keptCount);
}
"

echo "Done!"
