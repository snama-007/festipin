"""
Service management API routes for image generation providers.

This module provides endpoints for monitoring, configuring, and managing
the image generation service system.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from app.services.motif.service_manager import ServiceManager, RoutingStrategy
from app.services.motif.providers.base import GenerationRequest, GenerationQuality
from app.models.motif.generation import (
    ImageGenerationRequest, ImageGenerationResponse,
    BatchGenerationRequest, BatchGenerationResponse
)

router = APIRouter(prefix="/services", tags=["Service Management"])
logger = logging.getLogger(__name__)

# Global service manager instance
service_manager = ServiceManager()

async def get_service_manager() -> ServiceManager:
    """Dependency injector for service manager"""
    if not service_manager._initialized:
        await service_manager.initialize()
    return service_manager

@router.get("/status")
async def get_services_status(manager: ServiceManager = Depends(get_service_manager)):
    """Get status of all available services"""
    try:
        statuses = await manager.get_service_status()
        metrics = await manager.get_provider_metrics()
        
        return {
            "success": True,
            "services": statuses,
            "metrics": {
                name: {
                    "status": metrics.status.value,
                    "response_time": metrics.response_time,
                    "success_rate": metrics.success_rate,
                    "cost_per_image": metrics.cost_per_image,
                    "queue_length": metrics.queue_length,
                    "total_requests": metrics.total_requests,
                    "total_successful": metrics.total_successful,
                    "consecutive_failures": metrics.consecutive_failures,
                    "last_used": metrics.last_used.isoformat() if metrics.last_used else None
                } for name, metrics in metrics.items()
            },
            "current_priority": manager.primary_provider,
            "routing_strategy": manager.routing_strategy.value,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get service status: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/routing-strategy")
async def set_routing_strategy(
    strategy: str,
    manager: ServiceManager = Depends(get_service_manager)
):
    """Change service routing strategy"""
    try:
        # Validate strategy
        try:
            routing_strategy = RoutingStrategy(strategy)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid routing strategy. Valid options: {[s.value for s in RoutingStrategy]}"
            )
        
        manager.set_routing_strategy(routing_strategy)
        
        return {
            "success": True,
            "message": f"Routing strategy changed to {strategy}",
            "new_strategy": strategy,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to set routing strategy: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/primary-provider")
async def set_primary_provider(
    provider: str,
    manager: ServiceManager = Depends(get_service_manager)
):
    """Set primary provider"""
    try:
        if provider not in manager.providers:
            raise HTTPException(
                status_code=400,
                detail=f"Provider '{provider}' not found. Available providers: {list(manager.providers.keys())}"
            )
        
        manager.set_primary_provider(provider)
        
        return {
            "success": True,
            "message": f"Primary provider changed to {provider}",
            "new_primary": provider,
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to set primary provider: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/providers")
async def get_available_providers(manager: ServiceManager = Depends(get_service_manager)):
    """Get list of available providers with their capabilities"""
    try:
        providers_info = {}
        
        for provider_name, provider in manager.providers.items():
            try:
                # Get provider capabilities
                supported_models = await provider.get_supported_models()
                supported_styles = await provider.get_supported_styles()
                health = await provider.get_service_health()
                
                providers_info[provider_name] = {
                    "name": provider.provider_name,
                    "version": provider.provider_version,
                    "status": health.status.value,
                    "supported_models": supported_models,
                    "supported_styles": supported_styles,
                    "is_primary": provider_name == manager.primary_provider,
                    "is_fallback": provider_name in manager.fallback_providers,
                    "last_health_check": health.last_check.isoformat(),
                    "response_time": health.response_time,
                    "error_rate": health.error_rate,
                    "uptime": health.uptime
                }
            except Exception as e:
                logger.error(f"Error getting info for {provider_name}: {e}")
                providers_info[provider_name] = {
                    "name": provider_name,
                    "status": "unavailable",
                    "error": str(e)
                }
        
        return {
            "success": True,
            "providers": providers_info,
            "total_providers": len(providers_info),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get providers info: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/test-generation")
async def test_generation(
    request: ImageGenerationRequest,
    manager: ServiceManager = Depends(get_service_manager)
):
    """Test image generation with current service configuration"""
    try:
        # Convert to standardized request format
        generation_request = GenerationRequest(
            prompt=request.prompt,
            style=request.style,
            width=1024,
            height=1024,
            quality=GenerationQuality.STANDARD,
            user_id=request.user_id or "test_user"
        )
        
        # Generate image
        result = await manager.generate_image(generation_request)
        
        return {
            "success": result.success,
            "generation_id": result.generation_id,
            "provider_used": result.provider_used,
            "processing_time": result.processing_time,
            "cost": result.cost,
            "error": result.error,
            "metadata": result.metadata,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Test generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/cost-estimate")
async def estimate_generation_cost(
    request: ImageGenerationRequest,
    manager: ServiceManager = Depends(get_service_manager)
):
    """Estimate cost for generation across all providers"""
    try:
        # Convert to standardized request format
        generation_request = GenerationRequest(
            prompt=request.prompt,
            style=request.style,
            width=1024,
            height=1024,
            quality=GenerationQuality.STANDARD,
            user_id=request.user_id or "estimate_user"
        )
        
        estimates = {}
        
        for provider_name, provider in manager.providers.items():
            try:
                estimate = await provider.estimate_cost(generation_request)
                estimates[provider_name] = {
                    "estimated_cost": estimate.estimated_cost,
                    "currency": estimate.currency,
                    "confidence": estimate.confidence,
                    "breakdown": estimate.breakdown
                }
            except Exception as e:
                estimates[provider_name] = {
                    "error": str(e)
                }
        
        return {
            "success": True,
            "estimates": estimates,
            "request": {
                "prompt": request.prompt,
                "style": request.style,
                "quality": "standard"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Cost estimation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/health-check")
async def force_health_check(manager: ServiceManager = Depends(get_service_manager)):
    """Force health check for all providers"""
    try:
        health_results = {}
        
        for provider_name, provider in manager.providers.items():
            try:
                health = await provider.get_service_health()
                health_results[provider_name] = {
                    "status": health.status.value,
                    "response_time": health.response_time,
                    "error_rate": health.error_rate,
                    "uptime": health.uptime,
                    "last_check": health.last_check.isoformat(),
                    "metadata": health.metadata
                }
            except Exception as e:
                health_results[provider_name] = {
                    "status": "unavailable",
                    "error": str(e)
                }
        
        return {
            "success": True,
            "health_results": health_results,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/metrics")
async def get_service_metrics(manager: ServiceManager = Depends(get_service_manager)):
    """Get detailed service metrics"""
    try:
        metrics = await manager.get_provider_metrics()
        
        # Calculate system-wide metrics
        total_requests = sum(m.total_requests for m in metrics.values())
        total_successful = sum(m.total_successful for m in metrics.values())
        overall_success_rate = total_successful / total_requests if total_requests > 0 else 0
        
        avg_response_time = sum(m.response_time for m in metrics.values()) / len(metrics) if metrics else 0
        avg_cost = sum(m.cost_per_image for m in metrics.values()) / len(metrics) if metrics else 0
        
        return {
            "success": True,
            "system_metrics": {
                "total_requests": total_requests,
                "total_successful": total_successful,
                "overall_success_rate": overall_success_rate,
                "average_response_time": avg_response_time,
                "average_cost_per_image": avg_cost,
                "active_providers": len([m for m in metrics.values() if m.status.value == "healthy"]),
                "total_providers": len(metrics)
            },
            "provider_metrics": {
                name: {
                    "status": metrics.status.value,
                    "response_time": metrics.response_time,
                    "success_rate": metrics.success_rate,
                    "cost_per_image": metrics.cost_per_image,
                    "queue_length": metrics.queue_length,
                    "total_requests": metrics.total_requests,
                    "total_successful": metrics.total_successful,
                    "consecutive_failures": metrics.consecutive_failures,
                    "last_used": metrics.last_used.isoformat() if metrics.last_used else None
                } for name, metrics in metrics.items()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/reinitialize")
async def reinitialize_services(manager: ServiceManager = Depends(get_service_manager)):
    """Reinitialize all services"""
    try:
        # Close existing connections
        await manager.close()
        
        # Reinitialize
        success = await manager.initialize()
        
        return {
            "success": success,
            "message": "Services reinitialized successfully" if success else "Service reinitialization failed",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Service reinitialization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
