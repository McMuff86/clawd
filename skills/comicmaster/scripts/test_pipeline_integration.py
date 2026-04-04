#!/usr/bin/env python3
"""
Tests for ComicMaster Pipeline Integration — Quality Tracker + Color Grading.

Tests that:
1. Quality tracker integration doesn't crash the pipeline
2. Color grading applies correctly in the pipeline
3. Skip flags work (--skip-quality, --color-grade)
4. Style-to-grade auto-mapping works
5. Story plan color_grade field is respected
"""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest
import numpy as np
from PIL import Image, ImageDraw

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent))

from comic_pipeline import run_pipeline, STYLE_COLOR_GRADE_MAP
from color_grading import COLOR_GRADES, apply_color_grade, list_grades
from quality_tracker import score_batch, score_panel


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_test_panel(size=(256, 256), color=None):
    """Create a test panel image with some features (not just solid color)."""
    if color:
        img = Image.new("RGB", size, color)
    else:
        # Create something with edges and variation for quality scoring
        img = Image.new("RGB", size, (60, 80, 100))
    draw = ImageDraw.Draw(img)
    w, h = size
    # Add shapes for contrast/edges
    draw.rectangle([w // 4, h // 4, 3 * w // 4, 3 * h // 4], fill=(200, 180, 160))
    draw.ellipse([w // 3, h // 3, 2 * w // 3, 2 * h // 3], fill=(255, 200, 100))
    draw.line([(0, 0), (w, h)], fill=(30, 30, 30), width=3)
    draw.line([(w, 0), (0, h)], fill=(30, 30, 30), width=3)
    return img


def _make_test_output_dir(panel_count=4):
    """Create a temp output dir with pre-generated panels for --skip-generate tests."""
    tmpdir = tempfile.mkdtemp(prefix="comicmaster_test_")
    panels_dir = os.path.join(tmpdir, "panels")
    os.makedirs(panels_dir)

    for i in range(1, panel_count + 1):
        pid = f"panel_{i:02d}"
        img = _make_test_panel(color=(
            50 + i * 40,
            80 + i * 20,
            100 + i * 10,
        ))
        img.save(os.path.join(panels_dir, f"{pid}.png"))

    return tmpdir


def _make_minimal_story_plan(panel_count=4, style="western", extra=None):
    """Create a minimal story plan for testing."""
    panels = []
    for i in range(1, panel_count + 1):
        panels.append({
            "id": f"panel_{i:02d}",
            "sequence": i,
            "scene": f"Test scene {i}",
            "action": f"Test action {i}",
            "characters_present": [],
            "dialogue": [],
        })

    plan = {
        "title": "Test Comic",
        "style": style,
        "panels": panels,
        "pages": [{
            "page_number": 1,
            "layout": "page_2x2",
            "panel_ids": [p["id"] for p in panels[:4]],
        }] if panel_count >= 4 else [{
            "page_number": 1,
            "layout": "page_2x2",
            "panel_ids": [p["id"] for p in panels],
        }],
    }

    if extra:
        plan.update(extra)

    return plan


# ---------------------------------------------------------------------------
# Test: Quality Tracker Integration
# ---------------------------------------------------------------------------

class TestQualityIntegration:
    """Tests for automatic quality report in the pipeline."""

    def test_quality_report_generated(self, tmp_path):
        """Quality scores.json is created after panel generation."""
        output_dir = str(tmp_path / "output")
        panels_dir = os.path.join(output_dir, "panels")
        os.makedirs(panels_dir)

        # Create test panels
        for i in range(1, 4):
            _make_test_panel().save(os.path.join(panels_dir, f"panel_{i:02d}.png"))

        plan = _make_minimal_story_plan(panel_count=3)
        result = run_pipeline(
            story_plan=plan,
            output_dir=output_dir,
            skip_generate=True,
            skip_bubbles=True,
        )

        # Check quality_scores.json was created
        scores_path = os.path.join(output_dir, "quality_scores.json")
        assert os.path.exists(scores_path), "quality_scores.json should be created"

        with open(scores_path) as f:
            scores = json.load(f)

        assert "mean_score" in scores
        assert "panels" in scores
        assert scores["panel_count"] >= 1

    def test_quality_report_in_result(self, tmp_path):
        """Pipeline result dict includes quality_report."""
        output_dir = str(tmp_path / "output")
        panels_dir = os.path.join(output_dir, "panels")
        os.makedirs(panels_dir)

        for i in range(1, 3):
            _make_test_panel().save(os.path.join(panels_dir, f"panel_{i:02d}.png"))

        plan = _make_minimal_story_plan(panel_count=2)
        plan["pages"] = [{
            "page_number": 1,
            "layout": "page_2x2",
            "panel_ids": ["panel_01", "panel_02"],
        }]

        result = run_pipeline(
            story_plan=plan,
            output_dir=output_dir,
            skip_generate=True,
            skip_bubbles=True,
        )

        assert "quality_report" in result
        qr = result["quality_report"]
        assert "avg_score" in qr
        assert "best_panel" in qr
        assert "worst_panel" in qr
        assert qr["avg_score"] > 0

    def test_skip_quality_flag(self, tmp_path):
        """--skip-quality prevents quality analysis."""
        output_dir = str(tmp_path / "output")
        panels_dir = os.path.join(output_dir, "panels")
        os.makedirs(panels_dir)

        for i in range(1, 3):
            _make_test_panel().save(os.path.join(panels_dir, f"panel_{i:02d}.png"))

        plan = _make_minimal_story_plan(panel_count=2)
        plan["pages"] = [{
            "page_number": 1,
            "layout": "page_2x2",
            "panel_ids": ["panel_01", "panel_02"],
        }]

        result = run_pipeline(
            story_plan=plan,
            output_dir=output_dir,
            skip_generate=True,
            skip_bubbles=True,
            skip_quality=True,
        )

        # quality_scores.json should NOT exist
        scores_path = os.path.join(output_dir, "quality_scores.json")
        assert not os.path.exists(scores_path), "quality_scores.json should NOT be created with --skip-quality"
        assert "quality_report" not in result

    def test_quality_doesnt_crash_on_empty_panels(self, tmp_path):
        """Quality analysis handles empty panels dir gracefully."""
        output_dir = str(tmp_path / "output")
        panels_dir = os.path.join(output_dir, "panels")
        os.makedirs(panels_dir)

        plan = _make_minimal_story_plan(panel_count=0)
        plan["panels"] = []
        plan["pages"] = []

        # Should not crash
        result = run_pipeline(
            story_plan=plan,
            output_dir=output_dir,
            skip_generate=True,
            skip_bubbles=True,
        )
        # No quality report since no panels found
        assert "quality_report" not in result or result.get("quality_report") is None


# ---------------------------------------------------------------------------
# Test: Color Grading Integration
# ---------------------------------------------------------------------------

class TestColorGradingIntegration:
    """Tests for color grading in the pipeline."""

    def test_color_grade_cli_arg(self, tmp_path):
        """--color-grade applies grading to panels."""
        output_dir = str(tmp_path / "output")
        panels_dir = os.path.join(output_dir, "panels")
        os.makedirs(panels_dir)

        # Create panels
        for i in range(1, 3):
            _make_test_panel().save(os.path.join(panels_dir, f"panel_{i:02d}.png"))

        plan = _make_minimal_story_plan(panel_count=2)
        plan["pages"] = [{
            "page_number": 1,
            "layout": "page_2x2",
            "panel_ids": ["panel_01", "panel_02"],
        }]

        result = run_pipeline(
            story_plan=plan,
            output_dir=output_dir,
            skip_generate=True,
            skip_bubbles=True,
            skip_quality=True,
            color_grade="noir",
        )

        # Graded dir should exist
        graded_dir = os.path.join(output_dir, "panels_graded")
        assert os.path.isdir(graded_dir), "panels_graded directory should exist"

        # Graded panels should exist
        graded_files = list(Path(graded_dir).glob("*.png"))
        assert len(graded_files) == 2, f"Expected 2 graded panels, got {len(graded_files)}"

        assert result.get("color_grade") == "noir"

    def test_color_grade_from_story_plan(self, tmp_path):
        """color_grade in story plan root is respected."""
        output_dir = str(tmp_path / "output")
        panels_dir = os.path.join(output_dir, "panels")
        os.makedirs(panels_dir)

        _make_test_panel().save(os.path.join(panels_dir, "panel_01.png"))

        plan = _make_minimal_story_plan(panel_count=1)
        plan["color_grade"] = "cyberpunk"
        plan["pages"] = [{
            "page_number": 1,
            "layout": "page_2x2",
            "panel_ids": ["panel_01"],
        }]

        result = run_pipeline(
            story_plan=plan,
            output_dir=output_dir,
            skip_generate=True,
            skip_bubbles=True,
            skip_quality=True,
        )

        assert result.get("color_grade") == "cyberpunk"
        graded_dir = os.path.join(output_dir, "panels_graded")
        assert os.path.isdir(graded_dir)

    def test_cli_arg_overrides_story_plan(self, tmp_path):
        """CLI --color-grade takes priority over story plan."""
        output_dir = str(tmp_path / "output")
        panels_dir = os.path.join(output_dir, "panels")
        os.makedirs(panels_dir)

        _make_test_panel().save(os.path.join(panels_dir, "panel_01.png"))

        plan = _make_minimal_story_plan(panel_count=1)
        plan["color_grade"] = "cyberpunk"
        plan["pages"] = [{
            "page_number": 1,
            "layout": "page_2x2",
            "panel_ids": ["panel_01"],
        }]

        result = run_pipeline(
            story_plan=plan,
            output_dir=output_dir,
            skip_generate=True,
            skip_bubbles=True,
            skip_quality=True,
            color_grade="vintage",  # CLI overrides story plan
        )

        assert result.get("color_grade") == "vintage"

    def test_no_color_grade_skips(self, tmp_path):
        """Without color grade, no grading directory is created."""
        output_dir = str(tmp_path / "output")
        panels_dir = os.path.join(output_dir, "panels")
        os.makedirs(panels_dir)

        _make_test_panel().save(os.path.join(panels_dir, "panel_01.png"))

        plan = _make_minimal_story_plan(panel_count=1)
        plan["pages"] = [{
            "page_number": 1,
            "layout": "page_2x2",
            "panel_ids": ["panel_01"],
        }]

        result = run_pipeline(
            story_plan=plan,
            output_dir=output_dir,
            skip_generate=True,
            skip_bubbles=True,
            skip_quality=True,
        )

        graded_dir = os.path.join(output_dir, "panels_graded")
        assert not os.path.exists(graded_dir), "No graded dir when no color grade"
        assert "color_grade" not in result

    def test_invalid_grade_handled(self, tmp_path):
        """Invalid color grade name doesn't crash pipeline."""
        output_dir = str(tmp_path / "output")
        panels_dir = os.path.join(output_dir, "panels")
        os.makedirs(panels_dir)

        _make_test_panel().save(os.path.join(panels_dir, "panel_01.png"))

        plan = _make_minimal_story_plan(panel_count=1)
        plan["pages"] = [{
            "page_number": 1,
            "layout": "page_2x2",
            "panel_ids": ["panel_01"],
        }]

        # Should not crash with invalid grade
        result = run_pipeline(
            story_plan=plan,
            output_dir=output_dir,
            skip_generate=True,
            skip_bubbles=True,
            skip_quality=True,
            color_grade="nonexistent_grade",
        )
        # Pipeline should still complete
        assert result["title"] == "Test Comic"

    def test_grading_before_bubbles(self, tmp_path):
        """Color grading is applied before bubbles (panels in bubbled dir use graded versions)."""
        output_dir = str(tmp_path / "output")
        panels_dir = os.path.join(output_dir, "panels")
        os.makedirs(panels_dir)

        # Create a distinctly colored panel
        original = _make_test_panel(color=(200, 100, 100))
        original.save(os.path.join(panels_dir, "panel_01.png"))

        plan = _make_minimal_story_plan(panel_count=1)
        plan["panels"][0]["dialogue"] = [
            {"character": "test", "text": "Hello", "type": "speech"}
        ]
        plan["pages"] = [{
            "page_number": 1,
            "layout": "page_2x2",
            "panel_ids": ["panel_01"],
        }]

        result = run_pipeline(
            story_plan=plan,
            output_dir=output_dir,
            skip_generate=True,
            skip_quality=True,
            color_grade="noir",
        )

        # The bubbled panel should be based on the graded version
        bubbled_path = os.path.join(output_dir, "panels_bubbled", "panel_01.png")
        assert os.path.exists(bubbled_path)

        # The graded version should also exist
        graded_path = os.path.join(output_dir, "panels_graded", "panel_01.png")
        assert os.path.exists(graded_path)


# ---------------------------------------------------------------------------
# Test: Style-to-Grade Auto-Mapping
# ---------------------------------------------------------------------------

class TestStyleGradeMapping:
    """Tests for automatic style → color grade mapping."""

    def test_noir_style_auto_grades(self, tmp_path):
        """Style 'noir' auto-selects 'noir' color grade."""
        output_dir = str(tmp_path / "output")
        panels_dir = os.path.join(output_dir, "panels")
        os.makedirs(panels_dir)

        _make_test_panel().save(os.path.join(panels_dir, "panel_01.png"))

        plan = _make_minimal_story_plan(panel_count=1, style="noir")
        plan["pages"] = [{
            "page_number": 1,
            "layout": "page_2x2",
            "panel_ids": ["panel_01"],
        }]

        result = run_pipeline(
            story_plan=plan,
            output_dir=output_dir,
            skip_generate=True,
            skip_bubbles=True,
            skip_quality=True,
        )

        assert result.get("color_grade") == "noir"

    def test_cyberpunk_style_auto_grades(self, tmp_path):
        """Style 'cyberpunk' auto-selects 'cyberpunk' color grade."""
        output_dir = str(tmp_path / "output")
        panels_dir = os.path.join(output_dir, "panels")
        os.makedirs(panels_dir)

        _make_test_panel().save(os.path.join(panels_dir, "panel_01.png"))

        plan = _make_minimal_story_plan(panel_count=1, style="cyberpunk")
        plan["pages"] = [{
            "page_number": 1,
            "layout": "page_2x2",
            "panel_ids": ["panel_01"],
        }]

        result = run_pipeline(
            story_plan=plan,
            output_dir=output_dir,
            skip_generate=True,
            skip_bubbles=True,
            skip_quality=True,
        )

        assert result.get("color_grade") == "cyberpunk"

    def test_manga_style_no_auto_grade(self, tmp_path):
        """Style 'manga' does NOT auto-select a color grade."""
        output_dir = str(tmp_path / "output")
        panels_dir = os.path.join(output_dir, "panels")
        os.makedirs(panels_dir)

        _make_test_panel().save(os.path.join(panels_dir, "panel_01.png"))

        plan = _make_minimal_story_plan(panel_count=1, style="manga")
        plan["pages"] = [{
            "page_number": 1,
            "layout": "page_2x2",
            "panel_ids": ["panel_01"],
        }]

        result = run_pipeline(
            story_plan=plan,
            output_dir=output_dir,
            skip_generate=True,
            skip_bubbles=True,
            skip_quality=True,
        )

        assert "color_grade" not in result

    def test_western_style_no_auto_grade(self, tmp_path):
        """Style 'western' does NOT auto-select a color grade."""
        assert "western" not in STYLE_COLOR_GRADE_MAP

    def test_style_mapping_overridden_by_story_plan(self, tmp_path):
        """Explicit color_grade in story plan overrides style auto-mapping."""
        output_dir = str(tmp_path / "output")
        panels_dir = os.path.join(output_dir, "panels")
        os.makedirs(panels_dir)

        _make_test_panel().save(os.path.join(panels_dir, "panel_01.png"))

        plan = _make_minimal_story_plan(panel_count=1, style="noir")
        plan["color_grade"] = "vintage"  # Override noir auto-grade
        plan["pages"] = [{
            "page_number": 1,
            "layout": "page_2x2",
            "panel_ids": ["panel_01"],
        }]

        result = run_pipeline(
            story_plan=plan,
            output_dir=output_dir,
            skip_generate=True,
            skip_bubbles=True,
            skip_quality=True,
        )

        # story plan explicit grade overrides style mapping
        assert result.get("color_grade") == "vintage"

    def test_style_grade_map_contents(self):
        """Verify the style→grade mapping has expected entries."""
        assert STYLE_COLOR_GRADE_MAP["noir"] == "noir"
        assert STYLE_COLOR_GRADE_MAP["cyberpunk"] == "cyberpunk"
        assert "manga" not in STYLE_COLOR_GRADE_MAP
        assert "western" not in STYLE_COLOR_GRADE_MAP
        assert "cartoon" not in STYLE_COLOR_GRADE_MAP


# ---------------------------------------------------------------------------
# Test: Color Grading Correctness
# ---------------------------------------------------------------------------

class TestColorGradingCorrectness:
    """Tests that color grading actually changes the image pixels."""

    def test_noir_desaturates(self, tmp_path):
        """Noir grade reduces saturation."""
        img = _make_test_panel(color=(200, 100, 50))
        src_path = str(tmp_path / "original.png")
        out_path = str(tmp_path / "graded.png")
        img.save(src_path)

        apply_color_grade(src_path, "noir", out_path)

        original = np.array(Image.open(src_path))
        graded = np.array(Image.open(out_path))

        # Noir desaturates — graded should be less saturated
        # Check by comparing channel spread (less spread = less saturated)
        orig_spread = float(np.std(original.astype(float), axis=2).mean())
        graded_spread = float(np.std(graded.astype(float), axis=2).mean())

        assert graded_spread < orig_spread, \
            f"Noir should desaturate: orig_spread={orig_spread:.1f}, graded={graded_spread:.1f}"

    def test_vibrant_saturates(self, tmp_path):
        """Vibrant grade increases saturation."""
        img = _make_test_panel(color=(150, 100, 80))
        src_path = str(tmp_path / "original.png")
        out_path = str(tmp_path / "graded.png")
        img.save(src_path)

        apply_color_grade(src_path, "vibrant", out_path)

        original = np.array(Image.open(src_path))
        graded = np.array(Image.open(out_path))

        orig_spread = float(np.std(original.astype(float), axis=2).mean())
        graded_spread = float(np.std(graded.astype(float), axis=2).mean())

        assert graded_spread > orig_spread, \
            f"Vibrant should increase saturation: orig={orig_spread:.1f}, graded={graded_spread:.1f}"

    def test_all_grades_produce_valid_images(self, tmp_path):
        """Every grade preset produces a valid PNG file."""
        img = _make_test_panel()
        src_path = str(tmp_path / "original.png")
        img.save(src_path)

        for grade_name in COLOR_GRADES:
            out_path = str(tmp_path / f"graded_{grade_name}.png")
            apply_color_grade(src_path, grade_name, out_path)
            assert os.path.exists(out_path), f"Grade '{grade_name}' should produce output"
            result_img = Image.open(out_path)
            assert result_img.size == img.size, f"Grade '{grade_name}' should preserve dimensions"

    def test_list_grades_returns_all(self):
        """list_grades() returns all defined presets."""
        grades = list_grades()
        assert "noir" in grades
        assert "cyberpunk" in grades
        assert "vintage" in grades
        assert "vibrant" in grades
        assert "pastel" in grades
        assert "manga_bw" in grades


# ---------------------------------------------------------------------------
# Test: Full Pipeline Integration (quality + grading together)
# ---------------------------------------------------------------------------

class TestFullIntegration:
    """Tests combining quality tracker and color grading in full pipeline."""

    def test_quality_and_grading_together(self, tmp_path):
        """Pipeline runs with both quality tracking and color grading."""
        output_dir = str(tmp_path / "output")
        panels_dir = os.path.join(output_dir, "panels")
        os.makedirs(panels_dir)

        for i in range(1, 3):
            _make_test_panel().save(os.path.join(panels_dir, f"panel_{i:02d}.png"))

        plan = _make_minimal_story_plan(panel_count=2)
        plan["pages"] = [{
            "page_number": 1,
            "layout": "page_2x2",
            "panel_ids": ["panel_01", "panel_02"],
        }]

        result = run_pipeline(
            story_plan=plan,
            output_dir=output_dir,
            skip_generate=True,
            skip_bubbles=True,
            color_grade="vintage",
        )

        # Both should be present
        assert "quality_report" in result
        assert result.get("color_grade") == "vintage"

        # Quality scores should exist
        assert os.path.exists(os.path.join(output_dir, "quality_scores.json"))
        # Graded panels should exist
        assert os.path.isdir(os.path.join(output_dir, "panels_graded"))

    def test_pipeline_skip_all_optional(self, tmp_path):
        """Pipeline works with all optional stages skipped."""
        output_dir = str(tmp_path / "output")
        panels_dir = os.path.join(output_dir, "panels")
        os.makedirs(panels_dir)

        _make_test_panel().save(os.path.join(panels_dir, "panel_01.png"))

        plan = _make_minimal_story_plan(panel_count=1)
        plan["pages"] = [{
            "page_number": 1,
            "layout": "page_2x2",
            "panel_ids": ["panel_01"],
        }]

        result = run_pipeline(
            story_plan=plan,
            output_dir=output_dir,
            skip_generate=True,
            skip_bubbles=True,
            skip_quality=True,
        )

        assert result["title"] == "Test Comic"
        assert "quality_report" not in result
        assert "color_grade" not in result
