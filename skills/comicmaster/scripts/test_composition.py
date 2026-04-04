#!/usr/bin/env python3
"""
Tests for Sequential Composition Rules in ComicMaster.

Tests story_planner enrichment (gaze_direction, subject_position, connects_to,
spatial_relation, focal_point) and panel_generator composition tag generation.
"""

import copy
import json
import sys
from pathlib import Path

# Add our own scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from story_planner import (
    validate_story_plan,
    enrich_story_plan,
    validate_shot_progression,
    _enrich_sequential_fields,
    _enrich_dialogue_positions,
    _enrich_180_degree_rule,
    _enrich_panel_importance,
    VALID_GAZE_DIRECTIONS,
    VALID_SUBJECT_POSITIONS,
    VALID_SPATIAL_RELATIONS,
    VALID_FOCAL_POINTS,
    VALID_PANEL_IMPORTANCE,
)
from panel_generator import (
    _get_sequential_composition_tags,
    _get_180_degree_rule_tags,
    _get_dynamic_camera_tags,
    build_panel_prompt,
    COMPOSITION_TEMPLATES,
    FOCAL_POINT_TAGS,
    SUBJECT_POSITION_TAGS,
    GAZE_DIRECTION_TAGS,
    CHARACTER_POSITION_TAGS,
    DYNAMIC_CAMERA_ANGLE_MAP,
)


# ── Test Fixtures ──────────────────────────────────────────────────────────

def make_base_plan():
    """Minimal valid story plan without sequential fields."""
    return {
        "title": "Test Comic",
        "style": "western",
        "characters": [
            {"id": "hero", "name": "Hero", "visual_description": "tall warrior with red cape"},
            {"id": "villain", "name": "Villain", "visual_description": "dark figure with glowing eyes"},
        ],
        "panels": [
            {
                "id": "p1", "sequence": 1,
                "scene": "Castle courtyard at dawn",
                "action": "Hero stands at the gate, looking outward",
                "characters_present": ["hero"],
                "shot_type": "long",
                "mood": "tense",
            },
            {
                "id": "p2", "sequence": 2,
                "scene": "Castle courtyard at dawn",
                "action": "Villain appears in the shadows",
                "characters_present": ["villain"],
                "shot_type": "medium",
                "mood": "menacing",
                "dialogue": [
                    {"character_id": "villain", "text": "You cannot escape."},
                ],
            },
            {
                "id": "p3", "sequence": 3,
                "scene": "Castle courtyard at dawn",
                "action": "Hero draws sword, determined expression",
                "characters_present": ["hero"],
                "shot_type": "medium_close_up",
                "mood": "determined",
                "dialogue": [
                    {"character_id": "hero", "text": "Watch me."},
                ],
            },
            {
                "id": "p4", "sequence": 4,
                "scene": "Castle courtyard at dawn",
                "action": "Clash of swords, sparks flying",
                "characters_present": ["hero", "villain"],
                "shot_type": "medium",
                "mood": "action",
            },
            {
                "id": "p5", "sequence": 5,
                "scene": "Forest path, later",
                "action": "Hero walking alone through misty forest",
                "characters_present": ["hero"],
                "shot_type": "wide",
                "mood": "reflective",
            },
            {
                "id": "p6", "sequence": 6,
                "scene": "Forest path, later",
                "action": "Hero reveals the stolen gem",
                "characters_present": ["hero"],
                "shot_type": "close_up",
                "mood": "mysterious",
                "narrative_weight": "high",
            },
        ],
        "pages": [
            {"page_number": 1, "layout": "page_2x3", "panel_ids": ["p1", "p2", "p3", "p4", "p5", "p6"]},
        ],
    }


def make_dialogue_plan():
    """Plan focused on dialogue exchange."""
    return {
        "title": "Dialogue Test",
        "style": "western",
        "characters": [
            {"id": "alice", "name": "Alice", "visual_description": "young woman with blue hair"},
            {"id": "bob", "name": "Bob", "visual_description": "tall man with glasses"},
        ],
        "panels": [
            {
                "id": "d1", "sequence": 1,
                "scene": "Coffee shop interior",
                "action": "Alice and Bob sitting across from each other",
                "characters_present": ["alice", "bob"],
                "shot_type": "medium",
                "mood": "neutral",
                "dialogue": [
                    {"character_id": "alice", "text": "Did you hear the news?"},
                ],
            },
            {
                "id": "d2", "sequence": 2,
                "scene": "Coffee shop interior",
                "action": "Bob reacts with surprise",
                "characters_present": ["bob"],
                "shot_type": "medium",
                "mood": "surprised",
                "dialogue": [
                    {"character_id": "bob", "text": "What news?"},
                ],
            },
            {
                "id": "d3", "sequence": 3,
                "scene": "Coffee shop interior",
                "action": "Alice leans in conspiratorially",
                "characters_present": ["alice"],
                "shot_type": "medium",
                "mood": "mysterious",
                "dialogue": [
                    {"character_id": "alice", "text": "The city is shutting down."},
                ],
            },
            {
                "id": "d4", "sequence": 4,
                "scene": "Coffee shop interior",
                "action": "Bob drops his cup in shock",
                "characters_present": ["bob"],
                "shot_type": "medium",
                "mood": "shocked",
                "dialogue": [
                    {"character_id": "bob", "text": "That's impossible!"},
                ],
            },
        ],
        "pages": [
            {"page_number": 1, "layout": "page_2x2", "panel_ids": ["d1", "d2", "d3", "d4"]},
        ],
    }


# ── Test Counter ───────────────────────────────────────────────────────────
_passed = 0
_failed = 0
_errors = []


