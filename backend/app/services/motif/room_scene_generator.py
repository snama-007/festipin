"""
Room Scene Generator Service

Generates complete 3D room scenes with party decorations.
Removes kitchen and irrelevant elements, adds detected decorations.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .party_decoration_classifier import DecorationType
import uuid
import json
import math

@dataclass
class SceneElement:
    """3D Scene Element"""
    id: str
    type: str
    geometry: Dict[str, Any]
    material: Dict[str, Any]
    position: List[float]
    rotation: List[float]
    scale: List[float]

@dataclass
class DecorationElement:
    """Party Decoration Element"""
    type: DecorationType
    count: int
    elements: List[Dict[str, Any]]
    colors: List[str]
    positions: List[List[float]]
    sizes: List[float]

@dataclass
class Scene3D:
    """Complete 3D Scene"""
    id: str
    name: str
    elements: List[SceneElement]
    lighting: Dict[str, Any]
    camera: Dict[str, Any]
    environment: Dict[str, Any]

class RoomSceneGenerator:
    """Generate 3D room scenes with party decorations"""
    
    def __init__(self):
        self.room_templates = self._load_room_templates()
    
    def _load_room_templates(self) -> Dict[str, Any]:
        """Load room templates"""
        return {
            "standard_room": {
                "floor_size": [20, 20],
                "wall_height": 8,
                "ceiling_height": 7,
                "window_size": [6, 4],
                "door_size": [3, 6]
            }
        }
    
    async def generate_scene(self, elements: List[DecorationElement]) -> Scene3D:
        """Generate complete 3D scene in room environment"""
        
        # Create base room
        room_scene = self._create_base_room()
        
        # Remove kitchen and irrelevant elements
        room_scene = self._remove_irrelevant_elements(room_scene)
        
        # Add detected decoration elements
        decorated_scene = await self._add_decoration_elements(room_scene, elements)
        
        # Optimize scene for desktop rendering
        optimized_scene = self._optimize_for_desktop(decorated_scene)
        
        return optimized_scene
    
    def _create_base_room(self) -> Scene3D:
        """Create base room environment"""
        
        room_scene = Scene3D(
            id=f"room_{uuid.uuid4()}",
            name="Party Room",
            elements=[],
            lighting=self._create_room_lighting(),
            camera=self._create_room_camera(),
            environment=self._create_room_environment()
        )
        
        # Add room structure
        room_scene.elements.append(self._create_floor())
        room_scene.elements.extend(self._create_walls())
        room_scene.elements.append(self._create_ceiling())
        room_scene.elements.append(self._create_windows())
        room_scene.elements.append(self._create_door())
        
        return room_scene
    
    def _create_floor(self) -> SceneElement:
        """Create realistic room floor with depth"""
        return SceneElement(
            id="floor",
            type="floor",
            geometry={
                "type": "plane",
                "width": 20,
                "height": 20
            },
            material={
                "type": "standard",
                "color": "#f8f8f8",
                "roughness": 0.9,
                "metalness": 0.05,
                "normalScale": [1, 1],
                "displacementScale": 0.1,
                "receiveShadow": True,
                "envMapIntensity": 0.3
            },
            position=[0, -1, 0],
            rotation=[0, 0, 0],
            scale=[1, 1, 1]
        )
    
    def _create_walls(self) -> List[SceneElement]:
        """Create room walls"""
        walls = []
        
        # Back wall
        walls.append(SceneElement(
            id="back_wall",
            type="wall",
            geometry={
                "type": "plane",
                "width": 20,
                "height": 8
            },
            material={
                "type": "standard",
                "color": "#fefefe",
                "roughness": 0.95,
                "metalness": 0.02,
                "normalScale": [0.5, 0.5],
                "receiveShadow": True,
                "envMapIntensity": 0.2
            },
            position=[0, 3, -10],
            rotation=[0, 0, 0],
            scale=[1, 1, 1]
        ))
        
        # Left wall
        walls.append(SceneElement(
            id="left_wall",
            type="wall",
            geometry={
                "type": "plane",
                "width": 20,
                "height": 8
            },
            material={
                "type": "standard",
                "color": "#ffffff",
                "roughness": 0.9,
                "metalness": 0.0
            },
            position=[-10, 3, 0],
            rotation=[0, 90, 0],
            scale=[1, 1, 1]
        ))
        
        # Right wall
        walls.append(SceneElement(
            id="right_wall",
            type="wall",
            geometry={
                "type": "plane",
                "width": 20,
                "height": 8
            },
            material={
                "type": "standard",
                "color": "#ffffff",
                "roughness": 0.9,
                "metalness": 0.0
            },
            position=[10, 3, 0],
            rotation=[0, -90, 0],
            scale=[1, 1, 1]
        ))
        
        return walls
    
    def _create_ceiling(self) -> SceneElement:
        """Create room ceiling"""
        return SceneElement(
            id="ceiling",
            type="ceiling",
            geometry={
                "type": "plane",
                "width": 20,
                "height": 20
            },
            material={
                "type": "standard",
                "color": "#f8f8f8",
                "roughness": 0.9,
                "metalness": 0.0
            },
            position=[0, 7, 0],
            rotation=[180, 0, 0],
            scale=[1, 1, 1]
        )
    
    def _create_windows(self) -> SceneElement:
        """Create room windows"""
        return SceneElement(
            id="window",
            type="window",
            geometry={
                "type": "plane",
                "width": 6,
                "height": 4
            },
            material={
                "type": "standard",
                "color": "#87ceeb",
                "transparent": True,
                "opacity": 0.3,
                "roughness": 0.1,
                "metalness": 0.0
            },
            position=[0, 4, -9.9],
            rotation=[0, 0, 0],
            scale=[1, 1, 1]
        )
    
    def _create_door(self) -> SceneElement:
        """Create room door"""
        return SceneElement(
            id="door",
            type="door",
            geometry={
                "type": "plane",
                "width": 3,
                "height": 6
            },
            material={
                "type": "standard",
                "color": "#8b4513",
                "roughness": 0.8,
                "metalness": 0.1
            },
            position=[6, 2, -9.9],
            rotation=[0, 0, 0],
            scale=[1, 1, 1]
        )
    
    def _remove_irrelevant_elements(self, scene: Scene3D) -> Scene3D:
        """Remove kitchen and other irrelevant elements"""
        
        # Elements to remove
        irrelevant_types = [
            "kitchen", "stove", "refrigerator", "sink", "cabinet",
            "bedroom", "bed", "closet", "bathroom", "toilet",
            "office", "desk", "computer", "bookshelf"
        ]
        
        # Filter out irrelevant elements
        scene.elements = [
            element for element in scene.elements
            if not any(irrelevant in element.type.lower() 
                      for irrelevant in irrelevant_types)
        ]
        
        return scene
    
    async def _add_decoration_elements(self, scene: Scene3D, 
                                     elements: List[DecorationElement]) -> Scene3D:
        """Add detected decoration elements to scene"""
        
        for element in elements:
            if element.type == DecorationType.BALLOONS:
                scene = await self._add_balloons_to_scene(scene, element)
            elif element.type == DecorationType.BANNERS:
                scene = await self._add_banners_to_scene(scene, element)
            elif element.type == DecorationType.FLOWERS:
                scene = await self._add_flowers_to_scene(scene, element)
            elif element.type == DecorationType.CAKE:
                scene = await self._add_cake_to_scene(scene, element)
            elif element.type == DecorationType.CONFETTI:
                scene = await self._add_confetti_to_scene(scene, element)
            elif element.type == DecorationType.GARLANDS:
                scene = await self._add_garlands_to_scene(scene, element)
        
        return scene
    
    async def _add_balloons_to_scene(self, scene: Scene3D, 
                                   balloon_element: DecorationElement) -> Scene3D:
        """Add realistic balloon arrangements to 3D scene"""
        
        # Create balloon arch
        arch_balloons = self._create_balloon_arch()
        scene.elements.extend(arch_balloons)
        
        # Create balloon clusters
        cluster_balloons = self._create_balloon_clusters()
        scene.elements.extend(cluster_balloons)
        
        # Create floating balloons
        floating_balloons = self._create_floating_balloons()
        scene.elements.extend(floating_balloons)
        
        return scene
    
    def _create_balloon_arch(self) -> List[SceneElement]:
        """Create a realistic balloon arch"""
        arch_balloons = []
        arch_colors = ['#ff69b4', '#87ceeb', '#ffd700', '#9370db', '#ff6347', '#32cd32', '#ff1493', '#00ced1']
        
        # Arch parameters
        arch_width = 8
        arch_height = 3
        arch_depth = -2
        num_balloons = 24
        
        for i in range(num_balloons):
            # Calculate arch position using parabolic curve
            t = i / (num_balloons - 1)  # 0 to 1
            x = (t - 0.5) * arch_width
            y = arch_height * (1 - (2 * t - 1) ** 2) + 1.5  # Parabolic arch
            
            # Add some randomness for natural look
            x += (hash(str(i)) % 100 - 50) / 1000  # Small random offset
            y += (hash(str(i + 1)) % 100 - 50) / 1000
            
            # Vary balloon sizes
            base_radius = 0.4
            size_variation = (hash(str(i + 2)) % 100) / 200  # 0 to 0.5
            radius = base_radius + size_variation
            
            balloon_3d = SceneElement(
                id=f"arch_balloon_{i}",
                type="balloon",
                geometry={
                    "type": "sphere",
                    "radius": radius,
                    "segments": 32
                },
                material={
                    "type": "standard",
                    "color": arch_colors[i % len(arch_colors)],
                    "roughness": 0.1,
                    "metalness": 0.2,
                    "emissive": arch_colors[i % len(arch_colors)],
                    "emissiveIntensity": 0.05,
                    "transparent": True,
                    "opacity": 0.95
                },
                position=[x, y, arch_depth],
                rotation=[
                    (hash(str(i)) % 360) * 0.0174533,  # Random rotation in radians
                    (hash(str(i + 1)) % 360) * 0.0174533,
                    (hash(str(i + 2)) % 360) * 0.0174533
                ],
                scale=[1, 1, 1]
            )
            
            arch_balloons.append(balloon_3d)
        
        return arch_balloons
    
    def _create_balloon_clusters(self) -> List[SceneElement]:
        """Create realistic balloon clusters"""
        cluster_balloons = []
        cluster_colors = ['#ff69b4', '#87ceeb', '#ffd700', '#9370db', '#ff6347']
        
        # Create 3 clusters
        cluster_positions = [
            [-6, 2.5, -1],  # Left cluster
            [0, 3, -3],      # Center cluster
            [6, 2.8, -1.5]   # Right cluster
        ]
        
        for cluster_idx, cluster_pos in enumerate(cluster_positions):
            cluster_size = 5 + cluster_idx  # 5, 6, 7 balloons per cluster
            
            for i in range(cluster_size):
                # Position around cluster center
                angle = (i / cluster_size) * 2 * 3.14159
                radius = 0.8 + (hash(str(cluster_idx + i)) % 100) / 200
                
                x = cluster_pos[0] + radius * math.cos(angle)
                y = cluster_pos[1] + (hash(str(i)) % 100 - 50) / 100
                z = cluster_pos[2] + radius * math.sin(angle)
                
                balloon_radius = 0.3 + (hash(str(i + cluster_idx)) % 100) / 300
                
                balloon_3d = SceneElement(
                    id=f"cluster_{cluster_idx}_balloon_{i}",
                    type="balloon",
                    geometry={
                        "type": "sphere",
                        "radius": balloon_radius,
                        "segments": 24
                    },
                    material={
                        "type": "standard",
                        "color": cluster_colors[i % len(cluster_colors)],
                        "roughness": 0.15,
                        "metalness": 0.25,
                        "emissive": cluster_colors[i % len(cluster_colors)],
                        "emissiveIntensity": 0.08,
                        "transparent": True,
                        "opacity": 0.9
                    },
                    position=[x, y, z],
                    rotation=[
                        (hash(str(i)) % 180) * 0.0174533,
                        (hash(str(i + 1)) % 180) * 0.0174533,
                        (hash(str(i + 2)) % 180) * 0.0174533
                    ],
                    scale=[1, 1, 1]
                )
                
                cluster_balloons.append(balloon_3d)
        
        return cluster_balloons
    
    def _create_floating_balloons(self) -> List[SceneElement]:
        """Create floating balloons for atmosphere"""
        floating_balloons = []
        float_colors = ['#ff69b4', '#87ceeb', '#ffd700', '#9370db', '#ff6347', '#32cd32']
        
        # Create 8 floating balloons
        for i in range(8):
            # Random positions in upper room area
            x = (hash(str(i)) % 1600 - 800) / 100  # -8 to 8
            y = 4 + (hash(str(i + 1)) % 300) / 100  # 4 to 7
            z = (hash(str(i + 2)) % 1000 - 500) / 100  # -5 to 5
            
            balloon_radius = 0.25 + (hash(str(i + 3)) % 100) / 400
            
            balloon_3d = SceneElement(
                id=f"floating_balloon_{i}",
                type="balloon",
                geometry={
                    "type": "sphere",
                    "radius": balloon_radius,
                    "segments": 20
                },
                material={
                    "type": "standard",
                    "color": float_colors[i % len(float_colors)],
                    "roughness": 0.2,
                    "metalness": 0.3,
                    "emissive": float_colors[i % len(float_colors)],
                    "emissiveIntensity": 0.1,
                    "transparent": True,
                    "opacity": 0.85
                },
                position=[x, y, z],
                rotation=[
                    (hash(str(i)) % 360) * 0.0174533,
                    (hash(str(i + 1)) % 360) * 0.0174533,
                    (hash(str(i + 2)) % 360) * 0.0174533
                ],
                scale=[1, 1, 1]
            )
            
            floating_balloons.append(balloon_3d)
        
        return floating_balloons
    
    async def _add_banners_to_scene(self, scene: Scene3D, 
                                  banner_element: DecorationElement) -> Scene3D:
        """Add banners to 3D scene"""
        
        for i, banner in enumerate(banner_element.elements):
            # Create 3D banner
            banner_3d = SceneElement(
                id=f"banner_{i}",
                type="banner",
                geometry={
                    "type": "plane",
                    "width": banner.get('bbox', [0, 0, 4, 1])[2] / 100,
                    "height": banner.get('bbox', [0, 0, 4, 1])[3] / 100
                },
                material={
                    "type": "standard",
                    "color": banner.get('colors', ['#ff6b6b'])[0],
                    "roughness": 0.4,
                    "metalness": 0.1
                },
                position=[
                    banner.get('bbox', [0, 0, 4, 1])[0] / 100 - 2.5,
                    banner.get('bbox', [0, 0, 4, 1])[1] / 100 + 4,
                    -4.5
                ],
                rotation=[0, 0, 0],
                scale=[1, 1, 1]
            )
            
            scene.elements.append(banner_3d)
        
        return scene
    
    async def _add_flowers_to_scene(self, scene: Scene3D, 
                                  flower_element: DecorationElement) -> Scene3D:
        """Add flowers to 3D scene"""
        
        for i, flower in enumerate(flower_element.elements):
            # Create 3D flower centerpiece
            flower_3d = SceneElement(
                id=f"flower_{i}",
                type="flower",
                geometry={
                    "type": "cylinder",
                    "radius": 0.3,
                    "height": 0.8,
                    "segments": 16
                },
                material={
                    "type": "standard",
                    "color": flower.get('color', '#32cd32'),
                    "roughness": 0.6,
                    "metalness": 0.2
                },
                position=[
                    flower.get('position', [0, 0, -2])[0],
                    flower.get('position', [0, 0, -2])[1],
                    flower.get('position', [0, 0, -2])[2]
                ],
                rotation=[0, 0, 0],
                scale=[1, 1, 1]
            )
            
            scene.elements.append(flower_3d)
        
        return scene
    
    async def _add_cake_to_scene(self, scene: Scene3D, 
                               cake_element: DecorationElement) -> Scene3D:
        """Add cake to 3D scene"""
        
        for i, cake in enumerate(cake_element.elements):
            # Create 3D cake
            cake_3d = SceneElement(
                id=f"cake_{i}",
                type="cake",
                geometry={
                    "type": "cylinder",
                    "radius": 1.5,
                    "height": 1.2,
                    "segments": 32
                },
                material={
                    "type": "standard",
                    "color": cake.get('color', '#ffb6c1'),
                    "roughness": 0.3,
                    "metalness": 0.1
                },
                position=[
                    cake.get('position', [0, 0, -2])[0],
                    cake.get('position', [0, 0, -2])[1],
                    cake.get('position', [0, 0, -2])[2]
                ],
                rotation=[0, 0, 0],
                scale=[1, 1, 1]
            )
            
            scene.elements.append(cake_3d)
        
        return scene
    
    async def _add_confetti_to_scene(self, scene: Scene3D, 
                                   confetti_element: DecorationElement) -> Scene3D:
        """Add confetti to 3D scene"""
        
        for i, confetti in enumerate(confetti_element.elements):
            # Create 3D confetti piece
            confetti_3d = SceneElement(
                id=f"confetti_{i}",
                type="confetti",
                geometry={
                    "type": "box",
                    "width": 0.1,
                    "height": 0.2,
                    "depth": 0.02
                },
                material={
                    "type": "standard",
                    "color": confetti.get('color', '#ff69b4'),
                    "roughness": 0.8,
                    "metalness": 0.0
                },
                position=[
                    confetti.get('position', [0, 0, 0])[0],
                    confetti.get('position', [0, 0, 0])[1],
                    confetti.get('position', [0, 0, 0])[2]
                ],
                rotation=[
                    confetti.get('rotation', [0, 0, 0])[0],
                    confetti.get('rotation', [0, 0, 0])[1],
                    confetti.get('rotation', [0, 0, 0])[2]
                ],
                scale=[1, 1, 1]
            )
            
            scene.elements.append(confetti_3d)
        
        return scene
    
    async def _add_garlands_to_scene(self, scene: Scene3D, 
                                   garland_element: DecorationElement) -> Scene3D:
        """Add garlands to 3D scene"""
        
        for i, garland in enumerate(garland_element.elements):
            # Create 3D garland
            garland_3d = SceneElement(
                id=f"garland_{i}",
                type="garland",
                geometry={
                    "type": "cylinder",
                    "radius": 0.1,
                    "height": 4,
                    "segments": 8
                },
                material={
                    "type": "standard",
                    "color": garland.get('color', '#ff6b6b'),
                    "roughness": 0.8,
                    "metalness": 0.2
                },
                position=[
                    garland.get('position', [-8, 4, -2])[0],
                    garland.get('position', [-8, 4, -2])[1],
                    garland.get('position', [-8, 4, -2])[2]
                ],
                rotation=[
                    garland.get('rotation', [0, 90, 0])[0],
                    garland.get('rotation', [0, 90, 0])[1],
                    garland.get('rotation', [0, 90, 0])[2]
                ],
                scale=[1, 1, 1]
            )
            
            scene.elements.append(garland_3d)
        
        return scene
    
    def _create_room_lighting(self) -> Dict[str, Any]:
        """Create realistic room lighting setup with depth and atmosphere"""
        return {
            "ambient": {
                "intensity": 0.3,
                "color": "#f8f8ff"  # Slightly cool ambient
            },
            "directional": {
                "position": [15, 20, 15],
                "intensity": 1.2,
                "color": "#fff8dc",  # Warm daylight
                "castShadow": True,
                "shadowBias": -0.0001,
                "shadowNormalBias": 0.02
            },
            "point": [
                {
                    "position": [-8, 6, -8],
                    "intensity": 0.8,
                    "color": "#ffd700",  # Warm accent
                    "distance": 25,
                    "decay": 2
                },
                {
                    "position": [8, 6, -8],
                    "intensity": 0.8,
                    "color": "#ffd700",
                    "distance": 25,
                    "decay": 2
                },
                {
                    "position": [0, 4, -5],
                    "intensity": 1.0,
                    "color": "#ff69b4",  # Party accent
                    "distance": 15,
                    "decay": 2
                },
                {
                    "position": [-5, 2, -3],
                    "intensity": 0.6,
                    "color": "#87ceeb",  # Cool accent
                    "distance": 12,
                    "decay": 2
                },
                {
                    "position": [5, 2, -3],
                    "intensity": 0.6,
                    "color": "#ff6347",  # Warm accent
                    "distance": 12,
                    "decay": 2
                }
            ],
            "spot": [
                {
                    "position": [0, 8, -2],
                    "target": [0, 0, -2],
                    "intensity": 1.5,
                    "color": "#ffffff",
                    "angle": 0.3,
                    "penumbra": 0.2,
                    "distance": 20,
                    "decay": 2
                }
            ],
            "hemisphere": {
                "skyColor": "#87ceeb",
                "groundColor": "#f5f5f5",
                "intensity": 0.4
            }
        }
    
    def _create_room_camera(self) -> Dict[str, Any]:
        """Create room camera setup"""
        return {
            "position": [0, 3, 12],
            "fov": 60,
            "near": 0.1,
            "far": 1000
        }
    
    def _create_room_environment(self) -> Dict[str, Any]:
        """Create enhanced room environment with depth and atmosphere"""
        return {
            "preset": "city",
            "background": {
                "type": "gradient",
                "topColor": "#87ceeb",
                "bottomColor": "#f0f8ff"
            },
            "fog": {
                "enabled": True,
                "color": "#f8f8ff",
                "near": 15,
                "far": 50,
                "density": 0.02
            },
            "postProcessing": {
                "bloom": {
                    "enabled": True,
                    "threshold": 0.8,
                    "strength": 0.5,
                    "radius": 0.4
                },
                "toneMapping": {
                    "exposure": 1.2,
                    "whitePoint": 1.0
                },
                "depthOfField": {
                    "enabled": True,
                    "focusDistance": 12,
                    "focalLength": 0.05,
                    "bokehScale": 2
                }
            }
        }
    
    def _optimize_for_desktop(self, scene: Scene3D) -> Scene3D:
        """Optimize scene for desktop rendering"""
        
        # Add performance optimizations
        for element in scene.elements:
            # Enable shadows for floor and walls
            if element.type in ['floor', 'wall', 'ceiling']:
                element.material['receiveShadow'] = True
            
            # Optimize geometry for desktop
            if element.geometry.get('segments', 32) > 32:
                element.geometry['segments'] = 32
        
        return scene
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert scene to dictionary for API response"""
        return {
            "id": self.id,
            "name": self.name,
            "elements": [
                {
                    "id": element.id,
                    "type": element.type,
                    "geometry": element.geometry,
                    "material": element.material,
                    "position": element.position,
                    "rotation": element.rotation,
                    "scale": element.scale
                }
                for element in self.elements
            ],
            "lighting": self.lighting,
            "camera": self.camera,
            "environment": self.environment
        }
