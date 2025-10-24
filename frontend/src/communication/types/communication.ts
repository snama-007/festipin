/**
 * Communication System Types
 * TypeScript interfaces for the communication system
 */

export interface Message {
  message_id: string
  conversation_id: string
  sender_id: string
  sender_type: 'user' | 'vendor' | 'festimo'
  content: string
  message_type: 'text' | 'image' | 'file' | 'quote' | 'system'
  attachments: Attachment[]
  reply_to?: string
  status: 'sent' | 'delivered' | 'read'
  timestamp: string
  metadata: Record<string, any>
}

export interface Attachment {
  attachment_id: string
  filename: string
  file_type: string
  file_size: number
  file_url: string
  thumbnail_url?: string
  uploaded_at: string
}

export interface Conversation {
  conversation_id: string
  party_id: string
  vendor_id?: string
  vendor_type?: string
  participants: string[]
  status: 'active' | 'archived' | 'closed'
  last_message?: Message
  unread_count: Record<string, number>
  created_at: string
  updated_at: string
  metadata: Record<string, any>
}

export interface VendorProfile {
  vendor_id: string
  vendor_type: string
  business_name: string
  contact_name: string
  email: string
  phone?: string
  avatar_url?: string
  rating: number
  response_time_avg: number
  availability_status: 'online' | 'away' | 'offline'
  specialties: string[]
  portfolio: string[]
  pricing_info: Record<string, any>
  created_at: string
  updated_at: string
}

export interface Notification {
  notification_id: string
  user_id: string
  notification_type: 'message_received' | 'vendor_response' | 'vendor_online' | 'system_alert'
  title: string
  message: string
  conversation_id?: string
  vendor_id?: string
  is_read: boolean
  created_at: string
  metadata: Record<string, any>
}

// Request/Response Types
export interface SendMessageRequest {
  conversation_id: string
  content: string
  message_type: 'text' | 'image' | 'file' | 'quote'
  reply_to?: string
  attachments: Attachment[]
}

export interface CreateConversationRequest {
  party_id: string
  vendor_id: string
  initial_message?: string
}

export interface ConversationResponse {
  conversation: Conversation
  messages: Message[]
  vendor_profile?: VendorProfile
}

export interface MessageResponse {
  message: Message
  conversation_id: string
}

export interface VendorListResponse {
  vendors: VendorProfile[]
  total_count: number
}

export interface NotificationListResponse {
  notifications: Notification[]
  unread_count: number
}

// WebSocket Types
export interface WebSocketMessage {
  type: 'message_sent' | 'message_received' | 'typing_start' | 'typing_stop' |
        'vendor_online' | 'vendor_offline' | 'conversation_created' |
        'notification_received' | 'message_status_update' | 'connection' | 'pong'
  conversation_id?: string
  message?: Message
  sender_id?: string
  vendor_id?: string
  notification?: Notification
  timestamp: string
  metadata?: Record<string, any>
}

export interface TypingIndicator {
  conversation_id: string
  sender_id: string
  sender_type: 'user' | 'vendor' | 'festimo'
  is_typing: boolean
  timestamp: string
}

// Component Props Types
export interface CommunicationHubProps {
  partyId: string
  vendorRecommendations: VendorRecommendation[]
  onBack: () => void
}

export interface ConversationListProps {
  conversations: Conversation[]
  selectedConversationId?: string
  onSelectConversation: (conversationId: string) => void
  onCreateConversation: (vendorId: string) => void
}

export interface ConversationViewProps {
  conversation: Conversation
  messages: Message[]
  vendorProfile?: VendorProfile
  onSendMessage: (content: string) => void
  onTyping: (isTyping: boolean) => void
}

export interface MessageBubbleProps {
  message: Message
  isOwn: boolean
  showAvatar: boolean
  showTimestamp: boolean
  onReply?: (message: Message) => void
}

export interface MessageComposerProps {
  onSendMessage: (content: string) => void
  onTyping: (isTyping: boolean) => void
  disabled?: boolean
  placeholder?: string
}

export interface VendorSelectorProps {
  vendors: VendorProfile[]
  selectedVendor?: string
  onSelectVendor: (vendorId: string) => void
  onCreateConversation: (vendorId: string) => void
}

export interface NotificationCenterProps {
  notifications: Notification[]
  unreadCount: number
  onMarkAsRead: (notificationId: string) => void
  onClearAll: () => void
}

// Hook Types
export interface UseCommunicationReturn {
  conversations: Conversation[]
  selectedConversation: Conversation | null
  messages: Message[]
  vendors: VendorProfile[]
  notifications: Notification[]
  unreadCount: number
  isLoading: boolean
  error: string | null
  sendMessage: (conversationId: string, content: string) => Promise<void>
  createConversation: (vendorId: string, initialMessage?: string) => Promise<void>
  selectConversation: (conversationId: string) => void
  markAsRead: (conversationId: string) => void
  refetch: () => Promise<void>
}

export interface UseWebSocketReturn {
  isConnected: boolean
  connectionStatus: ConnectionStatus
  sendMessage: (message: WebSocketMessage) => void
  sendTypingIndicator: (conversationId: string, isTyping: boolean) => void
  reconnect: () => void
}

// State Types
export interface CommunicationState {
  conversations: Conversation[]
  selectedConversationId: string | null
  messages: Record<string, Message[]> // conversation_id -> messages
  vendors: VendorProfile[]
  notifications: Notification[]
  unreadCount: number
  isLoading: boolean
  error: string | null
  typingIndicators: Record<string, TypingIndicator[]> // conversation_id -> typing indicators
}

// Utility Types
export type MessageStatus = 'sent' | 'delivered' | 'read'
export type VendorStatus = 'online' | 'away' | 'offline'
export type ConversationStatus = 'active' | 'archived' | 'closed'
export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error'
export type NotificationType = 'message_received' | 'vendor_response' | 'vendor_online' | 'system_alert'

// Demo Data Types (for testing)
export interface DemoVendorRecommendation {
  type: string
  name: string
  services: string[]
  price_range: string
  contact_info: string
}

// Integration with existing Party Summary
export interface VendorRecommendation {
  type: string
  why_needed: string
  budget_range: number[]
  book_by?: string
  suggested_vendors?: string[]
}

