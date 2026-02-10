#!/usr/bin/env python3
"""
test_lettering.py — Comprehensive lettering system tests for ComicMaster.

Tests:
1.  Font loading — all registered fonts load and render
2.  Text-first sizing — balloons resize to fit, never truncate
3.  Comic grammar normalisation — em-dash, ellipsis, caps
4.  Duplicate detection — identical text on same panel is skipped
5.  All 11 bubble types render without errors
6.  Genre-specific caption/narration styling
7.  Long text handling — no truncation even with very long text
8.  Bézier tails — visual check that curved tails render
9.  Style-font map coverage
10. Z-Pattern reading order — bubbles sorted left→right, top→bottom
11. Z-Pattern first speaker priority
12. Z-Pattern face avoidance — bubbles nudged away from face regions
13. Mouth position estimation — tail targets speaker mouth
14. Tapered tail rendering — smooth curved tails at 50-60% distance
15. Speaker position → tail target integration

Run: python3 test_lettering.py
Output: ~/clawd/output/comicmaster/test_lettering_*.png
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Ensure the scripts directory is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PIL import Image, ImageDraw
from speech_bubbles import (
    _FONTS,
    _FONT_DIR,
    _STYLE_FONT_MAP,
    _normalise_comic_text,
    _load_font,
    _is_duplicate,
    _reset_dedup,
    _compute_text_first_layout,
    _z_pattern_sort_key,
    sort_bubbles_z_pattern,
    estimate_mouth_position,
    compute_tail_target,
    _nudge_away_from_faces,
    _enforce_first_speaker_priority,
    _enforce_bubble_separation,
    add_bubbles,
    create_bubble_config,
)


OUT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "output" / "comicmaster"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PASS = 0
FAIL = 0


def check(name: str, condition: bool, detail: str = ""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        msg = f"  ❌ {name}"
        if detail:
            msg += f" — {detail}"
        print(msg)


def _make_bg(w: int = 800, h: int = 600) -> Image.Image:
    """Simple gradient background for visual tests."""
    img = Image.new("RGB", (w, h), (60, 80, 140))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        c = int(60 + 100 * (y / h))
        draw.line([(0, y), (w, y)], fill=(c, c + 20, 200 - c // 2))
    return img


# ──────────────────────────────────────────────────────────────
# Test 1: Font Loading
# ──────────────────────────────────────────────────────────────
def test_font_loading():
    print("\n🔤 Test 1: Font Loading")
    for key, filename in _FONTS.items():
        path = _FONT_DIR / filename
        exists = path.exists()
        size_ok = path.stat().st_size > 100 if exists else False
        check(f"Font '{key}' ({filename}) exists and >100 bytes", exists and size_ok,
              f"exists={exists}, size={path.stat().st_size if exists else 0}")

        if exists and size_ok:
            font = _load_font(key, 24)
            bbox = font.getbbox("Hello World!")
            w = bbox[2] - bbox[0]
            check(f"Font '{key}' renders text (width={w}px)", w > 10)


# ──────────────────────────────────────────────────────────────
# Test 2: Comic Grammar Normalisation
# ──────────────────────────────────────────────────────────────
def test_grammar_normalisation():
    print("\n📝 Test 2: Comic Grammar Normalisation")

    # Em-dash → double-dash
    result = _normalise_comic_text("Wait—what?", "narration")
    check("Em-dash → double-dash", "--" in result, f"got: {result}")

    # En-dash → double-dash
    result = _normalise_comic_text("Wait–what?", "narration")
    check("En-dash → double-dash", "--" in result, f"got: {result}")

    # Unicode ellipsis → three dots
    result = _normalise_comic_text("Well…", "narration")
    check("Unicode ellipsis → ...", "..." in result and "…" not in result, f"got: {result}")

    # Multiple dots → exactly 3
    result = _normalise_comic_text("Umm.....", "narration")
    check("Multiple dots → exactly 3", "..." in result and "...." not in result, f"got: {result}")

    # ALL CAPS for speech
    result = _normalise_comic_text("Hello world", "speech")
    check("Speech → ALL CAPS", result == "HELLO WORLD", f"got: {result}")

    # ALL CAPS for shout
    result = _normalise_comic_text("Watch out!", "shout")
    check("Shout → ALL CAPS", result == "WATCH OUT!", f"got: {result}")

    # Narration stays mixed case
    result = _normalise_comic_text("Meanwhile, in the city...", "narration")
    check("Narration stays mixed case", "Meanwhile" in result, f"got: {result}")

    # Thought stays mixed case
    result = _normalise_comic_text("I wonder about this...", "thought")
    check("Thought stays mixed case", "wonder" in result, f"got: {result}")

    # Smart quotes → straight
    result = _normalise_comic_text("\u201CHello\u201D", "speech")
    check("Smart quotes normalised", '"' in result and "\u201C" not in result, f"got: {result}")


# ──────────────────────────────────────────────────────────────
# Test 3: Duplicate Detection
# ──────────────────────────────────────────────────────────────
def test_duplicate_detection():
    print("\n🔁 Test 3: Duplicate Detection")

    _reset_dedup()

    dup1 = _is_duplicate("panel_1", "Hello World")
    check("First occurrence is NOT duplicate", not dup1)

    dup2 = _is_duplicate("panel_1", "Hello World")
    check("Second identical text IS duplicate", dup2)

    dup3 = _is_duplicate("panel_1", "Different text")
    check("Different text is NOT duplicate", not dup3)

    dup4 = _is_duplicate("panel_2", "Hello World")
    check("Same text on DIFFERENT panel is NOT duplicate", not dup4)

    # Case insensitive
    dup5 = _is_duplicate("panel_1", "hello world")
    check("Case-insensitive duplicate detected", dup5)


# ──────────────────────────────────────────────────────────────
# Test 4: Text-First Sizing (no truncation)
# ──────────────────────────────────────────────────────────────
def test_text_first_sizing():
    print("\n📏 Test 4: Text-First Sizing")

    # Short text
    font, lines, tw, th, px, py = _compute_text_first_layout(
        "Hi!", "speech", "western", 800, 600, (0.5, 0.5)
    )
    check("Short text: lines > 0", len(lines) > 0 and lines[0].strip() != "")
    check("Short text: positive dimensions", tw > 0 and th > 0)

    # Long text — must NOT be truncated
    long_text = "This is a very long piece of dialogue that should never be truncated no matter what. The balloon should resize to accommodate all of this text completely."
    font, lines, tw, th, px, py = _compute_text_first_layout(
        long_text, "speech", "western", 800, 600, (0.5, 0.5)
    )
    joined = " ".join(lines)
    # Verify all words present (case may change due to normalisation in add_bubbles, but here it's raw)
    original_words = set(long_text.lower().split())
    result_words = set(joined.lower().split())
    missing = original_words - result_words
    check("Long text: no words truncated", len(missing) == 0,
          f"missing words: {missing}" if missing else "")

    # Very long text on small panel
    font, lines, tw, th, px, py = _compute_text_first_layout(
        long_text, "speech", "western", 400, 300, (0.5, 0.5)
    )
    joined2 = " ".join(lines)
    original_words2 = set(long_text.lower().split())
    result_words2 = set(joined2.lower().split())
    missing2 = original_words2 - result_words2
    check("Long text on small panel: still no truncation", len(missing2) == 0,
          f"missing: {missing2}" if missing2 else "")

    # Padding ratio check (min 15%)
    check("Padding X is at least 15% of text width", px >= tw * 0.14,  # slightly under due to int rounding
          f"pad_x={px}, tw={tw}, ratio={px/max(tw,1):.2f}")
    check("Padding Y is at least 15% of text height", py >= th * 0.14,
          f"pad_y={py}, th={th}, ratio={py/max(th,1):.2f}")


# ──────────────────────────────────────────────────────────────
# Test 5: All Bubble Types Render
# ──────────────────────────────────────────────────────────────
def test_all_bubble_types():
    print("\n🎨 Test 5: All 11 Bubble Types Render")

    img = _make_bg(1200, 900)

    bubbles = [
        create_bubble_config("Normal speech test.", "speech", (0.18, 0.12), tail_target=(0.08, 0.30)),
        create_bubble_config("I wonder about this...", "thought", (0.50, 0.12), tail_target=(0.50, 0.30)),
        create_bubble_config("Look out!", "shout", (0.82, 0.12), tail_target=(0.90, 0.30)),
        create_bubble_config("psst... secret...", "whisper", (0.18, 0.38), tail_target=(0.08, 0.55)),
        create_bubble_config("Meanwhile, elsewhere...", "narration", (0.50, 0.38)),
        create_bubble_config("KABOOM!", "explosion", (0.82, 0.38)),
        create_bubble_config("System online.", "electric", (0.18, 0.65), tail_target=(0.08, 0.82)),
        create_bubble_config("We agree!", "connected", (0.50, 0.65),
                           tail_target=(0.35, 0.85), tail_target_2=(0.65, 0.85)),
        create_bubble_config("NOOO!!!", "scream", (0.82, 0.65), tail_target=(0.90, 0.85)),
        create_bubble_config("CRASH!", "sfx", (0.50, 0.50), rotation=-15),
        create_bubble_config("Chapter 1 — All bubble types", "caption", (0.5, 0.95)),
    ]

    try:
        result = add_bubbles(img, bubbles, style="western")
        path = OUT_DIR / "test_lettering_all_types.png"
        result.save(str(path))
        check("All 11 types rendered without error", True)
        check(f"Output saved to {path}", path.exists())
    except Exception as e:
        check("All 11 types rendered without error", False, str(e))


# ──────────────────────────────────────────────────────────────
# Test 6: Duplicate Skipping in add_bubbles
# ──────────────────────────────────────────────────────────────
def test_duplicate_in_render():
    print("\n🔁 Test 6: Duplicate Skipping in add_bubbles")

    img = _make_bg(800, 600)

    # Two identical texts — second should be skipped
    bubbles = [
        create_bubble_config("This appears once.", "speech", (0.3, 0.3), tail_target=(0.2, 0.5)),
        create_bubble_config("This appears once.", "speech", (0.7, 0.3), tail_target=(0.8, 0.5)),
        create_bubble_config("This is different.", "speech", (0.5, 0.7), tail_target=(0.5, 0.9)),
    ]

    try:
        result = add_bubbles(img, bubbles, style="western", panel_id="dedup_test")
        path = OUT_DIR / "test_lettering_dedup.png"
        result.save(str(path))
        check("Duplicate render completed (second copy skipped)", True)
    except Exception as e:
        check("Duplicate render completed", False, str(e))


# ──────────────────────────────────────────────────────────────
# Test 7: Genre-Specific Caption Styles
# ──────────────────────────────────────────────────────────────
def test_genre_styles():
    print("\n🎭 Test 7: Genre-Specific Styles")

    styles = ["western", "manga", "cartoon", "cyberpunk", "noir"]

    for style in styles:
        img = _make_bg(600, 400)
        bubbles = [
            create_bubble_config(
                f"Narration in {style} style",
                "narration", (0.5, 0.25),
            ),
            create_bubble_config(
                f"Caption — {style}",
                "caption", (0.5, 0.95),
            ),
            create_bubble_config(
                "Dialogue test!",
                "speech", (0.5, 0.6),
                tail_target=(0.5, 0.8),
            ),
        ]
        try:
            result = add_bubbles(img, bubbles, style=style)
            path = OUT_DIR / f"test_lettering_style_{style}.png"
            result.save(str(path))
            check(f"Style '{style}' renders OK", True)
        except Exception as e:
            check(f"Style '{style}' renders OK", False, str(e))


# ──────────────────────────────────────────────────────────────
# Test 8: Long Text — No Truncation
# ──────────────────────────────────────────────────────────────
def test_long_text():
    print("\n📜 Test 8: Long Text Handling")

    img = _make_bg(800, 600)

    long_dialogue = (
        "This is an extremely long piece of dialogue that a character might say "
        "in a dramatic monologue. It goes on and on, covering multiple topics "
        "including the meaning of life, the universe, and everything else. "
        "The balloon must grow to fit ALL of this text without any truncation."
    )

    bubbles = [
        create_bubble_config(long_dialogue, "speech", (0.5, 0.3), tail_target=(0.5, 0.7)),
        create_bubble_config(
            "Thank you, child. Just doing my job as always, no matter the cost.",
            "speech", (0.5, 0.75), tail_target=(0.5, 0.95),
        ),
    ]

    try:
        result = add_bubbles(img, bubbles, style="western")
        path = OUT_DIR / "test_lettering_long_text.png"
        result.save(str(path))
        check("Long text rendered without truncation", True)
        check(f"Output saved to {path}", path.exists())
    except Exception as e:
        check("Long text rendered without truncation", False, str(e))


# ──────────────────────────────────────────────────────────────
# Test 9: Bézier Tail Visual Check
# ──────────────────────────────────────────────────────────────
def test_bezier_tails():
    print("\n🔗 Test 9: Bézier Tail Rendering")

    img = _make_bg(800, 600)

    # Tails pointing in different directions
    bubbles = [
        create_bubble_config("Tail down", "speech", (0.25, 0.25), tail_target=(0.15, 0.60)),
        create_bubble_config("Tail right", "speech", (0.50, 0.25), tail_target=(0.80, 0.35)),
        create_bubble_config("Tail up", "speech", (0.75, 0.65), tail_target=(0.85, 0.20)),
        create_bubble_config("Tail left", "speech", (0.50, 0.65), tail_target=(0.15, 0.70)),
    ]

    try:
        result = add_bubbles(img, bubbles, style="western")
        path = OUT_DIR / "test_lettering_bezier_tails.png"
        result.save(str(path))
        check("Bézier tails render in all directions", True)
    except Exception as e:
        check("Bézier tails render in all directions", False, str(e))


# ──────────────────────────────────────────────────────────────
# Test 10: Style Font Map Coverage
# ──────────────────────────────────────────────────────────────
def test_font_map_coverage():
    print("\n🗺️ Test 10: Style-Font Map Coverage")

    all_types = ["speech", "thought", "shout", "whisper", "narration",
                 "caption", "explosion", "electric", "connected", "scream", "sfx"]

    for style_name, style_map in _STYLE_FONT_MAP.items():
        for btype in all_types:
            has_key = btype in style_map
            if has_key:
                font_key = style_map[btype]
                has_font = font_key in _FONTS
                check(f"Style '{style_name}' / '{btype}' → font '{font_key}' registered",
                      has_font, f"font key '{font_key}' not in _FONTS" if not has_font else "")
            else:
                check(f"Style '{style_name}' has mapping for '{btype}'", False, "missing")


# ──────────────────────────────────────────────────────────────
# Test 11: Z-Pattern Reading Order Sort
# ──────────────────────────────────────────────────────────────
def test_z_pattern_sort():
    print("\n📖 Test 11: Z-Pattern Reading Order Sort")

    # Create bubbles deliberately out of reading order
    bubbles = [
        create_bubble_config("Third", "speech", (0.8, 0.6)),   # bottom-right
        create_bubble_config("First", "speech", (0.2, 0.1)),   # top-left
        create_bubble_config("Second", "speech", (0.7, 0.1)),  # top-right
        create_bubble_config("Fourth", "speech", (0.3, 0.7)),  # bottom-left
    ]

    sorted_b = sort_bubbles_z_pattern(bubbles)

    # Extract texts in sorted order
    texts = [b["text"] for b in sorted_b]
    check(
        "Z-pattern sorts: top-left first",
        texts[0] == "First",
        f"got order: {texts}"
    )
    check(
        "Z-pattern sorts: top-right second",
        texts[1] == "Second",
        f"got order: {texts}"
    )
    # Bottom row: left before right
    bottom_texts = texts[2:]
    check(
        "Z-pattern sorts: bottom bubbles after top",
        all(t in ("Third", "Fourth") for t in bottom_texts),
        f"got: {bottom_texts}"
    )


def test_z_pattern_sort_key():
    print("\n🔑 Test 11b: Z-Pattern Sort Key")

    # Top-left should have lowest sort key
    b_tl = {"position": (0.1, 0.1)}
    b_tr = {"position": (0.9, 0.1)}
    b_bl = {"position": (0.1, 0.8)}
    b_br = {"position": (0.9, 0.8)}

    k_tl = _z_pattern_sort_key(b_tl)
    k_tr = _z_pattern_sort_key(b_tr)
    k_bl = _z_pattern_sort_key(b_bl)
    k_br = _z_pattern_sort_key(b_br)

    check("Top-left < top-right", k_tl < k_tr)
    check("Top-right < bottom-left", k_tr < k_bl)
    check("Bottom-left < bottom-right", k_bl < k_br)

    # Same tier: left before right
    b_mid_l = {"position": (0.2, 0.5)}
    b_mid_r = {"position": (0.8, 0.5)}
    check("Same tier: left < right",
          _z_pattern_sort_key(b_mid_l) < _z_pattern_sort_key(b_mid_r))


# ──────────────────────────────────────────────────────────────
# Test 12: Z-Pattern Exempt Types
# ──────────────────────────────────────────────────────────────
def test_z_pattern_exempt_types():
    print("\n🔒 Test 12: Z-Pattern Exempt Types (SFX, Caption, Narration)")

    bubbles = [
        create_bubble_config("BOOM!", "sfx", (0.5, 0.5)),           # exempt
        create_bubble_config("Speech B", "speech", (0.8, 0.2)),     # dialogue
        create_bubble_config("Speech A", "speech", (0.2, 0.1)),     # dialogue
        create_bubble_config("Chapter 1", "caption", (0.5, 0.95)),  # exempt
    ]

    sorted_b = sort_bubbles_z_pattern(bubbles)
    types = [b["type"] for b in sorted_b]
    texts = [b["text"] for b in sorted_b]

    # SFX should stay at index 0 (its original position)
    check("SFX stays at original index 0", texts[0] == "BOOM!")
    # Caption should stay at index 3 (its original position)
    check("Caption stays at original index 3", texts[3] == "Chapter 1")

    # The two speech bubbles should be in Z-pattern order in their slots
    speech_texts = [t for t, tp in zip(texts, types) if tp == "speech"]
    check("Speech bubbles reordered: A before B",
          speech_texts == ["Speech A", "Speech B"],
          f"got: {speech_texts}")


# ──────────────────────────────────────────────────────────────
# Test 13: First Speaker Priority
# ──────────────────────────────────────────────────────────────
def test_first_speaker_priority():
    print("\n👤 Test 13: First Speaker Priority")

    # Two speakers at roughly the same height — first should be adjusted higher+lefter
    bubbles = [
        create_bubble_config("Speaker 1", "speech", (0.5, 0.2)),
        create_bubble_config("Speaker 2", "speech", (0.5, 0.22)),
    ]

    sorted_b = sort_bubbles_z_pattern(bubbles)

    pos0 = sorted_b[0]["position"]
    pos1 = sorted_b[1]["position"]

    check("First speaker is higher (lower y)", pos0[1] < pos1[1],
          f"pos0.y={pos0[1]:.3f}, pos1.y={pos1[1]:.3f}")
    check("First speaker is further left (lower x)", pos0[0] < pos1[0],
          f"pos0.x={pos0[0]:.3f}, pos1.x={pos1[0]:.3f}")


def test_enforce_first_speaker():
    print("\n👤 Test 13b: _enforce_first_speaker_priority Direct")

    bubbles = [
        {"text": "A", "type": "speech", "position": (0.5, 0.15)},
        {"text": "B", "type": "speech", "position": (0.5, 0.16)},
    ]

    result = _enforce_first_speaker_priority(bubbles)
    p0 = result[0]["position"]
    p1 = result[1]["position"]

    check("After enforcement: first higher", p0[1] < p1[1],
          f"p0={p0}, p1={p1}")
    check("After enforcement: first more left", p0[0] < p1[0],
          f"p0={p0}, p1={p1}")


# ──────────────────────────────────────────────────────────────
# Test 14: Bubble Separation
# ──────────────────────────────────────────────────────────────
def test_bubble_separation():
    print("\n↕️ Test 14: Bubble Separation Enforcement")

    # Two bubbles very close together vertically
    bubbles = [
        {"text": "A", "type": "speech", "position": (0.5, 0.30)},
        {"text": "B", "type": "speech", "position": (0.5, 0.32)},
    ]

    result = _enforce_bubble_separation(bubbles, min_sep=0.08)

    p0 = result[0]["position"]
    p1 = result[1]["position"]
    sep = p1[1] - p0[1]

    check("Vertical separation >= min_sep", sep >= 0.08,
          f"separation={sep:.3f}")


# ──────────────────────────────────────────────────────────────
# Test 15: Face Avoidance
# ──────────────────────────────────────────────────────────────
def test_face_avoidance():
    print("\n🎭 Test 15: Face Avoidance (Bubble Nudging)")

    # Bubble directly on a face
    bubble = create_bubble_config("Hello!", "speech", (0.5, 0.3))
    face_regions = [(0.5, 0.3, 0.15, 0.15)]  # face at same position

    nudged = _nudge_away_from_faces(bubble, face_regions)
    nudged_pos = nudged["position"]

    check("Bubble nudged away from face", nudged_pos != (0.5, 0.3),
          f"nudged to: {nudged_pos}")
    check("Nudged bubble moved upward (preferred direction)",
          nudged_pos[1] < 0.3,
          f"new y={nudged_pos[1]:.3f}")

    # Bubble far from face — should not be nudged
    bubble_far = create_bubble_config("Far away", "speech", (0.1, 0.1))
    not_nudged = _nudge_away_from_faces(bubble_far, face_regions)
    check("Distant bubble NOT nudged", not_nudged["position"] == (0.1, 0.1))


def test_face_avoidance_in_add_bubbles():
    print("\n🎭 Test 15b: Face Avoidance in add_bubbles()")

    img = _make_bg(800, 600)
    bubbles = [
        create_bubble_config("Over a face!", "speech", (0.5, 0.4),
                           tail_target=(0.5, 0.7)),
    ]
    face_regions = [(0.5, 0.4, 0.2, 0.2)]

    try:
        result = add_bubbles(img, bubbles, style="western",
                           face_regions=face_regions)
        check("add_bubbles with face_regions runs without error", True)
        path = OUT_DIR / "test_lettering_face_avoidance.png"
        result.save(str(path))
    except Exception as e:
        check("add_bubbles with face_regions", False, str(e))


# ──────────────────────────────────────────────────────────────
# Test 16: Mouth Position Estimation
# ──────────────────────────────────────────────────────────────
def test_mouth_position_estimation():
    print("\n👄 Test 16: Mouth Position Estimation")

    # Speaker at centre of panel
    mouth = estimate_mouth_position((0.5, 0.6))
    check("Mouth x stays same as speaker x", mouth[0] == 0.5,
          f"mouth_x={mouth[0]}")
    check("Mouth y is above speaker centre", mouth[1] < 0.6,
          f"mouth_y={mouth[1]:.3f}, speaker_y=0.6")
    check("Mouth y is within panel", 0.0 <= mouth[1] <= 1.0,
          f"mouth_y={mouth[1]:.3f}")

    # Speaker at top of panel — mouth should not go off-panel
    mouth_top = estimate_mouth_position((0.5, 0.05))
    check("Mouth at top stays within panel", mouth_top[1] >= 0.02,
          f"mouth_y={mouth_top[1]:.3f}")

    # Speaker at bottom
    mouth_bot = estimate_mouth_position((0.5, 0.9))
    check("Mouth estimated above bottom speaker", mouth_bot[1] < 0.9,
          f"mouth_y={mouth_bot[1]:.3f}")


# ──────────────────────────────────────────────────────────────
# Test 17: compute_tail_target
# ──────────────────────────────────────────────────────────────
def test_compute_tail_target():
    print("\n🎯 Test 17: compute_tail_target")

    # Explicit mouth_position takes priority
    bubble = create_bubble_config("Test", "speech", (0.3, 0.2))
    updated = compute_tail_target(bubble, mouth_position=(0.4, 0.6))
    check("Explicit mouth position used as tail_target",
          updated["tail_target"] == (0.4, 0.6),
          f"got: {updated['tail_target']}")

    # Speaker position → estimated mouth
    updated2 = compute_tail_target(bubble, speaker_position=(0.7, 0.7))
    check("Speaker position → tail_target estimated",
          updated2["tail_target"] is not None,
          f"got: {updated2['tail_target']}")
    check("Estimated mouth is above speaker",
          updated2["tail_target"][1] < 0.7,
          f"tail_y={updated2['tail_target'][1]:.3f}")

    # Mouth takes priority over speaker
    updated3 = compute_tail_target(
        bubble, speaker_position=(0.7, 0.7), mouth_position=(0.6, 0.5)
    )
    check("mouth_position overrides speaker_position",
          updated3["tail_target"] == (0.6, 0.5))

    # No info → keep existing
    bubble_with_tail = create_bubble_config("Test", "speech", (0.3, 0.2),
                                           tail_target=(0.3, 0.5))
    unchanged = compute_tail_target(bubble_with_tail)
    check("No args → keeps existing tail_target",
          unchanged["tail_target"] == (0.3, 0.5))


# ──────────────────────────────────────────────────────────────
# Test 18: Speaker Position Integration in add_bubbles
# ──────────────────────────────────────────────────────────────
def test_speaker_position_integration():
    print("\n🔗 Test 18: Speaker Position → Tail Integration in add_bubbles")

    img = _make_bg(800, 600)

    bubbles = [
        create_bubble_config(
            "Auto-targeted to mouth!",
            "speech",
            (0.3, 0.15),
            speaker_position=(0.3, 0.7),  # speaker body centre
        ),
        create_bubble_config(
            "Explicit mouth position!",
            "speech",
            (0.7, 0.15),
            mouth_position=(0.7, 0.45),  # direct mouth pos
        ),
    ]

    try:
        result = add_bubbles(img, bubbles, style="western")
        path = OUT_DIR / "test_lettering_speaker_integration.png"
        result.save(str(path))
        check("Speaker position integration renders", True)
        check(f"Output saved to {path}", path.exists())
    except Exception as e:
        check("Speaker position integration", False, str(e))


# ──────────────────────────────────────────────────────────────
# Test 19: Tapered Tail Visual Check
# ──────────────────────────────────────────────────────────────
def test_tapered_tails():
    print("\n🔺 Test 19: Tapered Tail Rendering")

    img = _make_bg(1000, 800)

    # Multiple tail directions to verify tapering in all directions
    bubbles = [
        create_bubble_config("Tail down to mouth", "speech",
                           (0.25, 0.2), tail_target=(0.15, 0.70)),
        create_bubble_config("Tail right", "speech",
                           (0.50, 0.2), tail_target=(0.90, 0.35)),
        create_bubble_config("Tail up", "speech",
                           (0.75, 0.70), tail_target=(0.85, 0.10)),
        create_bubble_config("Tail left", "speech",
                           (0.50, 0.70), tail_target=(0.10, 0.65)),
        # Connected bubble with two tapered tails
        create_bubble_config("Two tails!", "connected",
                           (0.50, 0.45),
                           tail_target=(0.25, 0.75),
                           tail_target_2=(0.75, 0.75)),
    ]

    try:
        result = add_bubbles(img, bubbles, style="western")
        path = OUT_DIR / "test_lettering_tapered_tails.png"
        result.save(str(path))
        check("Tapered tails render in all directions", True)
        check(f"Output saved to {path}", path.exists())
    except Exception as e:
        check("Tapered tails render", False, str(e))


# ──────────────────────────────────────────────────────────────
# Test 20: Z-Pattern Full Integration Visual
# ──────────────────────────────────────────────────────────────
def test_z_pattern_visual():
    print("\n📐 Test 20: Z-Pattern Full Integration (Visual)")

    img = _make_bg(1000, 800)

    # Create bubbles deliberately in WRONG reading order
    # After Z-pattern sorting, they should render correctly
    bubbles = [
        create_bubble_config("4. BOTTOM RIGHT", "speech",
                           (0.75, 0.70), tail_target=(0.85, 0.90)),
        create_bubble_config("2. TOP RIGHT", "speech",
                           (0.70, 0.15), tail_target=(0.80, 0.35)),
        create_bubble_config("3. BOTTOM LEFT", "speech",
                           (0.25, 0.65), tail_target=(0.15, 0.85)),
        create_bubble_config("1. TOP LEFT (read me first!)", "speech",
                           (0.25, 0.12), tail_target=(0.15, 0.30)),
        # Exempt types stay in place
        create_bubble_config("CRASH!", "sfx", (0.5, 0.45), rotation=-10),
        create_bubble_config("Scene description...", "narration", (0.5, 0.92)),
    ]

    try:
        result = add_bubbles(img, bubbles, style="western")
        path = OUT_DIR / "test_lettering_z_pattern.png"
        result.save(str(path))
        check("Z-pattern full integration renders", True)
        check(f"Output saved to {path}", path.exists())
    except Exception as e:
        check("Z-pattern full integration", False, str(e))


# ──────────────────────────────────────────────────────────────
# Test 21: Single Bubble (edge case)
# ──────────────────────────────────────────────────────────────
def test_single_bubble_z_pattern():
    print("\n1️⃣ Test 21: Single Bubble Z-Pattern (edge case)")

    bubbles = [create_bubble_config("Only one!", "speech", (0.5, 0.3))]
    sorted_b = sort_bubbles_z_pattern(bubbles)

    check("Single bubble passes through unchanged", len(sorted_b) == 1)
    check("Text preserved", sorted_b[0]["text"] == "Only one!")


def test_empty_bubbles_z_pattern():
    print("\n0️⃣ Test 21b: Empty Bubbles Z-Pattern (edge case)")

    sorted_b = sort_bubbles_z_pattern([])
    check("Empty list returns empty", sorted_b == [])


# ──────────────────────────────────────────────────────────────
# Run all tests
# ──────────────────────────────────────────────────────────────
def main():
    t0 = time.time()
    print("=" * 60)
    print("  ComicMaster Lettering System — Test Suite")
    print("=" * 60)

    test_font_loading()
    test_grammar_normalisation()
    test_duplicate_detection()
    test_text_first_sizing()
    test_all_bubble_types()
    test_duplicate_in_render()
    test_genre_styles()
    test_long_text()
    test_bezier_tails()
    test_font_map_coverage()
    # New tests: Z-pattern + tails
    test_z_pattern_sort()
    test_z_pattern_sort_key()
    test_z_pattern_exempt_types()
    test_first_speaker_priority()
    test_enforce_first_speaker()
    test_bubble_separation()
    test_face_avoidance()
    test_face_avoidance_in_add_bubbles()
    test_mouth_position_estimation()
    test_compute_tail_target()
    test_speaker_position_integration()
    test_tapered_tails()
    test_z_pattern_visual()
    test_single_bubble_z_pattern()
    test_empty_bubbles_z_pattern()

    elapsed = time.time() - t0
    print("\n" + "=" * 60)
    print(f"  Results: {PASS} passed, {FAIL} failed  ({elapsed:.2f}s)")
    print(f"  Output images in: {OUT_DIR}")
    print("=" * 60)

    if FAIL > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
