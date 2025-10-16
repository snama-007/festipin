"""
Performance Monitoring API Routes

API endpoints for monitoring and analyzing image generation performance.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import logging
from datetime import datetime

from app.services.motif.performance_monitor import performance_monitor, AggregatedMetrics

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/performance", tags=["Performance Monitoring"])

@router.get("/summary")
async def get_performance_summary(
    time_period: str = Query("1h", description="Time period: 1h, 24h, 7d")
):
    """Get aggregated performance metrics for a time period"""
    try:
        if time_period not in ["1h", "24h", "7d"]:
            raise HTTPException(status_code=400, detail="Time period must be one of: 1h, 24h, 7d")
        
        metrics = performance_monitor.get_performance_summary(time_period)
        
        return {
            "success": True,
            "metrics": {
                "total_generations": metrics.total_generations,
                "successful_generations": metrics.successful_generations,
                "failed_generations": metrics.failed_generations,
                "success_rate": round(metrics.success_rate * 100, 2),
                "average_processing_time": round(metrics.average_processing_time, 3),
                "median_processing_time": round(metrics.median_processing_time, 3),
                "p95_processing_time": round(metrics.p95_processing_time, 3),
                "p99_processing_time": round(metrics.p99_processing_time, 3),
                "most_used_quality": metrics.most_used_quality,
                "most_used_style": metrics.most_used_style,
                "time_period": metrics.time_period
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get performance summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quality")
async def get_quality_performance():
    """Get performance metrics by quality setting"""
    try:
        quality_performance = performance_monitor.get_quality_performance()
        
        # Format the response
        formatted_performance = {}
        for quality, stats in quality_performance.items():
            formatted_performance[quality] = {
                "average_time": round(stats["average_time"], 3),
                "median_time": round(stats["median_time"], 3),
                "min_time": round(stats["min_time"], 3),
                "max_time": round(stats["max_time"], 3),
                "count": stats["count"],
                "threshold_exceeded": stats["threshold_exceeded"],
                "threshold_exceeded_rate": round(stats["threshold_exceeded"] / stats["count"] * 100, 2) if stats["count"] > 0 else 0
            }
        
        return {
            "success": True,
            "quality_performance": formatted_performance
        }
        
    except Exception as e:
        logger.error(f"Failed to get quality performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/style")
async def get_style_performance():
    """Get performance metrics by style"""
    try:
        style_performance = performance_monitor.get_style_performance()
        
        # Format the response
        formatted_performance = {}
        for style, stats in style_performance.items():
            formatted_performance[style] = {
                "average_time": round(stats["average_time"], 3),
                "median_time": round(stats["median_time"], 3),
                "min_time": round(stats["min_time"], 3),
                "max_time": round(stats["max_time"], 3),
                "count": stats["count"]
            }
        
        return {
            "success": True,
            "style_performance": formatted_performance
        }
        
    except Exception as e:
        logger.error(f"Failed to get style performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}")
async def get_user_performance(user_id: str):
    """Get performance metrics for a specific user"""
    try:
        metrics = performance_monitor.get_user_performance(user_id)
        
        if metrics is None:
            return {
                "success": True,
                "message": "No performance data available for this user",
                "metrics": None
            }
        
        return {
            "success": True,
            "metrics": {
                "total_generations": metrics.total_generations,
                "successful_generations": metrics.successful_generations,
                "failed_generations": metrics.failed_generations,
                "success_rate": round(metrics.success_rate * 100, 2),
                "average_processing_time": round(metrics.average_processing_time, 3),
                "median_processing_time": round(metrics.median_processing_time, 3),
                "p95_processing_time": round(metrics.p95_processing_time, 3),
                "p99_processing_time": round(metrics.p99_processing_time, 3),
                "most_used_quality": metrics.most_used_quality,
                "most_used_style": metrics.most_used_style,
                "time_period": metrics.time_period
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get user performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_performance_alerts():
    """Get performance alerts based on thresholds"""
    try:
        alerts = performance_monitor.get_performance_alerts()
        
        return {
            "success": True,
            "alerts": alerts,
            "alert_count": len(alerts)
        }
        
    except Exception as e:
        logger.error(f"Failed to get performance alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear-metrics")
async def clear_old_metrics(
    days: int = Query(7, ge=1, le=30, description="Clear metrics older than this many days")
):
    """Clear performance metrics older than specified days"""
    try:
        performance_monitor.clear_old_metrics(days)
        
        return {
            "success": True,
            "message": f"Cleared metrics older than {days} days"
        }
        
    except Exception as e:
        logger.error(f"Failed to clear old metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def get_performance_health():
    """Get overall performance health status"""
    try:
        # Get recent performance summary
        metrics = performance_monitor.get_performance_summary("1h")
        alerts = performance_monitor.get_performance_alerts()
        
        # Determine health status
        health_status = "healthy"
        if alerts:
            error_alerts = [a for a in alerts if a.get("severity") == "error"]
            warning_alerts = [a for a in alerts if a.get("severity") == "warning"]
            
            if error_alerts:
                health_status = "critical"
            elif warning_alerts:
                health_status = "warning"
        
        # Calculate health score (0-100)
        health_score = 100
        if metrics.total_generations > 0:
            # Deduct points for low success rate
            if metrics.success_rate < 0.9:
                health_score -= 20
            elif metrics.success_rate < 0.95:
                health_score -= 10
            
            # Deduct points for slow processing
            if metrics.average_processing_time > 5.0:
                health_score -= 20
            elif metrics.average_processing_time > 3.0:
                health_score -= 10
            
            # Deduct points for alerts
            health_score -= len(alerts) * 5
        
        health_score = max(0, min(100, health_score))
        
        return {
            "success": True,
            "health": {
                "status": health_status,
                "score": health_score,
                "total_generations": metrics.total_generations,
                "success_rate": round(metrics.success_rate * 100, 2),
                "average_processing_time": round(metrics.average_processing_time, 3),
                "alert_count": len(alerts),
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get performance health: {e}")
        raise HTTPException(status_code=500, detail=str(e))
