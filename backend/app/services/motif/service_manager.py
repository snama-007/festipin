"""
Service manager for intelligent routing and fallback between image generation providers.

This module manages multiple providers, implements load balancing, health monitoring,
and automatic failover strategies with optimized performance.
"""

import asyncio
import time
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque
import weakref

from app.core.logger import logger, log_info, log_error, log_warning, log_metrics
from .providers.base import (
    ImageGenerationProvider, GenerationRequest, GenerationResponse,
    BatchGenerationRequest, BatchGenerationResponse, ServiceHealth,
    ServiceStatus, GenerationQuality
)
from .providers.runware_provider import RunwareProvider

class RoutingStrategy(str, Enum):
    """Service routing strategies"""
    PRIMARY_FIRST = "primary_first"  # Try primary, then fallback
    ROUND_ROBIN = "round_robin"       # Distribute evenly
    LEAST_LOADED = "least_loaded"     # Route to least busy service
    COST_OPTIMIZED = "cost_optimized" # Route based on cost
    QUALITY_FOCUSED = "quality_focused" # Route to highest quality
    HEALTH_BASED = "health_based"    # Route based on health status

@dataclass
class ProviderMetrics:
    """Optimized metrics for a provider with caching"""
    name: str
    status: ServiceStatus = ServiceStatus.UNAVAILABLE
    response_time: float = 0.0
    success_rate: float = 1.0
    cost_per_image: float = 0.02
    queue_length: int = 0
    last_used: datetime = field(default_factory=datetime.utcnow)
    consecutive_failures: int = 0
    total_requests: int = 0
    total_successful: int = 0
    _response_times: deque = field(default_factory=lambda: deque(maxlen=100))
    _last_health_check: Optional[datetime] = None
    _health_cache: Optional[ServiceHealth] = None
    
    def update_response_time(self, response_time: float):
        """Update response time with moving average"""
        self._response_times.append(response_time)
        self.response_time = sum(self._response_times) / len(self._response_times)
    
    def get_cached_health(self, max_age_seconds: int = 30) -> Optional[ServiceHealth]:
        """Get cached health if still valid"""
        if (self._health_cache and self._last_health_check and 
            (datetime.utcnow() - self._last_health_check).seconds < max_age_seconds):
            return self._health_cache
        return None
    
    def cache_health(self, health: ServiceHealth):
        """Cache health information"""
        self._health_cache = health
        self._last_health_check = datetime.utcnow()
        self.status = health.status

