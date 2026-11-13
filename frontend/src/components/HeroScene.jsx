
import { Suspense, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import {
  Float,
  MeshDistortMaterial,
  Environment,
  ContactShadows,
} from "@react-three/drei";

function FloatingOrb({ position, color, scale = 1, speed = 2 }) {
  const mesh = useRef();

  useFrame((state, delta) => {
    if (!mesh.current) return;

    mesh.current.rotation.x += delta * 0.18;
    mesh.current.rotation.y += delta * 0.25;
    mesh.current.position.y +=
      Math.sin(state.clock.elapsedTime * speed) * delta * 0.12;
  });

  return (
    <Float speed={speed} rotationIntensity={0.6} floatIntensity={1.2}>
      <mesh ref={mesh} position={position} scale={scale}>
        <icosahedronGeometry args={[1, 5]} />
        <MeshDistortMaterial
          color={color}
          roughness={0.22}
          metalness={0.18}
          distort={0.32}
          speed={2}
        />
      </mesh>
    </Float>
  );
}

function FloatingRing({ position, rotation, scale = 1 }) {
  const ring = useRef();

  useFrame((_, delta) => {
    if (ring.current) {
      ring.current.rotation.z += delta * 0.16;
    }
  });

  return (
    <mesh
      ref={ring}
      position={position}
      rotation={rotation}
      scale={scale}
    >
      <torusGeometry args={[1.1, 0.025, 16, 120]} />
      <meshStandardMaterial
        color="#173d2b"
        metalness={0.8}
        roughness={0.2}
      />
    </mesh>
  );
}

function SceneObjects() {
  return (
    <>
      <ambientLight intensity={1.4} />
      <directionalLight position={[4, 5, 5]} intensity={2.5} />
      <pointLight position={[-4, -2, 3]} color="#d4ff68" intensity={35} />

      <FloatingOrb
        position={[0, 0, 0]}
        color="#c8ff55"
        scale={1.35}
        speed={1.6}
      />

      <FloatingOrb
        position={[-1.65, 1.15, -1]}
        color="#f2f0d8"
        scale={0.36}
        speed={2.2}
      />

      <FloatingOrb
        position={[1.65, -1.05, -0.8]}
        color="#315e43"
        scale={0.48}
        speed={1.8}
      />

      <FloatingRing
        position={[0, 0, -0.5]}
        rotation={[0.9, 0.3, 0.2]}
        scale={1.5}
      />

      <FloatingRing
        position={[0, 0, -0.7]}
        rotation={[1.2, 0.8, 0.8]}
        scale={1.85}
      />

      <ContactShadows
        position={[0, -2.1, 0]}
        opacity={0.22}
        scale={5}
        blur={2.5}
      />

      <Environment preset="studio" />
    </>
  );
}

export default function HeroScene() {
  return (
    <div className="hero-scene">
      <Canvas
        camera={{ position: [0, 0, 5.5], fov: 42 }}
        dpr={[1, 1.5]}
        gl={{ alpha: true, antialias: true }}
      >
        <Suspense fallback={null}>
          <SceneObjects />
        </Suspense>
      </Canvas>

      <div className="scene-label scene-label-top">
        <span className="scene-dot" />
        OBJECTS OF EVERYDAY DESIRE
      </div>

      <div className="scene-label scene-label-bottom">
        NEXORA® — THE EVERYDAY, REIMAGINED
      </div>
    </div>
  );
}
