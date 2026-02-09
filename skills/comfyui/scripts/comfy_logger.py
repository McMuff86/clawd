#!/usr/bin/env python3
"""ComfyUI Activity Logger - Loggt alle Aktionen."""

import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from comfy_client import get_config

def get_log_dir():
    cfg = get_config().get("logging", {})
    log_dir = cfg.get("log_dir", "/home/mcmuff/clawd/logs/comfyui")
    os.makedirs(log_dir, exist_ok=True)
    return log_dir

def log_event(event_type, details):
    """Log an event to the daily log file."""
    log_dir = get_log_dir()
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"{today}.jsonl")
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event_type,
        **details
    }
    
    with open(log_file, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    return entry

def log_startup(method, success, duration_s=None, error=None):
    """Log a ComfyUI startup attempt."""
    return log_event("startup", {
        "method": method,
        "success": success,
        "duration_s": duration_s,
        "error": error
    })

def log_generation(prompt, preset, model, width, height, steps, cfg, 
                   seed, output_paths, duration_s, success, error=None):
    """Log an image generation."""
    return log_event("generation", {
        "prompt": prompt[:200],
        "preset": preset,
        "model": model,
        "resolution": f"{width}x{height}",
        "steps": steps,
        "cfg": cfg,
        "seed": seed,
        "output_paths": output_paths,
        "duration_s": round(duration_s, 2),
        "success": success,
        "error": error
    })

def log_workflow(workflow_name, output_paths, duration_s, success, error=None):
    """Log a custom workflow execution."""
    return log_event("workflow", {
        "workflow": workflow_name,
        "output_paths": output_paths,
        "duration_s": round(duration_s, 2),
        "success": success,
        "error": error
    })

def get_stats(days=7):
    """Get generation stats for the last N days."""
    log_dir = get_log_dir()
    total_gens = 0
    total_time = 0
    models_used = {}
    presets_used = {}
    errors = 0
    startups = 0
    
    for filename in sorted(os.listdir(log_dir)):
        if not filename.endswith(".jsonl"):
            continue
        filepath = os.path.join(log_dir, filename)
        with open(filepath) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if entry["event"] == "generation":
                        total_gens += 1
                        total_time += entry.get("duration_s", 0)
                        model = entry.get("model", "unknown")
                        models_used[model] = models_used.get(model, 0) + 1
                        preset = entry.get("preset", "custom")
                        presets_used[preset] = presets_used.get(preset, 0) + 1
                        if not entry.get("success"):
                            errors += 1
                    elif entry["event"] == "startup":
                        startups += 1
                except:
                    pass
    
    return {
        "total_generations": total_gens,
        "total_time_s": round(total_time, 1),
        "avg_time_s": round(total_time / max(total_gens, 1), 1),
        "errors": errors,
        "startups": startups,
        "models_used": dict(sorted(models_used.items(), key=lambda x: -x[1])),
        "presets_used": dict(sorted(presets_used.items(), key=lambda x: -x[1]))
    }

def print_today():
    """Print today's log entries."""
    log_dir = get_log_dir()
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"{today}.jsonl")
    
    if not os.path.exists(log_file):
        print("Keine Einträge heute.")
        return
    
    with open(log_file) as f:
        for line in f:
            entry = json.loads(line)
            ts = entry["timestamp"].split("T")[1][:8]
            event = entry["event"]
            if event == "generation":
                status = "✅" if entry.get("success") else "❌"
                print(f"[{ts}] {status} Generation: {entry.get('preset', '?')} | {entry.get('resolution')} | {entry.get('duration_s', '?')}s | {entry.get('prompt', '')[:60]}")
            elif event == "startup":
                status = "✅" if entry.get("success") else "❌"
                print(f"[{ts}] {status} Startup: {entry.get('method')} ({entry.get('duration_s', '?')}s)")
            elif event == "workflow":
                status = "✅" if entry.get("success") else "❌"
                print(f"[{ts}] {status} Workflow: {entry.get('workflow')} | {entry.get('duration_s', '?')}s")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "today"
    
    if action == "today":
        print_today()
    elif action == "stats":
        stats = get_stats()
        print(json.dumps(stats, indent=2))
    else:
        print("Usage: comfy_logger.py [today|stats]")