def check(condition: bool, name: str, detail: str = ""):
    global _passed, _failed
    if condition:
        _passed += 1
        print(f"  ✅ {name}")
    else:
        _failed += 1
        msg = f"  ❌ {name}"
        if detail:
            msg += f": {detail}"
        print(msg)
        _errors.append(name)


# ── Tests: Validation ──────────────────────────────────────────────────────

def test_validate_new_fields_valid():
    """Valid values for new sequential fields pass validation."""
    print("\n── test_validate_new_fields_valid ──")
    plan = make_base_plan()
    plan["panels"][0]["gaze_direction"] = "left"
    plan["panels"][0]["subject_position"] = "right_third"
    plan["panels"][0]["connects_to"] = "p2"
    plan["panels"][0]["spatial_relation"] = "same_location"
    plan["panels"][0]["focal_point"] = "upper_left"

    is_valid, errors = validate_story_plan(plan)
    check(is_valid, "Plan with valid sequential fields passes", str(errors))


def test_validate_new_fields_invalid():
    """Invalid values for new sequential fields are caught."""
    print("\n── test_validate_new_fields_invalid ──")

    # Invalid gaze_direction
    plan = make_base_plan()
    plan["panels"][0]["gaze_direction"] = "diagonal"
    _, errors = validate_story_plan(plan)
    check(any("gaze_direction" in e for e in errors), "Invalid gaze_direction caught")

    # Invalid subject_position
    plan = make_base_plan()
    plan["panels"][0]["subject_position"] = "far_left"
    _, errors = validate_story_plan(plan)
    check(any("subject_position" in e for e in errors), "Invalid subject_position caught")

    # Invalid spatial_relation
    plan = make_base_plan()
    plan["panels"][0]["spatial_relation"] = "teleport"
    _, errors = validate_story_plan(plan)
    check(any("spatial_relation" in e for e in errors), "Invalid spatial_relation caught")

    # Invalid focal_point
    plan = make_base_plan()
    plan["panels"][0]["focal_point"] = "dead_center"
    _, errors = validate_story_plan(plan)
    check(any("focal_point" in e for e in errors), "Invalid focal_point caught")

    # Invalid connects_to (non-existent panel)
    plan = make_base_plan()
    plan["panels"][0]["connects_to"] = "nonexistent"
    _, errors = validate_story_plan(plan)
    check(any("connects_to" in e for e in errors), "Invalid connects_to caught")


def test_backward_compatibility():
    """Plans without new fields still validate and enrich correctly."""
    print("\n── test_backward_compatibility ──")
    plan = make_base_plan()
    is_valid, errors = validate_story_plan(plan)
    check(is_valid, "Base plan without new fields is still valid", str(errors))

    enriched = enrich_story_plan(plan)
    check("panels" in enriched, "Enrichment works without new fields present")
    for p in enriched["panels"]:
        check("gaze_direction" in p, f"Panel {p['id']} got gaze_direction auto-set")
        check("subject_position" in p, f"Panel {p['id']} got subject_position auto-set")


# ── Tests: Sequential Field Enrichment ─────────────────────────────────────

def test_enrich_gaze_direction():
    """Auto-enrichment sets gaze_direction based on dialogue/sequence."""
    print("\n── test_enrich_gaze_direction ──")
    plan = make_base_plan()
    enriched = enrich_story_plan(plan)

    for p in enriched["panels"]:
        gaze = p.get("gaze_direction")
        check(gaze in VALID_GAZE_DIRECTIONS,
              f"Panel {p['id']} gaze_direction='{gaze}' is valid")

    # Panels with pre-set gaze should NOT be overwritten
    plan2 = make_base_plan()
    plan2["panels"][0]["gaze_direction"] = "up"
    enriched2 = enrich_story_plan(plan2)
    check(enriched2["panels"][0]["gaze_direction"] == "up",
          "Pre-set gaze_direction='up' preserved")


def test_enrich_subject_position():
    """Auto-enrichment alternates subject_position by sequence."""
    print("\n── test_enrich_subject_position ──")
    plan = make_base_plan()
    enriched = enrich_story_plan(plan)

    for p in enriched["panels"]:
        subj = p.get("subject_position")
        check(subj in VALID_SUBJECT_POSITIONS,
              f"Panel {p['id']} subject_position='{subj}' is valid")

    # Odd sequence → right_third, even → left_third (for non-splash)
    p1 = next(p for p in enriched["panels"] if p["id"] == "p1")
    p2 = next(p for p in enriched["panels"] if p["id"] == "p2")
    check(p1["subject_position"] == "right_third",
          "Odd panel (p1) → right_third")
    check(p2["subject_position"] == "left_third",
          "Even panel (p2) → left_third")


def test_enrich_connects_to():
    """Auto-enrichment sets connects_to to next panel."""
    print("\n── test_enrich_connects_to ──")
    plan = make_base_plan()
    enriched = enrich_story_plan(plan)

    panels = sorted(enriched["panels"], key=lambda p: p["sequence"])
    for i, p in enumerate(panels[:-1]):
        check(p.get("connects_to") == panels[i + 1]["id"],
              f"Panel {p['id']} connects_to={p.get('connects_to')}")

    # Last panel should NOT have connects_to
    last = panels[-1]
    check("connects_to" not in last or last.get("connects_to") == "",
          f"Last panel {last['id']} has no connects_to")


