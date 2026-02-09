#!/usr/bin/env python3
"""
Generate images with ComfyUI using predefined workflow templates.

Usage:
    python generate.py "prompt" [--negative "..."] [--model MODEL] [--width W] [--height H]
                                [--steps N] [--cfg C] [--seed S] [--output DIR] [--batch N]
                                [--sampler NAME] [--scheduler NAME] [--template TEMPLATE]
"""

import argparse
import json
import os
import random
import sys
import time

# Add parent scripts dir
sys.path.insert(0, os.path.dirname(__file__))
from comfy_client import generate_and_download, get_config, ensure_running
from comfy_logger import log_generation

DEFAULT_OUTPUT = "/home/mcmuff/clawd/output/comfyui"
PRESETS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "presets.json")
WORKFLOWS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "workflows")

def load_presets():
    """Load presets from presets.json."""
    if os.path.exists(PRESETS_FILE):
        with open(PRESETS_FILE) as f:
            data = json.load(f)
            # Remove _comment key
            return {k: v for k, v in data.items() if not k.startswith("_")}
    return {}

# --- Workflow Templates ---

def txt2img_sdxl(args):
    """Text-to-image workflow for SDXL models."""
    seed = args.seed if args.seed >= 0 else random.randint(0, 2**32 - 1)
    
    return {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": args.steps,
                "cfg": args.cfg,
                "sampler_name": args.sampler,
                "scheduler": args.scheduler,
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            }
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": args.model
            }
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": args.width,
                "height": args.height,
                "batch_size": args.batch
            }
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": args.prompt,
                "clip": ["4", 1]
            }
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": args.negative,
                "clip": ["4", 1]
            }
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            }
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": args.prefix,
                "images": ["8", 0]
            }
        }
    }

def txt2img_flux(args):
    """Text-to-image workflow for Flux models (uses UNETLoader + DualCLIPLoader)."""
    seed = args.seed if args.seed >= 0 else random.randint(0, 2**32 - 1)

    return {
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": args.prompt,
                "clip": ["38", 0]
            },
            "_meta": {"title": "CLIP Text Encode (Positive Prompt)"}
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["13", 0],
                "vae": ["10", 0]
            }
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": args.prefix,
                "images": ["8", 0]
            }
        },
        "10": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": getattr(args, 'flux_vae', 'ae.safetensors')
            }
        },
        "12": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": args.model,
                "weight_dtype": "fp8_e4m3fn"
            }
        },
        "13": {
            "class_type": "SamplerCustomAdvanced",
            "inputs": {
                "noise": ["25", 0],
                "guider": ["22", 0],
                "sampler": ["16", 0],
                "sigmas": ["17", 0],
                "latent_image": ["27", 0]
            }
        },
        "16": {
            "class_type": "KSamplerSelect",
            "inputs": {
                "sampler_name": args.sampler
            }
        },
        "17": {
            "class_type": "BasicScheduler",
            "inputs": {
                "scheduler": args.scheduler,
                "steps": args.steps,
                "denoise": 1.0,
                "model": ["12", 0]
            }
        },
        "22": {
            "class_type": "BasicGuider",
            "inputs": {
                "model": ["12", 0],
                "conditioning": ["26", 0]
            }
        },
        "25": {
            "class_type": "RandomNoise",
            "inputs": {
                "noise_seed": seed
            }
        },
        "26": {
            "class_type": "FluxGuidance",
            "inputs": {
                "guidance": args.cfg,
                "conditioning": ["6", 0]
            }
        },
        "27": {
            "class_type": "EmptySD3LatentImage",
            "inputs": {
                "width": args.width,
                "height": args.height,
                "batch_size": args.batch
            }
        },
        "38": {
            "class_type": "DualCLIPLoader",
            "inputs": {
                "clip_name1": getattr(args, 'flux_clip1', 't5xxl_fp8_e4m3fn.safetensors'),
                "clip_name2": getattr(args, 'flux_clip2', 'clip_l.safetensors'),
                "type": "flux"
            }
        }
    }


def txt2img_sd15(args):
    """Text-to-image workflow for SD 1.5 models."""
    seed = args.seed if args.seed >= 0 else random.randint(0, 2**32 - 1)
    
    return {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": args.steps,
                "cfg": args.cfg,
                "sampler_name": args.sampler,
                "scheduler": args.scheduler,
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            }
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": args.model
            }
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": args.width,
                "height": args.height,
                "batch_size": args.batch
            }
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": args.prompt,
                "clip": ["4", 1]
            }
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": args.negative,
                "clip": ["4", 1]
            }
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            }
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": args.prefix,
                "images": ["8", 0]
            }
        }
    }

