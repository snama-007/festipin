"""
Generation History Service

Service for managing image generation history, favorites, and user statistics.
"""

import asyncio
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from pathlib import Path

from app.models.motif.history import (
    GenerationHistory, GenerationHistoryRequest, GenerationHistoryResponse,
    FavoriteRequest, FavoriteResponse, TagRequest, TagResponse,
    GenerationStats, GenerationStatsResponse, GenerationStatus, GenerationType
)

logger = logging.getLogger(__name__)

class GenerationHistoryService:
    """Service for managing generation history and user data"""
    
    def __init__(self, storage_path: str = "./memory_store/generations"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.history_file = self.storage_path / "history.json"
        self.favorites_file = self.storage_path / "favorites.json"
        self.stats_file = self.storage_path / "stats.json"
        
        # Initialize storage files
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize storage files if they don't exist"""
        if not self.history_file.exists():
            with open(self.history_file, 'w') as f:
                json.dump({}, f)
        
        if not self.favorites_file.exists():
            with open(self.favorites_file, 'w') as f:
                json.dump({}, f)
        
        if not self.stats_file.exists():
            with open(self.stats_file, 'w') as f:
                json.dump({}, f)
    
    async def save_generation(self, generation: GenerationHistory) -> bool:
        """Save a generation to history"""
        try:
            # Load existing history
            with open(self.history_file, 'r') as f:
                history_data = json.load(f)
            
            # Add generation
            history_data[generation.id] = generation.dict()
            
            # Save back to file
            with open(self.history_file, 'w') as f:
                json.dump(history_data, f, default=str)
            
            # Update user statistics
            await self._update_user_stats(generation.user_id)
            
            logger.info(f"Saved generation {generation.id} for user {generation.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save generation {generation.id}: {e}")
            return False
    
    async def get_generation_history(self, request: GenerationHistoryRequest) -> GenerationHistoryResponse:
        """Get generation history for a user with filtering and pagination"""
        try:
            # Load history data
            with open(self.history_file, 'r') as f:
                history_data = json.load(f)
            
            # Filter by user
            user_generations = [
                GenerationHistory(**gen_data) 
                for gen_data in history_data.values() 
                if gen_data.get('user_id') == request.user_id
            ]
            
            # Apply filters
            filtered_generations = user_generations
            
            if request.status:
                filtered_generations = [
                    g for g in filtered_generations 
                    if g.status == request.status
                ]
            
            if request.generation_type:
                filtered_generations = [
                    g for g in filtered_generations 
                    if g.generation_type == request.generation_type
                ]
            
            if request.style:
                filtered_generations = [
                    g for g in filtered_generations 
                    if g.style == request.style
                ]
            
            if request.favorites_only:
                filtered_generations = [
                    g for g in filtered_generations 
                    if g.is_favorite
                ]
            
            if request.search_query:
                search_lower = request.search_query.lower()
                filtered_generations = [
                    g for g in filtered_generations 
                    if search_lower in g.prompt.lower() or search_lower in g.enhanced_prompt.lower()
                ]
            
            # Sort by creation date (newest first)
            filtered_generations.sort(key=lambda x: x.created_at, reverse=True)
            
            # Apply pagination
            total_count = len(filtered_generations)
            paginated_generations = filtered_generations[
                request.offset:request.offset + request.limit
            ]
            
            has_more = request.offset + request.limit < total_count
            
            return GenerationHistoryResponse(
                success=True,
                generations=paginated_generations,
                total_count=total_count,
                has_more=has_more
            )
            
        except Exception as e:
            logger.error(f"Failed to get generation history: {e}")
            return GenerationHistoryResponse(
                success=False,
                generations=[],
                total_count=0,
                has_more=False
            )
    
    async def toggle_favorite(self, request: FavoriteRequest) -> FavoriteResponse:
        """Toggle favorite status for a generation"""
        try:
            # Load history data
            with open(self.history_file, 'r') as f:
                history_data = json.load(f)
            
            if request.generation_id not in history_data:
                return FavoriteResponse(
                    success=False,
                    is_favorite=False,
                    message="Generation not found"
                )
            
            generation_data = history_data[request.generation_id]
            
            # Check if user owns this generation
            if generation_data.get('user_id') != request.user_id:
                return FavoriteResponse(
                    success=False,
                    is_favorite=False,
                    message="Unauthorized access"
                )
            
            # Update favorite status
            generation_data['is_favorite'] = request.is_favorite
            history_data[request.generation_id] = generation_data
            
            # Save back to file
            with open(self.history_file, 'w') as f:
                json.dump(history_data, f, default=str)
            
            # Update user statistics
            await self._update_user_stats(request.user_id)
            
            return FavoriteResponse(
                success=True,
                is_favorite=request.is_favorite,
                message=f"Generation {'marked as' if request.is_favorite else 'removed from'} favorite"
            )
            
        except Exception as e:
            logger.error(f"Failed to toggle favorite: {e}")
            return FavoriteResponse(
                success=False,
                is_favorite=False,
                message=f"Error: {str(e)}"
            )
    
    async def update_tags(self, request: TagRequest) -> TagResponse:
        """Add or remove tags from a generation"""
        try:
            # Load history data
            with open(self.history_file, 'r') as f:
                history_data = json.load(f)
            
            if request.generation_id not in history_data:
                return TagResponse(
                    success=False,
                    tags=[],
                    message="Generation not found"
                )
            
            generation_data = history_data[request.generation_id]
            
            # Check if user owns this generation
            if generation_data.get('user_id') != request.user_id:
                return TagResponse(
                    success=False,
                    tags=[],
                    message="Unauthorized access"
                )
            
            current_tags = generation_data.get('tags', [])
            
            if request.action == 'add':
                # Add new tags (avoid duplicates)
                for tag in request.tags:
                    if tag not in current_tags:
                        current_tags.append(tag)
            elif request.action == 'remove':
                # Remove tags
                for tag in request.tags:
                    if tag in current_tags:
                        current_tags.remove(tag)
            else:
                return TagResponse(
                    success=False,
                    tags=current_tags,
                    message="Invalid action. Use 'add' or 'remove'"
                )
            
            # Update tags
            generation_data['tags'] = current_tags
            history_data[request.generation_id] = generation_data
            
            # Save back to file
            with open(self.history_file, 'w') as f:
                json.dump(history_data, f, default=str)
            
            return TagResponse(
                success=True,
                tags=current_tags,
                message=f"Tags {request.action}ed successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to update tags: {e}")
            return TagResponse(
                success=False,
                tags=[],
                message=f"Error: {str(e)}"
            )
    
    async def get_user_stats(self, user_id: str) -> GenerationStatsResponse:
        """Get generation statistics for a user"""
        try:
            # Load stats data
            with open(self.stats_file, 'r') as f:
                stats_data = json.load(f)
            
            user_stats = stats_data.get(user_id, {})
            
            stats = GenerationStats(
                user_id=user_id,
                total_generations=user_stats.get('total_generations', 0),
                successful_generations=user_stats.get('successful_generations', 0),
                failed_generations=user_stats.get('failed_generations', 0),
                favorite_count=user_stats.get('favorite_count', 0),
                total_processing_time=user_stats.get('total_processing_time', 0.0),
                average_rating=user_stats.get('average_rating'),
                most_used_style=user_stats.get('most_used_style'),
                most_used_type=user_stats.get('most_used_type'),
                last_generation=user_stats.get('last_generation')
            )
            
            return GenerationStatsResponse(
                success=True,
                stats=stats
            )
            
        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            return GenerationStatsResponse(
                success=False,
                stats=GenerationStats(user_id=user_id)
            )
    
    async def _update_user_stats(self, user_id: str):
        """Update user statistics based on current history"""
        try:
            # Load history data
            with open(self.history_file, 'r') as f:
                history_data = json.load(f)
            
            # Get user's generations
            user_generations = [
                GenerationHistory(**gen_data) 
                for gen_data in history_data.values() 
                if gen_data.get('user_id') == user_id
            ]
            
            if not user_generations:
                return
            
            # Calculate statistics
            total_generations = len(user_generations)
            successful_generations = len([g for g in user_generations if g.status == GenerationStatus.COMPLETED])
            failed_generations = len([g for g in user_generations if g.status == GenerationStatus.FAILED])
            favorite_count = len([g for g in user_generations if g.is_favorite])
            
            total_processing_time = sum([
                g.processing_time for g in user_generations 
                if g.processing_time is not None
            ])
            
            # Calculate average rating
            ratings = [g.rating for g in user_generations if g.rating is not None]
            average_rating = sum(ratings) / len(ratings) if ratings else None
            
            # Find most used style
            styles = [g.style for g in user_generations if g.style is not None]
            most_used_style = max(set(styles), key=styles.count) if styles else None
            
            # Find most used type
            types = [g.generation_type for g in user_generations]
            most_used_type = max(set(types), key=types.count) if types else None
            
            # Find last generation
            last_generation = max([g.created_at for g in user_generations]) if user_generations else None
            
            # Load existing stats
            with open(self.stats_file, 'r') as f:
                stats_data = json.load(f)
            
            # Update user stats
            stats_data[user_id] = {
                'total_generations': total_generations,
                'successful_generations': successful_generations,
                'failed_generations': failed_generations,
                'favorite_count': favorite_count,
                'total_processing_time': total_processing_time,
                'average_rating': average_rating,
                'most_used_style': most_used_style,
                'most_used_type': most_used_type,
                'last_generation': last_generation.isoformat() if last_generation else None
            }
            
            # Save stats
            with open(self.stats_file, 'w') as f:
                json.dump(stats_data, f, default=str)
            
        except Exception as e:
            logger.error(f"Failed to update user stats: {e}")
    
    async def delete_generation(self, generation_id: str, user_id: str) -> bool:
        """Delete a generation (soft delete by marking as deleted)"""
        try:
            # Load history data
            with open(self.history_file, 'r') as f:
                history_data = json.load(f)
            
            if generation_id not in history_data:
                return False
            
            generation_data = history_data[generation_id]
            
            # Check if user owns this generation
            if generation_data.get('user_id') != user_id:
                return False
            
            # Mark as deleted (don't actually delete for audit purposes)
            generation_data['status'] = 'deleted'
            generation_data['deleted_at'] = datetime.utcnow().isoformat()
            history_data[generation_id] = generation_data
            
            # Save back to file
            with open(self.history_file, 'w') as f:
                json.dump(history_data, f, default=str)
            
            # Update user statistics
            await self._update_user_stats(user_id)
            
            logger.info(f"Deleted generation {generation_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete generation {generation_id}: {e}")
            return False
