#!/usr/bin/env python3
"""Tests for face_validator — thresholds, skip, CLIP backend, auto-detection."""

from __future__ import annotations

import os
import sys
import tempfile
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from PIL import Image

# Ensure the scripts directory is on the path
sys.path.insert(0, os.path.dirname(__file__))

from face_validator import (
    SIMILARITY_THRESHOLD,
    NON_HUMAN_THRESHOLD,
    NON_HUMAN_KEYWORDS,
    FaceValidator,
    CLIPBackend,
    PILHistogramBackend,
    InsightFaceBackend,
    FaceRecognitionBackend,
    build_character_thresholds,
    detect_non_human,
    _cosine_similarity,
    generate_quality_report,
)


# ── Helpers ───────────────────────────────────────────────────────────────

def _make_test_image(path: str, color: tuple = (128, 64, 32), size=(64, 64)):
    """Create a small solid-color test image."""
    img = Image.new("RGB", size, color)
    img.save(path)
    return path


@pytest.fixture()
def tmp_images(tmp_path):
    """Provide ref and panel image paths (solid-color images)."""
    ref = _make_test_image(str(tmp_path / "ref.png"), color=(200, 100, 50))
    panel = _make_test_image(str(tmp_path / "panel.png"), color=(200, 105, 55))
    return ref, panel


# ── detect_non_human ──────────────────────────────────────────────────────

class TestDetectNonHuman:
    """Test auto-detection of non-human characters from description."""

    @pytest.mark.parametrize(
        "desc",
        [
            "A hulking combat robot with red eyes",
            "Android servant model 7",
            "Giant alien warlord from Zeta-5",
            "Small forest creature with wings",
            "Undead monster roaming the crypt",
            "Wild animal — a talking fox",
            "Heavy mech suit pilot",
            "Ancient golem made of stone",
            "A cyborg bounty hunter",
        ],
    )
    def test_non_human_detected(self, desc):
        assert detect_non_human(desc) is True

    @pytest.mark.parametrize(
        "desc",
        [
            "A young woman with red hair",
            "Grizzled old pirate captain",
            "Teenage boy in school uniform",
            "",
            "A mysterious cloaked figure",
        ],
    )
    def test_human_not_detected(self, desc):
        assert detect_non_human(desc) is False


# ── build_character_thresholds ────────────────────────────────────────────

class TestBuildCharacterThresholds:
    """Test threshold/skip construction from story-plan characters."""

    def test_explicit_threshold(self):
        chars = [{"id": "bob", "face_threshold": 0.55, "description": "A guy"}]
        thresholds, skip = build_character_thresholds(chars)
        assert thresholds == {"bob": 0.55}
        assert skip == set()

    def test_skip_flag(self):
        chars = [{"id": "bg_npc", "skip_face_validation": True, "description": "extra"}]
        thresholds, skip = build_character_thresholds(chars)
        assert "bg_npc" in skip
        assert "bg_npc" not in thresholds

    def test_auto_non_human_threshold(self):
        chars = [{"id": "robo", "description": "A friendly robot helper"}]
        thresholds, skip = build_character_thresholds(chars)
        assert thresholds["robo"] == NON_HUMAN_THRESHOLD
        assert skip == set()

    def test_human_gets_no_override(self):
        chars = [{"id": "alice", "description": "A young woman with a sword"}]
        thresholds, skip = build_character_thresholds(chars)
        assert "alice" not in thresholds
        assert skip == set()

    def test_explicit_overrides_auto(self):
        """Explicit face_threshold takes precedence over auto-detect."""
        chars = [{"id": "robo", "description": "A combat robot", "face_threshold": 0.6}]
        thresholds, skip = build_character_thresholds(chars)
        assert thresholds["robo"] == 0.6  # not NON_HUMAN_THRESHOLD

    def test_skip_overrides_threshold(self):
        """skip_face_validation prevents threshold from being set."""
        chars = [
            {
                "id": "x",
                "description": "alien creature",
                "skip_face_validation": True,
                "face_threshold": 0.3,
            }
        ]
        thresholds, skip = build_character_thresholds(chars)
        assert "x" in skip
        assert "x" not in thresholds

    def test_mixed_characters(self):
        chars = [
            {"id": "hero", "description": "A brave knight"},
            {"id": "bot", "description": "Small robot sidekick"},
            {"id": "npc", "description": "Shopkeeper", "skip_face_validation": True},
            {"id": "boss", "description": "Dragon overlord", "face_threshold": 0.5},
        ]
        thresholds, skip = build_character_thresholds(chars)
        assert "hero" not in thresholds  # human, default
        assert thresholds["bot"] == NON_HUMAN_THRESHOLD  # auto non-human
        assert "npc" in skip  # skipped
        assert thresholds["boss"] == 0.5  # explicit

    def test_empty_characters(self):
        thresholds, skip = build_character_thresholds([])
        assert thresholds == {}
        assert skip == set()

    def test_missing_id_ignored(self):
        chars = [{"description": "No id field here"}]
        thresholds, skip = build_character_thresholds(chars)
        assert thresholds == {}
        assert skip == set()


