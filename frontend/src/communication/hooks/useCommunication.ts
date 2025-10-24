/**
 * Communication Hooks
 * Custom React hooks for the communication system
 */

import { useState, useEffect, useCallback, useRef } from 'react'
import { 
  Conversation, 
  Message, 
  VendorProfile, 
  Notification,
  UseCommunicationReturn,
  UseWebSocketReturn,
  WebSocketMessage,
  ConversationStatus,
  ConnectionStatus
} from '../types/communication'
import { communicationAPI } from '../services/communicationApi'
import { createPartyWebSocket } from '../services/websocketService'
import { getDemoCommunicationData } from '../data/demoData'

export function useCommunication(partyId: string): UseCommunicationReturn {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Record<string, Message[]>>({})
  const [vendors, setVendors] = useState<VendorProfile[]>([])
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadConversations = useCallback(async () => {
    try {
      console.log('🔄 Loading conversations for party:', partyId)
      const data = await communicationAPI.getPartyConversations(partyId)
      console.log('✅ API conversations loaded:', data.conversations.length)
      setConversations(data.conversations)
    } catch (error) {
      console.error('❌ Error loading conversations:', error)
      console.log('🔄 Falling back to demo data...')
      // Use demo data as fallback
      const demoData = getDemoCommunicationData(partyId)
      console.log('📊 Demo data loaded:', {
        conversations: demoData.conversations.length,
        vendors: demoData.vendors.length,
        messageGroups: Object.keys(demoData.messages).length
      })
      setConversations(demoData.conversations)
      setMessages(demoData.messages)
    }
  }, [partyId])

  const loadVendors = useCallback(async () => {
    try {
      console.log('🔄 Loading vendors...')
      const data = await communicationAPI.getVendors()
      console.log('✅ API vendors loaded:', data.vendors.length)
      setVendors(data.vendors)
    } catch (error) {
      console.error('❌ Error loading vendors:', error)
      console.log('🔄 Falling back to demo vendors...')
      // Use demo data as fallback
      const demoData = getDemoCommunicationData(partyId)
      console.log('📊 Demo vendors loaded:', demoData.vendors.length)
      setVendors(demoData.vendors)
    }
  }, [partyId])

  const loadNotifications = useCallback(async () => {
    try {
      const data = await communicationAPI.getNotifications()
      setNotifications(data.notifications)
      setUnreadCount(data.unread_count)
    } catch (error) {
      console.error('Error loading notifications:', error)
    }
  }, [])

  const loadMessages = useCallback(async (conversationId: string) => {
    try {
      const data = await communicationAPI.getConversationMessages(conversationId)
      setMessages(prev => ({
        ...prev,
        [conversationId]: data.messages,
      }))
    } catch (error) {
      console.error('Error loading messages:', error)
      setError(error instanceof Error ? error.message : 'Failed to load messages')
    }
  }, [])

  const sendMessage = useCallback(async (conversationId: string, content: string) => {
    try {
      const response = await communicationAPI.sendMessage(conversationId, {
        conversation_id: conversationId,
        content,
        message_type: 'text',
        attachments: [],
      })

      // Add message to local state
      setMessages(prev => ({
        ...prev,
        [conversationId]: [
          ...(prev[conversationId] || []),
          response.message,
        ],
      }))

      // Update conversation's last message
      setConversations(prev => 
        prev.map(conv => 
          conv.conversation_id === conversationId
            ? { ...conv, last_message: response.message, updated_at: new Date().toISOString() }
            : conv
        )
      )

    } catch (error) {
      console.error('Error sending message:', error)
      setError(error instanceof Error ? error.message : 'Failed to send message')
      throw error
    }
  }, [])

  const createConversation = useCallback(async (vendorId: string, initialMessage?: string) => {
    try {
      const response = await communicationAPI.createConversation({
        party_id: partyId,
        vendor_id: vendorId,
        initial_message: initialMessage,
      })

      // Add conversation to local state
      setConversations(prev => [response.conversation, ...prev])

      // If there's an initial message, add it to messages
      if (initialMessage) {
        const message: Message = {
          message_id: `temp_${Date.now()}`,
          conversation_id: response.conversation.conversation_id,
          sender_id: 'user_123',
          sender_type: 'user',
          content: initialMessage,
          message_type: 'text',
          attachments: [],
          status: 'sent',
          timestamp: new Date().toISOString(),
          metadata: {},
        }

        setMessages(prev => ({
          ...prev,
          [response.conversation.conversation_id]: [message],
        }))
      }

    } catch (error) {
      console.error('Error creating conversation:', error)
      setError(error instanceof Error ? error.message : 'Failed to create conversation')
      throw error
    }
  }, [partyId])

  const selectConversation = useCallback((conversationId: string) => {
    setSelectedConversationId(conversationId)
    
    // Load messages if not already loaded
    if (!messages[conversationId]) {
      loadMessages(conversationId)
    }

    // Mark conversation as read
    communicationAPI.markConversationAsRead(conversationId)
  }, [messages, loadMessages])

  const markAsRead = useCallback(async (conversationId: string) => {
    try {
      await communicationAPI.markConversationAsRead(conversationId)
      
      // Update local state
      setConversations(prev => 
        prev.map(conv => 
          conv.conversation_id === conversationId
            ? { ...conv, unread_count: { ...conv.unread_count, 'user_123': 0 } }
            : conv
        )
      )
    } catch (error) {
      console.error('Error marking conversation as read:', error)
    }
  }, [])

  const refreshData = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      await Promise.all([
        loadConversations(),
        loadVendors(),
        loadNotifications(),
      ])
    } catch (error) {
      console.error('Error refreshing data:', error)
    } finally {
      setIsLoading(false)
    }
  }, [loadConversations, loadVendors, loadNotifications])

  // Load initial data
  useEffect(() => {
    refreshData()
  }, [refreshData])

  const selectedConversation = conversations.find(c => c.conversation_id === selectedConversationId) ?? null

  return {
    conversations,
    selectedConversation,
    messages: selectedConversationId ? messages[selectedConversationId] || [] : [],
    vendors,
    notifications,
    unreadCount,
    isLoading,
    error,
    sendMessage,
    createConversation,
    selectConversation,
    markAsRead,
    refetch: refreshData,
  }
}

