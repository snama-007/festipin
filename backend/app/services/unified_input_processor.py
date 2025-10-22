"""
Unified Input Processor

Single processor for all input types:
- Text only
- Image/URL only
- Text + Image combined

Integrates Smart Router, Vision AI, and LLM Planning
"""

from typing import Dict, Any, Optional
from app.core.logging import logger
from app.services.smart_input_router import get_smart_router
from app.services.vision_processor import get_vision_processor
from app.services.vision_to_text import get_vision_converter


class UnifiedInputProcessor:
    """
    Unified processor for all input types with intelligent routing

    Handles:
    1. Text-only inputs → Smart Router → Regex or LLM
    2. Image-only inputs → Vision AI → Text description → Smart Router
    3. Combined inputs → Vision AI + Text → Smart Router
    """

    def __init__(self):
        self.router = get_smart_router()
        self.vision_processor = get_vision_processor()
        self.vision_converter = get_vision_converter()

        logger.info("Unified Input Processor initialized")

    async def process(
        self,
        content: str,
        source_type: str = "text",
        image_url: Optional[str] = None,
        tags: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Process any type of input with optimal strategy

        Args:
            content: User's text input
            source_type: Type of input (text, image, url, upload)
            image_url: Optional image URL for vision analysis
            tags: Optional tags from user

        Returns:
            Dict with:
            - natural_language: Combined description for agent classification
            - extracted_data: Structured extraction results
            - vision_data: Vision analysis if image provided
            - routing_info: Which processors were used
            - tags: Enhanced tags for agent routing
        """

        logger.info(
            "Processing unified input",
            source_type=source_type,
            has_text=bool(content),
            has_image=bool(image_url),
            content_length=len(content) if content else 0
        )

        result = {
            "natural_language": "",
            "extracted_data": {},
            "vision_data": None,
            "routing_info": {},
            "tags": tags or [],
            "processor_chain": []
        }

        descriptions = []
        vision_description = None
        vision_confidence = None

        # Step 1: Process image if provided
        if image_url or source_type in ["image", "url", "upload"]:
            try:
                vision_result = await self._process_image(image_url or content)

                if vision_result:
                    result["vision_data"] = vision_result["scene_data"]
                    vision_description = vision_result["text_description"]
                    vision_confidence = vision_result["scene_data"].confidence  # Extract vision confidence
                    descriptions.append(f"Image shows: {vision_description}")

                    # Add vision-derived tags
                    result["tags"].extend(vision_result["tags"])

                    # Add agent context from vision
                    result["agent_context"] = vision_result["agent_context"]

                    result["processor_chain"].append("vision_ai")

                    logger.info(
                        "Vision processing complete",
                        theme=vision_result["scene_data"].theme if vision_result["scene_data"] else None,
                        tags_added=len(vision_result["tags"])
                    )
            except Exception as e:
                logger.error(
                    "Vision processing failed",
                    error=str(e),
                    error_type=type(e).__name__
                )
                # Continue processing with text only

        # Step 2: Process text content (if provided)
        if content and source_type == "text":
            descriptions.append(content)

        # Step 3: Combine all descriptions
        combined_description = "\n\n".join(descriptions)

        if not combined_description:
            logger.warning("No content to process")
            return result

        # Step 4: Use Smart Router for extraction
        try:
            extraction_result = await self.router.process_input(
                user_input=combined_description,
                image_description=vision_description,
                vision_confidence=vision_confidence
            )

            result["natural_language"] = extraction_result.get("natural_language", combined_description)
            result["extracted_data"] = extraction_result.get("extracted_data", {})
            result["routing_info"] = extraction_result.get("routing", {})
            result["confidence"] = extraction_result.get("confidence", 0.0)
            result["needs_user_input"] = extraction_result.get("needs_user_input", False)
            result["missing_fields"] = extraction_result.get("missing_fields", [])

            processor = extraction_result.get("processor", "unknown")
            result["processor_chain"].append(processor)

            logger.info(
                "Extraction complete",
                processor=processor,
                confidence=result["confidence"],
                chain=result["processor_chain"]
            )

        except Exception as e:
            logger.error(
                "Extraction failed",
                error=str(e),
                error_type=type(e).__name__
            )
            result["natural_language"] = combined_description
            result["error"] = str(e)

        # Step 5: Deduplicate tags
        result["tags"] = list(set(result["tags"]))

        logger.info(
            "Unified processing complete",
            processor_chain=result["processor_chain"],
            final_tags=result["tags"],
            confidence=result.get("confidence", 0.0)
        )

        return result

    async def _process_image(self, image_url: str) -> Optional[Dict[str, Any]]:
        """
        Process image with Vision AI

        Returns:
            Dict with scene_data, text_description, tags, agent_context
        """

        logger.info("Processing image with Vision AI", url=image_url[:50])

        try:
            # Analyze image
            scene_data = await self.vision_processor.analyze_party_image(image_url)

            # Convert to text description
            text_description = self.vision_converter.scene_to_text(scene_data, verbose=True)

            # Extract tags for agent routing
            tags = self.vision_converter.scene_to_tags(scene_data)

            # Get agent-specific context
            agent_context = self.vision_converter.scene_to_agent_context(scene_data)

            return {
                "scene_data": scene_data,
                "text_description": text_description,
                "tags": tags,
                "agent_context": agent_context
            }

        except Exception as e:
            logger.error(
                "Vision processing error",
                error=str(e),
                error_type=type(e).__name__,
                url=image_url[:50]
            )
            return None


# Singleton instance
_processor: Optional[UnifiedInputProcessor] = None


def get_unified_processor() -> UnifiedInputProcessor:
    """Get global unified processor instance"""
    global _processor
    if _processor is None:
        _processor = UnifiedInputProcessor()
    return _processor


# Export
__all__ = ["UnifiedInputProcessor", "get_unified_processor"]
