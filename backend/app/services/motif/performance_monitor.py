"""
Performance Monitoring Service

Service for monitoring and optimizing image generation performance.
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for a single generation"""
    generation_id: str
    prompt_length: int
    style: Optional[str]
    quality: str
    processing_time: float
    success: bool
    error_message: Optional[str]
    timestamp: datetime
    user_id: str

@dataclass
class AggregatedMetrics:
    """Aggregated performance metrics"""
    total_generations: int
    successful_generations: int
    failed_generations: int
    average_processing_time: float
    median_processing_time: float
    p95_processing_time: float
    p99_processing_time: float
    success_rate: float
    most_used_quality: str
    most_used_style: Optional[str]
    time_period: str

class PerformanceMonitor:
    """Monitor and analyze image generation performance"""
    
    def __init__(self, max_history: int = 10000):
        self.max_history = max_history
        self.metrics_history: deque = deque(maxlen=max_history)
        self.user_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.quality_stats: Dict[str, List[float]] = defaultdict(list)
        self.style_stats: Dict[str, List[float]] = defaultdict(list)
        
        # Performance thresholds
        self.thresholds = {
            "fast": {"max_time": 2.0, "target_time": 1.0},
            "medium": {"max_time": 4.0, "target_time": 2.0},
            "high": {"max_time": 8.0, "target_time": 3.0}
        }
    
    def record_generation(
        self,
        generation_id: str,
        prompt_length: int,
        style: Optional[str],
        quality: str,
        processing_time: float,
        success: bool,
        error_message: Optional[str] = None,
        user_id: str = "anonymous"
    ):
        """Record performance metrics for a generation"""
        try:
            metric = PerformanceMetrics(
                generation_id=generation_id,
                prompt_length=prompt_length,
                style=style,
                quality=quality,
                processing_time=processing_time,
                success=success,
                error_message=error_message,
                timestamp=datetime.utcnow(),
                user_id=user_id
            )
            
            # Add to history
            self.metrics_history.append(metric)
            self.user_metrics[user_id].append(metric)
            
            # Update quality and style stats
            if success:
                self.quality_stats[quality].append(processing_time)
                if style:
                    self.style_stats[style].append(processing_time)
            
            logger.debug(f"Recorded metrics for generation {generation_id}: {processing_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to record metrics: {e}")
    
    def get_performance_summary(self, time_period: str = "1h") -> AggregatedMetrics:
        """Get aggregated performance metrics for a time period"""
        try:
            # Calculate time threshold
            now = datetime.utcnow()
            if time_period == "1h":
                threshold = now - timedelta(hours=1)
            elif time_period == "24h":
                threshold = now - timedelta(hours=24)
            elif time_period == "7d":
                threshold = now - timedelta(days=7)
            else:
                threshold = now - timedelta(hours=1)
            
            # Filter metrics by time period
            recent_metrics = [
                m for m in self.metrics_history 
                if m.timestamp >= threshold
            ]
            
            if not recent_metrics:
                return AggregatedMetrics(
                    total_generations=0,
                    successful_generations=0,
                    failed_generations=0,
                    average_processing_time=0.0,
                    median_processing_time=0.0,
                    p95_processing_time=0.0,
                    p99_processing_time=0.0,
                    success_rate=0.0,
                    most_used_quality="medium",
                    most_used_style=None,
                    time_period=time_period
                )
            
            # Calculate basic stats
            total_generations = len(recent_metrics)
            successful_generations = len([m for m in recent_metrics if m.success])
            failed_generations = total_generations - successful_generations
            success_rate = successful_generations / total_generations if total_generations > 0 else 0
            
            # Calculate processing time stats
            processing_times = [m.processing_time for m in recent_metrics if m.success]
            
            if processing_times:
                average_processing_time = statistics.mean(processing_times)
                median_processing_time = statistics.median(processing_times)
                p95_processing_time = statistics.quantiles(processing_times, n=20)[18] if len(processing_times) > 20 else max(processing_times)
                p99_processing_time = statistics.quantiles(processing_times, n=100)[98] if len(processing_times) > 100 else max(processing_times)
            else:
                average_processing_time = 0.0
                median_processing_time = 0.0
                p95_processing_time = 0.0
                p99_processing_time = 0.0
            
            # Find most used quality and style
            quality_counts = defaultdict(int)
            style_counts = defaultdict(int)
            
            for metric in recent_metrics:
                quality_counts[metric.quality] += 1
                if metric.style:
                    style_counts[metric.style] += 1
            
            most_used_quality = max(quality_counts.items(), key=lambda x: x[1])[0] if quality_counts else "medium"
            most_used_style = max(style_counts.items(), key=lambda x: x[1])[0] if style_counts else None
            
            return AggregatedMetrics(
                total_generations=total_generations,
                successful_generations=successful_generations,
                failed_generations=failed_generations,
                average_processing_time=average_processing_time,
                median_processing_time=median_processing_time,
                p95_processing_time=p95_processing_time,
                p99_processing_time=p99_processing_time,
                success_rate=success_rate,
                most_used_quality=most_used_quality,
                most_used_style=most_used_style,
                time_period=time_period
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate performance summary: {e}")
            return AggregatedMetrics(
                total_generations=0,
                successful_generations=0,
                failed_generations=0,
                average_processing_time=0.0,
                median_processing_time=0.0,
                p95_processing_time=0.0,
                p99_processing_time=0.0,
                success_rate=0.0,
                most_used_quality="medium",
                most_used_style=None,
                time_period=time_period
            )
    
    def get_quality_performance(self) -> Dict[str, Dict[str, float]]:
        """Get performance metrics by quality setting"""
        try:
            quality_performance = {}
            
            for quality, times in self.quality_stats.items():
                if times:
                    quality_performance[quality] = {
                        "average_time": statistics.mean(times),
                        "median_time": statistics.median(times),
                        "min_time": min(times),
                        "max_time": max(times),
                        "count": len(times),
                        "threshold_exceeded": sum(1 for t in times if t > self.thresholds.get(quality, {}).get("max_time", 10.0))
                    }
            
            return quality_performance
            
        except Exception as e:
            logger.error(f"Failed to get quality performance: {e}")
            return {}
    
    def get_style_performance(self) -> Dict[str, Dict[str, float]]:
        """Get performance metrics by style"""
        try:
            style_performance = {}
            
            for style, times in self.style_stats.items():
                if times:
                    style_performance[style] = {
                        "average_time": statistics.mean(times),
                        "median_time": statistics.median(times),
                        "min_time": min(times),
                        "max_time": max(times),
                        "count": len(times)
                    }
            
            return style_performance
            
        except Exception as e:
            logger.error(f"Failed to get style performance: {e}")
            return {}
    
    def get_user_performance(self, user_id: str) -> Optional[AggregatedMetrics]:
        """Get performance metrics for a specific user"""
        try:
            user_metrics = list(self.user_metrics.get(user_id, []))
            
            if not user_metrics:
                return None
            
            # Calculate stats for user
            total_generations = len(user_metrics)
            successful_generations = len([m for m in user_metrics if m.success])
            failed_generations = total_generations - successful_generations
            success_rate = successful_generations / total_generations if total_generations > 0 else 0
            
            processing_times = [m.processing_time for m in user_metrics if m.success]
            
            if processing_times:
                average_processing_time = statistics.mean(processing_times)
                median_processing_time = statistics.median(processing_times)
                p95_processing_time = statistics.quantiles(processing_times, n=20)[18] if len(processing_times) > 20 else max(processing_times)
                p99_processing_time = statistics.quantiles(processing_times, n=100)[98] if len(processing_times) > 100 else max(processing_times)
            else:
                average_processing_time = 0.0
                median_processing_time = 0.0
                p95_processing_time = 0.0
                p99_processing_time = 0.0
            
            # Find most used quality and style
            quality_counts = defaultdict(int)
            style_counts = defaultdict(int)
            
            for metric in user_metrics:
                quality_counts[metric.quality] += 1
                if metric.style:
                    style_counts[metric.style] += 1
            
            most_used_quality = max(quality_counts.items(), key=lambda x: x[1])[0] if quality_counts else "medium"
            most_used_style = max(style_counts.items(), key=lambda x: x[1])[0] if style_counts else None
            
            return AggregatedMetrics(
                total_generations=total_generations,
                successful_generations=successful_generations,
                failed_generations=failed_generations,
                average_processing_time=average_processing_time,
                median_processing_time=median_processing_time,
                p95_processing_time=p95_processing_time,
                p99_processing_time=p99_processing_time,
                success_rate=success_rate,
                most_used_quality=most_used_quality,
                most_used_style=most_used_style,
                time_period="all_time"
            )
            
        except Exception as e:
            logger.error(f"Failed to get user performance: {e}")
            return None
    
    def get_performance_alerts(self) -> List[Dict[str, Any]]:
        """Get performance alerts based on thresholds"""
        try:
            alerts = []
            
            # Check quality performance against thresholds
            quality_performance = self.get_quality_performance()
            
            for quality, stats in quality_performance.items():
                threshold = self.thresholds.get(quality, {}).get("max_time", 10.0)
                
                if stats["average_time"] > threshold:
                    alerts.append({
                        "type": "performance_degradation",
                        "severity": "warning",
                        "message": f"Average processing time for {quality} quality ({stats['average_time']:.2f}s) exceeds threshold ({threshold}s)",
                        "quality": quality,
                        "current_time": stats["average_time"],
                        "threshold": threshold
                    })
                
                if stats["threshold_exceeded"] > stats["count"] * 0.1:  # More than 10% exceed threshold
                    alerts.append({
                        "type": "threshold_exceeded",
                        "severity": "error",
                        "message": f"{stats['threshold_exceeded']}/{stats['count']} generations exceeded {quality} quality threshold",
                        "quality": quality,
                        "exceeded_count": stats["threshold_exceeded"],
                        "total_count": stats["count"]
                    })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get performance alerts: {e}")
            return []
    
    def clear_old_metrics(self, days: int = 7):
        """Clear metrics older than specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Clear from main history
            self.metrics_history = deque(
                [m for m in self.metrics_history if m.timestamp >= cutoff_date],
                maxlen=self.max_history
            )
            
            # Clear from user metrics
            for user_id in list(self.user_metrics.keys()):
                self.user_metrics[user_id] = deque(
                    [m for m in self.user_metrics[user_id] if m.timestamp >= cutoff_date],
                    maxlen=1000
                )
                
                # Remove empty user metrics
                if not self.user_metrics[user_id]:
                    del self.user_metrics[user_id]
            
            logger.info(f"Cleared metrics older than {days} days")
            
        except Exception as e:
            logger.error(f"Failed to clear old metrics: {e}")

# Global performance monitor instance
performance_monitor = PerformanceMonitor()