def test_enrich_spatial_relation():
    """Auto-enrichment detects same_location vs cut_to."""
    print("\n── test_enrich_spatial_relation ──")
    plan = make_base_plan()
    enriched = enrich_story_plan(plan)

    panels = sorted(enriched["panels"], key=lambda p: p["sequence"])

    # p1-p4 are all "Castle courtyard at dawn" → same_location
    for p in panels[:3]:  # p1, p2, p3
        check(p.get("spatial_relation") == "same_location",
              f"Panel {p['id']} spatial_relation='same_location' (same scene)")

    # p4→p5 transitions to "Forest path" → cut_to
    p4 = next(p for p in panels if p["id"] == "p4")
    check(p4.get("spatial_relation") == "cut_to",
          f"Panel p4 spatial_relation='cut_to' (scene change)")


def test_enrich_focal_point():
    """Auto-enrichment derives focal_point from subject_position + gaze."""
    print("\n── test_enrich_focal_point ──")
    plan = make_base_plan()
    enriched = enrich_story_plan(plan)

    for p in enriched["panels"]:
        fp = p.get("focal_point")
        check(fp in VALID_FOCAL_POINTS,
              f"Panel {p['id']} focal_point='{fp}' is valid")


# ── Tests: Shot Progression Validator ──────────────────────────────────────

def test_shot_progression_repetition():
    """Warns on >3 consecutive identical shot types."""
    print("\n── test_shot_progression_repetition ──")
    panels = [
        {"id": f"r{i}", "sequence": i, "shot_type": "medium", "scene": "same"}
        for i in range(1, 6)
    ]
    warnings = validate_shot_progression(panels, auto_fix=False)
    check(any("repetition" in w.lower() or "consecutive" in w.lower() for w in warnings),
          "Detects >3 consecutive medium shots")


def test_shot_progression_autofix():
    """Auto-fix varies repeated shot types."""
    print("\n── test_shot_progression_autofix ──")
    panels = [
        {"id": f"r{i}", "sequence": i, "shot_type": "medium", "scene": "same"}
        for i in range(1, 6)
    ]
    warnings = validate_shot_progression(panels, auto_fix=True)
    # After auto-fix, the 4th or 5th panel should have been changed
    shot_types = [p["shot_type"] for p in panels]
    check(len(set(shot_types)) > 1,
          f"Auto-fix varied shot types: {shot_types}")


def test_shot_progression_scene_opening():
    """Warns when a new scene doesn't open with an establishing shot."""
    print("\n── test_shot_progression_scene_opening ──")
    panels = [
        {"id": "s1", "sequence": 1, "shot_type": "close_up", "scene": "kitchen"},
        {"id": "s2", "sequence": 2, "shot_type": "medium", "scene": "kitchen"},
    ]
    warnings = validate_shot_progression(panels, auto_fix=False)
    check(any("scene opening" in w.lower() or "establishing" in w.lower() for w in warnings),
          "Detects non-establishing shot at scene opening")


def test_shot_progression_dialogue_monotony():
    """Warns when dialogue speaker change doesn't vary shot type."""
    print("\n── test_shot_progression_dialogue_monotony ──")
    panels = [
        {
            "id": "dm1", "sequence": 1, "shot_type": "medium", "scene": "room",
            "dialogue": [{"character_id": "alice", "text": "Hello"}],
        },
        {
            "id": "dm2", "sequence": 2, "shot_type": "medium", "scene": "room",
            "dialogue": [{"character_id": "bob", "text": "Hi"}],
        },
    ]
    warnings = validate_shot_progression(panels, auto_fix=False)
    check(any("dialogue" in w.lower() or "monotony" in w.lower() for w in warnings),
          "Detects dialogue monotony with same shot type")


# ── Tests: Dialogue Reading Order ──────────────────────────────────────────

def test_dialogue_position_hints():
    """Multiple dialogue entries get ordered position hints."""
    print("\n── test_dialogue_position_hints ──")
    plan = make_base_plan()
    # Add a panel with multiple speakers
    plan["panels"].append({
        "id": "p7", "sequence": 7,
        "scene": "Forest path",
        "action": "Hero and Villain argue",
        "characters_present": ["hero", "villain"],
        "shot_type": "medium",
        "mood": "tense",
        "dialogue": [
            {"character_id": "hero", "text": "This ends now."},
            {"character_id": "villain", "text": "You wish."},
            {"character_id": "hero", "text": "I know."},
        ],
    })
    plan["pages"][0]["panel_ids"].append("p7")
    # Need a layout that fits 7 panels
    plan["pages"] = [
        {"page_number": 1, "layout": "page_2x3", "panel_ids": ["p1", "p2", "p3", "p4", "p5", "p6"]},
        {"page_number": 2, "layout": "page_splash", "panel_ids": ["p7"]},
    ]

    enriched = enrich_story_plan(plan)
    p7 = next(p for p in enriched["panels"] if p["id"] == "p7")
    dialogue = p7.get("dialogue", [])

    check(dialogue[0].get("position_hint") == "top_left",
          f"First speaker → top_left (got {dialogue[0].get('position_hint')})")
    check(dialogue[1].get("position_hint") == "top_right",
          f"Second speaker → top_right (got {dialogue[1].get('position_hint')})")
    check(dialogue[2].get("position_hint") == "bottom_left",
          f"Third speaker → bottom_left (got {dialogue[2].get('position_hint')})")


# ── Tests: Panel Generator Composition Tags ────────────────────────────────

def test_composition_templates_exist():
    """COMPOSITION_TEMPLATES has all expected keys."""
    print("\n── test_composition_templates_exist ──")
    expected_keys = [
        "dialogue_speaker_a", "dialogue_speaker_b", "establishing",
        "reaction", "action_peak", "transition", "reveal",
        "confrontation", "climax", "contemplation",
    ]
    for key in expected_keys:
        check(key in COMPOSITION_TEMPLATES,
              f"Template '{key}' exists")


