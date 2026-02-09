#!/usr/bin/env python3
"""ComfyUI API Client - Connects to ComfyUI from WSL2."""

import json
import time
import uuid
import urllib.request
import urllib.error
import sys
import os

DEFAULT_HOST = "host.docker.internal"
DEFAULT_PORT = 8188

def get_config():
    """Load config from config.json if available."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
    if os.path.exists(config_path):
        with open(config_path) as f:
            return json.load(f)
    return {}

def get_base_url():
    cfg = get_config().get("connection", {})
    host = cfg.get("host", DEFAULT_HOST)
    port = cfg.get("port", DEFAULT_PORT)
    return f"http://{host}:{port}"

def is_running():
    """Check if ComfyUI is reachable (fast check with short timeout)."""
    try:
        url = f"{get_base_url()}/system_stats"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except:
        return False

def start_comfyui():
    """Start ComfyUI on Windows via cmd.exe."""
    import subprocess
    cfg = get_config().get("startup", {})
    bat_path = cfg.get("bat_path")
    
    if not bat_path:
        raise RuntimeError("No bat_path configured in config.json")
    
    startup_wait = cfg.get("startup_wait", 30)
    max_retries = cfg.get("max_retries", 3)
    
    print(f"Starting ComfyUI: {bat_path}")
    
    # Start bat file on Windows via cmd.exe
    # cwd must be a Windows path to avoid UNC error
    cmd_exe = "/mnt/c/Windows/System32/cmd.exe"
    bat_dir = os.path.dirname(bat_path)
    subprocess.Popen(
        [cmd_exe, "/c", f"cd /d {bat_dir} && start \"\" \"{bat_path}\""],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd="/mnt/c/"
    )
    
    # Wait for ComfyUI to become available
    start_time = time.time()
    for i in range(startup_wait):
        time.sleep(1)
        if is_running():
            duration = time.time() - start_time
            print(f"ComfyUI ready after {duration:.1f}s")
            return True, duration
        if (i + 1) % 5 == 0:
            print(f"  Waiting... ({i+1}s)")
    
    return False, time.time() - start_time

def ensure_running():
    """Ensure ComfyUI is running, start if needed."""
    if is_running():
        return True
    
    print("ComfyUI not reachable. Attempting auto-start...")
    
    try:
        from comfy_logger import log_startup
    except ImportError:
        log_startup = None
    
    success, duration = start_comfyui()
    
    if log_startup:
        log_startup("auto-start", success, duration_s=duration,
                    error=None if success else "Timeout waiting for ComfyUI")
    
    if not success:
        raise RuntimeError(f"ComfyUI did not start within timeout. "
                          f"Please start manually with --listen 0.0.0.0")
    
    return True

def api_get(endpoint):
    """GET request to ComfyUI API."""
    url = f"{get_base_url()}{endpoint}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())

def api_post(endpoint, data):
    """POST request to ComfyUI API."""
    url = f"{get_base_url()}{endpoint}"
    payload = json.dumps(data).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())

def api_get_binary(endpoint):
    """GET request returning binary data."""
    url = f"{get_base_url()}{endpoint}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()

def system_stats():
    """Get ComfyUI system stats."""
    return api_get("/system_stats")

def get_queue():
    """Get current queue status."""
    return api_get("/queue")

def get_history(prompt_id=None):
    """Get generation history."""
    if prompt_id:
        return api_get(f"/history/{prompt_id}")
    return api_get("/history")

def queue_prompt(workflow, client_id=None):
    """Queue a workflow for execution."""
    if client_id is None:
        client_id = str(uuid.uuid4())
    payload = {
        "prompt": workflow,
        "client_id": client_id
    }
    return api_post("/prompt", payload)

def wait_for_completion(prompt_id, timeout=300, poll_interval=2):
    """Poll until a prompt is completed."""
    start = time.time()
    while time.time() - start < timeout:
        history = get_history(prompt_id)
        if prompt_id in history:
            entry = history[prompt_id]
            if entry.get("status", {}).get("completed", False) or "outputs" in entry:
                return entry
            status_msg = entry.get("status", {}).get("status_str", "")
            if "error" in status_msg.lower():
                return entry
        time.sleep(poll_interval)
    raise TimeoutError(f"Prompt {prompt_id} did not complete within {timeout}s")

def download_image(filename, subfolder="", folder_type="output"):
    """Download a generated image from ComfyUI."""
    params = f"?filename={filename}&subfolder={subfolder}&type={folder_type}"
    return api_get_binary(f"/view{params}")

def get_output_images(history_entry):
    """Extract output image info from a history entry."""
    images = []
    outputs = history_entry.get("outputs", {})
    for node_id, node_output in outputs.items():
        if "images" in node_output:
            for img in node_output["images"]:
                images.append({
                    "filename": img["filename"],
                    "subfolder": img.get("subfolder", ""),
                    "type": img.get("type", "output"),
                    "node_id": node_id
                })
    return images

def generate_and_download(workflow, output_dir, timeout=300):
    """Queue a workflow, wait for completion, download results."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Queue
    result = queue_prompt(workflow)
    prompt_id = result["prompt_id"]
    print(f"Queued: {prompt_id}")
    
    # Wait
    print("Waiting for completion...")
    history = wait_for_completion(prompt_id, timeout=timeout)
    
    # Check for errors
    status = history.get("status", {})
    if status.get("status_str") == "error":
        msgs = status.get("messages", [])
        raise RuntimeError(f"Generation failed: {msgs}")
    
    # Download images
    images = get_output_images(history)
    downloaded = []
    for img in images:
        data = download_image(img["filename"], img["subfolder"], img["type"])
        local_path = os.path.join(output_dir, img["filename"])
        with open(local_path, "wb") as f:
            f.write(data)
        downloaded.append(local_path)
        print(f"Saved: {local_path}")
    
    return downloaded


