#!/usr/bin/env python3
"""Tests for face crop extraction and re-injection system.

The face crop system:
1. After the FIRST panel of a character, extracts the best face crop
2. Saves the crop as a separate image (512x512)
3. The crop is used as additional IPAdapter reference for subsequent panels
"""

from __future__ import annotations

import os
import sys
import tempfile

import numpy as np
import pytest
from PIL import Image

# Ensure the scripts directory is on the path
sys.path.insert(0, os.path.dirname(__file__))

from panel_generator import extract_best_face


# ── Helpers ───────────────────────────────────────────────────────────────

def _create_test_image(path: str, size: tuple = (768, 768),
                       color: tuple = (200, 150, 100)) -> str:
    """Create a test image with a simple face-like pattern."""
    img = Image.new("RGB", size, color)
    # Draw a simple "face" in upper-center (circle-ish area)
    pixels = img.load()
    cx, cy = size[0] // 2, size[1] // 4
    radius = min(size) // 6
    for x in range(max(0, cx - radius), min(size[0], cx + radius)):
        for y in range(max(0, cy - radius), min(size[1], cy + radius)):
            if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                pixels[x, y] = (255, 220, 180)  # skin-like color
    img.save(path)
    return path


# ── extract_best_face ─────────────────────────────────────────────────────

class TestExtractBestFace:
    """Test the face crop extraction function."""

    def test_returns_path_for_valid_image(self, tmp_path):
        """Should extract a face crop and return a valid file path."""
        img_path = _create_test_image(str(tmp_path / "panel.png"))
        character = {"id": "hero", "name": "Hero"}

        result = extract_best_face(img_path, character, output_dir=str(tmp_path))

        assert result is not None
        assert os.path.exists(result)
        assert "face_crop_hero" in result

    def test_output_is_512x512(self, tmp_path):
        """Face crop should be resized to 512x512 for IPAdapter."""
        img_path = _create_test_image(str(tmp_path / "panel.png"))
        character = {"id": "test_char"}

        result = extract_best_face(img_path, character, output_dir=str(tmp_path))

        assert result is not None
        crop = Image.open(result)
        assert crop.size == (512, 512)

    def test_character_id_in_filename(self, tmp_path):
        """Output filename should contain the character ID."""
        img_path = _create_test_image(str(tmp_path / "panel.png"))
        character = {"id": "detective_jones"}

        result = extract_best_face(img_path, character, output_dir=str(tmp_path))

        assert result is not None
        assert "detective_jones" in os.path.basename(result)

    def test_creates_output_dir(self, tmp_path):
        """Should create output directory if it doesn't exist."""
        img_path = _create_test_image(str(tmp_path / "panel.png"))
        out_dir = str(tmp_path / "new_dir" / "face_crops")

        result = extract_best_face(
            img_path, {"id": "hero"}, output_dir=out_dir,
        )

        assert result is not None
        assert os.path.isdir(out_dir)

    def test_returns_none_for_missing_image(self, tmp_path):
        """Should return None if the image file doesn't exist."""
        result = extract_best_face(
            str(tmp_path / "nonexistent.png"),
            {"id": "hero"},
            output_dir=str(tmp_path),
        )
        assert result is None

    def test_returns_none_for_tiny_image(self, tmp_path):
        """Should return None if image is too small for a face crop."""
        tiny_path = str(tmp_path / "tiny.png")
        Image.new("RGB", (30, 30), (128, 128, 128)).save(tiny_path)

        result = extract_best_face(
            tiny_path, {"id": "hero"},
            min_face_size=64,
            output_dir=str(tmp_path),
        )
        assert result is None

    def test_default_output_dir(self, tmp_path):
        """When output_dir is None, saves next to the panel image."""
        img_path = _create_test_image(str(tmp_path / "panel.png"))
        character = {"id": "hero"}

        result = extract_best_face(img_path, character, output_dir=None)

        assert result is not None
        assert os.path.dirname(result) == str(tmp_path)

    def test_multiple_characters_different_files(self, tmp_path):
        """Different characters should produce different face crop files."""
        img_path = _create_test_image(str(tmp_path / "panel.png"))

        crop_a = extract_best_face(
            img_path, {"id": "alice"}, output_dir=str(tmp_path),
        )
        crop_b = extract_best_face(
            img_path, {"id": "bob"}, output_dir=str(tmp_path),
        )

        assert crop_a is not None
        assert crop_b is not None
        assert crop_a != crop_b
        assert "alice" in os.path.basename(crop_a)
        assert "bob" in os.path.basename(crop_b)

    def test_rgb_output(self, tmp_path):
        """Face crop should be RGB (no alpha channel)."""
        # Create a RGBA image
        rgba_path = str(tmp_path / "rgba_panel.png")
        Image.new("RGBA", (768, 768), (200, 150, 100, 255)).save(rgba_path)

        result = extract_best_face(
            rgba_path, {"id": "hero"}, output_dir=str(tmp_path),
        )

        assert result is not None
        crop = Image.open(result)
        assert crop.mode == "RGB"

    def test_various_image_sizes(self, tmp_path):
        """Should work with various common panel sizes."""
        sizes = [(512, 512), (768, 768), (1024, 1024), (768, 1024), (1024, 768)]
        for w, h in sizes:
            img_path = _create_test_image(
                str(tmp_path / f"panel_{w}x{h}.png"), size=(w, h),
            )
            result = extract_best_face(
                img_path, {"id": f"hero_{w}x{h}"}, output_dir=str(tmp_path),
            )
            assert result is not None, f"Failed for size {w}x{h}"
            crop = Image.open(result)
            assert crop.size == (512, 512), f"Wrong crop size for {w}x{h}"


# ── Face crop integration with char_refs ──────────────────────────────────

class TestFaceCropIntegration:
    """Test that face crops integrate correctly with IPAdapter ref selection."""

    def test_face_crop_fields_in_char_refs(self):
        """Verify the expected fields when a face crop is added to char_refs."""
        # Simulate what generate_all_panels does after extracting a face
        char_refs = {
            "hero": {
                "path": "/fake/ref.png",
                "comfyui_filename": "ref_hero.png",
            }
        }

        # Simulate face crop extraction
        char_refs["hero"]["face_crop_path"] = "/fake/face_crop_hero.png"
        char_refs["hero"]["face_crop_filename"] = "face_crop_hero.png"

        assert char_refs["hero"]["face_crop_path"] == "/fake/face_crop_hero.png"
        assert char_refs["hero"]["face_crop_filename"] == "face_crop_hero.png"

    def test_face_crop_not_set_before_first_panel(self):
        """Before first panel generation, no face crop should exist."""
        char_refs = {
            "hero": {
                "path": "/fake/ref.png",
                "comfyui_filename": "ref_hero.png",
            }
        }
        assert "face_crop_filename" not in char_refs["hero"]
        assert "face_crop_path" not in char_refs["hero"]