def test_composition_tags_anti_centering():
    """Non-splash, non-establishing panels get off-center tags."""
    print("\n── test_composition_tags_anti_centering ──")
    panel = {
        "id": "t1", "sequence": 1, "shot_type": "medium",
        "mood": "neutral", "characters_present": ["hero"],
        "subject_position": "right_third",
    }
    tags = _get_sequential_composition_tags(panel)
    tag_str = " ".join(tags).lower()
    check("off-center" in tag_str or "rule of thirds" in tag_str,
          "Normal panel gets off-center composition")
    check("right third" in tag_str,
          "subject_position=right_third reflected in tags")


def test_composition_tags_splash_centered():
    """Splash panels are allowed centered/symmetric compositions."""
    print("\n── test_composition_tags_splash_centered ──")
    panel = {
        "id": "t2", "sequence": 5, "shot_type": "medium",
        "mood": "dramatic", "narrative_weight": "splash",
        "characters_present": ["hero"],
    }
    tags = _get_sequential_composition_tags(panel)
    tag_str = " ".join(tags).lower()
    check("splash" in tag_str or "climax" in tag_str or "impact" in tag_str,
          f"Splash panel gets splash/climax composition tags")


def test_composition_tags_eyeline_matching():
    """Eyeline matching: prev panel gaze_direction affects current panel."""
    print("\n── test_composition_tags_eyeline_matching ──")
    panels = [
        {"id": "e1", "sequence": 1, "shot_type": "medium", "mood": "neutral",
         "characters_present": ["hero"], "gaze_direction": "left",
         "scene": "room"},
        {"id": "e2", "sequence": 2, "shot_type": "medium", "mood": "neutral",
         "characters_present": ["villain"], "scene": "room"},
    ]
    tags = _get_sequential_composition_tags(panels[1], all_panels=panels)
    tag_str = " ".join(tags).lower()
    check("left" in tag_str and "eyeline" in tag_str,
          f"Panel after left-gazing panel gets left-side eyeline match")


def test_composition_tags_action_reaction():
    """After an action panel, the next panel gets reaction tags."""
    print("\n── test_composition_tags_action_reaction ──")
    panels = [
        {"id": "a1", "sequence": 1, "shot_type": "medium", "mood": "action",
         "characters_present": ["hero"], "scene": "arena"},
        {"id": "a2", "sequence": 2, "shot_type": "close_up", "mood": "sad",
         "characters_present": ["villain"], "scene": "arena"},
    ]
    tags = _get_sequential_composition_tags(panels[1], all_panels=panels)
    tag_str = " ".join(tags).lower()
    check("reaction" in tag_str or "close-up" in tag_str or "facial expression" in tag_str,
          f"Post-action panel gets reaction composition")


def test_composition_tags_spatial_continuity():
    """same_location spatial_relation adds continuity tags."""
    print("\n── test_composition_tags_spatial_continuity ──")
    panels = [
        {"id": "sc1", "sequence": 1, "shot_type": "wide", "mood": "neutral",
         "characters_present": ["hero"], "scene": "park",
         "spatial_relation": "same_location"},
        {"id": "sc2", "sequence": 2, "shot_type": "medium", "mood": "neutral",
         "characters_present": ["hero"], "scene": "park",
         "spatial_relation": "same_location"},
    ]
    tags = _get_sequential_composition_tags(panels[1], all_panels=panels)
    tag_str = " ".join(tags).lower()
    check("continuity" in tag_str or "same environment" in tag_str,
          "same_location adds spatial continuity tags")


def test_composition_tags_scene_opening():
    """First panel of a new scene gets establishing tags."""
    print("\n── test_composition_tags_scene_opening ──")
    panels = [
        {"id": "so1", "sequence": 1, "shot_type": "medium", "mood": "neutral",
         "characters_present": ["hero"], "scene": "office"},
        {"id": "so2", "sequence": 2, "shot_type": "wide", "mood": "neutral",
         "characters_present": ["hero"], "scene": "rooftop"},
    ]
    tags = _get_sequential_composition_tags(panels[1], all_panels=panels)
    tag_str = " ".join(tags).lower()
    check("establishing" in tag_str or "new scene" in tag_str,
          "New scene gets establishing composition")


def test_composition_tags_climax():
    """High narrative_weight panels get dramatic composition."""
    print("\n── test_composition_tags_climax ──")
    panel = {
        "id": "cl1", "sequence": 5, "shot_type": "low_angle",
        "mood": "dramatic", "narrative_weight": "high",
        "characters_present": ["hero"],
    }
    tags = _get_sequential_composition_tags(panel)
    tag_str = " ".join(tags).lower()
    check("dramatic" in tag_str or "impact" in tag_str or "powerful" in tag_str,
          "High narrative_weight gets dramatic composition")


def test_composition_tags_confrontation():
    """Confrontation mood gets centered symmetric composition."""
    print("\n── test_composition_tags_confrontation ──")
    panel = {
        "id": "cf1", "sequence": 3, "shot_type": "medium",
        "mood": "confrontation", "characters_present": ["hero", "villain"],
    }
    tags = _get_sequential_composition_tags(panel)
    tag_str = " ".join(tags).lower()
    check("symmetrical" in tag_str or "confrontation" in tag_str or "facing" in tag_str,
          "Confrontation gets centered/symmetric composition")


