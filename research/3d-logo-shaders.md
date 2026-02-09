# 3D Logo mit Shadern auf einer Webseite rendern

> **Recherche-Datum:** 08.02.2026  
> **Kontext:** LocAI Startseite – 3D-Logo mit Shader-Effekten  
> **Tech-Stack:** React / Vite (angenommen)

---

## Inhaltsverzeichnis

1. [Technologie-Optionen im Vergleich](#1-technologie-optionen-im-vergleich)
2. [Shader-Techniken für Logos](#2-shader-techniken-für-logos)
3. [Workflow: 3D Logo → Web](#3-workflow-3d-logo--web)
4. [Performance & Best Practices](#4-performance--best-practices)
5. [Konkrete Code-Beispiele](#5-konkrete-code-beispiele)
6. [Inspiration & Ressourcen](#6-inspiration--ressourcen)
7. [Empfehlung für LocAI](#7-empfehlung-für-locai)

---

## 1. Technologie-Optionen im Vergleich

### Three.js + React Three Fiber (R3F) ⭐ Empfohlen

| Aspekt | Bewertung |
|--------|-----------|
| **Kontrolle** | Volle Kontrolle über Shader, Geometrie, Post-Processing |
| **React-Integration** | Nahtlos via `@react-three/fiber` (R3F) |
| **Ökosystem** | Riesig: `@react-three/drei`, `@react-three/postprocessing`, `three-custom-shader-material` |
| **Lernkurve** | Mittel – Three.js Basics + GLSL lernen |
| **Performance** | Sehr gut, volle WebGL-Kontrolle |
| **Community** | Grösste Community, beste Docs |

**Kernpakete:**
```bash
npm install three @react-three/fiber @react-three/drei @react-three/postprocessing
```

### Babylon.js

| Aspekt | Bewertung |
|--------|-----------|
| **Kontrolle** | Gleichwertig zu Three.js |
| **React-Integration** | `react-babylonjs` existiert, aber deutlich kleiner als R3F |
| **Ökosystem** | Gut, aber weniger Shader-Community |
| **Lernkurve** | Mittel-Hoch |
| **Performance** | Vergleichbar mit Three.js |
| **Best für** | Game-artige Anwendungen, PBR-heavy Szenen |

**Fazit:** Babylon.js ist mächtiger für komplexe 3D-Szenen/Games, aber für ein einzelnes 3D-Logo auf einer Landing Page ist Three.js/R3F der bessere Fit wegen des Ökosystems.

### Spline (No-Code / Low-Code)

| Aspekt | Bewertung |
|--------|-----------|
| **Kontrolle** | Limitiert – visueller Editor, keine Custom Shaders |
| **React-Integration** | `@splinetool/react-spline` – einfachstes Setup |
| **Ökosystem** | Closed Source, proprietär |
| **Lernkurve** | Sehr niedrig |
| **Performance** | Mittel – generierter Code ist nicht optimal |
| **Best für** | Prototyping, schnelle visuelle 3D-Objekte ohne Shader-Customization |

**React-Einbindung:**
```jsx
import Spline from '@splinetool/react-spline';

function Logo3D() {
  return <Spline scene="https://prod.spline.design/xxx/scene.splinecode" />;
}
```

**Fazit:** Spline ist super zum Prototypen, aber für Custom-Shader-Effekte (Hologramm, Glow, etc.) viel zu limitiert. Man kann allerdings in Spline modellieren und als GLTF exportieren, um es dann in Three.js mit eigenen Shadern zu verwenden.

### CSS 3D Transforms

- Nur für einfache Rotationen/Perspektive
- Keine echten Shader, keine Beleuchtung, kein echtes 3D
- **Nicht geeignet** für ein 3D-Logo mit Shader-Effekten

### Direkt WebGL / GLSL

- Maximale Kontrolle, aber extrem viel Boilerplate
- Für ein Landing-Page-Logo völlig übertrieben
- Three.js ist die richtige Abstraktionsebene

---

## 2. Shader-Techniken für Logos

### 2.1 Vertex Shader – Geometrie-Deformation

Vertex Shader laufen einmal pro Vertex und bestimmen dessen Position. Damit lässt sich die Form des Logos animieren:

**Wave / Wobble:**
```glsl
void main() {
  vec4 modelPosition = modelMatrix * vec4(position, 1.0);
  // Sinuswelle entlang X-Achse
  modelPosition.y += sin(modelPosition.x * 4.0 + u_time) * 0.1;
  vec4 viewPosition = viewMatrix * modelPosition;
  gl_Position = projectionMatrix * viewPosition;
}
```

**Morphing / Breathing:**
```glsl
void main() {
  vec3 pos = position;
  // "Atmen"-Effekt: Vertices pulsieren nach aussen
  float scale = 1.0 + sin(u_time * 2.0) * 0.05;
  pos *= scale;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
}
```

**Noise-basierte Deformation:**
```glsl
// Mit Simplex/Perlin Noise organische Deformation
void main() {
  vec3 pos = position;
  float noise = snoise(pos * 2.0 + u_time * 0.5);
  pos += normal * noise * 0.1;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
}
```

### 2.2 Fragment Shader – Materialien

Fragment Shader bestimmen die Farbe jedes Pixels:

**Fresnel / Rim Light** (der wichtigste Effekt für 3D-Logos):
```glsl
uniform vec3 rimColor;
uniform float rimPower;    // 2.0-5.0 typisch
uniform float rimIntensity; // 0.5-2.0 typisch

varying vec3 vNormal;
varying vec3 vViewPosition;

void main() {
  vec3 normal = normalize(vNormal);
  vec3 viewDir = normalize(vViewPosition);
  
  // Fresnel-Effekt: Kanten leuchten
  float rim = 1.0 - max(0.0, dot(normal, viewDir));
  rim = pow(rim, rimPower) * rimIntensity;
  
  vec3 baseColor = vec3(0.05, 0.05, 0.1);
  vec3 finalColor = baseColor + rimColor * rim;
  
  gl_FragColor = vec4(finalColor, 1.0);
}
```

**Hologramm-Effekt:**
```glsl
uniform float u_time;
uniform vec3 hologramColor;   // z.B. #00d5ff
uniform float scanlineSize;    // 8.0
uniform float signalSpeed;     // 0.45
uniform float fresnelAmount;   // 0.45

varying vec3 vNormal;
varying vec3 vViewPosition;
varying vec3 vWorldPosition;

void main() {
  vec3 normal = normalize(vNormal);
  vec3 viewDir = normalize(vViewPosition);
  
  // Fresnel
  float fresnel = pow(1.0 - dot(normal, viewDir), 3.0) * fresnelAmount;
  
  // Scanlines
  float scanline = sin(vWorldPosition.y * scanlineSize + u_time * signalSpeed) * 0.5 + 0.5;
  scanline = pow(scanline, 1.6);
  
  // Signal flicker
  float flicker = sin(u_time * 20.0) * 0.05 + 0.95;
  
  vec3 color = hologramColor * (fresnel + scanline * 0.3) * flicker;
  float alpha = fresnel + scanline * 0.3;
  
  gl_FragColor = vec4(color, alpha);
}
```

**Gradient / Iridescent:**
```glsl
uniform float u_time;
varying vec3 vNormal;
varying vec3 vViewPosition;
varying vec2 vUv;

void main() {
  vec3 viewDir = normalize(vViewPosition);
  vec3 normal = normalize(vNormal);
  float fresnel = pow(1.0 - dot(normal, viewDir), 2.0);
  
  // Schillernde Farben basierend auf Blickwinkel
  vec3 color1 = vec3(0.1, 0.3, 0.8);  // Blau
  vec3 color2 = vec3(0.8, 0.1, 0.6);  // Pink
  vec3 color3 = vec3(0.1, 0.8, 0.5);  // Grün
  
  float t = fresnel + sin(u_time * 0.5) * 0.2;
  vec3 color = mix(mix(color1, color2, t), color3, fresnel);
  
  gl_FragColor = vec4(color, 1.0);
}
```

### 2.3 Post-Processing Effekte

Post-Processing wird nach dem Rendern auf das gesamte Bild angewandt:

| Effekt | Beschreibung | Impact |
|--------|-------------|--------|
| **Bloom** | Überstrahlungseffekt, lässt helle Bereiche glühen | ⭐ Must-Have für Glow-Effekte |
| **Chromatic Aberration** | Farbverschiebung an den Rändern | Subtiler Sci-Fi Look |
| **Vignette** | Abdunkelung der Ecken | Fokus auf Mitte |
| **Noise/Film Grain** | Subtiles Bildrauschen | Organischer Look |
| **SSAO** | Ambient Occlusion in Echtzeit | Tiefe, aber performance-heavy |

### 2.4 Noise-basierte Effekte

**Perlin Noise** und **Simplex Noise** sind die Grundlage für organische, nicht-repetitive Animationen:

- Fluid-artige Oberflächen
- Plasma/Energie-Effekte
- Terrain-ähnliche Deformationen
- Wolken/Nebel-Texturen

Libraries zum Einbinden:
- [glsl-noise](https://github.com/ashima/webgl-noise) – GLSL Noise-Funktionen (Snippet einfügen)
- [lygia](https://github.com/patriciogonzalezvivo/lygia) – Umfangreiche GLSL Shader Library

---

## 3. Workflow: 3D Logo → Web

### Option A: Modellieren in Blender/Rhino → Export als GLTF/GLB ⭐

**Der sauberste Workflow:**

1. **Modellieren** in Blender (oder Rhino/Grasshopper)
2. **Optimieren** – Low-Poly halten, nur nötige Geometrie
3. **Export** als `.glb` (binär, kleiner als `.gltf`)
   - In Blender: `File → Export → glTF 2.0`
   - "Custom Properties", "Cameras", "Punctual Lights" deaktivieren
   - `.glb` Format wählen (alles in einer Datei)
4. **Komprimieren** mit [gltf-transform](https://gltf-transform.donmccurdy.com/) oder Draco
5. **In React laden** mit `useGLTF` von drei:

```jsx
import { useGLTF } from '@react-three/drei'

function Logo({ ...props }) {
  const { nodes, materials } = useGLTF('/locai-logo.glb')
  return (
    <mesh 
      geometry={nodes.Logo.geometry} 
      {...props}
    >
      {/* Eigenes Shader-Material statt importiertem Material */}
      <shaderMaterial
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms}
        transparent
      />
    </mesh>
  )
}

useGLTF.preload('/locai-logo.glb')
```

6. **Automatisch als React-Komponente:** Tool [gltfjsx](https://gltf.pmnd.rs/) konvertiert `.glb` direkt in eine React-Komponente.

**Aus Rhino/Grasshopper:**
- Export als `.obj` oder `.3dm` → Blender Import → `.glb` Export
- Oder direkt als `.gltf` via Rhino 7+ Plugin
- Vorteil: Grasshopper kann parametrische Logo-Varianten generieren

### Option B: SVG → 3D Extrusion im Browser

**Ideal wenn das Logo als SVG vorliegt:**

```jsx
import { useLoader } from '@react-three/fiber'
import { SVGLoader } from 'three/examples/jsm/loaders/SVGLoader'
import * as THREE from 'three'
import { useMemo } from 'react'

function ExtrudedLogo() {
  const svgData = useLoader(SVGLoader, '/locai-logo.svg')
  
  const shapes = useMemo(() => {
    return svgData.paths.flatMap(path => path.toShapes(true))
  }, [svgData])

  return (
    <mesh scale={0.01} rotation={[Math.PI, 0, 0]}>
      <extrudeGeometry 
        args={[shapes, { 
          depth: 20,           // Extrusionstiefe
          bevelEnabled: true,
          bevelThickness: 2,
          bevelSize: 1,
          bevelSegments: 3
        }]} 
      />
      <shaderMaterial
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms}
      />
    </mesh>
  )
}
```

**Vorteile:** Kein 3D-Tool nötig, Logo direkt aus SVG  
**Nachteile:** Komplexe SVGs können Probleme machen, weniger Kontrolle über Geometrie

### Option C: Prozedural in Three.js generieren

Für simple geometrische Logos (Text, einfache Formen):

```jsx
import { Text3D, Center } from '@react-three/drei'

function ProceduralLogo() {
  return (
    <Center>
      <Text3D
        font="/fonts/inter-bold.json"
        size={1.5}
        height={0.3}
        bevelEnabled
        bevelThickness={0.05}
        bevelSize={0.02}
      >
        LocAI
        <shaderMaterial
          vertexShader={vertexShader}
          fragmentShader={fragmentShader}
          uniforms={uniforms}
          transparent
        />
      </Text3D>
    </Center>
  )
}
```

### Vergleich der Workflows

| Kriterium | Blender → GLB | SVG → Extrude | Prozedural |
|-----------|---------------|---------------|------------|
| **Kontrolle Geometrie** | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| **Setup-Aufwand** | Mittel | Niedrig | Niedrig |
| **Komplexe Formen** | ✅ | ⚠️ limitiert | ❌ |
| **Dateigrösse** | Klein (GLB) | Sehr klein | Null |
| **Änderbarkeit** | Blender nötig | SVG editieren | Code ändern |

---

## 4. Performance & Best Practices

### 4.1 Geometrie optimieren

- **Low-Poly** – Ein Logo braucht keine 100k Vertices. 1-5k reichen meist.
- **Draco Compression** – Reduziert GLB-Dateigrösse um 80-90%:
  ```bash
  npx gltf-transform draco input.glb output.glb
  ```
- **Merge Meshes** – Wenn möglich alle Logo-Teile in ein Mesh zusammenfassen (weniger Draw Calls)
- **BufferGeometry** verwenden (Three.js Standard seit v125+)

### 4.2 Shader-Performance

- **Shader-Komplexität minimieren** – Einfache Formeln bevorzugen
- **Branching vermeiden** – `if/else` in Shadern ist teuer; `step()`, `smoothstep()`, `mix()` verwenden
- **Textur-Lookups** reduzieren – Prozeduale Effekte sind oft schneller
- **Uniforms statt Attribute** wo möglich
- **Precision Qualifiers**: `mediump` für Mobile, `highp` nur wenn nötig

### 4.3 Rendering

- **Pixel Ratio limitieren:**
  ```jsx
  <Canvas dpr={[1, 2]}> {/* Max 2x, nicht das native DPR */}
  ```
- **PerformanceMonitor** aus drei:
  ```jsx
  import { PerformanceMonitor } from '@react-three/drei'
  
  <PerformanceMonitor onDecline={() => setDpr(1)}>
    {/* Scene */}
  </PerformanceMonitor>
  ```
- **frameloop="demand"** wenn keine kontinuierliche Animation nötig
- **Post-Processing sparsam** – Bloom ist ok, aber jeder zusätzliche Pass kostet

### 4.4 Laden & Anzeigen

- **Suspense & Lazy Loading:**
  ```jsx
  import { Suspense, lazy } from 'react'
  
  const Logo3D = lazy(() => import('./Logo3D'))
  
  function Hero() {
    return (
      <Suspense fallback={<LogoFallback2D />}>
        <Canvas>
          <Logo3D />
        </Canvas>
      </Suspense>
    )
  }
  ```

- **Intersection Observer** – Canvas erst rendern wenn sichtbar:
  ```jsx
  import { useInView } from 'react-intersection-observer'
  
  function HeroSection() {
    const { ref, inView } = useInView({ triggerOnce: true })
    
    return (
      <div ref={ref}>
        {inView && (
          <Canvas>
            <Logo3D />
          </Canvas>
        )}
      </div>
    )
  }
  ```

- **Preloading:**
  ```jsx
  useGLTF.preload('/locai-logo.glb')
  ```

### 4.5 Mobile & Fallback

- **Feature Detection:**
  ```jsx
  function HeroSection() {
    const supportsWebGL = useMemo(() => {
      try {
        const canvas = document.createElement('canvas')
        return !!(canvas.getContext('webgl2') || canvas.getContext('webgl'))
      } catch { return false }
    }, [])
    
    if (!supportsWebGL) return <Logo2DFallback />
    return <Canvas><Logo3D /></Canvas>
  }
  ```

- **Adaptive Quality:** Weniger Shader-Komplexität auf Mobile
- **Canvas-Grösse reduzieren** auf Mobile (kleiner = schneller)

### 4.6 OffscreenCanvas / Web Worker

Für maximale Performance kann Three.js in einem Web Worker laufen:
- Library: [offscreen-canvas](https://github.com/nicholasmckinney/offscreen-canvas)
- Vorteil: Main Thread bleibt frei für UI-Interaktionen
- Nachteil: Mehr Setup-Komplexität

---

## 5. Konkrete Code-Beispiele

### 5.1 Komplettes R3F Setup mit Custom Shader Material

```jsx
// Logo3DScene.jsx
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, Environment, useGLTF } from '@react-three/drei'
import { EffectComposer, Bloom } from '@react-three/postprocessing'
import { useRef, useMemo } from 'react'
import * as THREE from 'three'

// Vertex Shader
const vertexShader = /* glsl */`
  uniform float u_time;
  varying vec3 vNormal;
  varying vec3 vViewPosition;
  varying vec2 vUv;
  varying vec3 vWorldPosition;

  void main() {
    vUv = uv;
    vNormal = normalize(normalMatrix * normal);
    
    vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
    vViewPosition = -mvPosition.xyz;
    
    vec4 worldPos = modelMatrix * vec4(position, 1.0);
    vWorldPosition = worldPos.xyz;
    
    gl_Position = projectionMatrix * mvPosition;
  }
`

// Fragment Shader – Hologramm/Glow Effekt
const fragmentShader = /* glsl */`
  uniform float u_time;
  uniform vec3 u_color;
  uniform vec3 u_rimColor;
  uniform float u_rimPower;
  uniform vec2 u_mouse;

  varying vec3 vNormal;
  varying vec3 vViewPosition;
  varying vec2 vUv;
  varying vec3 vWorldPosition;

  void main() {
    vec3 normal = normalize(vNormal);
    vec3 viewDir = normalize(vViewPosition);
    
    // Fresnel / Rim Light
    float fresnel = pow(1.0 - max(0.0, dot(normal, viewDir)), u_rimPower);
    
    // Scanlines
    float scanline = sin(vWorldPosition.y * 30.0 + u_time * 2.0) * 0.5 + 0.5;
    scanline = smoothstep(0.4, 0.6, scanline);
    
    // Noise-artiger Shimmer
    float shimmer = sin(vWorldPosition.x * 50.0 + u_time * 3.0) 
                  * sin(vWorldPosition.z * 50.0 + u_time * 2.0);
    shimmer = shimmer * 0.05;
    
    // Zusammensetzen
    vec3 baseColor = u_color;
    vec3 rimGlow = u_rimColor * fresnel * 2.0;
    vec3 scanColor = u_rimColor * scanline * 0.15;
    
    vec3 finalColor = baseColor + rimGlow + scanColor + shimmer;
    float alpha = 0.85 + fresnel * 0.15;
    
    gl_FragColor = vec4(finalColor, alpha);
  }
`

function Logo({ url = '/locai-logo.glb' }) {
  const meshRef = useRef()
  const { nodes } = useGLTF(url)
  
  const uniforms = useMemo(() => ({
    u_time: { value: 0 },
    u_color: { value: new THREE.Color('#0a0a2e') },
    u_rimColor: { value: new THREE.Color('#00d4ff') },
    u_rimPower: { value: 3.0 },
    u_mouse: { value: new THREE.Vector2(0, 0) },
  }), [])

  useFrame(({ clock, pointer }) => {
    if (meshRef.current) {
      meshRef.current.material.uniforms.u_time.value = clock.elapsedTime
      meshRef.current.material.uniforms.u_mouse.value.set(pointer.x, pointer.y)
      // Sanfte Rotation
      meshRef.current.rotation.y = Math.sin(clock.elapsedTime * 0.3) * 0.1
    }
  })

  return (
    <mesh ref={meshRef} geometry={nodes.Logo.geometry}>
      <shaderMaterial
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms}
        transparent
        side={THREE.DoubleSide}
      />
    </mesh>
  )
}

// Hauptszene
export default function Logo3DScene() {
  return (
    <div style={{ width: '100%', height: '100vh' }}>
      <Canvas
        dpr={[1, 2]}
        camera={{ position: [0, 0, 5], fov: 45 }}
        gl={{ antialias: true, alpha: true }}
      >
        <color attach="background" args={['#000000']} />
        
        <ambientLight intensity={0.2} />
        <pointLight position={[10, 10, 10]} intensity={0.5} />
        
        <Logo />
        
        <OrbitControls 
          enableZoom={false} 
          enablePan={false}
          autoRotate 
          autoRotateSpeed={0.5}
        />
        
        {/* Post-Processing */}
        <EffectComposer>
          <Bloom 
            luminanceThreshold={0.2}
            luminanceSmoothing={0.9}
            intensity={1.5}
          />
        </EffectComposer>
      </Canvas>
    </div>
  )
}

useGLTF.preload('/locai-logo.glb')
```

### 5.2 Drei's `shaderMaterial` Helper (einfacher)

```jsx
import { shaderMaterial } from '@react-three/drei'
import { extend, useFrame } from '@react-three/fiber'
import { useRef } from 'react'
import * as THREE from 'three'

// Material definieren mit Defaults + Shadern
const HologramMaterial = shaderMaterial(
  // Uniforms mit Defaults
  {
    u_time: 0,
    u_color: new THREE.Color('#00d4ff'),
    u_opacity: 0.85,
  },
  // Vertex Shader
  /* glsl */`
    varying vec3 vNormal;
    varying vec3 vViewPosition;
    varying vec3 vWorldPosition;
    
    void main() {
      vNormal = normalize(normalMatrix * normal);
      vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
      vViewPosition = -mvPosition.xyz;
      vWorldPosition = (modelMatrix * vec4(position, 1.0)).xyz;
      gl_Position = projectionMatrix * mvPosition;
    }
  `,
  // Fragment Shader
  /* glsl */`
    uniform float u_time;
    uniform vec3 u_color;
    uniform float u_opacity;
    
    varying vec3 vNormal;
    varying vec3 vViewPosition;
    varying vec3 vWorldPosition;
    
    void main() {
      vec3 normal = normalize(vNormal);
      vec3 viewDir = normalize(vViewPosition);
      float fresnel = pow(1.0 - max(0.0, dot(normal, viewDir)), 3.0);
      
      float scanline = sin(vWorldPosition.y * 20.0 + u_time * 2.0) * 0.5 + 0.5;
      
      vec3 color = u_color * (fresnel + scanline * 0.2);
      gl_FragColor = vec4(color, u_opacity * (fresnel + 0.3));
    }
  `
)

// Als JSX-Element registrieren
extend({ HologramMaterial })

// Verwendung
function Logo() {
  const matRef = useRef()
  
  useFrame(({ clock }) => {
    matRef.current.u_time = clock.elapsedTime
  })
  
  return (
    <mesh>
      <torusKnotGeometry args={[1, 0.3, 128, 32]} />
      <hologramMaterial ref={matRef} transparent side={THREE.DoubleSide} />
    </mesh>
  )
}
```

### 5.3 Custom Shader Material (CSM) – Extending Standard Materials

```jsx
// three-custom-shader-material lässt dich Standard-Materialien erweitern
// → Behalte PBR-Lighting + füge eigene Effekte hinzu!

import CustomShaderMaterial from 'three-custom-shader-material/vanilla'
import * as THREE from 'three'

const material = new CustomShaderMaterial({
  baseMaterial: THREE.MeshPhysicalMaterial,
  
  vertexShader: /* glsl */`
    varying vec3 vWorldNormal;
    void main() {
      vWorldNormal = normalize(normalMatrix * normal);
    }
  `,
  
  fragmentShader: /* glsl */`
    uniform float u_time;
    varying vec3 vWorldNormal;
    
    void main() {
      float fresnel = pow(1.0 - dot(vWorldNormal, vec3(0.0, 0.0, 1.0)), 3.0);
      vec3 glow = vec3(0.0, 0.8, 1.0) * fresnel;
      csm_FragColor = vec4(glow, 1.0);  // CSM-spezifische Output-Variable
    }
  `,
  
  uniforms: {
    u_time: { value: 0 },
  },
  
  // Standard MeshPhysicalMaterial Props funktionieren weiterhin:
  metalness: 0.8,
  roughness: 0.2,
  transmission: 0.5,
  thickness: 1.0,
})
```

### 5.4 Holographic Material (Fertige Lösung)

Von [Anderson Mancini](https://github.com/ektogamat/threejs-vanilla-holographic-material):

```jsx
import HolographicMaterial from './HolographicMaterialVanilla.js'

const material = new HolographicMaterial({
  fresnelAmount: 0.45,
  fresnelOpacity: 1.0,
  scanlineSize: 8.0,
  hologramBrightness: 1.2,
  signalSpeed: 0.45,
  hologramColor: '#00d5ff',
  enableBlinking: true,
  hologramOpacity: 1.0,
  enableAdditive: true,
})

// Im Render-Loop:
holographicMaterial.update()  // Time-Uniform updaten
```

→ GitHub: https://github.com/ektogamat/threejs-vanilla-holographic-material  
→ Demo: https://threejs-vanilla-holographic-material.vercel.app/

### 5.5 MeshTransmissionMaterial (Glass/Crystal Effekt)

Aus `@react-three/drei` – erzeugt Glas/Kristall-Effekte:

```jsx
import { MeshTransmissionMaterial } from '@react-three/drei'

function GlassLogo() {
  return (
    <mesh geometry={logoGeometry}>
      <MeshTransmissionMaterial
        transmission={1}
        thickness={0.5}
        roughness={0}
        chromaticAberration={0.03}
        anisotropicBlur={0.1}
        distortion={0.5}
        distortionScale={0.5}
        temporalDistortion={0.1}
        ior={1.5}
        color="#ffffff"
      />
    </mesh>
  )
}
```

---

## 6. Inspiration & Ressourcen

### 6.1 Websites mit beeindruckenden 3D-Logos/Elementen

| Website | Technik | Link |
|---------|---------|------|
| **Lusion** | Three.js, Custom Shaders, WebGL | [lusion.co](https://lusion.co) |
| **Active Theory** | Three.js, Custom WebGL Engine | [activetheory.net](https://activetheory.net) |
| **Awwwards WebGL Collection** | Kuratierte Sammlung | [awwwards.com/webgl](https://www.awwwards.com/awwwards/collections/webgl/) |
| **Bruno Simon** | Three.js Portfolio | [bruno-simon.com](https://bruno-simon.com) |
| **David Hckh** | R3F + Postprocessing | [davidhckh.com](https://davidhckh.com) |

### 6.2 Shader-Playgrounds & Tools

| Tool | Beschreibung | Link |
|------|-------------|------|
| **Shadertoy** | GLSL Shader Editor im Browser | [shadertoy.com](https://www.shadertoy.com) |
| **GLSL Editor** | Live GLSL Preview | [editor.thebookofshaders.com](https://editor.thebookofshaders.com) |
| **gltf.pmnd.rs** | GLTF → React Komponente | [gltf.pmnd.rs](https://gltf.pmnd.rs) |
| **threejsresources.com** | SVG → 3D Converter + Resources | [threejsresources.com](https://threejsresources.com/3d-logo-generator) |

### 6.3 Lern-Ressourcen

**Must-Read:**
- 📖 [The Book of Shaders](https://thebookofshaders.com) – GLSL Grundlagen (Patricio Gonzalez Vivo)
- 📝 [Maxime Heckel: Study of Shaders with R3F](https://blog.maximeheckel.com/posts/the-study-of-shaders-with-react-three-fiber/) – Bester R3F Shader Guide
- 📝 [Three.js Journey: Hologram Shader](https://threejs-journey.com/lessons/hologram-shader) – Hologramm-Effekt Schritt für Schritt

**Tutorials:**
- 🎥 [Three.js Journey](https://threejs-journey.com) – Umfassendster Three.js Kurs (kostenpflichtig, aber exzellent)
- 🎥 [Wawa Sensei: R3F Post Processing](https://wawasensei.dev/courses/react-three-fiber/lessons/post-processing)
- 📝 [Codrops: Shader Background Effect mit R3F](https://tympanus.net/codrops/2024/10/31/how-to-code-a-subtle-shader-background-effect-with-react-three-fiber/)
- 📝 [Codrops: Shader Reveal Effect](https://tympanus.net/codrops/2024/12/02/how-to-code-a-shader-based-reveal-effect-with-react-three-fiber-glsl/)
- 📝 [LogRocket: SVGs to Three.js](https://blog.logrocket.com/bringing-svgs-three-js-svgloader/)

### 6.4 Bibliotheken & Pakete

| Paket | Beschreibung |
|-------|-------------|
| `@react-three/fiber` | React Renderer für Three.js |
| `@react-three/drei` | Nützliche Helpers (Environment, Controls, Text3D, etc.) |
| `@react-three/postprocessing` | Post-Processing Effekte (Bloom, etc.) |
| `three-custom-shader-material` | Standard-Materialien mit eigenen Shadern erweitern |
| `lamina` (pmndrs) | Layer-basierte Shader-Materialien (⚠️ evtl. nicht mehr maintained) |
| `leva` | GUI für Uniform-Tweaking im Dev-Modus |

---

## 7. Empfehlung für LocAI

### TL;DR

**React Three Fiber + Custom ShaderMaterial + Bloom Post-Processing**

### Empfohlener Stack

```
React + Vite
├── @react-three/fiber       → 3D Rendering
├── @react-three/drei        → Helpers (useGLTF, OrbitControls, etc.)
├── @react-three/postprocessing → Bloom Effekt
└── three                    → Three.js Core
```

### Empfohlener Workflow

1. **Logo in Blender/Rhino modellieren** (oder SVG extrudieren)
   - Low-Poly halten (< 5k Vertices)
   - Als `.glb` exportieren
   - Mit `gltf-transform draco` komprimieren

2. **In React laden** mit `useGLTF`
   - Tool: [gltf.pmnd.rs](https://gltf.pmnd.rs) generiert direkt die React-Komponente

3. **Custom Shader anwenden:**
   - Start mit **Fresnel/Rim Light** – der einfachste und wirkungsvollste Effekt
   - Dann: Scanlines, Noise-basierter Shimmer hinzufügen
   - `useFrame` für Time-Uniform Animation

4. **Post-Processing:** Bloom für Glow-Effekt
   - `luminanceThreshold: 0.2-0.5` für selektiven Glow
   - `intensity: 1.0-2.0`

5. **Interaktivität:**
   - Mouse-Position als Uniform → Shader reagiert auf Cursor
   - Sanfte Auto-Rotation
   - Optional: Scroll-linked Animation

### Schnellster Einstieg (MVP in 1-2h)

1. Nimm die fertige **HolographicMaterial** Lösung von ektogamat
2. Lade dein Logo als GLB
3. Wende das Material an
4. Füge Bloom hinzu
5. → Fertig, sieht sofort gut aus

### Für mehr Kontrolle (Custom Shader)

1. Starte mit dem Code-Beispiel 5.1 oben
2. Tweake die Shader-Parameter mit [leva](https://github.com/pmndrs/leva) GUI
3. Finde deinen Look
4. Entferne leva für Production

### Performance-Checkliste

- [ ] `dpr={[1, 2]}` setzen
- [ ] GLB mit Draco komprimiert
- [ ] `<Suspense>` mit 2D-Fallback
- [ ] WebGL Feature Detection
- [ ] Bloom `luminanceThreshold > 0` (nicht alles glüht)
- [ ] `PerformanceMonitor` für adaptive Qualität
- [ ] Mobile: Reduzierte Shader-Komplexität oder 2D-Fallback

---

## Quick Reference: Shader-Einsteiger-Tipps

### GLSL Basics die man kennen muss

| Funktion | Was sie tut | Typischer Einsatz |
|----------|------------|-------------------|
| `mix(a, b, t)` | Interpoliert zwischen a und b | Farbverläufe |
| `step(edge, x)` | 0 wenn x < edge, sonst 1 | Harte Kanten |
| `smoothstep(e0, e1, x)` | Weicher Übergang | Weiche Kanten |
| `dot(a, b)` | Skalarprodukt | Fresnel, Lighting |
| `pow(x, n)` | Potenz | Fresnel-Schärfe |
| `sin/cos` | Trigonometrie | Wellen, Animation |
| `fract(x)` | Nachkommastellen | Wiederholende Muster |
| `clamp(x, min, max)` | Wert begrenzen | Werte normalisieren |

### GLSL Datentypen

| Typ | Beschreibung | Beispiel |
|-----|-------------|---------|
| `float` | Einzelner Wert | `1.0` |
| `vec2` | 2D Vektor | `vec2(0.5, 0.5)` – UV Coords |
| `vec3` | 3D Vektor / Farbe | `vec3(1.0, 0.0, 0.0)` – Rot |
| `vec4` | 4D Vektor / RGBA | `vec4(1.0, 0.0, 0.0, 1.0)` |
| `mat4` | 4x4 Matrix | Transformation |
| `sampler2D` | Textur | Texture Lookup |

### Die 3 Variablen-Typen in GLSL

| Typ | Richtung | Beispiel |
|-----|---------|---------|
| **uniform** | JS → Shader (beide) | `u_time`, `u_mouse`, `u_color` |
| **attribute** | Geometrie → Vertex Shader | `position`, `normal`, `uv` |
| **varying** | Vertex → Fragment Shader | `vNormal`, `vUv`, `vViewPosition` |
