"""
Communication System Models
Pydantic models for the communication system
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


# ===== Base Models =====

class Attachment(BaseModel):
    """File attachment for messages"""
    attachment_id: str = Field(default_factory=lambda: f"att_{uuid.uuid4().hex[:12]}")
    filename: str
    file_type: str  # "image", "document", "video", etc.
    file_size: int  # bytes
    file_url: str
    thumbnail_url: Optional[str] = None
    uploaded_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class Message(BaseModel):
    """Individual message in a conversation"""
    message_id: str = Field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}")
    conversation_id: str
    sender_id: str  # user_id or vendor_id
    sender_type: Literal["user", "vendor", "festimo"]
    content: str
    message_type: Literal["text", "image", "file", "quote", "system"] = "text"
    attachments: List[Attachment] = Field(default_factory=list)
    reply_to: Optional[str] = None  # message_id being replied to
    status: Literal["sent", "delivered", "read"] = "sent"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "message_id": "msg_abc123",
                "conversation_id": "conv_xyz789",
                "sender_id": "user_123",
                "sender_type": "user",
                "content": "Hi! I'm interested in your balloon services for my daughter's birthday party.",
                "message_type": "text",
                "attachments": [],
                "reply_to": None,
                "status": "sent",
                "timestamp": "2025-01-22T10:30:00Z",
                "metadata": {}
            }
        }


class Conversation(BaseModel):
    """Conversation between user and vendor(s)"""
    conversation_id: str = Field(default_factory=lambda: f"conv_{uuid.uuid4().hex[:12]}")
    party_id: str  # Links to existing party
    vendor_id: Optional[str] = None
    vendor_type: Optional[str] = None  # "balloon_artist", "caterer", etc.
    participants: List[str]  # [user_id, vendor_id, "festimo"]
    status: Literal["active", "archived", "closed"] = "active"
    last_message: Optional[Message] = None
    unread_count: Dict[str, int] = Field(default_factory=dict)  # per participant
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_xyz789",
                "party_id": "fp2025A12345",
                "vendor_id": "vendor_balloon_123",
                "vendor_type": "balloon_artist",
                "participants": ["user_123", "vendor_balloon_123", "festimo"],
                "status": "active",
                "last_message": None,
                "unread_count": {"user_123": 0, "vendor_balloon_123": 1},
                "created_at": "2025-01-22T10:00:00Z",
                "updated_at": "2025-01-22T10:30:00Z",
                "metadata": {}
            }
        }


class VendorProfile(BaseModel):
    """Vendor profile information"""
    vendor_id: str
    vendor_type: str  # "balloon_artist", "caterer", "photographer"
    business_name: str
    contact_name: str
    email: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    rating: float = Field(ge=0, le=5, default=0.0)
    response_time_avg: int = Field(default=60)  # minutes
    availability_status: Literal["online", "away", "offline"] = "offline"
    specialties: List[str] = Field(default_factory=list)
    portfolio: List[str] = Field(default_factory=list)  # image URLs
    pricing_info: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    class Config:
        json_schema_extra = {
            "example": {
                "vendor_id": "vendor_balloon_123",
                "vendor_type": "balloon_artist",
                "business_name": "Sarah's Magical Balloons",
                "contact_name": "Sarah Johnson",
                "email": "sarah@magicalballoons.com",
                "phone": "+1-555-0123",
                "avatar_url": "https://example.com/avatars/sarah.jpg",
                "rating": 4.8,
                "response_time_avg": 15,
                "availability_status": "online",
                "specialties": ["Animal balloons", "Balloon arches", "Party decorations"],
                "portfolio": ["https://example.com/portfolio/1.jpg"],
                "pricing_info": {"hourly_rate": 75, "package_deals": True},
                "created_at": "2025-01-20T09:00:00Z",
                "updated_at": "2025-01-22T10:30:00Z"
            }
        }


class Notification(BaseModel):
    """Notification for users"""
    notification_id: str = Field(default_factory=lambda: f"notif_{uuid.uuid4().hex[:12]}")
    user_id: str
    notification_type: Literal["message_received", "vendor_response", "vendor_online", "system_alert"]
    title: str
    message: str
    conversation_id: Optional[str] = None
    vendor_id: Optional[str] = None
    is_read: bool = False
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "notification_id": "notif_abc123",
                "user_id": "user_123",
                "notification_type": "vendor_response",
                "title": "New Message from Sarah's Balloons",
                "message": "Sarah replied to your message about balloon decorations",
                "conversation_id": "conv_xyz789",
                "vendor_id": "vendor_balloon_123",
                "is_read": False,
                "created_at": "2025-01-22T10:35:00Z",
                "metadata": {}
            }
        }


# ===== Request/Response Models =====

class SendMessageRequest(BaseModel):
    """Request to send a message"""
    conversation_id: str
    content: str
    message_type: Literal["text", "image", "file", "quote"] = "text"
    reply_to: Optional[str] = None
    attachments: List[Attachment] = Field(default_factory=list)


class CreateConversationRequest(BaseModel):
    """Request to create a new conversation"""
    party_id: str
    vendor_id: str
    initial_message: Optional[str] = None


class ConversationResponse(BaseModel):
    """Response for conversation data"""
    conversation: Conversation
    messages: List[Message]
    vendor_profile: Optional[VendorProfile] = None


class MessageResponse(BaseModel):
    """Response for message data"""
    message: Message
    conversation_id: str


class VendorListResponse(BaseModel):
    """Response for vendor list"""
    vendors: List[VendorProfile]
    total_count: int


class NotificationListResponse(BaseModel):
    """Response for notification list"""
    notifications: List[Notification]
    unread_count: int


# ===== WebSocket Message Models =====

class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    type: Literal[
        "message_sent", "message_received", "typing_start", "typing_stop",
        "vendor_online", "vendor_offline", "conversation_created",
        "notification_received", "message_status_update"
    ]
    conversation_id: Optional[str] = None
    message: Optional[Message] = None
    sender_id: Optional[str] = None
    vendor_id: Optional[str] = None
    notification: Optional[Notification] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TypingIndicator(BaseModel):
    """Typing indicator for real-time communication"""
    conversation_id: str
    sender_id: str
    sender_type: Literal["user", "vendor", "festimo"]
    is_typing: bool
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ===== Helper Functions =====

def create_message(
    conversation_id: str,
    sender_id: str,
    sender_type: Literal["user", "vendor", "festimo"],
    content: str,
    message_type: Literal["text", "image", "file", "quote", "system"] = "text",
    reply_to: Optional[str] = None
) -> Message:
    """Helper to create a new message"""
    return Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        sender_type=sender_type,
        content=content,
        message_type=message_type,
        reply_to=reply_to
    )


def create_conversation(
    party_id: str,
    vendor_id: str,
    vendor_type: str,
    participants: List[str]
) -> Conversation:
    """Helper to create a new conversation"""
    return Conversation(
        party_id=party_id,
        vendor_id=vendor_id,
        vendor_type=vendor_type,
        participants=participants
    )


def create_notification(
    user_id: str,
    notification_type: Literal["message_received", "vendor_response", "vendor_online", "system_alert"],
    title: str,
    message: str,
    conversation_id: Optional[str] = None,
    vendor_id: Optional[str] = None
) -> Notification:
    """Helper to create a new notification"""
    return Notification(
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        message=message,
        conversation_id=conversation_id,
        vendor_id=vendor_id
    )