def test_composition_tags_gaze_from_plan():
    """gaze_direction from story plan is used instead of auto-alternation."""
    print("\n── test_composition_tags_gaze_from_plan ──")
    panel = {
        "id": "gp1", "sequence": 2, "shot_type": "medium",
        "mood": "neutral", "characters_present": ["hero"],
        "gaze_direction": "up",
        "dialogue": [{"character_id": "hero", "text": "Look!"}],
    }
    tags = _get_sequential_composition_tags(panel)
    tag_str = " ".join(tags).lower()
    check("upward" in tag_str,
          "gaze_direction='up' from plan reflected in tags")


def test_composition_tags_focal_point():
    """focal_point from story plan adds specific focal tags."""
    print("\n── test_composition_tags_focal_point ──")
    panel = {
        "id": "fp1", "sequence": 1, "shot_type": "medium",
        "mood": "neutral", "characters_present": ["hero"],
        "focal_point": "upper_left",
    }
    tags = _get_sequential_composition_tags(panel)
    tag_str = " ".join(tags).lower()
    check("upper left" in tag_str or "top-left" in tag_str,
          "focal_point='upper_left' reflected in tags")


def test_build_panel_prompt_includes_composition():
    """build_panel_prompt includes sequential composition tags."""
    print("\n── test_build_panel_prompt_includes_composition ──")
    characters = [
        {"id": "hero", "name": "Hero", "visual_description": "warrior with red cape"},
    ]
    panel = {
        "id": "bp1", "sequence": 1, "shot_type": "medium",
        "mood": "neutral", "characters_present": ["hero"],
        "action": "Hero stands ready",
        "scene": "battleground",
        "subject_position": "right_third",
        "gaze_direction": "left",
    }
    prompt = build_panel_prompt(panel, characters, "western")
    check("right third" in prompt.lower(),
          "Prompt includes subject position")
    check("looking" in prompt.lower() and "left" in prompt.lower(),
          "Prompt includes gaze direction")


def test_full_enrichment_pipeline():
    """Full pipeline: validate → enrich → generate tags for all panels."""
    print("\n── test_full_enrichment_pipeline ──")
    plan = make_base_plan()

    # Validate
    is_valid, errors = validate_story_plan(plan)
    check(is_valid, "Base plan validates", str(errors))

    # Enrich
    enriched = enrich_story_plan(plan)
    panels = sorted(enriched["panels"], key=lambda p: p["sequence"])

    # Check all panels have sequential fields
    for p in panels:
        check("gaze_direction" in p, f"Panel {p['id']} has gaze_direction")
        check("subject_position" in p, f"Panel {p['id']} has subject_position")
        check("focal_point" in p, f"Panel {p['id']} has focal_point")

    # Generate composition tags for each panel
    characters = enriched["characters"]
    for p in panels:
        tags = _get_sequential_composition_tags(p, all_panels=panels)
        check(len(tags) > 0,
              f"Panel {p['id']} gets {len(tags)} composition tags")

    # Validate enriched plan still validates
    is_valid2, errors2 = validate_story_plan(enriched)
    check(is_valid2, "Enriched plan still validates", str(errors2))


def test_dialogue_plan_enrichment():
    """Dialogue-heavy plan gets proper shot/gaze variation."""
    print("\n── test_dialogue_plan_enrichment ──")
    plan = make_dialogue_plan()
    enriched = enrich_story_plan(plan)
    panels = sorted(enriched["panels"], key=lambda p: p["sequence"])

    # Check that dialogue panels alternate gaze
    gazes = [p["gaze_direction"] for p in panels]
    check(len(set(gazes)) > 1,
          f"Dialogue panels have varied gaze directions: {gazes}")

    # Check warnings about dialogue monotony (all panels start as medium)
    warnings = enriched.get("_enrichment_warnings", [])
    check(len(warnings) > 0,
          f"Got {len(warnings)} enrichment warnings for monotonous dialogue plan")


# ── Tests: 180-Degree Rule ─────────────────────────────────────────────────

def test_180_degree_rule_basic():
    """180-degree rule assigns consistent character positions per scene."""
    print("\n── test_180_degree_rule_basic ──")
    plan = make_dialogue_plan()
    enriched = enrich_story_plan(plan)
    panels = sorted(enriched["panels"], key=lambda p: p["sequence"])

    # d1 has both alice and bob → should get character_positions
    d1 = next(p for p in panels if p["id"] == "d1")
    check("character_positions" in d1,
          "Dialogue panel with 2+ chars gets character_positions")

    positions = d1.get("character_positions", {})
    check("alice" in positions and "bob" in positions,
          f"Both characters have positions: {positions}")
    check(positions.get("alice") != positions.get("bob"),
          f"Characters on different sides: {positions}")


