"""
Message Service
Handles all message-related operations for the communication system
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
from app.core.logging import logger
from app.communication.models import (
    Message, Conversation, SendMessageRequest, MessageResponse,
    create_message, create_notification
)


class MessageService:
    """Service for managing messages and conversations"""
    
    def __init__(self):
        # In-memory storage for demo (replace with database in production)
        self.messages: Dict[str, Message] = {}
        self.conversations: Dict[str, Conversation] = {}
        self.conversation_messages: Dict[str, List[str]] = {}  # conversation_id -> message_ids
        
    async def send_message(
        self, 
        conversation_id: str, 
        sender_id: str, 
        sender_type: str,
        content: str,
        message_type: str = "text",
        reply_to: Optional[str] = None
    ) -> Message:
        """Send a new message"""
        try:
            # Create the message
            message = create_message(
                conversation_id=conversation_id,
                sender_id=sender_id,
                sender_type=sender_type,
                content=content,
                message_type=message_type,
                reply_to=reply_to
            )
            
            # Store the message
            self.messages[message.message_id] = message
            
            # Add to conversation
            if conversation_id not in self.conversation_messages:
                self.conversation_messages[conversation_id] = []
            self.conversation_messages[conversation_id].append(message.message_id)
            
            # Update conversation
            if conversation_id in self.conversations:
                conversation = self.conversations[conversation_id]
                conversation.last_message = message
                conversation.updated_at = datetime.utcnow().isoformat()
                
                # Update unread count for other participants
                for participant in conversation.participants:
                    if participant != sender_id:
                        conversation.unread_count[participant] = conversation.unread_count.get(participant, 0) + 1
            
            logger.info(
                "Message sent successfully",
                message_id=message.message_id,
                conversation_id=conversation_id,
                sender_id=sender_id,
                sender_type=sender_type
            )
            
            return message
            
        except Exception as e:
            logger.error(
                "Failed to send message",
                conversation_id=conversation_id,
                sender_id=sender_id,
                error=str(e)
            )
            raise
    
    async def get_conversation_messages(
        self, 
        conversation_id: str, 
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """Get messages for a conversation"""
        try:
            if conversation_id not in self.conversation_messages:
                return []
            
            message_ids = self.conversation_messages[conversation_id]
            messages = []
            
            # Get messages in reverse order (newest first)
            for message_id in reversed(message_ids[offset:offset + limit]):
                if message_id in self.messages:
                    messages.append(self.messages[message_id])
            
            logger.info(
                "Retrieved conversation messages",
                conversation_id=conversation_id,
                message_count=len(messages),
                limit=limit,
                offset=offset
            )
            
            return messages
            
        except Exception as e:
            logger.error(
                "Failed to get conversation messages",
                conversation_id=conversation_id,
                error=str(e)
            )
            raise
    
    async def mark_messages_read(
        self, 
        conversation_id: str, 
        user_id: str
    ) -> None:
        """Mark all messages in a conversation as read for a user"""
        try:
            if conversation_id not in self.conversations:
                return
            
            conversation = self.conversations[conversation_id]
            
            # Reset unread count for this user
            conversation.unread_count[user_id] = 0
            
            # Update message statuses
            if conversation_id in self.conversation_messages:
                for message_id in self.conversation_messages[conversation_id]:
                    if message_id in self.messages:
                        message = self.messages[message_id]
                        if message.sender_id != user_id and message.status != "read":
                            message.status = "read"
            
            logger.info(
                "Messages marked as read",
                conversation_id=conversation_id,
                user_id=user_id
            )
            
        except Exception as e:
            logger.error(
                "Failed to mark messages as read",
                conversation_id=conversation_id,
                user_id=user_id,
                error=str(e)
            )
            raise
    
    async def delete_message(self, message_id: str) -> bool:
        """Delete a message"""
        try:
            if message_id not in self.messages:
                return False
            
            message = self.messages[message_id]
            conversation_id = message.conversation_id
            
            # Remove from conversation
            if conversation_id in self.conversation_messages:
                if message_id in self.conversation_messages[conversation_id]:
                    self.conversation_messages[conversation_id].remove(message_id)
            
            # Delete the message
            del self.messages[message_id]
            
            logger.info(
                "Message deleted",
                message_id=message_id,
                conversation_id=conversation_id
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Failed to delete message",
                message_id=message_id,
                error=str(e)
            )
            raise
    
    async def search_messages(
        self, 
        query: str, 
        conversation_id: str,
        limit: int = 20
    ) -> List[Message]:
        """Search messages in a conversation"""
        try:
            if conversation_id not in self.conversation_messages:
                return []
            
            matching_messages = []
            query_lower = query.lower()
            
            for message_id in self.conversation_messages[conversation_id]:
                if message_id in self.messages:
                    message = self.messages[message_id]
                    if query_lower in message.content.lower():
                        matching_messages.append(message)
            
            # Sort by timestamp (newest first)
            matching_messages.sort(key=lambda x: x.timestamp, reverse=True)
            
            logger.info(
                "Message search completed",
                conversation_id=conversation_id,
                query=query,
                results_count=len(matching_messages)
            )
            
            return matching_messages[:limit]
            
        except Exception as e:
            logger.error(
                "Failed to search messages",
                conversation_id=conversation_id,
                query=query,
                error=str(e)
            )
            raise
    
    async def get_message(self, message_id: str) -> Optional[Message]:
        """Get a specific message by ID"""
        return self.messages.get(message_id)
    
    async def update_message_status(
        self, 
        message_id: str, 
        status: str
    ) -> bool:
        """Update message status (sent, delivered, read)"""
        try:
            if message_id not in self.messages:
                return False
            
            message = self.messages[message_id]
            message.status = status
            
            logger.info(
                "Message status updated",
                message_id=message_id,
                status=status
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Failed to update message status",
                message_id=message_id,
                status=status,
                error=str(e)
            )
            raise


# Global message service instance
message_service = MessageService()

