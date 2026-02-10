#!/usr/bin/env python3
"""
ComicMaster Pipeline Orchestrator.
Takes a story_plan.json and produces finished comic pages.

Usage:
    python comic_pipeline.py story_plan.json [--output DIR] [--preset NAME]
    python comic_pipeline.py story_plan.json --skip-generate  # layout only (panels exist)
    python comic_pipeline.py story_plan.json --color-grade noir
    python comic_pipeline.py story_plan.json --skip-quality
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from PIL import Image

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent))

from speech_bubbles import add_bubbles, POSITION_HINTS
from page_layout import compose_page, load_template, auto_layout
from export import export_pdf, export_pages_png
from quality_tracker import score_batch
from color_grading import (
    COLOR_GRADES, grade_all_panels, apply_color_grade,
    grade_panel_for_pipeline, list_grades,
)

# Lazy import panel_generator — only needed when generating panels (not for --skip-generate)
# This avoids importing comfy_client which tries to connect to ComfyUI at import time.
generate_all_panels = None
generate_character_ref = None

# Style → default color grade mapping
STYLE_COLOR_GRADE_MAP = {
    "noir": "noir",
    "cyberpunk": "cyberpunk",
    # manga: skip by default (use manga_bw only if explicitly requested)
    # other styles: no auto-grade
}

def _ensure_panel_generator():
    global generate_all_panels, generate_character_ref
    if generate_all_panels is None:
        from panel_generator import generate_all_panels as _gap, generate_character_ref as _gcr
        generate_all_panels = _gap
        generate_character_ref = _gcr


def run_pipeline(story_plan: dict, output_dir: str,
                 preset_name: str = None,
                 panel_width: int = 768, panel_height: int = 768,
                 skip_generate: bool = False,
                 skip_bubbles: bool = False,
                 skip_quality: bool = False,
                 color_grade: str = None,
                 export_formats: list = None) -> dict:
    """
    Run the full comic pipeline.

    Stages:
        1. Validate & prepare
        2. Generate panels (ComfyUI)
        1.5q. Quality report (after generation, optional)
        1.5. Color grading (after generation, before bubbles, optional)
        3. Add speech bubbles (PIL)
        4. Compose pages (PIL)
        5. Export (PNG/PDF/CBZ)

    Returns dict with paths and stats.
    """
    export_formats = export_formats or ["png", "pdf"]
    start_time = time.time()

    title = story_plan.get("title", "Untitled Comic")
    style = story_plan.get("style", "western")
    preset = preset_name or story_plan.get("preset", "dreamshaperXL")
    panels = story_plan.get("panels", [])
    pages_config = story_plan.get("pages", [])
    characters = story_plan.get("characters", [])

    # Create output dirs
    os.makedirs(output_dir, exist_ok=True)
    panels_dir = os.path.join(output_dir, "panels")
    bubbled_dir = os.path.join(output_dir, "panels_bubbled")
    pages_dir = os.path.join(output_dir, "pages")
    exports_dir = os.path.join(output_dir, "exports")
    for d in [panels_dir, bubbled_dir, pages_dir, exports_dir]:
        os.makedirs(d, exist_ok=True)

    # Auto-generate page layouts if not provided
    if not pages_config:
        print("\n📐 Auto-generating dynamic layouts from narrative_weight...")
        pages_config = auto_layout(panels, reading_direction=story_plan.get("reading_direction", "ltr"))
        story_plan["pages"] = pages_config
        for pc in pages_config:
            pids = pc.get("panel_ids", [])
            print(f"   Page {pc['page_number']}: {len(pids)} panels → dynamic layout")

    # Save story plan
    plan_path = os.path.join(output_dir, "story_plan.json")
    with open(plan_path, "w") as f:
        json.dump(story_plan, f, indent=2, ensure_ascii=False)

    print(f"{'='*60}")
    print(f"🎬 ComicMaster Pipeline")
    print(f"   Title: {title}")
    print(f"   Style: {style} | Preset: {preset}")
    print(f"   Panels: {len(panels)} | Pages: {len(pages_config)}")
    print(f"   Output: {output_dir}")
    print(f"{'='*60}")

    # -----------------------------------------------------------
    # STAGE 0.5: Generate character references (IPAdapter)
    # -----------------------------------------------------------
    char_refs = {}
    refs_dir = os.path.join(output_dir, "refs")
    os.makedirs(refs_dir, exist_ok=True)

    if not skip_generate and characters:
        _ensure_panel_generator()
        print("\n🧑 Stage 0.5: Generating character references...")
        for char in characters:
            char_id = char.get("id", "")
            try:
                ref_result = generate_character_ref(
                    character=char,
                    style=style,
                    preset_name=preset,
                    output_dir=refs_dir,
                )
                char_refs[char_id] = ref_result
                print(f"   {char.get('name', char_id)}: ✅ ({ref_result.get('duration_s', '?')}s)")
            except Exception as e:
                print(f"   {char.get('name', char_id)}: ⚠️ {e} (continuing without ref)")

    # -----------------------------------------------------------
    # STAGE 1: Generate panels
    # -----------------------------------------------------------
    panel_results = {}

    if skip_generate:
        print("\n⏭️  Skipping panel generation (--skip-generate)")
        # Load existing panels
        for panel in panels:
            pid = panel.get("id", "")
            # Find matching file
            for ext in [".png", ".jpg", ".jpeg"]:
                candidates = list(Path(panels_dir).glob(f"*{pid}*{ext}"))
                if candidates:
                    panel_results[pid] = {"path": str(candidates[0])}
                    break
            # Also check for numbered files
            if pid not in panel_results:
                idx = panel.get("sequence", panels.index(panel) + 1)
                for ext in [".png", ".jpg"]:
                    candidates = list(Path(panels_dir).glob(f"*{idx:02d}*{ext}")) + \
                                 list(Path(panels_dir).glob(f"*{idx:03d}*{ext}"))
                    if candidates:
                        panel_results[pid] = {"path": str(candidates[0])}
                        break

        print(f"   Found {len(panel_results)}/{len(panels)} existing panels")
    else:
        _ensure_panel_generator()
        print("\n🎨 Stage 1: Generating panels...")
        panel_results, failed = generate_all_panels(
            story_plan=story_plan,
            output_dir=output_dir,
            preset_name=preset,
            width=panel_width,
            height=panel_height,
            char_refs=char_refs if char_refs else None,
        )
        if failed:
            print(f"\n⚠️  {len(failed)} panels failed: {[f[0] for f in failed]}")

    # -----------------------------------------------------------
    # STAGE 1.5q: Quality Report (auto, unless --skip-quality)
    # -----------------------------------------------------------
    quality_report = None

    if not skip_quality and panel_results:
        print("\n📊 Stage 1.5q: Quality analysis...")
        try:
            batch_score = score_batch(
                panels_dir,
                run_id=title,
                composition=True,
                sequence=True,
            )
            quality_report = {
                "avg_score": batch_score.mean_score,
                "best_panel": batch_score.best_panel,
                "worst_panel": batch_score.worst_panel,
                "panel_count": batch_score.panel_count,
                "mean_sharpness": batch_score.mean_sharpness,
                "mean_contrast": batch_score.mean_contrast,
                "mean_composition": batch_score.mean_composition_score,
            }
            # Save quality_scores.json
            from dataclasses import asdict
            scores_path = os.path.join(output_dir, "quality_scores.json")
            with open(scores_path, "w") as f:
                json.dump(asdict(batch_score), f, indent=2, ensure_ascii=False)

            # Print summary
            print(f"   Avg Score: {batch_score.mean_score:.1f}/100")
            print(f"   Best:  {batch_score.best_panel} ({batch_score.max_score:.1f})")
            print(f"   Worst: {batch_score.worst_panel} ({batch_score.min_score:.1f})")
            if batch_score.mean_composition_score is not None:
                print(f"   Composition: {batch_score.mean_composition_score:.1f}/100")
            if batch_score.sequence_analysis:
                seq = batch_score.sequence_analysis
                print(f"   Sequence: {seq.get('sequence_score', 0):.1f}/100")
            print(f"   Saved: {scores_path}")
        except Exception as e:
            print(f"   ⚠️ Quality analysis failed: {e}")
    elif skip_quality:
        print("\n⏭️  Skipping quality analysis (--skip-quality)")

    # -----------------------------------------------------------
    # STAGE 1.5: Color Grading (optional)
    # -----------------------------------------------------------
    # Determine color grade: CLI arg > story plan > style auto-map
    effective_grade = color_grade
    if not effective_grade:
        effective_grade = story_plan.get("color_grade")
    if not effective_grade:
        effective_grade = STYLE_COLOR_GRADE_MAP.get(style)

    if effective_grade and panel_results:
        if effective_grade not in COLOR_GRADES:
            print(f"\n⚠️  Unknown color grade '{effective_grade}', skipping. "
                  f"Available: {', '.join(COLOR_GRADES.keys())}")
        else:
            print(f"\n🎨 Stage 1.5: Color grading ({effective_grade})...")
            graded_dir = os.path.join(output_dir, "panels_graded")
            os.makedirs(graded_dir, exist_ok=True)

            graded_count = 0
            for pid, result in panel_results.items():
                panel_path = result["path"]
                graded_path = os.path.join(graded_dir, f"{pid}.png")
                try:
                    apply_color_grade(panel_path, effective_grade, graded_path)
                    # Update panel_results to point to graded version
                    panel_results[pid] = {"path": graded_path}
                    graded_count += 1
                except Exception as e:
                    print(f"   ⚠️ {pid}: grading failed: {e}")

            print(f"   Graded {graded_count}/{len(panel_results)} panels → {graded_dir}")

    # -----------------------------------------------------------
    # STAGE 2: Add speech bubbles
    # -----------------------------------------------------------
    bubbled_panels = {}

    if skip_bubbles:
        print("\n⏭️  Skipping speech bubbles")
        bubbled_panels = panel_results
    else:
        print("\n💬 Stage 2: Adding speech bubbles...")
        for panel in panels:
            pid = panel.get("id", "")
            if pid not in panel_results:
                continue

            panel_path = panel_results[pid]["path"]
            panel_img = Image.open(panel_path)

            # Build bubble configs from dialogue
            bubbles = []
            shot = panel.get("shot_type", "medium")
            num_dialogues = len(panel.get("dialogue", []))

            for i, dlg in enumerate(panel.get("dialogue", [])):
                hint = dlg.get("position_hint")

                # Smart default positioning: keep bubbles ABOVE character faces
                # Close-ups: faces fill the panel → bubbles at very top
                # Wide shots: more room → can use standard positions
                if not hint:
                    if shot in ("close_up", "extreme_close", "medium_close"):
                        # Face fills panel → force bubbles to top edge
                        hint = "top_left" if i % 2 == 0 else "top_right"
                    else:
                        hint = "top_left" if i % 2 == 0 else "top_right"

                pos = POSITION_HINTS.get(hint, (0.5, 0.12))

                # For close-ups, force Y even higher to avoid face
                if shot in ("close_up", "extreme_close"):
                    pos = (pos[0], min(pos[1], 0.10))
                elif shot == "medium_close":
                    pos = (pos[0], min(pos[1], 0.12))

                # Stack multiple dialogues vertically with offset
                if num_dialogues > 1:
                    y_offset = i * 0.06  # slight vertical offset per dialogue
                    pos = (pos[0], pos[1] + y_offset)

                # Estimate tail target — point toward character area
                # but keep it short (tail length is already limited in renderer)
                char_positions = {
                    0: (0.35, 0.40),
                    1: (0.65, 0.40),
                    2: (0.50, 0.40),
                }
                char_idx = panel.get("characters_present", []).index(dlg.get("character", "")) \
                    if dlg.get("character") in panel.get("characters_present", []) else i
                tail = char_positions.get(char_idx % 3, (0.5, 0.40))

                bubbles.append({
                    "text": dlg.get("text", ""),
                    "type": dlg.get("type", "speech"),
                    "position": pos,
                    "tail_target": tail if dlg.get("type", "speech") != "narration" else None,
                })

            # Add narration box if present — bottom of panel, away from faces
            # BUT skip if narration text already appears in dialogue entries
            # (story plans often duplicate narration both as a dialogue entry
            #  with type="narration" and as the panel's narration field)
            if panel.get("narration"):
                narration_text = panel["narration"].strip()
                already_in_dialogue = any(
                    b.get("text", "").strip() == narration_text
                    for b in bubbles
                )
                if not already_in_dialogue:
                    bubbles.append({
                        "text": narration_text,
                        "type": "narration",
                        "position": (0.5, 0.92),
                        "tail_target": None,
                    })

            if bubbles:
                panel_img = add_bubbles(panel_img, bubbles, style=style)

            # Save bubbled panel
            out_path = os.path.join(bubbled_dir, f"{pid}.png")
            panel_img.save(out_path)
            bubbled_panels[pid] = {"path": out_path}
            print(f"   {pid}: {len(bubbles)} bubble(s) added")

        # Panels without dialogue: copy as-is
        for pid, result in panel_results.items():
            if pid not in bubbled_panels:
                panel_img = Image.open(result["path"])
                out_path = os.path.join(bubbled_dir, f"{pid}.png")
                panel_img.save(out_path)
                bubbled_panels[pid] = {"path": out_path}

    # -----------------------------------------------------------
    # STAGE 3: Compose pages
    # -----------------------------------------------------------
    print("\n📄 Stage 3: Composing pages...")
    page_images = []

    for page_cfg in pages_config:
        page_num = page_cfg.get("page_number", len(page_images) + 1)
        layout_name = page_cfg.get("layout", None)
        layout_data = page_cfg.get("layout_data", None)
        panel_ids = page_cfg.get("panel_ids", [])

        # Collect panel images for this page
        page_panels = []
        for pid in panel_ids:
            if pid in bubbled_panels:
                page_panels.append(Image.open(bubbled_panels[pid]["path"]))
            else:
                print(f"   ⚠️ Panel {pid} not found, using placeholder")
                placeholder = Image.new("RGB", (panel_width, panel_height), "#cccccc")
                page_panels.append(placeholder)

        try:
            page_img = compose_page(
                panel_images=page_panels,
                layout_name=layout_name or (None if layout_data else "page_2x2"),
                layout_data=layout_data,
                page_number=page_num,
            )
            page_path = os.path.join(pages_dir, f"page_{page_num:02d}.png")
            page_img.save(page_path, quality=95)
            page_images.append(page_img)
            layout_label = layout_name or "dynamic"
            print(f"   Page {page_num}: {layout_label} ({len(page_panels)} panels) → {page_path}")
        except Exception as e:
            print(f"   ❌ Page {page_num} failed: {e}")

    # -----------------------------------------------------------
    # STAGE 4: Export
    # -----------------------------------------------------------
    print("\n📦 Stage 4: Exporting...")
    export_paths = {}

    if "png" in export_formats:
        png_paths = export_pages_png(page_images, pages_dir)
        export_paths["png"] = png_paths
        print(f"   PNG: {len(png_paths)} pages saved")

    if "pdf" in export_formats and page_images:
        pdf_path = os.path.join(exports_dir, f"{title.lower().replace(' ', '_')}.pdf")
        export_pdf(page_images, pdf_path, title=title)
        export_paths["pdf"] = pdf_path
        print(f"   PDF: {pdf_path}")

    # -----------------------------------------------------------
    # Summary
    # -----------------------------------------------------------
    total_time = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"✅ Comic complete!")
    print(f"   Title: {title}")
    print(f"   Panels: {len(panel_results)}/{len(panels)}")
    print(f"   Pages: {len(page_images)}")
    if effective_grade:
        print(f"   Color Grade: {effective_grade}")
    if quality_report:
        print(f"   Quality: {quality_report['avg_score']:.1f}/100 avg")
    print(f"   Time: {total_time:.1f}s")
    print(f"   Output: {output_dir}")
    print(f"{'='*60}")

    result = {
        "title": title,
        "output_dir": output_dir,
        "panel_results": panel_results,
        "page_count": len(page_images),
        "export_paths": export_paths,
        "total_time_s": round(total_time, 1),
        "panels_generated": len(panel_results),
        "panels_failed": len(panels) - len(panel_results),
    }
    if quality_report:
        result["quality_report"] = quality_report
    if effective_grade:
        result["color_grade"] = effective_grade
    return result


# --- CLI ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ComicMaster Pipeline")
    parser.add_argument("story_plan", help="Path to story_plan.json")
    parser.add_argument("--output", "-o", default=None, help="Output directory")
    parser.add_argument("--preset", "-p", default=None, help="ComfyUI preset")
    parser.add_argument("--width", "-W", type=int, default=768)
    parser.add_argument("--height", "-H", type=int, default=768)
    parser.add_argument("--skip-generate", action="store_true",
                        help="Skip panel generation (use existing)")
    parser.add_argument("--skip-bubbles", action="store_true",
                        help="Skip speech bubble overlay")
    parser.add_argument("--skip-quality", action="store_true",
                        help="Skip automatic quality analysis after panel generation")
    parser.add_argument("--color-grade", default=None,
                        help=f"Apply color grade preset before bubbles. "
                             f"Options: {', '.join(COLOR_GRADES.keys())}")
    parser.add_argument("--formats", default="png,pdf",
                        help="Export formats (comma-separated: png,pdf,cbz)")

    args = parser.parse_args()

    with open(args.story_plan) as f:
        plan = json.load(f)

    output = args.output or os.path.join(
        "/home/mcmuff/clawd/output/comicmaster",
        plan.get("title", "comic").lower().replace(" ", "_"),
    )

    run_pipeline(
        story_plan=plan,
        output_dir=output,
        preset_name=args.preset,
        panel_width=args.width,
        panel_height=args.height,
        skip_generate=args.skip_generate,
        skip_bubbles=args.skip_bubbles,
        skip_quality=args.skip_quality,
        color_grade=args.color_grade,
        export_formats=args.formats.split(","),
    )