def test_180_degree_rule_consistency_across_scene():
    """Character positions remain consistent across all panels in the same scene."""
    print("\n── test_180_degree_rule_consistency_across_scene ──")
    plan = {
        "title": "180 Test",
        "style": "western",
        "characters": [
            {"id": "a", "name": "Alpha", "visual_description": "tall man"},
            {"id": "b", "name": "Beta", "visual_description": "short woman"},
        ],
        "panels": [
            {
                "id": "s1", "sequence": 1,
                "scene": "Office meeting room",
                "action": "Alpha and Beta discuss plans",
                "characters_present": ["a", "b"],
                "shot_type": "medium",
                "mood": "neutral",
                "dialogue": [{"character_id": "a", "text": "Let's begin."}],
            },
            {
                "id": "s2", "sequence": 2,
                "scene": "Office meeting room",
                "action": "Beta responds passionately",
                "characters_present": ["a", "b"],
                "shot_type": "medium_close_up",
                "mood": "determined",
                "dialogue": [{"character_id": "b", "text": "I agree!"}],
            },
            {
                "id": "s3", "sequence": 3,
                "scene": "Office meeting room",
                "action": "Both stand up",
                "characters_present": ["a", "b"],
                "shot_type": "medium",
                "mood": "happy",
            },
        ],
        "pages": [
            {"page_number": 1, "layout": "page_1x3", "panel_ids": ["s1", "s2", "s3"]},
        ],
    }
    enriched = enrich_story_plan(plan)
    panels = sorted(enriched["panels"], key=lambda p: p["sequence"])

    # All 3 panels should have the same positions for a and b
    positions_list = [p.get("character_positions", {}) for p in panels]
    for pos in positions_list:
        check(len(pos) >= 2, f"Panel has character_positions: {pos}")

    # Check consistency: same char → same side across all panels
    a_sides = [p.get("character_positions", {}).get("a") for p in panels]
    b_sides = [p.get("character_positions", {}).get("b") for p in panels]
    check(len(set(a_sides)) == 1,
          f"Alpha consistent across scene: {a_sides}")
    check(len(set(b_sides)) == 1,
          f"Beta consistent across scene: {b_sides}")


def test_180_degree_rule_different_scenes():
    """Different scenes can have different character positions."""
    print("\n── test_180_degree_rule_different_scenes ──")
    plan = {
        "title": "Multi Scene 180",
        "style": "western",
        "characters": [
            {"id": "a", "name": "Alpha", "visual_description": "tall man"},
            {"id": "b", "name": "Beta", "visual_description": "short woman"},
        ],
        "panels": [
            {
                "id": "sc1p1", "sequence": 1,
                "scene": "Office",
                "action": "Conversation",
                "characters_present": ["a", "b"],
                "shot_type": "medium",
                "mood": "neutral",
                "dialogue": [{"character_id": "a", "text": "Hi"}],
            },
            {
                "id": "sc2p1", "sequence": 2,
                "scene": "Park bench",
                "action": "Different conversation",
                "characters_present": ["a", "b"],
                "shot_type": "medium",
                "mood": "calm",
                "dialogue": [{"character_id": "b", "text": "Hello"}],
            },
        ],
        "pages": [
            {"page_number": 1, "layout": "page_2x1", "panel_ids": ["sc1p1", "sc2p1"]},
        ],
    }
    enriched = enrich_story_plan(plan)
    panels = sorted(enriched["panels"], key=lambda p: p["sequence"])

    # Both panels should have character_positions (different scenes)
    for p in panels:
        check("character_positions" in p,
              f"Panel {p['id']} has character_positions")


def test_180_degree_rule_single_char_skipped():
    """Panels with only 1 character don't get character_positions."""
    print("\n── test_180_degree_rule_single_char_skipped ──")
    plan = make_base_plan()
    enriched = enrich_story_plan(plan)

    # p1 has only "hero" → should NOT have character_positions
    p1 = next(p for p in enriched["panels"] if p["id"] == "p1")
    check("character_positions" not in p1 or len(p1.get("character_positions", {})) == 0,
          "Single-character panel has no character_positions")


def test_180_degree_rule_preserves_explicit():
    """Pre-set character_positions are not overwritten."""
    print("\n── test_180_degree_rule_preserves_explicit ──")
    plan = make_dialogue_plan()
    plan["panels"][0]["character_positions"] = {"alice": "right", "bob": "left"}
    enriched = enrich_story_plan(plan)
    d1 = next(p for p in enriched["panels"] if p["id"] == "d1")
    check(d1["character_positions"]["alice"] == "right",
          "Explicit position preserved: alice=right")
    check(d1["character_positions"]["bob"] == "left",
          "Explicit position preserved: bob=left")


def test_180_degree_rule_prompt_tags():
    """_get_180_degree_rule_tags generates position prompts."""
    print("\n── test_180_degree_rule_prompt_tags ──")
    characters = [
        {"id": "alice", "name": "Alice", "visual_description": "woman with blue hair"},
        {"id": "bob", "name": "Bob", "visual_description": "man with glasses"},
    ]
    panel = {
        "id": "tp1", "sequence": 1,
        "characters_present": ["alice", "bob"],
        "character_positions": {"alice": "left", "bob": "right"},
    }
    tags = _get_180_degree_rule_tags(panel, characters)
    tag_str = " ".join(tags).lower()
    check("alice" in tag_str and "left" in tag_str,
          f"Alice on left in tags: {tags}")
    check("bob" in tag_str and "right" in tag_str,
          f"Bob on right in tags: {tags}")


def test_180_degree_rule_no_tags_single_char():
    """No position tags for single-character panels."""
    print("\n── test_180_degree_rule_no_tags_single_char ──")
    characters = [
        {"id": "alice", "name": "Alice", "visual_description": "woman"},
    ]
    panel = {
        "id": "tp2", "sequence": 1,
        "characters_present": ["alice"],
    }
    tags = _get_180_degree_rule_tags(panel, characters)
    check(len(tags) == 0, "No position tags for single character")


def test_180_degree_rule_in_prompt():
    """build_panel_prompt includes 180-degree character positions."""
    print("\n── test_180_degree_rule_in_prompt ──")
    characters = [
        {"id": "alice", "name": "Alice", "visual_description": "woman with blue hair"},
        {"id": "bob", "name": "Bob", "visual_description": "man with glasses"},
    ]
    panel = {
        "id": "pp1", "sequence": 1,
        "shot_type": "medium", "mood": "neutral",
        "characters_present": ["alice", "bob"],
        "character_positions": {"alice": "left", "bob": "right"},
        "action": "Talking at table",
        "scene": "café",
    }
    prompt = build_panel_prompt(panel, characters, "western")
    prompt_lower = prompt.lower()
    check("alice" in prompt_lower and "left" in prompt_lower,
          "Prompt includes Alice on left")
    check("bob" in prompt_lower and "right" in prompt_lower,
          "Prompt includes Bob on right")


