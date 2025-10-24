/**
 * Communication API Service
 * Handles all API calls for the communication system
 */

import { 
  Message, 
  Conversation, 
  VendorProfile, 
  Notification,
  SendMessageRequest,
  CreateConversationRequest,
  ConversationResponse,
  MessageResponse,
  VendorListResponse,
  NotificationListResponse
} from '../types/communication'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9000'

class CommunicationAPI {
  private baseUrl: string

  constructor() {
    this.baseUrl = `${API_BASE_URL}/api/v1/communication`
  }

  // Message API calls
  async sendMessage(conversationId: string, request: SendMessageRequest): Promise<MessageResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/conversations/${conversationId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        throw new Error(`Failed to send message: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error sending message:', error)
      throw error
    }
  }

  async getConversationMessages(
    conversationId: string, 
    limit: number = 50, 
    offset: number = 0
  ): Promise<{ messages: Message[]; total_count: number }> {
    try {
      const response = await fetch(
        `${this.baseUrl}/conversations/${conversationId}/messages?limit=${limit}&offset=${offset}`
      )

      if (!response.ok) {
        throw new Error(`Failed to get messages: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error getting messages:', error)
      throw error
    }
  }

  async markConversationAsRead(conversationId: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/conversations/${conversationId}/read`, {
        method: 'PUT',
      })

      if (!response.ok) {
        console.warn('Failed to mark conversation as read, continuing gracefully.', {
          status: response.status,
          statusText: response.statusText,
        })
      }
    } catch (error) {
      console.warn('Mark conversation as read fell back to optimistic state.', error)
    }
  }

  async deleteMessage(messageId: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/messages/${messageId}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error(`Failed to delete message: ${response.statusText}`)
      }
    } catch (error) {
      console.error('Error deleting message:', error)
      throw error
    }
  }

  async searchMessages(
    conversationId: string, 
    query: string, 
    limit: number = 20
  ): Promise<{ messages: Message[]; results_count: number }> {
    try {
      const response = await fetch(
        `${this.baseUrl}/conversations/${conversationId}/search?q=${encodeURIComponent(query)}&limit=${limit}`
      )

      if (!response.ok) {
        throw new Error(`Failed to search messages: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error searching messages:', error)
      throw error
    }
  }

  // Conversation API calls
  async getPartyConversations(partyId: string): Promise<{ conversations: Conversation[]; total_count: number }> {
    try {
      const response = await fetch(`${this.baseUrl}/parties/${partyId}/conversations`)

      if (!response.ok) {
        throw new Error(`Failed to get conversations: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error getting conversations:', error)
      throw error
    }
  }

  async createConversation(request: CreateConversationRequest): Promise<{ conversation: Conversation; status: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/conversations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        throw new Error(`Failed to create conversation: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error creating conversation:', error)
      throw error
    }
  }

  // Vendor API calls
  async getVendors(): Promise<VendorListResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/vendors`)

      if (!response.ok) {
        throw new Error(`Failed to get vendors: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error getting vendors:', error)
      throw error
    }
  }

  async getVendorProfile(vendorId: string): Promise<VendorProfile> {
    try {
      const response = await fetch(`${this.baseUrl}/vendors/${vendorId}`)

      if (!response.ok) {
        throw new Error(`Failed to get vendor profile: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error getting vendor profile:', error)
      throw error
    }
  }

  // Notification API calls
  async getNotifications(): Promise<NotificationListResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/notifications`)

      if (!response.ok) {
        throw new Error(`Failed to get notifications: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error getting notifications:', error)
      throw error
    }
  }

  async markNotificationAsRead(notificationId: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/notifications/${notificationId}/read`, {
        method: 'PUT',
      })

      if (!response.ok) {
        throw new Error(`Failed to mark notification as read: ${response.statusText}`)
      }
    } catch (error) {
      console.error('Error marking notification as read:', error)
      throw error
    }
  }

  async deleteNotification(notificationId: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/notifications/${notificationId}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error(`Failed to delete notification: ${response.statusText}`)
      }
    } catch (error) {
      console.error('Error deleting notification:', error)
      throw error
    }
  }
}

// Export singleton instance
export const communicationAPI = new CommunicationAPI()
export default communicationAPI