export function useWebSocket(
  partyId: string,
  onMessage?: (message: WebSocketMessage) => void
): UseWebSocketReturn {
  const [isConnected, setIsConnected] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('disconnected')
  const wsServiceRef = useRef<any>(null)

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (wsServiceRef.current) {
      wsServiceRef.current.sendMessage(message)
    }
  }, [])

  const sendTypingIndicator = useCallback((conversationId: string, isTyping: boolean) => {
    if (wsServiceRef.current) {
      wsServiceRef.current.sendTypingIndicator(conversationId, isTyping)
    }
  }, [])

  const reconnect = useCallback(() => {
    if (wsServiceRef.current) {
      wsServiceRef.current.disconnect()
      wsServiceRef.current.connect()
    }
  }, [])

  useEffect(() => {
    const ws = createPartyWebSocket(partyId, {
      onMessage: (message) => {
        console.log('📥 WebSocket message received:', message.type)
        onMessage?.(message)
      },
      onConnectionChange: (status) => {
        console.log('🔌 WebSocket status changed:', status)
        setConnectionStatus(status)
        setIsConnected(status === 'connected')
      },
      onError: (error) => {
        console.error('❌ WebSocket error:', error)
        setConnectionStatus('error')
        setIsConnected(false)
      },
    })

    ws.connect()
    wsServiceRef.current = ws

    return () => {
      ws.disconnect()
      wsServiceRef.current = null
    }
  }, [partyId, onMessage])

  return {
    isConnected,
    connectionStatus,
    sendMessage,
    sendTypingIndicator,
    reconnect,
  }
}

export function useMessages(conversationId: string | null) {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadMessages = useCallback(async () => {
    if (!conversationId) return

    setIsLoading(true)
    setError(null)

    try {
      const data = await communicationAPI.getConversationMessages(conversationId)
      setMessages(data.messages)
    } catch (error) {
      console.error('Error loading messages:', error)
      setError(error instanceof Error ? error.message : 'Failed to load messages')
    } finally {
      setIsLoading(false)
    }
  }, [conversationId])

  const addMessage = useCallback((message: Message) => {
    setMessages(prev => [...prev, message])
  }, [])

  const updateMessage = useCallback((messageId: string, updates: Partial<Message>) => {
    setMessages(prev => 
      prev.map(msg => 
        msg.message_id === messageId ? { ...msg, ...updates } : msg
      )
    )
  }, [])

  const deleteMessage = useCallback(async (messageId: string) => {
    try {
      await communicationAPI.deleteMessage(messageId)
      setMessages(prev => prev.filter(msg => msg.message_id !== messageId))
    } catch (error) {
      console.error('Error deleting message:', error)
      setError(error instanceof Error ? error.message : 'Failed to delete message')
    }
  }, [])

  useEffect(() => {
    loadMessages()
  }, [loadMessages])

  return {
    messages,
    isLoading,
    error,
    addMessage,
    updateMessage,
    deleteMessage,
    refreshMessages: loadMessages,
  }
}

export function useNotifications() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [isLoading, setIsLoading] = useState(false)

  const loadNotifications = useCallback(async () => {
    setIsLoading(true)
    try {
      const data = await communicationAPI.getNotifications()
      setNotifications(data.notifications)
      setUnreadCount(data.unread_count)
    } catch (error) {
      console.error('Error loading notifications:', error)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const markAsRead = useCallback(async (notificationId: string) => {
    try {
      await communicationAPI.markNotificationAsRead(notificationId)
      setNotifications(prev => 
        prev.map(notif => 
          notif.notification_id === notificationId 
            ? { ...notif, is_read: true }
            : notif
        )
      )
      setUnreadCount(prev => Math.max(0, prev - 1))
    } catch (error) {
      console.error('Error marking notification as read:', error)
    }
  }, [])

  const deleteNotification = useCallback(async (notificationId: string) => {
    try {
      await communicationAPI.deleteNotification(notificationId)
      setNotifications(prev => prev.filter(notif => notif.notification_id !== notificationId))
    } catch (error) {
      console.error('Error deleting notification:', error)
    }
  }, [])

  useEffect(() => {
    loadNotifications()
  }, [loadNotifications])

  return {
    notifications,
    unreadCount,
    isLoading,
    markAsRead,
    deleteNotification,
    refreshNotifications: loadNotifications,
  }
}