# ── Tests: Dynamic Camera Angles ──────────────────────────────────────────

def test_dynamic_camera_action_panel():
    """Action panels get dramatic low-angle camera hints."""
    print("\n── test_dynamic_camera_action_panel ──")
    panel = {
        "id": "ca1", "sequence": 1, "shot_type": "medium",
        "mood": "action", "action": "Hero punches villain",
        "characters_present": ["hero"],
    }
    tags = _get_dynamic_camera_tags(panel)
    tag_str = " ".join(tags).lower()
    check("low angle" in tag_str or "worm" in tag_str or "dynamic" in tag_str,
          f"Action panel gets dramatic angle: {tags}")


def test_dynamic_camera_dialogue_panel():
    """Dialogue panels get eye-level camera hints."""
    print("\n── test_dynamic_camera_dialogue_panel ──")
    panel = {
        "id": "ca2", "sequence": 2, "shot_type": "medium",
        "mood": "neutral", "action": "Talking calmly",
        "characters_present": ["hero"],
        "dialogue": [{"character_id": "hero", "text": "Hello"}],
    }
    tags = _get_dynamic_camera_tags(panel)
    tag_str = " ".join(tags).lower()
    check("eye-level" in tag_str or "natural" in tag_str or "conversational" in tag_str,
          f"Dialogue panel gets eye-level: {tags}")


def test_dynamic_camera_establishing_panel():
    """Establishing (wide) panels get elevated wide angle hints."""
    print("\n── test_dynamic_camera_establishing_panel ──")
    panel = {
        "id": "ca3", "sequence": 1, "shot_type": "wide",
        "mood": "neutral", "action": "View of the city",
        "characters_present": [],
    }
    tags = _get_dynamic_camera_tags(panel)
    tag_str = " ".join(tags).lower()
    check("elevated" in tag_str or "wide angle" in tag_str or "overview" in tag_str,
          f"Establishing panel gets elevated angle: {tags}")


def test_dynamic_camera_emotion_panel():
    """Emotional close-up panels get slight angle hints."""
    print("\n── test_dynamic_camera_emotion_panel ──")
    panel = {
        "id": "ca4", "sequence": 3, "shot_type": "close_up",
        "mood": "sad", "action": "Hero cries",
        "characters_present": ["hero"],
    }
    tags = _get_dynamic_camera_tags(panel)
    tag_str = " ".join(tags).lower()
    check("intimate" in tag_str or "slight" in tag_str or "close-up" in tag_str,
          f"Emotion panel gets intimate angle: {tags}")


def test_dynamic_camera_in_composition_tags():
    """Dynamic camera tags are included in sequential composition tags."""
    print("\n── test_dynamic_camera_in_composition_tags ──")
    panel = {
        "id": "ccomp1", "sequence": 1, "shot_type": "medium",
        "mood": "action", "action": "Hero fights",
        "characters_present": ["hero"],
    }
    tags = _get_sequential_composition_tags(panel)
    tag_str = " ".join(tags).lower()
    # Should contain some camera angle hint from dynamic angles
    check("angle" in tag_str or "perspective" in tag_str or "dynamic" in tag_str,
          f"Composition tags include dynamic camera hint")


# ── Tests: Panel Importance (Pacing) ──────────────────────────────────────

def test_panel_importance_splash_is_3():
    """Splash panels get panel_importance=3."""
    print("\n── test_panel_importance_splash_is_3 ──")
    panels = [
        {"id": "pi1", "sequence": 1, "narrative_weight": "splash",
         "mood": "dramatic", "action": "Epic reveal", "shot_type": "wide"},
    ]
    _enrich_panel_importance(panels)
    check(panels[0].get("panel_importance") == 3,
          f"Splash → importance 3 (got {panels[0].get('panel_importance')})")


def test_panel_importance_high_narrative():
    """High narrative weight + dramatic action → importance 3."""
    print("\n── test_panel_importance_high_narrative ──")
    panels = [
        {"id": "pi2", "sequence": 1, "narrative_weight": "high",
         "mood": "dramatic", "action": "Hero reveals the truth", "shot_type": "medium"},
    ]
    _enrich_panel_importance(panels)
    check(panels[0].get("panel_importance") == 3,
          f"High weight + reveal → importance 3 (got {panels[0].get('panel_importance')})")


def test_panel_importance_transition_is_1():
    """Calm transition panels with low weight → importance 1."""
    print("\n── test_panel_importance_transition_is_1 ──")
    panels = [
        {"id": "pi3", "sequence": 1, "narrative_weight": "low",
         "mood": "calm", "action": "Character walks through hallway", "shot_type": "wide"},
    ]
    _enrich_panel_importance(panels)
    check(panels[0].get("panel_importance") == 1,
          f"Low + calm walk → importance 1 (got {panels[0].get('panel_importance')})")


def test_panel_importance_default_is_2():
    """Standard panels get panel_importance=2 by default."""
    print("\n── test_panel_importance_default_is_2 ──")
    panels = [
        {"id": "pi4", "sequence": 1, "narrative_weight": "medium",
         "mood": "neutral", "action": "Character enters room", "shot_type": "medium"},
    ]
    _enrich_panel_importance(panels)
    check(panels[0].get("panel_importance") == 2,
          f"Medium/neutral → importance 2 (got {panels[0].get('panel_importance')})")


