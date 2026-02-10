#!/usr/bin/env python3
"""Tests for costume locking feature.

Costume locking ensures that each character's outfit description is:
1. Defined ONCE (via explicit ``outfit`` field or auto-extracted from costume_details)
2. Injected into EVERY panel prompt where the character appears
"""

from __future__ import annotations

import os
import sys

import pytest

# Ensure the scripts directory is on the path
sys.path.insert(0, os.path.dirname(__file__))

from panel_generator import _build_costume_string, build_panel_prompt
from story_planner import (
    _build_outfit_from_costume_details,
    _extract_costume_from_description,
    enrich_story_plan,
)


# ── _build_outfit_from_costume_details ────────────────────────────────────

class TestBuildOutfitFromCostumeDetails:
    """Test the canonical outfit string builder."""

    def test_full_costume(self):
        costume = {
            "top": "grey hoodie",
            "bottom": "dark jeans",
            "shoes": "white sneakers",
            "accessories": ["silver watch", "red backpack"],
        }
        result = _build_outfit_from_costume_details(costume)
        assert "grey hoodie" in result
        assert "dark jeans" in result
        assert "white sneakers" in result
        assert "silver watch" in result
        assert "red backpack" in result

    def test_partial_costume(self):
        costume = {"top": "leather jacket", "bottom": "", "shoes": "boots"}
        result = _build_outfit_from_costume_details(costume)
        assert "leather jacket" in result
        assert "boots" in result
        assert result  # not empty

    def test_empty_costume(self):
        assert _build_outfit_from_costume_details({}) == ""
        assert _build_outfit_from_costume_details(None) == ""
        assert _build_outfit_from_costume_details({"top": "", "bottom": ""}) == ""

    def test_accessories_only(self):
        costume = {"top": "", "bottom": "", "shoes": "", "accessories": ["gold necklace"]}
        result = _build_outfit_from_costume_details(costume)
        assert "gold necklace" in result

    def test_invalid_types_handled(self):
        # Non-dict input
        assert _build_outfit_from_costume_details("not a dict") == ""
        # None accessories
        costume = {"top": "shirt", "accessories": None}
        result = _build_outfit_from_costume_details(costume)
        assert "shirt" in result


# ── _build_costume_string (panel_generator.py) ────────────────────────────

class TestBuildCostumeString:
    """Test costume string builder used in prompt injection."""

    def test_outfit_field_takes_priority(self):
        """When ``outfit`` is set, it should be used verbatim."""
        char = {
            "outfit": "blue denim jacket, white t-shirt, dark jeans",
            "costume_details": {
                "top": "something completely different",
                "bottom": "other pants",
            },
        }
        result = _build_costume_string(char)
        assert result == "wearing blue denim jacket, white t-shirt, dark jeans"

    def test_falls_back_to_costume_details(self):
        """When ``outfit`` is empty/missing, falls back to costume_details."""
        char = {
            "costume_details": {
                "top": "red shirt",
                "bottom": "black pants",
                "shoes": "brown boots",
                "accessories": ["leather belt"],
            },
        }
        result = _build_costume_string(char)
        assert "wearing" in result
        assert "red shirt" in result
        assert "black pants" in result
        assert "brown boots" in result
        assert "leather belt" in result

    def test_empty_outfit_falls_back(self):
        char = {
            "outfit": "",
            "costume_details": {"top": "jacket"},
        }
        result = _build_costume_string(char)
        assert "jacket" in result

    def test_no_costume_info(self):
        char = {"id": "hero", "name": "Hero"}
        result = _build_costume_string(char)
        assert result == ""

    def test_whitespace_outfit_ignored(self):
        char = {"outfit": "   ", "costume_details": {"top": "vest"}}
        result = _build_costume_string(char)
        assert "vest" in result


# ── Enrichment Integration ────────────────────────────────────────────────

