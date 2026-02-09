# Bug Report: Control UI freezes during message streaming

**Save this for later if the issue returns**

---

## Summary

The Control UI (webchat) freezes for 5-10 seconds during/after message streaming, especially with larger session histories. The freeze occurs at the **end** of streaming, not during.

## Environment

- **OpenClaw Version:** 2026.2.1 (also tested 2026.1.30 - same issue)
- **OS:** WSL2 Ubuntu on Windows 11
- **Browser:** Chrome (latest)
- **Hardware:** AMD Threadripper 32-Core, 128GB RAM

## Symptoms

1. **UI freezes for ~8 seconds** at the end of each message streaming
2. **"event gap detected"** errors appear (e.g., "expected seq 4, got 17")
3. **WebSocket disconnects** with code 1001 during freezes
4. Screen sometimes goes black momentarily
5. Browser shows "Page unresponsive" dialog

## Performance Profile Data

From Chrome DevTools Performance tab:
- `Run microtasks`: **8.68 seconds** duration
- **99% of time spent in "System"** (layout/reflow)
- Only 0.18ms in "self" time

## Root Cause Analysis

### 1. Markdown Re-Parsing on Every Token

During streaming, `toSanitizedMarkdownHtml()` is called on the **full text** for every delta token:

```
Delta 1: "Hello" → parse full text
Delta 2: "Hello world" → parse full text (cache miss - new string!)
Delta 3: "Hello world!" → parse full text (cache miss!)
...
Final: "very long text..." → FULL PARSE (most expensive!)
```

**Location:** `ui/src/ui/chat/grouped-render.ts` → `renderStreamingGroup()` → `renderGroupedMessage()` → `toSanitizedMarkdownHtml()`

The markdown cache uses the input string as key, but during streaming the string changes every token, so the cache is useless.

### 2. Session History Size Amplifies Problem

With many sessions (we had 17) and large chat history, the initial load and re-renders become expensive. Cleaning old sessions significantly improved performance.

### 3. Scroll + Layout Thrashing

The scroll handler reads `scrollHeight` which triggers layout reflow. Combined with Lit's `updateComplete.then()` microtask pattern, this creates a cascade of layout calculations.

**Location:** `ui/src/ui/app-scroll.ts` → `scheduleChatScroll()`

## Reproduction Steps

1. Use OpenClaw for several days (accumulate sessions and chat history)
2. Open Control UI in Chrome
3. Send a message that generates a long response
4. Observe UI freeze near the end of streaming
5. Check for "event gap detected" errors

## Attempted Fixes

| Fix | Result |
|-----|--------|
| Downgrade to 2026.1.30 | ❌ No improvement |
| Monkey-patch `scrollTo` with debouncing | ❌ No improvement |
| Monkey-patch `scrollHeight` with 50ms cache | ❌ No improvement |
| Block scroll-related `requestAnimationFrame` | ❌ No improvement |
| Disable audio transcription | ❌ No improvement |
| Disable memory search | ❌ No improvement |
| **Delete old sessions (17 → 1)** | ✅ **Significant improvement** |

## Suggested Fixes

### Option 1: Debounce Streaming Renders
Only re-render every 100-200ms during streaming instead of on every token.

### Option 2: Plaintext During Streaming
Use simple `<pre>` or escaped text during streaming, only apply full markdown parsing when streaming completes.

### Option 3: Incremental Markdown
Parse only the new portion of text, append to existing HTML.

### Option 4: Session Pruning
Add built-in session cleanup command: `openclaw sessions prune --older-than 7d`

## Workaround

Periodically clean old sessions:

```bash
# Keep only main session, archive others
cd ~/.openclaw/agents/main/sessions
cp sessions.json sessions.json.bak
node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('sessions.json', 'utf8'));
const main = { 'agent:main:main': data['agent:main:main'] };
fs.writeFileSync('sessions.json', JSON.stringify(main, null, 2));
"
```

## Logs

WebSocket disconnect pattern during freeze:
```
webchat disconnected code=1001 reason=n/a
webchat connected conn=...
```

Event gap errors:
```
event gap detected (expected seq 4, got 17); refresh recommended
event gap detected (expected seq 994, got 995); refresh recommended
```

---

**Reporter:** @mcmuff  
**Date:** 2026-02-03  
**Status:** Workaround found (session cleanup), root cause identified