def upload_image(image_path, subfolder="", overwrite=True):
    """Upload an image to ComfyUI's input directory.

    Args:
        image_path: Local path to the image file.
        subfolder: Optional subfolder within ComfyUI's input dir.
        overwrite: Whether to overwrite if file exists.

    Returns:
        The filename as stored by ComfyUI (use this in LoadImage nodes).
    """
    import mimetypes

    url = f"{get_base_url()}/upload/image"
    filename = os.path.basename(image_path)
    mime_type = mimetypes.guess_type(image_path)[0] or "image/png"

    # Build multipart/form-data manually (no requests dependency)
    boundary = f"----ComfyUpload{uuid.uuid4().hex}"

    body_parts = []

    # image field
    body_parts.append(f"--{boundary}\r\n".encode())
    body_parts.append(
        f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'.encode()
    )
    body_parts.append(f"Content-Type: {mime_type}\r\n\r\n".encode())
    with open(image_path, "rb") as f:
        body_parts.append(f.read())
    body_parts.append(b"\r\n")

    # overwrite field
    body_parts.append(f"--{boundary}\r\n".encode())
    body_parts.append(b'Content-Disposition: form-data; name="overwrite"\r\n\r\n')
    body_parts.append(b"true\r\n" if overwrite else b"false\r\n")

    # subfolder field (if provided)
    if subfolder:
        body_parts.append(f"--{boundary}\r\n".encode())
        body_parts.append(b'Content-Disposition: form-data; name="subfolder"\r\n\r\n')
        body_parts.append(f"{subfolder}\r\n".encode())

    body_parts.append(f"--{boundary}--\r\n".encode())

    body = b"".join(body_parts)

    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode())

    # ComfyUI returns {"name": "filename.png", "subfolder": "", "type": "input"}
    return result.get("name", filename)


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if action == "status":
        stats = system_stats()
        print(json.dumps(stats, indent=2))
    
    elif action == "queue":
        q = get_queue()
        running = len(q.get("queue_running", []))
        pending = len(q.get("queue_pending", []))
        print(f"Running: {running}, Pending: {pending}")
    
    elif action == "generate":
        if len(sys.argv) < 3:
            print("Usage: comfy_client.py generate <workflow.json> [output_dir]")
            sys.exit(1)
        workflow_path = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) > 3 else "/home/mcmuff/clawd/output/comfyui"
        
        with open(workflow_path) as f:
            workflow = json.load(f)
        
        paths = generate_and_download(workflow, output_dir)
        print(f"\nGenerated {len(paths)} image(s)")
    
    else:
        print(f"Unknown action: {action}")
        print("Usage: comfy_client.py [status|queue|generate]")
        sys.exit(1)
