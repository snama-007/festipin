'use client'

import { Canvas, useThree } from '@react-three/fiber'
import { OrbitControls, Environment, PerspectiveCamera, Center } from '@react-three/drei'
import { Suspense, useEffect, useRef, useState } from 'react'
import * as THREE from 'three'

// Shadow map configuration
function ShadowMapConfig() {
  const { gl } = useThree()
  
  useEffect(() => {
    gl.shadowMap.enabled = true
    gl.shadowMap.type = THREE.PCFSoftShadowMap
    gl.shadowMap.autoUpdate = true
  }, [gl])
  
  return null
}

// Spot light with target
function SpotLightWithTarget() {
  const lightRef = useRef<THREE.SpotLight>(null)
  const targetRef = useRef<THREE.Object3D>(null)
  
  useEffect(() => {
    if (lightRef.current && targetRef.current) {
      lightRef.current.target = targetRef.current
    }
  }, [])
  
  return (
    <>
      <spotLight
        ref={lightRef}
        position={[0, 8, -2]}
        intensity={1.5}
        color="#ffffff"
        angle={0.3}
        penumbra={0.2}
        distance={20}
        decay={2}
        castShadow
      />
      <primitive ref={targetRef} object={new THREE.Object3D()} position={[0, 0, -2]} />
    </>
  )
}

