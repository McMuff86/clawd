---
name: rhinomcp
description: Control Rhino 3D via RhinoMCP plugin. Use when creating, modifying, or deleting 3D geometry (spheres, boxes, cylinders, lines, curves, meshes), managing layers and materials (including PBR), executing RhinoScript, or querying document information. Requires Rhino running on Windows with RhinoMCP plugin started (`tcpstart` command for WSL access).
---

# RhinoMCP Skill

Control Rhino 3D directly from Clawdbot via TCP socket connection to the RhinoMCP plugin.

## Prerequisites

1. **Rhino 7/8** running on Windows
2. **RhinoMCP plugin** installed via Rhino Package Manager
3. **Plugin started**: In Rhino command line, type `tcpstart` (for WSL/remote access)

> **Note:** Use `mcpstart` for local-only access (Cursor, Claude Desktop), `tcpstart` for WSL/Clawdbot.

## Configuration

Edit `config.json` to change connection settings:

```json
{
  "connection": {
    "host": "172.31.96.1",   // Windows host IP from WSL
    "port": 1999,
    "timeout": 15.0
  }
}
```

## Quick Test

```bash
cd ~/clawd/skills/rhinomcp/scripts
python3 rhino_client.py ping
```

---

## 🔍 Log Monitoring (Important!)

**Always monitor the Rhino log file** to see what's happening in real-time.

Log path is in `config.json` under `logging.log_file`.

```bash
# Check recent log entries (after each command or on errors)
tail -30 "/mnt/c/Users/Adi.Muff/AppData/Local/Temp/rhinomcp.log"

# Or start background tail for continuous monitoring during complex operations
tail -f "/mnt/c/Users/Adi.Muff/AppData/Local/Temp/rhinomcp.log" &
```

The log shows:
- `[DEBUG] Executing: <command>` - Which command is running
- `[TRACE] Parameters: {...}` - Exact parameters sent
- `[DEBUG] Command <name> completed` - Success confirmation
- `[ERROR] ...` - Any errors that occurred

**Before debugging issues:** Always check the log first to see what actually happened.

---

## Scripts Overview

| Script | Purpose |
|--------|---------|
| `rhino_client.py` | Base TCP client, raw commands |
| `geometry.py` | Create primitives (box, sphere, cylinder...) |
| `objects.py` | Get info, modify, delete, select objects |
| `layers.py` | Layer management |
| `materials.py` | PBR materials |
| `transforms.py` | Copy, mirror, arrays |
| `booleans.py` | Union, difference, intersection |
| `render.py` | Lights, render settings, render to image |
| `curves.py` | Offset, fillet, chamfer |
| `surfaces.py` | Loft, extrude, revolve |
| `viewport.py` | Views, camera, screenshots |
| `scene.py` | Document info, clear, batch operations |

---

## Geometry Creation

```bash
# Primitives
python3 geometry.py sphere --radius 5 --position 0,0,0 --name "Ball"
python3 geometry.py box --width 10 --length 10 --height 5 --color 255,0,0
python3 geometry.py cylinder --radius 2 --height 8 --layer "Parts"
python3 geometry.py cone --radius 3 --height 6
python3 geometry.py line --start 0,0,0 --end 10,10,0
python3 geometry.py circle --radius 5

# Raw command (any type)
python3 geometry.py raw --type MESH --params '{"vertices": [...], "faces": [...]}'
```

### Supported Types

| Type | Parameters |
|------|------------|
| POINT | location |
| LINE | start, end |
| POLYLINE | points |
| CIRCLE | radius |
| ARC | start_angle, end_angle, radius |
| ELLIPSE | rx, ry |
| CURVE | points, degree |
| BOX | width, length, height |
| SPHERE | radius |
| CONE | radius, height |
| CYLINDER | radius, height |
| SURFACE | points (grid) |
| MESH | vertices, faces |

---

## Object Operations

```bash
# Get object info
python3 objects.py info <object_id>

# Modify object
python3 objects.py modify <object_id> --name "NewName"
python3 objects.py modify <object_id> --layer "OtherLayer"
python3 objects.py modify <object_id> --translate 10,0,0
python3 objects.py modify <object_id> --color 255,0,0
python3 objects.py modify <object_id> --visible false

# Delete object
python3 objects.py delete <object_id>

# Select objects
python3 objects.py select --ids <id1> <id2>
python3 objects.py select --layer "MyLayer"
python3 objects.py select --name "Box*"

# Get selected objects info
python3 objects.py selected
```

---

## Layer Management

```bash
python3 layers.py create "MyLayer" --color 255,100,100
python3 layers.py set "MyLayer"
python3 layers.py list
python3 layers.py delete "OldLayer"
```

---

## Materials (PBR)

