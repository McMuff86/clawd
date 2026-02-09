
## Inline-Bilder in Web-UI Chat

**Erstellt:** 2026-02-03
**Priorität:** Nice-to-have
**Aufwand:** Medium (1-2h)

### Problem
Wenn Sentinel ein Bild mit dem `Read` Tool lädt oder mit ComfyUI generiert, wird es nicht inline im Webchat angezeigt - nur "Read image file [image/png]" erscheint.

### Lösung
Die UI hat schon `extractImages()` und `renderMessageImages()` - das Problem ist dass Tool-Ergebnisse mit Bildern nicht als Image-Blöcke formatiert werden.

**Optionen:**
1. **Backend-Fix:** Tool-Ergebnisse mit Bildern als `{type: "image", url: "..."}` Blöcke zurückgeben
2. **Local HTTP Endpoint:** Bilder aus dem Workspace über einen lokalen Endpoint serven (`/files/...`)
3. **Base64 Data-URLs:** Zu gross, würde Performance killen

### Relevante Dateien
- `ui/src/ui/chat/grouped-render.ts` - `extractImages()`, `renderMessageImages()`
- Backend: Tool-Result Formatting

### Workaround
Bilder via Telegram senden - dort werden sie inline angezeigt.