// Dynamic scene elements from API
function DynamicSceneElements() {
  const [sceneData, setSceneData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [elementCounts, setElementCounts] = useState({
    total: 0,
    balloons: 0,
    banners: 0,
    confetti: 0,
    walls: 0,
    windows: 0,
    doors: 0,
    floors: 0,
    ceilings: 0
  })

  useEffect(() => {
    const fetchSceneData = async () => {
      try {
        const response = await fetch('http://localhost:8000/motif/scene/test-room-scene')
        const data = await response.json()
        
        if (data.success && data.scene) {
          setSceneData(data.scene)
          
          // Count elements by type
          const counts = {
            total: data.scene.elements.length,
            balloons: data.scene.elements.filter((el: any) => el.type === 'balloon').length,
            banners: data.scene.elements.filter((el: any) => el.type === 'banner').length,
            confetti: data.scene.elements.filter((el: any) => el.type === 'confetti').length,
            walls: data.scene.elements.filter((el: any) => el.type === 'wall').length,
            windows: data.scene.elements.filter((el: any) => el.type === 'window').length,
            doors: data.scene.elements.filter((el: any) => el.type === 'door').length,
            floors: data.scene.elements.filter((el: any) => el.type === 'floor').length,
            ceilings: data.scene.elements.filter((el: any) => el.type === 'ceiling').length
          }
          setElementCounts(counts)
        }
      } catch (error) {
        console.error('Failed to fetch scene data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchSceneData()
  }, [])

  if (loading) {
    return <LoadingFallback />
  }

  if (!sceneData) {
    return <RoomDecorationElements />
  }

  return (
    <group>
      {/* Render dynamic elements from API */}
      {sceneData.elements.map((element: any, index: number) => {
        const { id, type, geometry, material, position, rotation, scale } = element
        
        return (
          <mesh
            key={id || index}
            position={position}
            rotation={rotation}
            scale={scale}
            castShadow
            receiveShadow
          >
            {geometry.type === 'sphere' && (
              <sphereGeometry args={[geometry.radius, geometry.segments || 32, geometry.segments || 32]} />
            )}
            {geometry.type === 'plane' && (
              <planeGeometry args={[geometry.width, geometry.height]} />
            )}
            {geometry.type === 'box' && (
              <boxGeometry args={[geometry.width || 1, geometry.height || 1, geometry.depth || 1]} />
            )}
            {geometry.type === 'cylinder' && (
              <cylinderGeometry args={[geometry.radiusTop || 1, geometry.radiusBottom || 1, geometry.height || 1, geometry.segments || 32]} />
            )}
            
            <meshStandardMaterial
              color={material.color}
              roughness={material.roughness || 0.5}
              metalness={material.metalness || 0.0}
              emissive={material.emissive}
              emissiveIntensity={material.emissiveIntensity || 0}
              transparent={material.transparent || false}
              opacity={material.opacity || 1}
            />
          </mesh>
        )
      })}
    </group>
  )
}

// Room structure components
function RoomStructure() {
  return (
    <group>
      {/* Floor */}
      <mesh position={[0, -1, 0]} receiveShadow>
        <planeGeometry args={[20, 20]} />
        <meshStandardMaterial
          color="#f5f5f5"
          roughness={0.8}
          metalness={0.1}
        />
      </mesh>

      {/* Back Wall */}
      <mesh position={[0, 3, -10]} rotation={[0, 0, 0]} receiveShadow>
        <planeGeometry args={[20, 8]} />
        <meshStandardMaterial
          color="#ffffff"
          roughness={0.9}
          metalness={0.0}
        />
      </mesh>

      {/* Left Wall */}
      <mesh position={[-10, 3, 0]} rotation={[0, Math.PI / 2, 0]} receiveShadow>
        <planeGeometry args={[20, 8]} />
        <meshStandardMaterial
          color="#ffffff"
          roughness={0.9}
          metalness={0.0}
        />
      </mesh>

      {/* Right Wall */}
      <mesh position={[10, 3, 0]} rotation={[0, -Math.PI / 2, 0]} receiveShadow>
        <planeGeometry args={[20, 8]} />
        <meshStandardMaterial
          color="#ffffff"
          roughness={0.9}
          metalness={0.0}
        />
      </mesh>

      {/* Ceiling */}
      <mesh position={[0, 7, 0]} rotation={[Math.PI, 0, 0]} receiveShadow>
        <planeGeometry args={[20, 20]} />
        <meshStandardMaterial
          color="#f8f8f8"
          roughness={0.9}
          metalness={0.0}
        />
      </mesh>

      {/* Windows */}
      <mesh position={[0, 4, -9.9]} rotation={[0, 0, 0]}>
        <planeGeometry args={[6, 4]} />
        <meshStandardMaterial
          color="#87ceeb"
          transparent
          opacity={0.3}
          roughness={0.1}
          metalness={0.0}
        />
      </mesh>

      {/* Door */}
      <mesh position={[6, 2, -9.9]} rotation={[0, 0, 0]}>
        <planeGeometry args={[3, 6]} />
        <meshStandardMaterial
          color="#8b4513"
          roughness={0.8}
          metalness={0.1}
        />
      </mesh>
    </group>
  )
}

// Party decoration elements in room context
function RoomDecorationElements() {
  return (
    <group>
      {/* Balloons floating in room */}
      <mesh position={[0, 2, -2]}>
        <sphereGeometry args={[0.8, 32, 32]} />
        <meshStandardMaterial
          color="#ff69b4"
          metalness={0.3}
          roughness={0.2}
          emissive="#ff69b4"
          emissiveIntensity={0.1}
        />
      </mesh>

      <mesh position={[-3, 1.5, -1]}>
        <sphereGeometry args={[0.7, 32, 32]} />
        <meshStandardMaterial
          color="#87ceeb"
          metalness={0.3}
          roughness={0.2}
          emissive="#87ceeb"
          emissiveIntensity={0.1}
        />
      </mesh>

      <mesh position={[3, 1.8, -1.5]}>
        <sphereGeometry args={[0.75, 32, 32]} />
        <meshStandardMaterial
          color="#ffd700"
          metalness={0.3}
          roughness={0.2}
          emissive="#ffd700"
          emissiveIntensity={0.1}
        />
      </mesh>

      <mesh position={[-5, 2.2, -3]}>
        <sphereGeometry args={[0.65, 32, 32]} />
        <meshStandardMaterial
          color="#9370db"
          metalness={0.3}
          roughness={0.2}
          emissive="#9370db"
          emissiveIntensity={0.1}
        />
      </mesh>

      <mesh position={[5, 1.6, -2.5]}>
        <sphereGeometry args={[0.68, 32, 32]} />
        <meshStandardMaterial
          color="#ff6347"
          metalness={0.3}
          roughness={0.2}
          emissive="#ff6347"
          emissiveIntensity={0.1}
        />
      </mesh>

      {/* Banner hanging from ceiling */}
      <mesh position={[0, 5.5, -8]} rotation={[0, 0, 0]}>
        <boxGeometry args={[8, 0.4, 0.1]} />
        <meshStandardMaterial
          color="#ff1493"
          metalness={0.4}
          roughness={0.3}
        />
      </mesh>

      {/* Party table in center */}
      <mesh position={[0, -0.5, -2]} receiveShadow>
        <cylinderGeometry args={[2, 2, 0.1, 32]} />
        <meshStandardMaterial
          color="#ffffff"
          metalness={0.1}
          roughness={0.8}
        />
      </mesh>

      {/* Table legs */}
      {[
        [1.5, -1, -1.5],
        [-1.5, -1, -1.5],
        [1.5, -1, -2.5],
        [-1.5, -1, -2.5]
      ].map((pos, i) => (
        <mesh key={i} position={pos as [number, number, number]} receiveShadow>
          <cylinderGeometry args={[0.1, 0.1, 1, 8]} />
          <meshStandardMaterial
            color="#8b4513"
            metalness={0.3}
            roughness={0.7}
          />
        </mesh>
      ))}

      {/* Centerpiece on table */}
      <mesh position={[0, 0, -2]}>
        <cylinderGeometry args={[0.3, 0.3, 0.8, 16]} />
        <meshStandardMaterial
          color="#32cd32"
          metalness={0.2}
          roughness={0.6}
        />
      </mesh>

      {/* Confetti scattered around */}
      {Array.from({ length: 15 }).map((_, i) => {
        const x = (Math.random() - 0.5) * 8
        const y = Math.random() * 0.5
        const z = (Math.random() - 0.5) * 6 - 2
        const rotation = [
          Math.random() * Math.PI,
          Math.random() * Math.PI,
          Math.random() * Math.PI
        ] as [number, number, number]

        const colors = ['#ff69b4', '#87ceeb', '#ffd700', '#9370db', '#ff6347', '#32cd32']
        const color = colors[Math.floor(Math.random() * colors.length)]

        return (
          <mesh key={i} position={[x, y, z]} rotation={rotation}>
            <boxGeometry args={[0.1, 0.2, 0.02]} />
            <meshStandardMaterial color={color} />
          </mesh>
        )
      })}

      {/* Garland hanging from walls */}
      <mesh position={[-8, 4, -2]} rotation={[0, Math.PI / 2, 0]}>
        <cylinderGeometry args={[0.1, 0.1, 4, 8]} />
        <meshStandardMaterial
          color="#ff6b6b"
          metalness={0.2}
          roughness={0.8}
        />
      </mesh>

      <mesh position={[8, 4, -2]} rotation={[0, Math.PI / 2, 0]}>
        <cylinderGeometry args={[0.1, 0.1, 4, 8]} />
        <meshStandardMaterial
          color="#4ecdc4"
          metalness={0.2}
          roughness={0.8}
        />
      </mesh>
    </group>
  )
}

function LoadingFallback() {
  return (
    <mesh>
      <sphereGeometry args={[1, 32, 32]} />
      <meshStandardMaterial color="#6b46c1" wireframe />
    </mesh>
  )
}

interface Scene3DViewerProps {
  imageUrl?: string
}

export function Scene3DViewer({ imageUrl }: Scene3DViewerProps) {
  const [elementCounts, setElementCounts] = useState({
    total: 0,
    balloons: 0,
    banners: 0,
    confetti: 0,
    walls: 0,
    windows: 0,
    doors: 0,
    floors: 0,
    ceilings: 0
  })

  useEffect(() => {
    const fetchElementCounts = async () => {
      try {
        const response = await fetch('http://localhost:8000/motif/scene/test-room-scene')
        const data = await response.json()
        
        if (data.success && data.scene) {
          const counts = {
            total: data.scene.elements.length,
            balloons: data.scene.elements.filter((el: any) => el.type === 'balloon').length,
            banners: data.scene.elements.filter((el: any) => el.type === 'banner').length,
            confetti: data.scene.elements.filter((el: any) => el.type === 'confetti').length,
            walls: data.scene.elements.filter((el: any) => el.type === 'wall').length,
            windows: data.scene.elements.filter((el: any) => el.type === 'window').length,
            doors: data.scene.elements.filter((el: any) => el.type === 'door').length,
            floors: data.scene.elements.filter((el: any) => el.type === 'floor').length,
            ceilings: data.scene.elements.filter((el: any) => el.type === 'ceiling').length
          }
          setElementCounts(counts)
        }
      } catch (error) {
        console.error('Failed to fetch element counts:', error)
      }
    }

    fetchElementCounts()
  }, [])

  return (
    <div className="w-full h-[600px] rounded-2xl overflow-hidden bg-gradient-to-br from-gray-900 to-gray-800">
      <Canvas
        shadows
        dpr={[1, 2]}
        gl={{
          antialias: true,
          toneMapping: THREE.ACESFilmicToneMapping,
          toneMappingExposure: 1.2,
          outputColorSpace: THREE.SRGBColorSpace
        }}
        camera={{
          position: [0, 3, 12],
          fov: 60,
          near: 0.1,
          far: 1000
        }}
      >
        {/* Camera */}
        <PerspectiveCamera makeDefault position={[0, 3, 12]} fov={60} />

        {/* Shadow Map Configuration */}
        <ShadowMapConfig />

        {/* Enhanced Lighting System */}
        <ambientLight intensity={0.3} color="#f8f8ff" />
        
        {/* Main directional light */}
        <directionalLight
          position={[15, 20, 15]}
          intensity={1.2}
          color="#fff8dc"
          castShadow
          shadow-bias={-0.0001}
          shadow-normalBias={0.02}
          shadow-mapSize={[4096, 4096]}
        />
        
        {/* Point lights for atmosphere */}
        <pointLight position={[-8, 6, -8]} intensity={0.8} color="#ffd700" distance={25} decay={2} />
        <pointLight position={[8, 6, -8]} intensity={0.8} color="#ffd700" distance={25} decay={2} />
        <pointLight position={[0, 4, -5]} intensity={1.0} color="#ff69b4" distance={15} decay={2} />
        <pointLight position={[-5, 2, -3]} intensity={0.6} color="#87ceeb" distance={12} decay={2} />
        <pointLight position={[5, 2, -3]} intensity={0.6} color="#ff6347" distance={12} decay={2} />
        
        {/* Spot light for focus */}
        <SpotLightWithTarget />
        
        {/* Hemisphere light for sky/ground */}
        <hemisphereLight
          args={["#87ceeb", "#f5f5f5", 0.4]}
        />

        {/* Environment */}
        <Environment preset="city" />

        {/* Scene Content */}
        <Suspense fallback={<LoadingFallback />}>
          {/* Room Structure */}
          <RoomStructure />
          
          {/* Dynamic Party Decorations from API */}
          <DynamicSceneElements />
        </Suspense>

        {/* Controls */}
        <OrbitControls
          makeDefault
          enableDamping
          dampingFactor={0.05}
          minDistance={8}
          maxDistance={25}
          maxPolarAngle={Math.PI / 2}
          target={[0, 2, -5]}
        />

        {/* Grid Helper */}
        <gridHelper args={[20, 20, '#444444', '#222222']} position={[0, -1.1, 0]} />
      </Canvas>

      {/* Overlay UI */}
      <div className="absolute top-4 left-4 bg-black/50 backdrop-blur-md rounded-lg px-4 py-2 text-white text-sm">
        <p className="font-medium">🏠 3D Party Room</p>
        <p className="text-xs text-gray-300 mt-1">Drag to rotate • Scroll to zoom</p>
      </div>

      {/* Element Counter */}
      <div className="absolute top-4 right-4 bg-black/50 backdrop-blur-md rounded-lg px-4 py-2 text-white text-sm">
        <p className="font-medium">{elementCounts.total} Elements in Room</p>
        <div className="flex gap-2 mt-2 flex-wrap">
          {elementCounts.balloons > 0 && (
            <span className="text-xs bg-pink-500/30 px-2 py-1 rounded">{elementCounts.balloons} Balloons</span>
          )}
          {elementCounts.banners > 0 && (
            <span className="text-xs bg-purple-500/30 px-2 py-1 rounded">{elementCounts.banners} Banners</span>
          )}
          {elementCounts.confetti > 0 && (
            <span className="text-xs bg-blue-500/30 px-2 py-1 rounded">{elementCounts.confetti} Confetti</span>
          )}
          {elementCounts.walls > 0 && (
            <span className="text-xs bg-gray-500/30 px-2 py-1 rounded">{elementCounts.walls} Walls</span>
          )}
          {elementCounts.windows > 0 && (
            <span className="text-xs bg-cyan-500/30 px-2 py-1 rounded">{elementCounts.windows} Windows</span>
          )}
          {elementCounts.doors > 0 && (
            <span className="text-xs bg-yellow-500/30 px-2 py-1 rounded">{elementCounts.doors} Doors</span>
          )}
          {elementCounts.floors > 0 && (
            <span className="text-xs bg-green-500/30 px-2 py-1 rounded">{elementCounts.floors} Floors</span>
          )}
          {elementCounts.ceilings > 0 && (
            <span className="text-xs bg-indigo-500/30 px-2 py-1 rounded">{elementCounts.ceilings} Ceilings</span>
          )}
        </div>
      </div>

      {/* Bottom Controls */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black/50 backdrop-blur-md rounded-full px-6 py-3 flex gap-4">
        <button className="text-white text-sm hover:text-pink-400 transition-colors">
          🎨 Change Colors
        </button>
        <button className="text-white text-sm hover:text-blue-400 transition-colors">
          🏠 Room Settings
        </button>
        <button className="text-white text-sm hover:text-purple-400 transition-colors">
          ➕ Add Decoration
        </button>
        <button className="text-white text-sm hover:text-green-400 transition-colors">
          💾 Export Room
        </button>
      </div>
    </div>
  )
}
