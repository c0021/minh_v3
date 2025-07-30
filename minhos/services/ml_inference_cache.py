#!/usr/bin/env python3
"""
ML Inference Cache Service

Optimizes ML model inference through intelligent caching, batch processing,
and performance monitoring to achieve <100ms latency targets.
"""

import asyncio
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from collections import defaultdict, deque
import json
import numpy as np
from dataclasses import dataclass, asdict
import threading
import time

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry for ML predictions"""
    key: str
    data: Any
    timestamp: datetime
    hit_count: int = 0
    model_type: str = ""
    confidence: float = 0.0

@dataclass
class BatchRequest:
    """Batch inference request"""
    model_type: str
    requests: List[Dict[str, Any]]
    timestamp: datetime
    callback: Optional[callable] = None

class MLInferenceCache:
    """
    High-performance ML inference cache with batch processing
    
    Features:
    - Intelligent caching with TTL and LRU eviction
    - Batch processing for efficient GPU utilization
    - Performance monitoring and optimization
    - Feature similarity-based cache hits
    """
    
    def __init__(self, max_cache_size: int = 1000, default_ttl: int = 300):
        """
        Initialize ML inference cache
        
        Args:
            max_cache_size: Maximum number of cache entries
            default_ttl: Default time-to-live in seconds
        """
        self.max_cache_size = max_cache_size
        self.default_ttl = default_ttl
        
        # Cache storage
        self.cache: Dict[str, CacheEntry] = {}
        self.cache_lock = threading.RLock()
        
        # Batch processing
        self.batch_queue: Dict[str, List[BatchRequest]] = defaultdict(list)
        self.batch_size = 32
        self.batch_timeout = 0.1  # 100ms batch timeout
        self.batch_lock = threading.RLock()
        
        # Performance tracking
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'total_requests': 0,
            'batch_processed': 0,
            'avg_latency': 0.0,
            'cache_hit_rate': 0.0
        }
        
        self.latency_history = deque(maxlen=1000)
        self.request_times = deque(maxlen=100)
        
        # Cache configuration
        self.config = {
            'enable_cache': True,
            'enable_batching': True,
            'similarity_threshold': 0.95,  # For feature similarity matching
            'max_batch_wait_ms': 100,
            'cache_ttl_seconds': 300,
            'performance_target_ms': 100
        }
        
        # Background tasks
        self.cleanup_task = None
        self.batch_processor_task = None
        self.running = False
        
        logger.info(f"ML Inference Cache initialized (max_size: {max_cache_size}, ttl: {default_ttl}s)")
    
    async def start(self):
        """Start background cache maintenance tasks"""
        if self.running:
            return
        
        self.running = True
        
        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cache_cleanup_loop())
        
        # Start batch processor
        self.batch_processor_task = asyncio.create_task(self._batch_processor_loop())
        
        logger.info("ML Inference Cache background tasks started")
    
    async def stop(self):
        """Stop background tasks and cleanup"""
        self.running = False
        
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        if self.batch_processor_task:
            self.batch_processor_task.cancel()
            try:
                await self.batch_processor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("ML Inference Cache stopped")
    
    def _generate_cache_key(self, model_type: str, input_data: Dict[str, Any]) -> str:
        """Generate cache key from model type and input data"""
        try:
            # Create a deterministic hash of the input data
            data_str = json.dumps(input_data, sort_keys=True, default=str)
            hash_obj = hashlib.md5(f"{model_type}:{data_str}".encode())
            return hash_obj.hexdigest()
        except Exception as e:
            logger.warning(f"Error generating cache key: {e}")
            return f"{model_type}:{hash(str(input_data))}"
    
    def _calculate_feature_similarity(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """Calculate similarity between two feature vectors"""
        try:
            if features1.shape != features2.shape:
                return 0.0
            
            # Cosine similarity
            dot_product = np.dot(features1, features2)
            norm1 = np.linalg.norm(features1)
            norm2 = np.linalg.norm(features2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception:
            return 0.0
    
    def _find_similar_cache_entry(self, model_type: str, input_data: Dict[str, Any]) -> Optional[CacheEntry]:
        """Find similar cache entry based on feature similarity"""
        if not self.config['enable_cache']:
            return None
        
        try:
            # Extract features for similarity comparison
            if 'features' not in input_data:
                return None
            
            input_features = np.array(input_data['features'])
            
            # Search for similar entries
            best_entry = None
            best_similarity = 0.0
            
            with self.cache_lock:
                for entry in self.cache.values():
                    if entry.model_type != model_type:
                        continue
                    
                    # Check if entry is still valid
                    if self._is_cache_entry_valid(entry):
                        try:
                            # Parse cached input to get features
                            cached_data = json.loads(entry.key.split(':', 1)[1])
                            if 'features' in cached_data:
                                cached_features = np.array(cached_data['features'])
                                similarity = self._calculate_feature_similarity(input_features, cached_features)
                                
                                if similarity > best_similarity and similarity >= self.config['similarity_threshold']:
                                    best_similarity = similarity
                                    best_entry = entry
                        except Exception:
                            continue
            
            if best_entry and best_similarity >= self.config['similarity_threshold']:
                logger.debug(f"Found similar cache entry with {best_similarity:.3f} similarity")
                return best_entry
            
        except Exception as e:
            logger.warning(f"Error finding similar cache entry: {e}")
        
        return None
    
    def _is_cache_entry_valid(self, entry: CacheEntry) -> bool:
        """Check if cache entry is still valid"""
        age_seconds = (datetime.now() - entry.timestamp).total_seconds()
        return age_seconds < self.config['cache_ttl_seconds']
    
    async def get_prediction(self, model_type: str, input_data: Dict[str, Any], 
                           predictor_func: callable) -> Dict[str, Any]:
        """
        Get ML prediction with caching and optimization
        
        Args:
            model_type: Type of ML model ('lstm', 'ensemble', 'kelly')
            input_data: Input data for prediction
            predictor_func: Function to call for actual prediction
            
        Returns:
            Prediction result with cache metadata
        """
        start_time = time.time()
        
        try:
            self.stats['total_requests'] += 1
            
            # Generate cache key
            cache_key = self._generate_cache_key(model_type, input_data)
            
            # Check direct cache hit
            cache_entry = None
            if self.config['enable_cache']:
                with self.cache_lock:
                    if cache_key in self.cache:
                        entry = self.cache[cache_key]
                        if self._is_cache_entry_valid(entry):
                            entry.hit_count += 1
                            cache_entry = entry
            
            # Check similarity-based cache hit if no direct hit
            if cache_entry is None and self.config['enable_cache']:
                cache_entry = self._find_similar_cache_entry(model_type, input_data)
                if cache_entry:
                    cache_entry.hit_count += 1
            
            # Cache hit
            if cache_entry:
                self.stats['cache_hits'] += 1
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
                self.latency_history.append(latency_ms)
                
                result = cache_entry.data.copy()
                result['cache_hit'] = True
                result['cache_latency_ms'] = latency_ms
                result['cache_age_seconds'] = (datetime.now() - cache_entry.timestamp).total_seconds()
                
                logger.debug(f"Cache hit for {model_type}: {latency_ms:.1f}ms")
                return result
            
            # Cache miss - need to compute prediction
            self.stats['cache_misses'] += 1
            
            # Use batch processing if enabled
            if self.config['enable_batching']:
                result = await self._batch_predict(model_type, input_data, predictor_func)
            else:
                result = await self._single_predict(model_type, input_data, predictor_func)
            
            # Cache the result
            if self.config['enable_cache'] and result:
                await self._cache_result(cache_key, model_type, result)
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            self.latency_history.append(latency_ms)
            
            result['cache_hit'] = False
            result['inference_latency_ms'] = latency_ms
            
            logger.debug(f"Cache miss for {model_type}: {latency_ms:.1f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Error in ML inference cache for {model_type}: {e}")
            # Fallback to direct prediction
            try:
                return await predictor_func(input_data)
            except Exception as fallback_error:
                logger.error(f"Fallback prediction failed: {fallback_error}")
                return {'error': str(e), 'fallback_error': str(fallback_error)}
        finally:
            # Update performance stats
            self._update_performance_stats()
    
    async def _single_predict(self, model_type: str, input_data: Dict[str, Any], 
                            predictor_func: callable) -> Dict[str, Any]:
        """Perform single prediction"""
        return await predictor_func(input_data)
    
    async def _batch_predict(self, model_type: str, input_data: Dict[str, Any], 
                           predictor_func: callable) -> Dict[str, Any]:
        """Add request to batch queue or process immediately if batch is full"""
        
        # For now, fall back to single prediction
        # Batch processing would require model-specific implementation
        return await self._single_predict(model_type, input_data, predictor_func)
    
    async def _cache_result(self, cache_key: str, model_type: str, result: Dict[str, Any]):
        """Cache a prediction result"""
        try:
            # Clean result for caching (remove non-serializable data)
            cacheable_result = {k: v for k, v in result.items() 
                              if isinstance(v, (int, float, str, bool, list, dict, type(None)))}
            
            entry = CacheEntry(
                key=cache_key,
                data=cacheable_result,
                timestamp=datetime.now(),
                model_type=model_type,
                confidence=result.get('confidence', 0.0)
            )
            
            with self.cache_lock:
                # Evict old entries if cache is full
                if len(self.cache) >= self.max_cache_size:
                    self._evict_cache_entries()
                
                self.cache[cache_key] = entry
            
            logger.debug(f"Cached result for {model_type} (cache size: {len(self.cache)})")
            
        except Exception as e:
            logger.warning(f"Error caching result: {e}")
    
    def _evict_cache_entries(self):
        """Evict old cache entries using LRU + age strategy"""
        try:
            # Remove expired entries first
            current_time = datetime.now()
            expired_keys = []
            
            for key, entry in self.cache.items():
                age_seconds = (current_time - entry.timestamp).total_seconds()
                if age_seconds > self.config['cache_ttl_seconds']:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
            
            # If still over limit, remove least recently used
            if len(self.cache) >= self.max_cache_size:
                # Sort by hit count (ascending) and timestamp (ascending)
                sorted_entries = sorted(
                    self.cache.items(),
                    key=lambda x: (x[1].hit_count, x[1].timestamp)
                )
                
                # Remove 25% of entries
                remove_count = max(1, len(self.cache) // 4)
                for i in range(remove_count):
                    if i < len(sorted_entries):
                        key = sorted_entries[i][0]
                        del self.cache[key]
            
            logger.debug(f"Cache eviction completed (size: {len(self.cache)})")
            
        except Exception as e:
            logger.error(f"Error during cache eviction: {e}")
    
    async def _cache_cleanup_loop(self):
        """Background task for cache cleanup"""
        while self.running:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                with self.cache_lock:
                    self._evict_cache_entries()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache cleanup loop: {e}")
    
    async def _batch_processor_loop(self):
        """Background task for processing batched requests"""
        while self.running:
            try:
                await asyncio.sleep(0.05)  # Check every 50ms
                
                # Process any pending batches
                # This would be implemented for specific model types that support batching
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in batch processor loop: {e}")
    
    def _update_performance_stats(self):
        """Update performance statistics"""
        try:
            # Update cache hit rate
            total_requests = self.stats['cache_hits'] + self.stats['cache_misses']
            if total_requests > 0:
                self.stats['cache_hit_rate'] = self.stats['cache_hits'] / total_requests
            
            # Update average latency
            if self.latency_history:
                self.stats['avg_latency'] = sum(self.latency_history) / len(self.latency_history)
            
        except Exception as e:
            logger.warning(f"Error updating performance stats: {e}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        return {
            'cache_stats': self.stats.copy(),
            'cache_size': len(self.cache),
            'max_cache_size': self.max_cache_size,
            'config': self.config,
            'recent_latencies': list(self.latency_history)[-10:],
            'performance_target_met': self.stats['avg_latency'] < self.config['performance_target_ms']
        }
    
    def clear_cache(self):
        """Clear all cache entries"""
        with self.cache_lock:
            self.cache.clear()
        logger.info("Cache cleared")
    
    def set_config(self, **kwargs):
        """Update cache configuration"""
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
                logger.info(f"Updated cache config: {key} = {value}")

# Global cache instance
_ml_inference_cache = None

def get_ml_inference_cache() -> MLInferenceCache:
    """Get global ML inference cache instance"""
    global _ml_inference_cache
    if _ml_inference_cache is None:
        _ml_inference_cache = MLInferenceCache()
    return _ml_inference_cache