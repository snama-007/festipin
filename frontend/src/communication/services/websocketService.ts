/**
 * WebSocket Service for Real-Time Communication
 * Handles WebSocket connections and real-time message updates
 */

import { WebSocketMessage, TypingIndicator } from '../types/communication'

export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error'

export interface WebSocketServiceOptions {
  partyId?: string
  vendorId?: string
  userId?: string
  onMessage?: (message: WebSocketMessage) => void
  onConnectionChange?: (status: ConnectionStatus) => void
  onError?: (error: Error) => void
  reconnectInterval?: number
  maxReconnectAttempts?: number
}

export class WebSocketService {
  private ws: WebSocket | null = null
  private options: WebSocketServiceOptions
  private reconnectAttempts = 0
  private reconnectTimeout: NodeJS.Timeout | null = null
  private heartbeatInterval: NodeJS.Timeout | null = null
  private isManualDisconnect = false

  constructor(options: WebSocketServiceOptions) {
    this.options = {
      reconnectInterval: 3000,
      maxReconnectAttempts: 5,
      ...options,
    }
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return
    }

    this.isManualDisconnect = false
    this.updateConnectionStatus('connecting')

    try {
      let wsUrl: string

      if (this.options.partyId) {
        wsUrl = `ws://localhost:9000/api/v1/communication/ws/party/${this.options.partyId}`
      } else if (this.options.vendorId) {
        wsUrl = `ws://localhost:9000/api/v1/communication/ws/vendor/${this.options.vendorId}`
      } else if (this.options.userId) {
        wsUrl = `ws://localhost:9000/api/v1/communication/ws/user/${this.options.userId}`
      } else {
        throw new Error('No connection target specified (partyId, vendorId, or userId)')
      }

      console.log('🔌 Connecting to WebSocket:', wsUrl)
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = this.handleOpen.bind(this)
      this.ws.onmessage = this.handleMessage.bind(this)
      this.ws.onclose = this.handleClose.bind(this)
      this.ws.onerror = this.handleError.bind(this)

    } catch (error) {
      console.error('❌ WebSocket connection error:', error)
      this.updateConnectionStatus('error')
      this.options.onError?.(error as Error)
    }
  }

  disconnect(): void {
    this.isManualDisconnect = true
    this.clearTimers()
    
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    
    this.updateConnectionStatus('disconnected')
  }

  sendMessage(message: WebSocketMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(message))
        console.log('📤 Sent WebSocket message:', message.type)
      } catch (error) {
        console.error('❌ Failed to send WebSocket message:', error)
        this.options.onError?.(error as Error)
      }
    } else {
      console.warn('⚠️ WebSocket not connected, cannot send message')
    }
  }

  sendTypingIndicator(conversationId: string, isTyping: boolean): void {
    const message: WebSocketMessage = {
      type: isTyping ? 'typing_start' : 'typing_stop',
      conversation_id: conversationId,
      timestamp: new Date().toISOString(),
      metadata: {
        typing_indicator: {
          conversation_id: conversationId,
          sender_id: this.options.userId || 'user_123',
          sender_type: 'user',
          is_typing: isTyping,
          timestamp: new Date().toISOString(),
        } as TypingIndicator,
      },
    }

    this.sendMessage(message)
  }

  sendPing(): void {
    const message: WebSocketMessage = {
      type: 'pong',
      timestamp: new Date().toISOString(),
    }

    this.sendMessage(message)
  }

  private handleOpen(): void {
    console.log('✅ WebSocket connected')
    this.updateConnectionStatus('connected')
    this.reconnectAttempts = 0
    
    // Start heartbeat
    this.startHeartbeat()
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data)
      console.log('📥 Received WebSocket message:', message.type)
      
      this.options.onMessage?.(message)
    } catch (error) {
      console.error('❌ Failed to parse WebSocket message:', error)
      this.options.onError?.(error as Error)
    }
  }

  private handleClose(event: CloseEvent): void {
    console.log('🔌 WebSocket disconnected:', event.code, event.reason)
    this.updateConnectionStatus('disconnected')
    this.clearTimers()

    // Attempt to reconnect if not manually disconnected
    if (!this.isManualDisconnect && this.reconnectAttempts < (this.options.maxReconnectAttempts || 5)) {
      this.scheduleReconnect()
    }
  }

  private handleError(error: Event): void {
    console.error('❌ WebSocket error:', error)
    this.updateConnectionStatus('error')
    this.options.onError?.(new Error('WebSocket connection error'))
  }

  private scheduleReconnect(): void {
    this.reconnectAttempts++
    const delay = (this.options.reconnectInterval || 3000) * this.reconnectAttempts
    
    console.log(`🔄 Scheduling reconnect attempt ${this.reconnectAttempts} in ${delay}ms`)
    
    this.reconnectTimeout = setTimeout(() => {
      this.connect()
    }, delay)
  }

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.sendPing()
      }
    }, 30000) // Send ping every 30 seconds
  }

  private clearTimers(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout)
      this.reconnectTimeout = null
    }
    
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  private updateConnectionStatus(status: ConnectionStatus): void {
    this.options.onConnectionChange?.(status)
  }

  getConnectionStatus(): ConnectionStatus {
    if (!this.ws) return 'disconnected'
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting'
      case WebSocket.OPEN:
        return 'connected'
      case WebSocket.CLOSING:
      case WebSocket.CLOSED:
        return 'disconnected'
      default:
        return 'error'
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

// Export singleton instances for different connection types
export const createPartyWebSocket = (partyId: string, options: Partial<WebSocketServiceOptions> = {}) => {
  return new WebSocketService({ ...options, partyId })
}

export const createVendorWebSocket = (vendorId: string, options: Partial<WebSocketServiceOptions> = {}) => {
  return new WebSocketService({ ...options, vendorId })
}

export const createUserWebSocket = (userId: string, options: Partial<WebSocketServiceOptions> = {}) => {
  return new WebSocketService({ ...options, userId })
}

