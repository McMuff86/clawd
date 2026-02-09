# Lettering System Overhaul

**Datum:** 2026-02-09
**Agent:** night-agent-a-lettering
**Projekt:** ComicMaster
**Dauer:** 6m 11s

## Zusammenfassung
Komplette Überarbeitung des Lettering-Systems in `speech_bubbles.py`. Kaputte Fonts repariert, 6 neue Pro-Fonts hinzugefügt, Text-First Sizing implementiert (Text wird nie mehr abgeschnitten), Bézier-Kurven-Tails, Duplikat-Erkennung und Comic-Grammar-Rules.

## Fonts — Fixed & Added

**Critical Bug Fixed:** 3 Fonts waren 0 Bytes und wurden durch echte Downloads ersetzt:
- `ComicNeue-Regular.ttf` (53KB)
- `ComicNeue-Bold.ttf` (52KB)
- `PatrickHand-Regular.ttf` (150KB)

**6 neue professionelle Fonts** (alle OFL/Google Fonts):

| Font | Grösse | Rolle |
|------|--------|-------|
| Permanent Marker | 72KB | SFX / Impact Text |
| Luckiest Guy | 57KB | Shout / Explosion |
| Special Elite | 147KB | Caption / Narration (Typewriter) |
| Caveat Regular | 246KB | Thought / Inner Monologue (Handwriting) |
| Caveat Bold | 246KB | Thought Bold Variant |
| Architects Daughter | 29KB | Cartoon Dialogue Alternative |

## Code-Änderungen in speech_bubbles.py

### 1. Text-First Sizing
`_compute_text_first_layout()` misst den Text ZUERST, dann berechnet die Balloon-Grösse. Font schrumpft bis 60% der Originalgrösse bevor der Balloon wächst. **Text wird NIEMALS abgeschnitten.**

### 2. Duplikat-Erkennung
`_is_duplicate()` prüft case-insensitive ob identischer Text schon auf dem Panel ist. Duplikate werden übersprungen mit Log-Warnung.

### 3. Comic Lettering Grammar
`_normalise_comic_text()` erzwingt:
- ALL CAPS für dialogue/shout/scream/connected/explosion/electric
- Em-dash (—) → Double-Dash (--)
- Unicode Ellipsis → genau 3 Punkte (...)
- Smart Quotes → Straight Quotes

### 4. Bézier Curved Tails
`_draw_speech_tail()` komplett neugeschrieben mit quadratischen Bézier-Kurven. Tail hängt sich automatisch an die nächste Bubble-Kante (top/bottom/left/right) Richtung Target. Breite proportional zur Bubble-Grösse.

### 5. Genre-Specific Caption Styling
`_CAPTION_STYLES` Dict mit thematischen Narration/Caption-Boxen für:
- **Western:** Klassisch
- **Cyberpunk:** Dunkler Hintergrund, Cyan-Rand
- **Noir:** Dunkel, hoher Kontrast
- **Manga:** Clean, minimal
- **Cartoon:** Bunt, verspielt

### 6. Erweitertes `_STYLE_FONT_MAP`
5 Styles (western, manga, cartoon, cyberpunk, noir) × 11 Bubble-Typen = alle 55 Kombinationen auf optimale Fonts gemappt.

### 7. Renderer-Signaturen aktualisiert
Alle Renderer empfangen jetzt vorberechnete `tw, th, pad_x, pad_y` vom Text-First Layout — Balloon passt IMMER zum Text.

## Tests
- **106/106 Tests bestanden** in `test_lettering.py`
- 10 visuelle Test-Bilder generiert in `~/clawd/output/comicmaster/`

## Offene Punkte
- Crossbar "I" Rule nicht implementierbar mit Standard-Fonts (bräuchte spezielle Comic-Fonts mit alternierenden Glyphen)
- Live-Test mit echtem Comic-Panel steht noch aus