class TestCostumeLockingEnrichment:
    """Test that enrichment correctly builds the ``outfit`` field."""

    def _make_plan(self, characters: list) -> dict:
        return {
            "title": "Test Comic",
            "style": "western",
            "characters": characters,
            "panels": [
                {
                    "id": "p1",
                    "sequence": 1,
                    "scene": "Street",
                    "action": "Walking",
                    "characters_present": [c["id"] for c in characters],
                },
            ],
            "pages": [],
        }

    def test_outfit_auto_generated_from_description(self):
        """Visual description with clothing → outfit field populated."""
        plan = self._make_plan([
            {
                "id": "hero",
                "name": "Hero",
                "visual_description": "tall man with brown hair, leather jacket, dark jeans, combat boots",
            },
        ])
        enriched = enrich_story_plan(plan)
        hero = enriched["characters"][0]
        assert "outfit" in hero
        assert hero["outfit"]  # not empty
        assert "leather jacket" in hero["outfit"]

    def test_explicit_outfit_preserved(self):
        """If user explicitly sets ``outfit``, it must not be overwritten."""
        plan = self._make_plan([
            {
                "id": "hero",
                "name": "Hero",
                "visual_description": "tall man, leather jacket",
                "outfit": "blue suit, red tie, black shoes",
            },
        ])
        enriched = enrich_story_plan(plan)
        hero = enriched["characters"][0]
        assert hero["outfit"] == "blue suit, red tie, black shoes"

    def test_outfit_empty_when_no_clothing_keywords(self):
        """Description without clothing → empty outfit (not an error)."""
        plan = self._make_plan([
            {
                "id": "abstract",
                "name": "Spirit",
                "visual_description": "glowing ethereal figure, translucent blue",
            },
        ])
        enriched = enrich_story_plan(plan)
        char = enriched["characters"][0]
        assert "outfit" in char
        # outfit may be empty since no clothing keywords detected


# ── Prompt Integration ────────────────────────────────────────────────────

class TestCostumeLockingInPrompt:
    """Test that costume/outfit is actually injected into panel prompts."""

    def test_outfit_appears_in_prompt(self):
        """The outfit string should appear in every panel prompt."""
        characters = [
            {
                "id": "hero",
                "name": "Hero",
                "visual_description": "tall muscular man with short black hair",
                "outfit": "blue denim jacket, white t-shirt, dark jeans",
            },
        ]
        panel = {
            "id": "p1",
            "sequence": 1,
            "scene": "City street at night",
            "action": "Walking down the street",
            "characters_present": ["hero"],
            "shot_type": "medium",
            "camera_angle": "eye_level",
            "mood": "neutral",
        }
        prompt = build_panel_prompt(panel, characters, "western")
        assert "blue denim jacket" in prompt
        assert "white t-shirt" in prompt
        assert "dark jeans" in prompt

    def test_costume_details_appears_in_prompt(self):
        """Fallback: costume_details dict also gets injected."""
        characters = [
            {
                "id": "hero",
                "name": "Hero",
                "visual_description": "young woman with red hair",
                "costume_details": {
                    "top": "green hoodie",
                    "bottom": "black leggings",
                    "shoes": "running shoes",
                    "accessories": [],
                },
            },
        ]
        panel = {
            "id": "p1",
            "sequence": 1,
            "scene": "Park",
            "action": "Jogging",
            "characters_present": ["hero"],
            "shot_type": "medium",
            "mood": "happy",
        }
        prompt = build_panel_prompt(panel, characters, "western")
        assert "green hoodie" in prompt

    def test_same_outfit_in_multiple_panels(self):
        """The SAME outfit appears in all panels — this is costume locking."""
        characters = [
            {
                "id": "hero",
                "name": "Hero",
                "visual_description": "man with glasses",
                "outfit": "grey trench coat, black turtleneck",
            },
        ]
        panels = [
            {
                "id": "p1", "sequence": 1, "scene": "Office",
                "action": "Typing", "characters_present": ["hero"],
                "shot_type": "medium", "mood": "neutral",
            },
            {
                "id": "p2", "sequence": 2, "scene": "Street",
                "action": "Running", "characters_present": ["hero"],
                "shot_type": "wide", "mood": "tense",
            },
            {
                "id": "p3", "sequence": 3, "scene": "Rooftop",
                "action": "Standing", "characters_present": ["hero"],
                "shot_type": "close_up", "mood": "dramatic",
            },
        ]
        for panel in panels:
            prompt = build_panel_prompt(panel, characters, "western", all_panels=panels)
            assert "grey trench coat" in prompt, (
                f"Costume not locked in panel {panel['id']}: {prompt}"
            )
            assert "black turtleneck" in prompt, (
                f"Costume not locked in panel {panel['id']}: {prompt}"
            )