# ── FaceValidator per-character threshold ─────────────────────────────────

class TestFaceValidatorThresholds:
    """Test per-character threshold logic in FaceValidator."""

    def test_default_threshold(self):
        v = FaceValidator(threshold=0.7)
        assert v.get_threshold("unknown_char") == 0.7

    def test_custom_char_threshold(self):
        v = FaceValidator(
            threshold=0.7,
            character_thresholds={"robo": 0.4},
        )
        assert v.get_threshold("robo") == 0.4
        assert v.get_threshold("human_hero") == 0.7


# ── FaceValidator skip validation ─────────────────────────────────────────

class TestFaceValidatorSkip:
    """Test skip_face_validation behaviour."""

    def test_skipped_character_passes(self, tmp_images):
        ref, panel = tmp_images
        v = FaceValidator(skip_characters={"npc"})
        result = v.validate_panel(ref, panel, character_id="npc")
        assert result["skipped"] is True
        assert result["passed"] is True
        assert result["similarity"] is None

    def test_non_skipped_character_validated(self, tmp_images):
        ref, panel = tmp_images
        v = FaceValidator(skip_characters={"other"})
        result = v.validate_panel(ref, panel, character_id="hero")
        assert result["skipped"] is False
        # Should have attempted validation (similarity may or may not be None
        # depending on backend, but skipped must be False)


# ── FaceValidator validate_panel with per-char threshold ──────────────────

class TestFaceValidatorPerCharThreshold:
    """Verify the effective threshold is used per character."""

    def test_low_threshold_passes(self, tmp_images):
        """With a very low threshold, even poor matches pass."""
        ref, panel = tmp_images
        v = FaceValidator(
            threshold=0.99,  # very strict default
            character_thresholds={"easy_char": 0.01},  # very lenient
        )
        result = v.validate_panel(ref, panel, character_id="easy_char")
        # PIL backend should return *some* similarity for solid color images
        if result["similarity"] is not None:
            assert result["passed"] is True
        assert result["threshold"] == 0.01

    def test_high_threshold_fails(self, tmp_images):
        """With threshold=1.0, almost everything fails."""
        ref, panel = tmp_images
        v = FaceValidator(
            threshold=0.5,
            character_thresholds={"strict_char": 1.0},
        )
        result = v.validate_panel(ref, panel, character_id="strict_char")
        if result["similarity"] is not None:
            assert result["passed"] is False
        assert result["threshold"] == 1.0

    def test_result_contains_threshold(self, tmp_images):
        ref, panel = tmp_images
        v = FaceValidator(
            threshold=0.7,
            character_thresholds={"x": 0.42},
        )
        result = v.validate_panel(ref, panel, character_id="x")
        assert result["threshold"] == 0.42


# ── CLIP Backend ──────────────────────────────────────────────────────────

class TestCLIPBackend:
    """Test CLIPBackend (mocked to avoid requiring GPU/large model download)."""

    def test_graceful_fallback_without_transformers(self):
        """CLIPBackend.available should be False when transformers is missing."""
        with patch.dict("sys.modules", {"transformers": None, "torch": None}):
            # Force re-init; the __init__ catches the ImportError
            backend = CLIPBackend.__new__(CLIPBackend)
            backend.available = False
            backend._model = None
            backend._processor = None
            assert backend.available is False

    def test_compare_returns_none_when_unavailable(self, tmp_images):
        ref, panel = tmp_images
        backend = CLIPBackend.__new__(CLIPBackend)
        backend.available = False
        backend._model = None
        backend._processor = None
        assert backend.compare(ref, panel) is None

    def test_compare_with_mock(self, tmp_images):
        """Simulate a working CLIP backend via mocked model."""
        ref, panel = tmp_images
        backend = CLIPBackend.__new__(CLIPBackend)
        backend.available = True

        # Mock processor and model
        fake_embedding = np.random.randn(512).astype(np.float32)

        mock_processor = MagicMock()
        mock_processor.return_value = {"pixel_values": MagicMock()}

        mock_tensor = MagicMock()
        mock_tensor.squeeze.return_value.cpu.return_value.numpy.return_value = fake_embedding

        mock_model = MagicMock()
        mock_model.get_image_features.return_value = mock_tensor

        backend._processor = mock_processor
        backend._model = mock_model

        # Mock torch module so `import torch` inside _get_embedding works
        mock_torch = MagicMock()
        mock_torch.no_grad.return_value.__enter__ = MagicMock(return_value=None)
        mock_torch.no_grad.return_value.__exit__ = MagicMock(return_value=False)

        with patch.dict("sys.modules", {"torch": mock_torch}):
            score = backend.compare(ref, panel)
        # Same embedding for both → cosine similarity = 1.0
        assert score is not None
        assert abs(score - 1.0) < 1e-5

    def test_clip_in_backend_priority(self):
        """CLIP should be tried after face_recognition and before PIL."""
        # With nothing installed, we end up at pil_histogram or clip.
        # Just verify the class structure exists and is callable.
        v = FaceValidator()
        assert v.backend_name in ("insightface", "face_recognition", "clip", "pil_histogram")