```bash
# Preset metals
python3 materials.py preset gold
python3 materials.py preset silver

# Custom PBR
python3 materials.py pbr "Chrome" --color 200,200,210 --metallic 0.95 --roughness 0.02

# Assign to layer
python3 materials.py assign "MyLayer" "material_id"
```

---

## Transform Operations

```bash
# Copy with offset
python3 transforms.py copy <object_id> --offset 10,0,0

# Mirror across YZ plane at origin
python3 transforms.py mirror <object_id> --origin 0,0,0 --normal 1,0,0

# Linear array: 5 copies along X axis
python3 transforms.py linear <object_id> --direction 1,0,0 --count 5 --distance 10

# Polar array: 8 copies around Z axis
python3 transforms.py polar <object_id> --center 0,0,0 --axis 0,0,1 --count 8
```

---

## Boolean Operations

```bash
# Union multiple objects
python3 booleans.py union <id1> <id2> <id3>

# Subtract cutter from base
python3 booleans.py difference <base_id> <cutter_id>

# Intersection
python3 booleans.py intersection <id1> <id2>

# Keep input objects (don't delete)
python3 booleans.py union <id1> <id2> --keep
```

---

## Curve Operations

```bash
# Offset curve
python3 curves.py offset <curve_id> --distance 5

# Fillet between two curves
python3 curves.py fillet <curve1_id> <curve2_id> --radius 2

# Chamfer between two curves
python3 curves.py chamfer <curve1_id> <curve2_id> --distance 3
```

---

## Surface Operations

```bash
# Loft through curves
python3 surfaces.py loft <curve1_id> <curve2_id> <curve3_id>

# Extrude curve
python3 surfaces.py extrude <curve_id> --direction 0,0,10

# Revolve curve around axis
python3 surfaces.py revolve <curve_id> --axis-start 0,0,0 --axis-end 0,0,1 --angle 360
```

---

## Viewport & Camera

```bash
# Set standard view
python3 viewport.py view Perspective
python3 viewport.py view Top

# Zoom to fit all
python3 viewport.py zoom

# Zoom to selection
python3 viewport.py zoom --selected

# Orbit camera
python3 viewport.py orbit --yaw 45 --pitch 30

# Set camera manually
python3 viewport.py camera --position 100,100,50 --target 0,0,0 --lens 35

# Capture screenshot
python3 viewport.py screenshot --output render.png --width 1920 --height 1080

# Render with materials
python3 viewport.py render --output render.png
```

---

## Render & Lighting

```bash
# Set render settings
python3 render.py settings --width 1920 --height 1080 --quality high
python3 render.py settings --background 50,50,50

# Add point light
python3 render.py light point --position 50,50,100 --intensity 1.5 --color 255,255,255

# Add directional light (sun)
python3 render.py light directional --direction -1,-1,-1 --intensity 1.0

# Add spot light
python3 render.py light spot --position 0,0,100 --target 0,0,0 --intensity 2.0

# Set camera
python3 render.py camera --position 100,100,50 --target 0,0,0 --lens 35

# Render to file
python3 render.py render --output scene.png --width 1920 --height 1080
```

---

## Scene Operations

```bash
# Get document info
python3 scene.py info

# Clear all objects
python3 scene.py clear

# Select all
python3 scene.py select-all

# Select by layer
python3 scene.py select-layer "MyLayer"

# Get selected objects info
python3 scene.py selected

# Batch create from JSON
python3 scene.py batch --json '[{"type":"SPHERE","params":{"radius":5},"translation":[0,0,0]}]'
```

---

## RhinoScript Execution

```bash
python3 script_exec.py -c "import rhinoscriptsyntax as rs; rs.AddSphere([0,0,0], 10)"
python3 script_exec.py -f ~/scripts/my_rhino_script.py
```

---

## Example Workflow: PBR Scene

```bash
# 1. Create layer
python3 layers.py create "Gold_Parts" --color 255,215,0

# 2. Create PBR material
python3 materials.py pbr "Gold" --color 255,215,0 --metallic 0.95 --roughness 0.05
# → Note material_id from output

# 3. Assign material to layer
python3 materials.py assign "Gold_Parts" "<material_id>"

# 4. Set as current layer
python3 layers.py set "Gold_Parts"

# 5. Create geometry (auto-inherits material)
python3 geometry.py sphere --radius 3 --name "Gold_Ball"

# 6. Set camera and render
python3 viewport.py camera --position 20,20,15 --target 0,0,0
python3 viewport.py render --output gold_scene.png
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection refused | Ensure Rhino is running and `tcpstart` was executed |
| Timeout | Reduce batch size, increase timeout in config.json |
| Unknown command | Check command spelling in RhinoMCP docs |

---

## Notes

- **Batch operations**: Use `create_objects` / `scene.py batch` for >10 items
- **Port**: Default 1999, configurable in config.json
- **Limits**: `get_document_info` returns max 30 objects
- **Screenshots**: Saved to path in config.json `screenshots.output_dir`