def test_panel_importance_preserves_explicit():
    """Explicit panel_importance is not overwritten."""
    print("\n── test_panel_importance_preserves_explicit ──")
    panels = [
        {"id": "pi5", "sequence": 1, "narrative_weight": "low",
         "mood": "calm", "action": "Walking", "shot_type": "wide",
         "panel_importance": 3},  # Explicit override
    ]
    _enrich_panel_importance(panels)
    check(panels[0].get("panel_importance") == 3,
          "Explicit panel_importance=3 preserved despite low weight")


def test_panel_importance_validation():
    """panel_importance validation catches invalid values."""
    print("\n── test_panel_importance_validation ──")
    plan = make_base_plan()

    # Valid value
    plan["panels"][0]["panel_importance"] = 2
    is_valid, errors = validate_story_plan(plan)
    check(is_valid, "panel_importance=2 is valid")

    # Invalid value
    plan2 = make_base_plan()
    plan2["panels"][0]["panel_importance"] = 5
    _, errors2 = validate_story_plan(plan2)
    check(any("panel_importance" in e for e in errors2),
          "panel_importance=5 is caught as invalid")

    # Invalid type
    plan3 = make_base_plan()
    plan3["panels"][0]["panel_importance"] = "high"
    _, errors3 = validate_story_plan(plan3)
    check(any("panel_importance" in e for e in errors3),
          "panel_importance='high' (string) is caught as invalid")


def test_panel_importance_in_enriched_plan():
    """Full enrichment sets panel_importance on all panels."""
    print("\n── test_panel_importance_in_enriched_plan ──")
    plan = make_base_plan()
    enriched = enrich_story_plan(plan)

    for p in enriched["panels"]:
        pi = p.get("panel_importance")
        check(pi in VALID_PANEL_IMPORTANCE,
              f"Panel {p['id']} has valid panel_importance={pi}")


def test_character_positions_validation():
    """character_positions validation catches invalid values."""
    print("\n── test_character_positions_validation ──")
    plan = make_base_plan()

    # Valid character_positions
    plan["panels"][3]["character_positions"] = {"hero": "left", "villain": "right"}
    is_valid, errors = validate_story_plan(plan)
    check(is_valid, "Valid character_positions passes")

    # Invalid side value
    plan2 = make_base_plan()
    plan2["panels"][3]["character_positions"] = {"hero": "top", "villain": "right"}
    _, errors2 = validate_story_plan(plan2)
    check(any("character_positions" in e for e in errors2),
          "Invalid side 'top' is caught")

    # Non-existent character
    plan3 = make_base_plan()
    plan3["panels"][3]["character_positions"] = {"ghost": "left"}
    _, errors3 = validate_story_plan(plan3)
    check(any("character_positions" in e for e in errors3),
          "Non-existent character in character_positions is caught")


# ── Run all tests ──────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("ComicMaster Sequential Composition Tests")
    print("=" * 60)

    # Validation tests
    test_validate_new_fields_valid()
    test_validate_new_fields_invalid()
    test_backward_compatibility()

    # Enrichment tests
    test_enrich_gaze_direction()
    test_enrich_subject_position()
    test_enrich_connects_to()
    test_enrich_spatial_relation()
    test_enrich_focal_point()

    # Shot progression tests
    test_shot_progression_repetition()
    test_shot_progression_autofix()
    test_shot_progression_scene_opening()
    test_shot_progression_dialogue_monotony()

    # Dialogue reading order
    test_dialogue_position_hints()

    # Panel generator composition tags
    test_composition_templates_exist()
    test_composition_tags_anti_centering()
    test_composition_tags_splash_centered()
    test_composition_tags_eyeline_matching()
    test_composition_tags_action_reaction()
    test_composition_tags_spatial_continuity()
    test_composition_tags_scene_opening()
    test_composition_tags_climax()
    test_composition_tags_confrontation()
    test_composition_tags_gaze_from_plan()
    test_composition_tags_focal_point()
    test_build_panel_prompt_includes_composition()
    test_full_enrichment_pipeline()
    test_dialogue_plan_enrichment()

    # 180-degree rule tests
    test_180_degree_rule_basic()
    test_180_degree_rule_consistency_across_scene()
    test_180_degree_rule_different_scenes()
    test_180_degree_rule_single_char_skipped()
    test_180_degree_rule_preserves_explicit()
    test_180_degree_rule_prompt_tags()
    test_180_degree_rule_no_tags_single_char()
    test_180_degree_rule_in_prompt()

    # Dynamic camera angle tests
    test_dynamic_camera_action_panel()
    test_dynamic_camera_dialogue_panel()
    test_dynamic_camera_establishing_panel()
    test_dynamic_camera_emotion_panel()
    test_dynamic_camera_in_composition_tags()

    # Panel importance (pacing) tests
    test_panel_importance_splash_is_3()
    test_panel_importance_high_narrative()
    test_panel_importance_transition_is_1()
    test_panel_importance_default_is_2()
    test_panel_importance_preserves_explicit()
    test_panel_importance_validation()
    test_panel_importance_in_enriched_plan()
    test_character_positions_validation()

    # Summary
    print("\n" + "=" * 60)
    total = _passed + _failed
    print(f"Results: {_passed}/{total} passed, {_failed} failed")
    if _errors:
        print(f"\nFailed tests:")
        for e in _errors:
            print(f"  ❌ {e}")
    print("=" * 60)

    return 0 if _failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