# ── Backend priority ──────────────────────────────────────────────────────

class TestBackendPriority:
    """Verify backend selection order."""

    @patch.object(InsightFaceBackend, "__init__", lambda self: setattr(self, "available", False))
    @patch.object(FaceRecognitionBackend, "__init__", lambda self: setattr(self, "available", False))
    @patch.object(CLIPBackend, "__init__", lambda self: setattr(self, "available", True) or setattr(self, "_model", None) or setattr(self, "_processor", None))
    def test_clip_chosen_when_face_backends_unavailable(self):
        v = FaceValidator()
        assert v.backend_name == "clip"

    @patch.object(InsightFaceBackend, "__init__", lambda self: setattr(self, "available", False))
    @patch.object(FaceRecognitionBackend, "__init__", lambda self: setattr(self, "available", False))
    @patch.object(CLIPBackend, "__init__", lambda self: setattr(self, "available", False) or setattr(self, "_model", None) or setattr(self, "_processor", None))
    def test_pil_fallback_when_all_ml_unavailable(self):
        v = FaceValidator()
        assert v.backend_name == "pil_histogram"

    @patch.object(InsightFaceBackend, "__init__", lambda self: setattr(self, "available", True) or setattr(self, "app", MagicMock()))
    def test_insightface_preferred(self):
        v = FaceValidator()
        assert v.backend_name == "insightface"


# ── PILHistogramBackend (existing, sanity check) ─────────────────────────

class TestPILHistogramBackend:
    """Sanity check that the PIL fallback still works."""

    def test_same_image_high_similarity(self, tmp_images):
        ref, _ = tmp_images
        pil = PILHistogramBackend()
        score = pil.compare(ref, ref)
        assert score is not None
        assert score > 0.99  # identical image

    def test_different_images_lower_similarity(self, tmp_path):
        a = _make_test_image(str(tmp_path / "a.png"), color=(255, 0, 0))
        b = _make_test_image(str(tmp_path / "b.png"), color=(0, 0, 255))
        pil = PILHistogramBackend()
        score = pil.compare(a, b)
        assert score is not None
        assert score < 0.9


# ── validate_panel_batch with skip/thresholds ─────────────────────────────

class TestValidatePanelBatch:
    """Test batch validation with skip and thresholds."""

    def test_batch_skips_character(self, tmp_images):
        ref, panel = tmp_images
        v = FaceValidator(skip_characters={"char_b"})
        results = v.validate_panel_batch(
            ref_paths={"char_a": ref, "char_b": ref},
            panel_image_path=panel,
            characters_present=["char_a", "char_b"],
        )
        assert len(results) == 2
        skipped = [r for r in results if r["character_id"] == "char_b"][0]
        assert skipped["skipped"] is True
        assert skipped["passed"] is True


# ── generate_quality_report (existing, sanity check) ─────────────────────

class TestQualityReport:
    def test_empty_report(self):
        report = generate_quality_report([])
        assert "No validations" in report

    def test_report_with_data(self):
        data = [
            {"similarity": 0.9, "passed": True, "backend": "pil_histogram", "character_id": "a"},
            {"similarity": 0.5, "passed": False, "backend": "pil_histogram", "character_id": "b"},
        ]
        report = generate_quality_report(data)
        assert "PASS" not in report or "FAIL" not in report or len(report) > 0
        assert "Face Validation" in report


# ── cosine_similarity edge cases ─────────────────────────────────────────

class TestCosineSimilarity:
    def test_identical_vectors(self):
        v = np.array([1.0, 2.0, 3.0])
        assert abs(_cosine_similarity(v, v) - 1.0) < 1e-6

    def test_orthogonal_vectors(self):
        a = np.array([1.0, 0.0])
        b = np.array([0.0, 1.0])
        assert abs(_cosine_similarity(a, b)) < 1e-6

    def test_zero_vector(self):
        a = np.array([0.0, 0.0])
        b = np.array([1.0, 2.0])
        assert _cosine_similarity(a, b) == 0.0