class ServiceManager:
    """
    Optimized intelligent service manager for image generation providers.
    
    Features:
    - Automatic provider discovery and registration
    - Health monitoring and status tracking with caching
    - Intelligent routing with multiple strategies
    - Automatic failover and load balancing
    - Cost optimization and quality-based routing
    - Metrics collection and performance tracking
    - Connection pooling and resource management
    """
    
    def __init__(self):
        self.providers: Dict[str, ImageGenerationProvider] = {}
        self.provider_metrics: Dict[str, ProviderMetrics] = {}
        self.routing_strategy = RoutingStrategy.PRIMARY_FIRST
        self.primary_provider = "runware"
        self.fallback_providers = ["gemini"]
        
        # Optimized health monitoring with caching
        self.health_check_interval = 60  # seconds
        self.health_cache_ttl = 30  # seconds
        self._health_cache: Dict[str, Tuple[datetime, ServiceHealth]] = {}
        self._last_health_check = None
        self._health_check_lock = asyncio.Lock()
        
        # Optimized load balancing with atomic operations
        self._round_robin_index = 0
        self._round_robin_lock = asyncio.Lock()
        self._request_counts: Dict[str, int] = defaultdict(int)
        
        # Performance tracking with bounded collections
        self._performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self._max_history_size = 100
        
        # Initialization state with thread safety
        self._initialized = False
        self._initialization_lock = asyncio.Lock()
        
        # Connection pooling
        self._connection_pool: Dict[str, Any] = {}
        self._pool_lock = asyncio.Lock()
        
        # Circuit breaker pattern for failed providers
        self._circuit_breakers: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'failure_count': 0,
            'last_failure': None,
            'state': 'closed',  # closed, open, half-open
            'failure_threshold': 5,
            'recovery_timeout': 60
        })
    
    async def initialize(self) -> bool:
        """Initialize the service manager and all providers"""
        async with self._initialization_lock:
            if self._initialized:
                return True
            
            try:
                log_info("Initializing Service Manager")

                # Register providers
                await self._register_providers()

                # Initialize all providers
                initialization_results = await self._initialize_providers()

                # Start health monitoring
                asyncio.create_task(self._health_monitoring_loop())

                self._initialized = True

                successful_providers = [name for name, success in initialization_results.items() if success]
                log_info(
                    "Service Manager initialized",
                    providers=successful_providers,
                    provider_count=len(successful_providers)
                )

                return len(successful_providers) > 0

            except Exception as e:
                log_error("Failed to initialize Service Manager", error=str(e), error_type=type(e).__name__)
                return False
    
    async def generate_image(self, request: GenerationRequest) -> GenerationResponse:
        """Generate image with intelligent provider selection and circuit breaker"""
        try:
            # Ensure manager is initialized
            if not self._initialized:
                if not await self.initialize():
                    return self._create_error_response(
                        request, "Service manager initialization failed"
                    )
            
            # Select optimal provider with circuit breaker check
            provider_name = await self._select_provider_with_circuit_breaker(request)
            if not provider_name:
                return self._create_error_response(
                    request, "No healthy providers available"
                )
            
            # Get provider and generate image
            provider = self.providers[provider_name]
            start_time = time.time()
            
            try:
                # Check circuit breaker state
                if self._is_circuit_open(provider_name):
                    log_warning(
                        "Circuit breaker open, trying fallback",
                        provider=provider_name,
                        request_id=request.request_id
                    )
                    fallback_result = await self._try_fallback(request, [provider_name])
                    if fallback_result:
                        return fallback_result
                    return self._create_error_response(request, f"Circuit breaker open for {provider_name}")
                
                result = await provider.generate_image(request)
                processing_time = time.time() - start_time

                # Update metrics and circuit breaker
                await self._update_provider_metrics(provider_name, result, processing_time)
                self._record_success(provider_name)

                # Log metrics
                log_metrics(
                    "image_generation_duration",
                    processing_time,
                    provider=provider_name,
                    quality=request.quality.value if request.quality else "standard",
                    success=result.success
                )

                return result

            except Exception as e:
                log_error(
                    "Generation failed",
                    provider=provider_name,
                    error=str(e),
                    error_type=type(e).__name__,
                    request_id=request.request_id
                )
                
                # Record failure in circuit breaker
                self._record_failure(provider_name)
                
                # Try fallback if primary failed
                if provider_name == self.primary_provider:
                    fallback_result = await self._try_fallback(request, [provider_name])
                    if fallback_result:
                        return fallback_result
                
                return self._create_error_response(request, str(e))
                
        except Exception as e:
            logger.error(f"Service manager error: {e}")
            return self._create_error_response(request, f"Service manager error: {str(e)}")
    
    async def generate_batch(self, request: BatchGenerationRequest) -> BatchGenerationResponse:
        """Generate multiple images with load balancing"""
        try:
            # Ensure manager is initialized
            if not self._initialized:
                if not await self.initialize():
                    return self._create_batch_error_response(
                        request, "Service manager initialization failed"
                    )
            
            # Get healthy providers
            healthy_providers = await self._get_healthy_providers()
            if not healthy_providers:
                return self._create_batch_error_response(
                    request, "No healthy providers available"
                )
            
            # Distribute requests across providers
            if self.routing_strategy == RoutingStrategy.ROUND_ROBIN:
                results = await self._round_robin_batch(request, healthy_providers)
            else:
                results = await self._primary_first_batch(request, healthy_providers)
            
            # Calculate batch metrics
            successful_count = sum(1 for r in results if r.success)
            failed_count = len(results) - successful_count
            total_cost = sum(r.cost or 0 for r in results)
            total_processing_time = max(r.processing_time for r in results)
            
            return BatchGenerationResponse(
                success=failed_count == 0 or not request.fail_fast,
                results=results,
                total_cost=total_cost,
                total_processing_time=total_processing_time,
                successful_count=successful_count,
                failed_count=failed_count
            )
            
        except Exception as e:
            logger.error(f"Batch generation error: {e}")
            return self._create_batch_error_response(request, str(e))
    
    async def get_service_status(self) -> Dict[str, ServiceHealth]:
        """Get status of all services"""
        statuses = {}
        
        for provider_name, provider in self.providers.items():
            try:
                # Check cache first
                cached_health = self._get_cached_health(provider_name)
                if cached_health:
                    statuses[provider_name] = cached_health
                else:
                    health = await provider.get_service_health()
                    self._cache_health(provider_name, health)
                    statuses[provider_name] = health
                    
            except Exception as e:
                logger.error(f"Error getting status for {provider_name}: {e}")
                statuses[provider_name] = ServiceHealth(
                    status=ServiceStatus.UNAVAILABLE,
                    metadata={"error": str(e)}
                )
        
        return statuses
    
    def set_routing_strategy(self, strategy: RoutingStrategy):
        """Change routing strategy"""
        self.routing_strategy = strategy
        logger.info(f"Routing strategy changed to: {strategy}")
    
    def set_primary_provider(self, provider_name: str):
        """Set primary provider"""
        if provider_name in self.providers:
            self.primary_provider = provider_name
            logger.info(f"Primary provider changed to: {provider_name}")
        else:
            logger.warning(f"Provider {provider_name} not found")
    
    async def get_provider_metrics(self) -> Dict[str, ProviderMetrics]:
        """Get metrics for all providers"""
        return self.provider_metrics.copy()
    
    async def close(self):
        """Close all provider connections"""
        for provider_name, provider in self.providers.items():
            try:
                await provider.close()
                logger.info(f"Closed {provider_name} provider")
            except Exception as e:
                logger.error(f"Error closing {provider_name}: {e}")
    
    # Private methods
    
    async def _register_providers(self):
        """Register all available providers"""
        # Register Runware provider
        try:
            runware_provider = RunwareProvider()
            self.providers["runware"] = runware_provider
            log_info("Registered Runware provider", provider="runware")
        except ImportError as e:
            log_warning("Runware provider not available", reason="library_not_installed", error=str(e))
        except Exception as e:
            log_error("Failed to register Runware provider", error=str(e), error_type=type(e).__name__)

        # Register Gemini provider
        try:
            from .providers.gemini_provider import GeminiProvider
            gemini_provider = GeminiProvider()
            self.providers["gemini"] = gemini_provider
            log_info("Registered Gemini provider", provider="gemini")
        except ImportError as e:
            log_warning("Gemini provider not available", reason="import_error", error=str(e))
        except Exception as e:
            log_error("Failed to register Gemini provider", error=str(e), error_type=type(e).__name__)
    
    async def _initialize_providers(self) -> Dict[str, bool]:
        """Initialize all registered providers"""
        results = {}
        
        for provider_name, provider in self.providers.items():
            try:
                success = await provider.initialize()
                results[provider_name] = success
                
                if success:
                    # Initialize metrics
                    self.provider_metrics[provider_name] = ProviderMetrics(
                        name=provider_name,
                        status=ServiceStatus.HEALTHY,
                        response_time=0.0,
                        success_rate=1.0,
                        cost_per_image=0.02,  # Default estimate
                        queue_length=0,
                        last_used=datetime.utcnow(),
                        consecutive_failures=0,
                        total_requests=0,
                        total_successful=0
                    )
                    
                log_info(
                    "Provider initialization result",
                    provider=provider_name,
                    success=success
                )
                
            except Exception as e:
                logger.error(f"Error initializing {provider_name}: {e}")
                results[provider_name] = False
        
        return results
    
    async def _select_provider_with_circuit_breaker(self, request: GenerationRequest) -> Optional[str]:
        """Select optimal provider with circuit breaker protection"""
        healthy_providers = await self._get_healthy_providers()
        
        if not healthy_providers:
            return None
        
        # Filter out providers with open circuit breakers
        available_providers = [
            p for p in healthy_providers 
            if not self._is_circuit_open(p)
        ]
        
        if not available_providers:
            # If all circuits are open, try half-open circuits
            available_providers = [
                p for p in healthy_providers 
                if self._is_circuit_half_open(p)
            ]
        
        if not available_providers:
            return None
        
        # Respect preferred provider if available
        if (request.preferred_provider and 
            request.preferred_provider in available_providers):
            return request.preferred_provider
        
        # Apply routing strategy
        return await self._select_provider_by_strategy(available_providers, request)
    
    async def _select_provider_by_strategy(self, providers: List[str], request: GenerationRequest) -> Optional[str]:
        """Select provider based on routing strategy"""
        if not providers:
            return None
        
        if self.routing_strategy == RoutingStrategy.PRIMARY_FIRST:
            return self.primary_provider if self.primary_provider in providers else providers[0]
        
        elif self.routing_strategy == RoutingStrategy.ROUND_ROBIN:
            return await self._round_robin_select(providers)
        
        elif self.routing_strategy == RoutingStrategy.LEAST_LOADED:
            return self._least_loaded_select(providers)
        
        elif self.routing_strategy == RoutingStrategy.COST_OPTIMIZED:
            return await self._cost_optimized_select(providers, request)
        
        elif self.routing_strategy == RoutingStrategy.QUALITY_FOCUSED:
            return await self._quality_focused_select(providers, request)
        
        elif self.routing_strategy == RoutingStrategy.HEALTH_BASED:
            return self._health_based_select(providers)
        
        # Default to primary first
        return self.primary_provider if self.primary_provider in providers else providers[0]
    
    def _is_circuit_open(self, provider_name: str) -> bool:
        """Check if circuit breaker is open for provider"""
        breaker = self._circuit_breakers[provider_name]
        if breaker['state'] != 'open':
            return False
        
        # Check if recovery timeout has passed
        if breaker['last_failure']:
            time_since_failure = (datetime.utcnow() - breaker['last_failure']).seconds
            if time_since_failure >= breaker['recovery_timeout']:
                breaker['state'] = 'half-open'
                return False
        
        return True
    
    def _is_circuit_half_open(self, provider_name: str) -> bool:
        """Check if circuit breaker is half-open for provider"""
        return self._circuit_breakers[provider_name]['state'] == 'half-open'
    
    def _record_success(self, provider_name: str):
        """Record successful request for circuit breaker"""
        breaker = self._circuit_breakers[provider_name]
        if breaker['state'] == 'half-open':
            breaker['state'] = 'closed'
            breaker['failure_count'] = 0
    
    def _record_failure(self, provider_name: str):
        """Record failed request for circuit breaker"""
        breaker = self._circuit_breakers[provider_name]
        breaker['failure_count'] += 1
        breaker['last_failure'] = datetime.utcnow()
        
        if breaker['failure_count'] >= breaker['failure_threshold']:
            breaker['state'] = 'open'
            log_warning(
                "Circuit breaker opened",
                provider=provider_name,
                failure_count=breaker['failure_count'],
                threshold=breaker['failure_threshold']
            )
    
    async def _get_healthy_providers(self) -> List[str]:
        """Get list of healthy providers"""
        healthy = []
        
        for provider_name, provider in self.providers.items():
            try:
                health = await provider.get_service_health()
                if health.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]:
                    healthy.append(provider_name)
            except Exception:
                continue
        
        return healthy
    
    async def _round_robin_select(self, providers: List[str]) -> str:
        """Optimized round-robin provider selection with atomic operations"""
        if not providers:
            return None
        
        async with self._round_robin_lock:
            provider = providers[self._round_robin_index % len(providers)]
            self._round_robin_index += 1
            return provider
    
    def _least_loaded_select(self, providers: List[str]) -> str:
        """Select least loaded provider with optimized metrics lookup"""
        if not providers:
            return None
        
        def get_load_score(provider_name: str) -> float:
            metrics = self.provider_metrics.get(provider_name)
            if not metrics:
                return float('inf')
            
            # Calculate load score based on queue length and response time
            queue_weight = 0.7
            response_weight = 0.3
            return (metrics.queue_length * queue_weight + 
                   metrics.response_time * response_weight)
        
        return min(providers, key=get_load_score)
    
    async def _cost_optimized_select(self, providers: List[str], request: GenerationRequest) -> str:
        """Select most cost-effective provider with caching"""
        if not providers:
            return None
        
        # Use cached cost estimates if available
        cost_cache = getattr(self, '_cost_cache', {})
        cache_key = f"{request.quality}_{request.width}_{request.height}"
        
        if cache_key not in cost_cache:
            cost_cache[cache_key] = {}
            self._cost_cache = cost_cache
        
        costs = {}
        for provider_name in providers:
            if provider_name in cost_cache[cache_key]:
                costs[provider_name] = cost_cache[cache_key][provider_name]
            else:
                try:
                    provider = self.providers[provider_name]
                    estimate = await provider.estimate_cost(request)
                    costs[provider_name] = estimate.estimated_cost
                    cost_cache[cache_key][provider_name] = estimate.estimated_cost
                except Exception:
                    costs[provider_name] = float('inf')
        
        return min(providers, key=lambda p: costs.get(p, float('inf')))
    
    async def _quality_focused_select(self, providers: List[str], request: GenerationRequest) -> str:
        """Select highest quality provider with quality scoring"""
        if not providers:
            return None
        
        # Quality scoring based on provider capabilities and metrics
        quality_scores = {}
        for provider_name in providers:
            metrics = self.provider_metrics.get(provider_name)
            if not metrics:
                continue
            
            # Calculate quality score
            success_rate_score = metrics.success_rate * 0.4
            response_time_score = max(0, 1 - (metrics.response_time / 10)) * 0.3  # Normalize to 0-1
            uptime_score = getattr(metrics, 'uptime', 0.95) * 0.3
            
            quality_scores[provider_name] = (
                success_rate_score + response_time_score + uptime_score
            )
        
        if not quality_scores:
            return providers[0]
        
        return max(providers, key=lambda p: quality_scores.get(p, 0))
    
    def _health_based_select(self, providers: List[str]) -> str:
        """Select provider based on health status with priority scoring"""
        if not providers:
            return None
        
        # Health priority scoring
        health_priority = {
            ServiceStatus.HEALTHY: 4,
            ServiceStatus.DEGRADED: 3,
            ServiceStatus.UNHEALTHY: 2,
            ServiceStatus.UNAVAILABLE: 1
        }
        
        def get_health_score(provider_name: str) -> int:
            metrics = self.provider_metrics.get(provider_name)
            if not metrics:
                return 0
            return health_priority.get(metrics.status, 0)
        
        return max(providers, key=get_health_score)
    
    async def _try_fallback(self, request: GenerationRequest, exclude: List[str]) -> Optional[GenerationResponse]:
        """Try fallback providers"""
        healthy_providers = await self._get_healthy_providers()
        fallback_providers = [p for p in healthy_providers if p not in exclude]
        
        for provider_name in fallback_providers:
            try:
                provider = self.providers[provider_name]
                result = await provider.generate_image(request)
                if result.success:
                    logger.info(f"Fallback successful with {provider_name}")
                    return result
            except Exception as e:
                logger.warning(f"Fallback failed with {provider_name}: {e}")
                continue
        
        return None
    
    async def _round_robin_batch(self, request: BatchGenerationRequest, providers: List[str]) -> List[GenerationResponse]:
        """Distribute batch requests using round-robin"""
        results = []
        
        for i, req in enumerate(request.requests):
            provider_name = providers[i % len(providers)]
            provider = self.providers[provider_name]
            
            try:
                result = await provider.generate_image(req)
                results.append(result)
            except Exception as e:
                results.append(self._create_error_response(req, str(e)))
        
        return results
    
    async def _primary_first_batch(self, request: BatchGenerationRequest, providers: List[str]) -> List[GenerationResponse]:
        """Distribute batch requests using primary-first strategy"""
        results = []
        primary = self.primary_provider if self.primary_provider in providers else providers[0]
        
        for req in request.requests:
            try:
                provider = self.providers[primary]
                result = await provider.generate_image(req)
                results.append(result)
            except Exception as e:
                # Try fallback
                fallback_result = await self._try_fallback(req, [primary])
                if fallback_result:
                    results.append(fallback_result)
                else:
                    results.append(self._create_error_response(req, str(e)))
        
        return results
    
    async def _update_provider_metrics(self, provider_name: str, result: GenerationResponse, processing_time: float):
        """Optimized provider metrics update with atomic operations"""
        if provider_name not in self.provider_metrics:
            return
        
        metrics = self.provider_metrics[provider_name]
        
        # Atomic update operations
        metrics.total_requests += 1
        metrics.last_used = datetime.utcnow()
        
        if result.success:
            metrics.total_successful += 1
            metrics.consecutive_failures = 0
            
            # Update response time with moving average
            metrics.update_response_time(processing_time)
            
        else:
            metrics.consecutive_failures += 1
        
        # Update success rate
        metrics.success_rate = metrics.total_successful / metrics.total_requests
        
        # Update cost if available
        if result.cost:
            metrics.cost_per_image = result.cost
        
        # Update performance history
        self._performance_history[provider_name].append(processing_time)
    
    async def _health_monitoring_loop(self):
        """Background health monitoring loop"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                for provider_name, provider in self.providers.items():
                    try:
                        health = await provider.get_service_health()
                        self._cache_health(provider_name, health)
                        
                        # Update metrics status
                        if provider_name in self.provider_metrics:
                            self.provider_metrics[provider_name].status = health.status
                        
                    except Exception as e:
                        logger.error(f"Health check failed for {provider_name}: {e}")
                
                self._last_health_check = datetime.utcnow()
                
            except Exception as e:
                logger.error(f"Health monitoring loop error: {e}")
    
    def _cache_health(self, provider_name: str, health: ServiceHealth):
        """Cache health information"""
        self._health_cache[provider_name] = (datetime.utcnow(), health)
    
    def _get_cached_health(self, provider_name: str) -> Optional[ServiceHealth]:
        """Get cached health information"""
        if provider_name not in self._health_cache:
            return None
        
        cached_time, health = self._health_cache[provider_name]
        if (datetime.utcnow() - cached_time).seconds < self.health_cache_ttl:
            return health
        
        return None
    
    def _create_error_response(self, request: GenerationRequest, error: str) -> GenerationResponse:
        """Create error response"""
        return GenerationResponse(
            success=False,
            generation_id=f"error_{int(time.time())}",
            image_data="",
            provider_used="service_manager",
            processing_time=0,
            error=error,
            metadata={"request_id": request.request_id}
        )
    
    def _create_batch_error_response(self, request: BatchGenerationRequest, error: str) -> BatchGenerationResponse:
        """Create batch error response"""
        error_results = [
            self._create_error_response(req, error) for req in request.requests
        ]
        
        return BatchGenerationResponse(
            success=False,
            results=error_results,
            total_processing_time=0,
            successful_count=0,
            failed_count=len(request.requests)
        )
