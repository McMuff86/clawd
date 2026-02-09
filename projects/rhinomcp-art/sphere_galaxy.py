#!/usr/bin/env python3
"""
Sphere Galaxy - Kunstwerk mit goldenen und silbernen Kugeln
Eine spiralförmige Anordnung inspiriert von Galaxien und Fibonacci
"""

import sys
sys.path.insert(0, '/home/mcmuff/rhinomcp/scripts/clawdbot')

import math
import json
from rhino_client import RhinoClient

# === KONFIGURATION ===
NUM_SPHERES = 120          # Anzahl Kugeln
SPIRAL_TURNS = 5           # Anzahl Windungen
MAX_RADIUS = 150           # Maximaler Radius der Spirale
HEIGHT_RANGE = 80          # Höhenvariation
BASE_SPHERE_RADIUS = 3     # Basis-Kugelradius
RADIUS_VARIATION = 2       # Variation der Kugelgrösse

# Farben (RGB)
GOLD = [255, 215, 0]
SILVER = [192, 192, 192]

def create_layer(client, name: str, color: list) -> dict:
    """Erstelle Layer mit Farbe."""
    return client.send_command("create_layer", {
        "name": name,
        "color": color
    })

def create_sphere(client, center: list, radius: float, layer: str, name: str = None) -> dict:
    """Erstelle eine Kugel."""
    params = {
        "type": "SPHERE",
        "params": {"radius": radius},
        "translation": center,
        "layer": layer
    }
    if name:
        params["name"] = name
    return client.send_command("create_object", params)

def fibonacci_sphere_positions(n: int, spiral_turns: float, max_radius: float, height_range: float):
    """
    Generiere Positionen in einer Fibonacci-Spirale.
    Goldener Winkel sorgt für gleichmässige Verteilung.
    """
    golden_angle = math.pi * (3 - math.sqrt(5))  # ~137.5°
    positions = []
    
    for i in range(n):
        # Fortschritt 0-1
        t = i / (n - 1) if n > 1 else 0
        
        # Spiralförmiger Radius (wächst nach aussen)
        r = max_radius * math.sqrt(t)
        
        # Winkel mit goldenem Verhältnis
        theta = i * golden_angle * spiral_turns
        
        # Position
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        
        # Höhe: Sinuswelle für organisches Gefühl
        z = height_range * math.sin(t * math.pi * 2) * (1 - t * 0.5)
        
        positions.append((x, y, z, t))
    
    return positions

def calculate_sphere_radius(t: float, base: float, variation: float) -> float:
    """Kugelgrösse variiert - grösser in der Mitte."""
    # Glockenform: grösser in der Mitte der Spirale
    size_factor = math.sin(t * math.pi)
    return base + variation * size_factor

def main():
    print("🌌 Sphere Galaxy - Kunstwerk Generator")
    print("=" * 50)
    
    with RhinoClient() as client:
        # Test Verbindung
        ping = client.send_command("ping")
        if ping.get("status") != "success":
            print("❌ Keine Verbindung zu Rhino!")
            return
        print("✅ Verbunden mit Rhino")
        
        # Layer erstellen
        print("\n📁 Erstelle Layer...")
        create_layer(client, "Gold_Spheres", GOLD)
        create_layer(client, "Silver_Spheres", SILVER)
        
        # Positionen berechnen
        print(f"\n🔢 Berechne {NUM_SPHERES} Positionen...")
        positions = fibonacci_sphere_positions(
            NUM_SPHERES, SPIRAL_TURNS, MAX_RADIUS, HEIGHT_RANGE
        )
        
        # Kugeln erstellen
        print("\n⭐ Erstelle Kugeln...")
        gold_count = 0
        silver_count = 0
        
        for i, (x, y, z, t) in enumerate(positions):
            # Abwechselnd Gold/Silber mit Fibonacci-Pattern
            # Mehr Gold im Zentrum, mehr Silber aussen
            is_gold = (i % 3 != 0) if t < 0.5 else (i % 3 == 0)
            
            layer = "Gold_Spheres" if is_gold else "Silver_Spheres"
            radius = calculate_sphere_radius(t, BASE_SPHERE_RADIUS, RADIUS_VARIATION)
            
            result = create_sphere(
                client,
                center=[x, y, z],
                radius=radius,
                layer=layer,
                name=f"Sphere_{i:03d}"
            )
            
            if is_gold:
                gold_count += 1
            else:
                silver_count += 1
            
            # Fortschritt
            if (i + 1) % 20 == 0:
                print(f"   {i + 1}/{NUM_SPHERES} Kugeln erstellt...")
        
        print(f"\n✨ Fertig!")
        print(f"   🥇 Gold: {gold_count} Kugeln")
        print(f"   🥈 Silber: {silver_count} Kugeln")
        print(f"\n💡 Tipp: In Rhino 'Shade' oder 'Rendered' Ansicht für beste Darstellung")

if __name__ == "__main__":
    main()
