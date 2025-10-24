"""
WebSocket Service for Real-Time Communication
Handles WebSocket connections and real-time message broadcasting
"""

from typing import Dict, List, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import json
from datetime import datetime
from app.core.logging import logger
from app.communication.models import WebSocketMessage, TypingIndicator


class CommunicationWebSocketManager:
    """Manages WebSocket connections for real-time communication"""
    
    def __init__(self):
        # party_id -> list of WebSocket connections
        self.party_connections: Dict[str, List[WebSocket]] = {}
        # vendor_id -> list of WebSocket connections
        self.vendor_connections: Dict[str, List[WebSocket]] = {}
        # user_id -> list of WebSocket connections
        self.user_connections: Dict[str, List[WebSocket]] = {}
        # conversation_id -> set of active typing indicators
        self.typing_indicators: Dict[str, Set[TypingIndicator]] = {}
        
    async def connect_party(self, party_id: str, websocket: WebSocket):
        """Connect a WebSocket to a party"""
        await websocket.accept()
        
        if party_id not in self.party_connections:
            self.party_connections[party_id] = []
        
        self.party_connections[party_id].append(websocket)
        
        logger.info(
            "WebSocket connected to party",
            party_id=party_id,
            total_connections=len(self.party_connections[party_id])
        )
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "party_id": party_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def connect_vendor(self, vendor_id: str, websocket: WebSocket):
        """Connect a WebSocket to a vendor"""
        await websocket.accept()
        
        if vendor_id not in self.vendor_connections:
            self.vendor_connections[vendor_id] = []
        
        self.vendor_connections[vendor_id].append(websocket)
        
        logger.info(
            "WebSocket connected to vendor",
            vendor_id=vendor_id,
            total_connections=len(self.vendor_connections[vendor_id])
        )
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "vendor_id": vendor_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def connect_user(self, user_id: str, websocket: WebSocket):
        """Connect a WebSocket to a user"""
        await websocket.accept()
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        
        self.user_connections[user_id].append(websocket)
        
        logger.info(
            "WebSocket connected to user",
            user_id=user_id,
            total_connections=len(self.user_connections[user_id])
        )
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def disconnect_party(self, party_id: str, websocket: WebSocket):
        """Disconnect a WebSocket from a party"""
        if party_id in self.party_connections:
            if websocket in self.party_connections[party_id]:
                self.party_connections[party_id].remove(websocket)
            
            if not self.party_connections[party_id]:
                del self.party_connections[party_id]
        
        logger.info(
            "WebSocket disconnected from party",
            party_id=party_id
        )
    
    async def disconnect_vendor(self, vendor_id: str, websocket: WebSocket):
        """Disconnect a WebSocket from a vendor"""
        if vendor_id in self.vendor_connections:
            if websocket in self.vendor_connections[vendor_id]:
                self.vendor_connections[vendor_id].remove(websocket)
            
            if not self.vendor_connections[vendor_id]:
                del self.vendor_connections[vendor_id]
        
        logger.info(
            "WebSocket disconnected from vendor",
            vendor_id=vendor_id
        )
    
    async def disconnect_user(self, user_id: str, websocket: WebSocket):
        """Disconnect a WebSocket from a user"""
        if user_id in self.user_connections:
            if websocket in self.user_connections[user_id]:
                self.user_connections[user_id].remove(websocket)
            
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        logger.info(
            "WebSocket disconnected from user",
            user_id=user_id
        )
    
    async def broadcast_to_party(self, party_id: str, message: WebSocketMessage):
        """Broadcast a message to all connections for a party"""
        if party_id not in self.party_connections:
            return
        
        message_json = message.model_dump()
        disconnected = []
        
        for websocket in self.party_connections[party_id]:
            try:
                await websocket.send_json(message_json)
            except Exception as e:
                logger.warning(
                    "Failed to send message to party WebSocket",
                    party_id=party_id,
                    error=str(e)
                )
                disconnected.append(websocket)
        
        # Remove disconnected WebSockets
        for websocket in disconnected:
            await self.disconnect_party(party_id, websocket)
    
    async def broadcast_to_vendor(self, vendor_id: str, message: WebSocketMessage):
        """Broadcast a message to all connections for a vendor"""
        if vendor_id not in self.vendor_connections:
            return
        
        message_json = message.model_dump()
        disconnected = []
        
        for websocket in self.vendor_connections[vendor_id]:
            try:
                await websocket.send_json(message_json)
            except Exception as e:
                logger.warning(
                    "Failed to send message to vendor WebSocket",
                    vendor_id=vendor_id,
                    error=str(e)
                )
                disconnected.append(websocket)
        
        # Remove disconnected WebSockets
        for websocket in disconnected:
            await self.disconnect_vendor(vendor_id, websocket)
    
    async def broadcast_to_user(self, user_id: str, message: WebSocketMessage):
        """Broadcast a message to all connections for a user"""
        if user_id not in self.user_connections:
            return
        
        message_json = message.model_dump()
        disconnected = []
        
        for websocket in self.user_connections[user_id]:
            try:
                await websocket.send_json(message_json)
            except Exception as e:
                logger.warning(
                    "Failed to send message to user WebSocket",
                    user_id=user_id,
                    error=str(e)
                )
                disconnected.append(websocket)
        
        # Remove disconnected WebSockets
        for websocket in disconnected:
            await self.disconnect_user(user_id, websocket)
    
    async def send_message_update(
        self, 
        conversation_id: str, 
        message_data: dict,
        party_id: Optional[str] = None,
        vendor_id: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """Send a message update to relevant connections"""
        ws_message = WebSocketMessage(
            type="message_sent",
            conversation_id=conversation_id,
            message=message_data,
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Broadcast to party if party_id provided
        if party_id:
            await self.broadcast_to_party(party_id, ws_message)
        
        # Broadcast to vendor if vendor_id provided
        if vendor_id:
            await self.broadcast_to_vendor(vendor_id, ws_message)
        
        # Broadcast to user if user_id provided
        if user_id:
            await self.broadcast_to_user(user_id, ws_message)
    
    async def send_typing_indicator(
        self, 
        conversation_id: str, 
        sender_id: str,
        sender_type: str,
        is_typing: bool,
        party_id: Optional[str] = None,
        vendor_id: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """Send typing indicator to relevant connections"""
        typing_indicator = TypingIndicator(
            conversation_id=conversation_id,
            sender_id=sender_id,
            sender_type=sender_type,
            is_typing=is_typing
        )
        
        ws_message = WebSocketMessage(
            type="typing_start" if is_typing else "typing_stop",
            conversation_id=conversation_id,
            sender_id=sender_id,
            timestamp=datetime.utcnow().isoformat(),
            metadata={"typing_indicator": typing_indicator.model_dump()}
        )
        
        # Broadcast to party if party_id provided
        if party_id:
            await self.broadcast_to_party(party_id, ws_message)
        
        # Broadcast to vendor if vendor_id provided
        if vendor_id:
            await self.broadcast_to_vendor(vendor_id, ws_message)
        
        # Broadcast to user if user_id provided
        if user_id:
            await self.broadcast_to_user(user_id, ws_message)
    
    async def send_vendor_status_update(
        self, 
        vendor_id: str, 
        status: str,
        party_id: Optional[str] = None
    ):
        """Send vendor status update to relevant connections"""
        ws_message = WebSocketMessage(
            type="vendor_online" if status == "online" else "vendor_offline",
            vendor_id=vendor_id,
            timestamp=datetime.utcnow().isoformat(),
            metadata={"status": status}
        )
        
        # Broadcast to vendor
        await self.broadcast_to_vendor(vendor_id, ws_message)
        
        # Broadcast to party if party_id provided
        if party_id:
            await self.broadcast_to_party(party_id, ws_message)
    
    def get_connection_count(self, party_id: str) -> int:
        """Get the number of active connections for a party"""
        return len(self.party_connections.get(party_id, []))
    
    def get_vendor_connection_count(self, vendor_id: str) -> int:
        """Get the number of active connections for a vendor"""
        return len(self.vendor_connections.get(vendor_id, []))
    
    def get_user_connection_count(self, user_id: str) -> int:
        """Get the number of active connections for a user"""
        return len(self.user_connections.get(user_id, []))


# Global WebSocket manager instance
websocket_manager = CommunicationWebSocketManager()

