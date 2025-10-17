"""
Gemini Flash Image Generation Service

Handles image generation using Google Gemini Flash model
with inspiration image analysis and prompt enhancement.
"""

import asyncio
import base64
import io
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import logging

logger = logging.getLogger(__name__)

class MotifGeminiGenerator:
    """Gemini Flash image generation service for Motif"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.mock_mode = False
        
        # Safety settings for image generation
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }
        
        # Style presets for different party themes
        self.style_presets = {
            "party": "vibrant, colorful, festive, celebration, balloons, confetti, fun",
            "elegant": "sophisticated, refined, minimalist, classy, elegant, upscale",
            "fun": "playful, whimsical, cheerful, bright, cartoonish, cute",
            "romantic": "soft, dreamy, intimate, warm, pastel, romantic, gentle",
            "birthday": "colorful, celebratory, cake, balloons, party hats, festive",
            "wedding": "elegant, romantic, white, flowers, sophisticated, beautiful",
            "holiday": "festive, seasonal, traditional, celebratory, themed"
        }
        
        # Quality optimization settings
        self.quality_settings = {
            "high": {
                "resolution": "1024x1024",
                "quality": "high",
                "detail_level": "detailed, intricate, high resolution, professional quality",
                "processing_time": 3.0
            },
            "medium": {
                "resolution": "512x512", 
                "quality": "medium",
                "detail_level": "good quality, clear, well-defined",
                "processing_time": 2.0
            },
            "fast": {
                "resolution": "256x256",
                "quality": "fast",
                "detail_level": "basic quality, simple, clean",
                "processing_time": 1.0
            }
        }
        
        # Performance optimization
        self.cache_enabled = True
        self.prompt_cache = {}  # Cache for enhanced prompts
        self.model_cache = {}   # Cache for model instances
        
        self.model = None
    
    async def initialize(self):
        """Initialize the generator"""
        try:
            if not self.api_key or self.api_key == "your_gemini_api_key_here":
                logger.warning("Gemini API key not configured - using mock mode")
                self.mock_mode = True
                return True
            
            genai.configure(api_key=self.api_key)

            # Note: Gemini is a text/multimodal model, not an image generation model
            # We use it for text generation and image analysis, not actual image creation
            # For now, we'll use mock mode for image generation
            try:
                # Use gemini-pro for text generation (can help with prompt enhancement)
                self.model = genai.GenerativeModel('gemini-pro')
                # Test connection with a simple prompt
                test_response = await asyncio.to_thread(
                    self.model.generate_content,
                    "Hello",
                    safety_settings=self.safety_settings
                )
                logger.info(f"🎨 MotifGeminiGenerator initialized with gemini-pro for prompt enhancement!")
                logger.info(f"Note: Using mock mode for actual image generation (Gemini is text-only)")
                # Even though model is connected, use mock for image generation
                self.mock_mode = True
                return True
            except Exception as e:
                logger.info(f"Gemini API not available (expected) - using mock mode for image generation")
                logger.debug(f"Gemini init details: {e}")
                self.mock_mode = True
                return True
        except Exception as e:
            logger.error(f"Failed to initialize MotifGeminiGenerator: {e}")
            self.mock_mode = True
            return True
    
    async def generate_image_from_prompt(
        self,
        prompt: str,
        style: Optional[str] = None,
        quality: str = "standard",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate image from text prompt only"""
        try:
            # Check if in mock mode
            if self.mock_mode:
                return await self._mock_generation(prompt, style, user_id)
            
            # Enhance prompt with style
            enhanced_prompt = self._enhance_prompt(prompt, style)
            
            # Generate image
            response = await asyncio.to_thread(
                self.model.generate_content,
                enhanced_prompt,
                safety_settings=self.safety_settings
            )
            
            # Process response
            result = {
                "success": True,
                "image_data": response.text,  # This might need adjustment based on actual API response
                "prompt_used": enhanced_prompt,
                "style_applied": style,
                "generation_id": f"gemini_{user_id}_{asyncio.get_event_loop().time()}"
            }
            
            logger.info(f"Generated image for prompt: {enhanced_prompt[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "prompt_used": prompt
            }
    
    async def generate_image_from_inspiration(
        self,
        inspiration_image: bytes,
        prompt: str,
        style: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate image from inspiration image + prompt"""
        try:
            # Check if in mock mode
            if self.mock_mode:
                return await self._mock_generation(prompt, style, user_id, inspiration_image)
            
            # Analyze inspiration image
            inspiration_analysis = await self._analyze_inspiration_image(inspiration_image)
            
            # Enhance prompt with inspiration analysis
            enhanced_prompt = self._enhance_prompt_with_inspiration(
                prompt, 
                inspiration_analysis, 
                style
            )
            
            # Generate image
            response = await asyncio.to_thread(
                self.model.generate_content,
                [inspiration_image, enhanced_prompt],
                safety_settings=self.safety_settings
            )
            
            # Process response
            result = {
                "success": True,
                "image_data": response.text,  # This might need adjustment
                "prompt_used": enhanced_prompt,
                "inspiration_analysis": inspiration_analysis,
                "style_applied": style,
                "generation_id": f"gemini_insp_{user_id}_{asyncio.get_event_loop().time()}"
            }
            
            logger.info(f"Generated image from inspiration with prompt: {enhanced_prompt[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Inspiration-based image generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "prompt_used": prompt
            }
    
    async def _analyze_inspiration_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """Analyze inspiration image to extract style elements"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Analyze with Gemini
            analysis_prompt = """
            Analyze this image and describe:
            1. Main colors and color palette
            2. Style (elegant, fun, romantic, etc.)
            3. Mood and atmosphere
            4. Key visual elements
            5. Party decoration elements if any
            6. Overall aesthetic
            """
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                [image, analysis_prompt],
                safety_settings=self.safety_settings
            )
            
            return {
                "analysis": response.text,
                "image_size": image.size,
                "format": image.format
            }
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return {"analysis": "Unable to analyze image", "error": str(e)}
    
    def _enhance_prompt_with_quality(self, prompt: str, style: Optional[str] = None, quality_config: Dict[str, Any] = None) -> str:
        """Enhance prompt with style and quality optimization"""
        if quality_config is None:
            quality_config = self.quality_settings["medium"]
        
        # Start with base prompt
        enhanced = prompt.strip()
        
        # Add style if specified
        if style and style in self.style_presets:
            style_keywords = self.style_presets[style]
            enhanced += f", {style_keywords}"
        
        # Add quality-specific keywords
        enhanced += f", {quality_config['detail_level']}"
        
        # Add resolution hint
        enhanced += f", {quality_config['resolution']} resolution"
        
        # Add general quality keywords
        enhanced += ", high quality, detailed, professional, party decoration"
        
        return enhanced
    
    def _enhance_prompt(self, base_prompt: str, style: Optional[str] = None) -> str:
        """Enhance prompt with style information"""
        enhanced = base_prompt
        
        if style and style in self.style_presets:
            style_keywords = self.style_presets[style]
            enhanced = f"{enhanced}, {style_keywords}"
        
        # Add general quality keywords
        enhanced += ", high quality, detailed, professional"
        
        return enhanced
    
    def _enhance_prompt_with_inspiration(
        self, 
        base_prompt: str, 
        inspiration_analysis: Dict[str, Any], 
        style: Optional[str] = None
    ) -> str:
        """Enhance prompt with inspiration analysis"""
        enhanced = base_prompt
        
        # Add inspiration analysis
        if "analysis" in inspiration_analysis:
            enhanced += f", inspired by: {inspiration_analysis['analysis'][:200]}"
        
        # Add style if specified
        if style and style in self.style_presets:
            style_keywords = self.style_presets[style]
            enhanced += f", {style_keywords}"
        
        # Add quality keywords
        enhanced += ", high quality, detailed, professional, party decoration"
        
        return enhanced
    
    async def get_available_styles(self) -> List[Dict[str, str]]:
        """Get available style presets"""
        return [
            {"key": key, "name": key.title(), "description": description}
            for key, description in self.style_presets.items()
        ]
    
    async def get_available_qualities(self) -> List[Dict[str, Any]]:
        """Get available quality settings"""
        return [
            {
                "key": key,
                "name": key.title(),
                "description": config["detail_level"],
                "resolution": config["resolution"],
                "processing_time": config["processing_time"]
            }
            for key, config in self.quality_settings.items()
        ]
    
    async def collect_feedback(
        self, 
        generation_id: str, 
        rating: int, 
        feedback: Optional[str] = None
    ) -> bool:
        """Collect user feedback for training data"""
        try:
            # Store feedback for future training
            feedback_data = {
                "generation_id": generation_id,
                "rating": rating,
                "feedback": feedback,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            # TODO: Store in database for training pipeline
            logger.info(f"Collected feedback for {generation_id}: {rating}/5")
            return True
            
        except Exception as e:
            logger.error(f"Failed to collect feedback: {e}")
            return False
    
    async def _mock_generation(
        self,
        prompt: str,
        style: Optional[str] = None,
        user_id: Optional[str] = None,
        inspiration_image: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """Mock generation for testing when API key is not configured"""
        try:
            # Simulate generation delay
            await asyncio.sleep(2)
            
            # Create a mock base64 image (1x1 pixel PNG)
            mock_image_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            
            enhanced_prompt = self._enhance_prompt(prompt, style)
            
            result = {
                "success": True,
                "image_data": mock_image_data,
                "prompt_used": enhanced_prompt,
                "style_applied": style,
                "generation_id": f"mock_{user_id}_{asyncio.get_event_loop().time()}",
                "mock_mode": True
            }
            
            logger.info(f"Mock generated image for prompt: {enhanced_prompt[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Mock generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "prompt_used": prompt
            }
    
    async def generate_batch_images(
        self,
        prompts: List[str],
        style: Optional[str] = None,
        user_id: Optional[str] = None,
        max_concurrent: int = 3
    ) -> Dict[str, Any]:
        """Generate multiple images in batch with concurrency control"""
        try:
            if self.mock_mode:
                return await self._mock_batch_generation(prompts, style, user_id)
            
            # Limit concurrent requests to avoid rate limiting
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def generate_single(prompt: str) -> Dict[str, Any]:
                async with semaphore:
                    return await self.generate_image_from_prompt(prompt, style, user_id)
            
            # Generate all images concurrently
            tasks = [generate_single(prompt) for prompt in prompts]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            successful_generations = []
            failed_generations = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_generations.append({
                        "prompt": prompts[i],
                        "error": str(result),
                        "index": i
                    })
                elif result.get("success"):
                    successful_generations.append({
                        "prompt": prompts[i],
                        "generation_id": result["generation_id"],
                        "image_data": result["image_data"],
                        "prompt_used": result["prompt_used"],
                        "style_applied": result["style_applied"],
                        "index": i
                    })
                else:
                    failed_generations.append({
                        "prompt": prompts[i],
                        "error": result.get("error", "Unknown error"),
                        "index": i
                    })
            
            return {
                "success": True,
                "batch_id": str(uuid.uuid4()),
                "total_prompts": len(prompts),
                "successful_count": len(successful_generations),
                "failed_count": len(failed_generations),
                "successful_generations": successful_generations,
                "failed_generations": failed_generations,
                "generated_at": datetime.utcnow().isoformat(),
                "mock_mode": self.mock_mode
            }
            
        except Exception as e:
            logger.error(f"Batch generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "batch_id": str(uuid.uuid4()),
                "total_prompts": len(prompts),
                "successful_count": 0,
                "failed_count": len(prompts),
                "successful_generations": [],
                "failed_generations": [{"prompt": p, "error": str(e), "index": i} for i, p in enumerate(prompts)],
                "generated_at": datetime.utcnow().isoformat(),
                "mock_mode": self.mock_mode
            }
    
    async def _mock_batch_generation(
        self,
        prompts: List[str],
        style: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mock batch generation for testing"""
        try:
            # Simulate processing time
            await asyncio.sleep(1)
            
            successful_generations = []
            failed_generations = []
            
            for i, prompt in enumerate(prompts):
                if len(prompt.strip()) < 5:  # Simulate some failures
                    failed_generations.append({
                        "prompt": prompt,
                        "error": "Prompt too short",
                        "index": i
                    })
                else:
                    generation_id = str(uuid.uuid4())
                    enhanced_prompt = self._enhance_prompt(prompt, style)
                    
                    # Generate mock image data
                    mock_image_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
                    
                    successful_generations.append({
                        "prompt": prompt,
                        "generation_id": generation_id,
                        "image_data": mock_image_data,
                        "prompt_used": enhanced_prompt,
                        "style_applied": style,
                        "index": i
                    })
            
            return {
                "success": True,
                "batch_id": str(uuid.uuid4()),
                "total_prompts": len(prompts),
                "successful_count": len(successful_generations),
                "failed_count": len(failed_generations),
                "successful_generations": successful_generations,
                "failed_generations": failed_generations,
                "generated_at": datetime.utcnow().isoformat(),
                "mock_mode": True
            }
            
        except Exception as e:
            logger.error(f"Mock batch generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "batch_id": str(uuid.uuid4()),
                "total_prompts": len(prompts),
                "successful_count": 0,
                "failed_count": len(prompts),
                "successful_generations": [],
                "failed_generations": [{"prompt": p, "error": str(e), "index": i} for i, p in enumerate(prompts)],
                "generated_at": datetime.utcnow().isoformat(),
                "mock_mode": True
            }
