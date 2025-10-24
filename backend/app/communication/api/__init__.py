"""
Communication API Routes
REST API endpoints for the communication system
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from typing import List, Optional
import json
from datetime import datetime
from app.core.logging import logger
from app.communication.models import (
    SendMessageRequest, CreateConversationRequest, ConversationResponse,
    MessageResponse, VendorListResponse, NotificationListResponse,
    WebSocketMessage, create_conversation, create_message
)
from app.communication.services import message_service
from app.communication.services.websocket_service import websocket_manager

router = APIRouter(prefix="/api/v1/communication", tags=["communication"])


# ===== Message Endpoints =====

@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    sender_id: str = "user_123"  # TODO: Get from authentication
):
    """Send a message to a conversation"""
    try:
        message = await message_service.send_message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            sender_type="user",
            content=request.content,
            message_type=request.message_type,
            reply_to=request.reply_to
        )
        
        # Broadcast to WebSocket connections
        await websocket_manager.send_message_update(
            conversation_id=conversation_id,
            message_data=message.model_dump(),
            user_id=sender_id
        )
        
        logger.info(
            "Message sent via API",
            message_id=message.message_id,
            conversation_id=conversation_id,
            sender_id=sender_id
        )
        
        return MessageResponse(
            message=message,
            conversation_id=conversation_id
        )
        
    except Exception as e:
        logger.error(
            "Failed to send message via API",
            conversation_id=conversation_id,
            sender_id=sender_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    limit: int = 50,
    offset: int = 0
):
    """Get messages for a conversation"""
    try:
        messages = await message_service.get_conversation_messages(
            conversation_id=conversation_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "messages": [message.model_dump() for message in messages],
            "conversation_id": conversation_id,
            "total_count": len(messages)
        }
        
    except Exception as e:
        logger.error(
            "Failed to get conversation messages",
            conversation_id=conversation_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")


@router.put("/conversations/{conversation_id}/read")
async def mark_conversation_read(
    conversation_id: str,
    user_id: str = "user_123"  # TODO: Get from authentication
):
    """Mark all messages in a conversation as read"""
    try:
        await message_service.mark_messages_read(
            conversation_id=conversation_id,
            user_id=user_id
        )
        
        return {"status": "success", "message": "Messages marked as read"}
        
    except Exception as e:
        logger.error(
            "Failed to mark conversation as read",
            conversation_id=conversation_id,
            user_id=user_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Failed to mark as read: {str(e)}")


@router.delete("/messages/{message_id}")
async def delete_message(message_id: str):
    """Delete a message"""
    try:
        success = await message_service.delete_message(message_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Message not found")
        
        return {"status": "success", "message": "Message deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to delete message",
            message_id=message_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Failed to delete message: {str(e)}")


@router.get("/conversations/{conversation_id}/search")
async def search_messages(
    conversation_id: str,
    q: str,
    limit: int = 20
):
    """Search messages in a conversation"""
    try:
        messages = await message_service.search_messages(
            query=q,
            conversation_id=conversation_id,
            limit=limit
        )
        
        return {
            "messages": [message.model_dump() for message in messages],
            "conversation_id": conversation_id,
            "query": q,
            "results_count": len(messages)
        }
        
    except Exception as e:
        logger.error(
            "Failed to search messages",
            conversation_id=conversation_id,
            query=q,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Failed to search messages: {str(e)}")


# ===== Conversation Endpoints =====

@router.get("/parties/{party_id}/conversations")
async def get_party_conversations(party_id: str):
    """Get all conversations for a party"""
    try:
        # TODO: Implement conversation service
        conversations = []
        
        return {
            "conversations": conversations,
            "party_id": party_id,
            "total_count": len(conversations)
        }
        
    except Exception as e:
        logger.error(
            "Failed to get party conversations",
            party_id=party_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Failed to get conversations: {str(e)}")


@router.post("/conversations")
async def create_conversation(request: CreateConversationRequest):
    """Create a new conversation"""
    try:
        # TODO: Implement conversation creation
        conversation = create_conversation(
            party_id=request.party_id,
            vendor_id=request.vendor_id,
            vendor_type="balloon_artist",  # TODO: Get from vendor profile
            participants=["user_123", request.vendor_id, "festimo"]
        )
        
        # Send initial message if provided
        if request.initial_message:
            message = await message_service.send_message(
                conversation_id=conversation.conversation_id,
                sender_id="user_123",
                sender_type="user",
                content=request.initial_message
            )
            conversation.last_message = message
        
        return {
            "conversation": conversation.model_dump(),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(
            "Failed to create conversation",
            party_id=request.party_id,
            vendor_id=request.vendor_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Failed to create conversation: {str(e)}")


# ===== Vendor Endpoints =====

@router.get("/vendors", response_model=VendorListResponse)
async def get_vendors():
    """Get list of available vendors"""
    try:
        # TODO: Implement vendor service
        vendors = []
        
        return VendorListResponse(
            vendors=vendors,
            total_count=len(vendors)
        )
        
    except Exception as e:
        logger.error("Failed to get vendors", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get vendors: {str(e)}")


@router.get("/vendors/{vendor_id}")
async def get_vendor_profile(vendor_id: str):
    """Get vendor profile"""
    try:
        # TODO: Implement vendor service
        return {"vendor_id": vendor_id, "status": "not_implemented"}
        
    except Exception as e:
        logger.error(
            "Failed to get vendor profile",
            vendor_id=vendor_id,
            error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Failed to get vendor profile: {str(e)}")


# ===== WebSocket Endpoints =====

@router.websocket("/ws/party/{party_id}")
async def websocket_party_endpoint(websocket: WebSocket, party_id: str):
    """WebSocket endpoint for party communication"""
    await websocket_manager.connect_party(party_id, websocket)
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            
            try:
                command = json.loads(data)
                
                if command.get("type") == "ping":
                    # Respond to heartbeat
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                elif command.get("type") == "typing":
                    # Handle typing indicator
                    await websocket_manager.send_typing_indicator(
                        conversation_id=command.get("conversation_id"),
                        sender_id=command.get("sender_id"),
                        sender_type=command.get("sender_type", "user"),
                        is_typing=command.get("is_typing", False),
                        party_id=party_id
                    )
                
            except json.JSONDecodeError:
                logger.warning(
                    "Received non-JSON message from WebSocket",
                    party_id=party_id,
                    message=data
                )
    
    except WebSocketDisconnect:
        await websocket_manager.disconnect_party(party_id, websocket)
    except Exception as e:
        logger.error(
            "WebSocket error for party",
            party_id=party_id,
            error=str(e)
        )
        await websocket_manager.disconnect_party(party_id, websocket)


@router.websocket("/ws/vendor/{vendor_id}")
async def websocket_vendor_endpoint(websocket: WebSocket, vendor_id: str):
    """WebSocket endpoint for vendor communication"""
    await websocket_manager.connect_vendor(vendor_id, websocket)
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            
            try:
                command = json.loads(data)
                
                if command.get("type") == "ping":
                    # Respond to heartbeat
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                elif command.get("type") == "status_update":
                    # Handle vendor status update
                    await websocket_manager.send_vendor_status_update(
                        vendor_id=vendor_id,
                        status=command.get("status", "offline")
                    )
                
            except json.JSONDecodeError:
                logger.warning(
                    "Received non-JSON message from vendor WebSocket",
                    vendor_id=vendor_id,
                    message=data
                )
    
    except WebSocketDisconnect:
        await websocket_manager.disconnect_vendor(vendor_id, websocket)
    except Exception as e:
        logger.error(
            "WebSocket error for vendor",
            vendor_id=vendor_id,
            error=str(e)
        )
        await websocket_manager.disconnect_vendor(vendor_id, websocket)


# Export router
__all__ = ["router"]