MODEL_PRESETS = load_presets()

DEFAULT_NEGATIVE = "bad quality, worst quality, low quality, blurry, deformed, disfigured, mutation, extra limbs, watermark, text, signature"

def main():
    parser = argparse.ArgumentParser(description="Generate images with ComfyUI")
    parser.add_argument("prompt", help="Positive prompt")
    parser.add_argument("--negative", "-n", default=DEFAULT_NEGATIVE, help="Negative prompt")
    parser.add_argument("--model", "-m", default=None, help="Model filename or preset name")
    parser.add_argument("--template", "-t", default=None, choices=["sdxl", "sd15", "flux"], help="Workflow template")
    parser.add_argument("--width", "-W", type=int, default=None, help="Image width")
    parser.add_argument("--height", "-H", type=int, default=None, help="Image height")
    parser.add_argument("--steps", "-s", type=int, default=None, help="Sampling steps")
    parser.add_argument("--cfg", "-c", type=float, default=None, help="CFG scale")
    parser.add_argument("--seed", type=int, default=-1, help="Seed (-1 = random)")
    parser.add_argument("--sampler", default=None, help="Sampler name")
    parser.add_argument("--scheduler", default=None, help="Scheduler")
    parser.add_argument("--batch", "-b", type=int, default=1, help="Batch size")
    parser.add_argument("--output", "-o", default=DEFAULT_OUTPUT, help="Output directory")
    parser.add_argument("--prefix", "-p", default="sentinel", help="Filename prefix")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds")
    parser.add_argument("--list-presets", action="store_true", help="List available presets")
    
    args = parser.parse_args()
    
    if args.list_presets:
        print("Available presets:")
        for name, preset in sorted(MODEL_PRESETS.items()):
            print(f"  {name:20s} → {preset['model']} ({preset['template']}, {preset['width']}x{preset['height']}, {preset['steps']} steps)")
        return
    
    # Apply preset if model matches a preset name
    preset_name = args.model or "dreamshaperXL"
    preset = MODEL_PRESETS.get(preset_name)
    
    if preset:
        # Preset found - apply defaults, but CLI args override
        args.model = args.model if args.model and args.model not in MODEL_PRESETS else preset["model"]
        args.template = args.template or preset["template"]
        args.width = args.width or preset["width"]
        args.height = args.height or preset["height"]
        args.steps = args.steps or preset["steps"]
        args.cfg = args.cfg or preset["cfg"]
        args.sampler = args.sampler or preset["sampler"]
        args.scheduler = args.scheduler or preset["scheduler"]
    else:
        # Direct model filename - use sensible defaults
        args.template = args.template or "sdxl"
        args.width = args.width or 1024
        args.height = args.height or 1024
        args.steps = args.steps or 25
        args.cfg = args.cfg or 7.0
        args.sampler = args.sampler or "euler"
        args.scheduler = args.scheduler or "normal"
    
    # Select workflow template
    if args.template == "flux":
        workflow = txt2img_flux(args)
    elif args.template == "sd15":
        workflow = txt2img_sd15(args)
    else:
        workflow = txt2img_sdxl(args)
    
    # Ensure ComfyUI is running
    ensure_running()
    
    print(f"Model:     {args.model}")
    print(f"Template:  {args.template}")
    print(f"Size:      {args.width}x{args.height}")
    print(f"Steps:     {args.steps}")
    print(f"CFG:       {args.cfg}")
    print(f"Sampler:   {args.sampler} / {args.scheduler}")
    print(f"Prompt:    {args.prompt[:80]}...")
    print(f"Output:    {args.output}")
    print()
    
    start_time = time.time()
    error_msg = None
    paths = []
    
    try:
        paths = generate_and_download(workflow, args.output, timeout=args.timeout)
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ Error: {error_msg}")
    
    duration = time.time() - start_time
    
    # Log generation
    log_generation(
        prompt=args.prompt,
        preset=preset_name,
        model=args.model,
        width=args.width,
        height=args.height,
        steps=args.steps,
        cfg=args.cfg,
        seed=args.seed,
        output_paths=paths,
        duration_s=duration,
        success=error_msg is None,
        error=error_msg
    )
    
    if paths:
        print(f"\n✅ Done! Generated {len(paths)} image(s) in {duration:.1f}s:")
        for p in paths:
            print(f"   {p}")
    
    return paths

if __name__ == "__main__":
    main()
