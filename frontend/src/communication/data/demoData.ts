/**
 * Demo Communication Data
 * Provides demo data for testing the communication system
 */

import { Conversation, Message, VendorProfile } from '../types/communication'

export const demoVendors: VendorProfile[] = [
  {
    vendor_id: 'vendor_balloon_123',
    vendor_type: 'balloon_artist',
    business_name: "Sarah's Magical Balloons",
    contact_name: 'Sarah Johnson',
    email: 'sarah@magicalballoons.com',
    phone: '+1-555-0123',
    avatar_url: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=100&h=100&fit=crop&crop=face',
    rating: 4.8,
    response_time_avg: 15,
    availability_status: 'online',
    specialties: ['Animal balloons', 'Balloon arches', 'Party decorations'],
    portfolio: [
      'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300&h=200&fit=crop',
      'https://images.unsplash.com/photo-1607082349566-187342175e2f?w=300&h=200&fit=crop'
    ],
    pricing_info: { hourly_rate: 75, package_deals: true },
    created_at: '2025-01-20T09:00:00Z',
    updated_at: '2025-01-22T10:30:00Z'
  },
  {
    vendor_id: 'vendor_caterer_456',
    vendor_type: 'caterer',
    business_name: 'Gourmet Party Catering',
    contact_name: 'Michael Chen',
    email: 'michael@gourmetcatering.com',
    phone: '+1-555-0456',
    avatar_url: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=face',
    rating: 4.9,
    response_time_avg: 30,
    availability_status: 'online',
    specialties: ['Finger foods', 'Custom menus', 'Dietary accommodations'],
    portfolio: [
      'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=300&h=200&fit=crop',
      'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=300&h=200&fit=crop'
    ],
    pricing_info: { per_person: 25, minimum_order: 200 },
    created_at: '2025-01-19T14:00:00Z',
    updated_at: '2025-01-22T11:00:00Z'
  },
  {
    vendor_id: 'vendor_photographer_789',
    vendor_type: 'photographer',
    business_name: 'Memory Makers Photography',
    contact_name: 'Emma Rodriguez',
    email: 'emma@memorymakers.com',
    phone: '+1-555-0789',
    avatar_url: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop&crop=face',
    rating: 4.7,
    response_time_avg: 45,
    availability_status: 'away',
    specialties: ['Event photography', 'Photo booths', 'Digital galleries'],
    portfolio: [
      'https://images.unsplash.com/photo-1511795409834-ef04bbd61622?w=300&h=200&fit=crop',
      'https://images.unsplash.com/photo-1530103862676-de8c9debad1d?w=300&h=200&fit=crop'
    ],
    pricing_info: { hourly_rate: 150, package_deals: true },
    created_at: '2025-01-18T16:30:00Z',
    updated_at: '2025-01-22T09:15:00Z'
  }
]

export const demoMessages: Record<string, Message[]> = {
  'conv_vendor_balloon_123': [
    {
      message_id: 'msg_balloon_1',
      conversation_id: 'conv_vendor_balloon_123',
      sender_id: 'user_123',
      sender_type: 'user',
      content: "Hi Sarah! I'm planning a jungle-themed birthday party for my daughter and would love to include some magical balloon decorations. What do you recommend?",
      message_type: 'text',
      attachments: [],
      status: 'read',
      timestamp: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
      metadata: {}
    },
    {
      message_id: 'msg_balloon_2',
      conversation_id: 'conv_vendor_balloon_123',
      sender_id: 'vendor_balloon_123',
      sender_type: 'vendor',
      content: "Hello! A jungle theme sounds amazing! 🦁 I'd love to create some animal balloons like lions, elephants, and monkeys. I can also make a beautiful balloon arch in jungle colors. What's your party date?",
      message_type: 'text',
      attachments: [],
      status: 'delivered',
      timestamp: new Date(Date.now() - 1800000).toISOString(), // 30 minutes ago
      metadata: {}
    },
    {
      message_id: 'msg_balloon_3',
      conversation_id: 'conv_vendor_balloon_123',
      sender_id: 'user_123',
      sender_type: 'user',
      content: "That sounds perfect! The party is on March 15th from 2-5 PM. We're expecting about 25 kids. What would be your package for something like that?",
      message_type: 'text',
      attachments: [],
      status: 'read',
      timestamp: new Date(Date.now() - 900000).toISOString(), // 15 minutes ago
      metadata: {}
    }
  ],
  'conv_vendor_caterer_456': [
    {
      message_id: 'msg_caterer_1',
      conversation_id: 'conv_vendor_caterer_456',
      sender_id: 'user_123',
      sender_type: 'user',
      content: "Hi Michael! I'm looking for catering for a jungle-themed birthday party. We need kid-friendly options and some vegetarian choices. What do you have available?",
      message_type: 'text',
      attachments: [],
      status: 'read',
      timestamp: new Date(Date.now() - 2700000).toISOString(), // 45 minutes ago
      metadata: {}
    },
    {
      message_id: 'msg_caterer_2',
      conversation_id: 'conv_vendor_caterer_456',
      sender_id: 'vendor_caterer_456',
      sender_type: 'vendor',
      content: "Hi there! 🌿 I have some great jungle-themed options! How about animal-shaped sandwiches, fruit skewers, and veggie cups? I can also do mini quiches and jungle-themed cookies. All vegetarian options available!",
      message_type: 'text',
      attachments: [],
      status: 'delivered',
      timestamp: new Date(Date.now() - 1200000).toISOString(), // 20 minutes ago
      metadata: {}
    }
  ],
  'conv_vendor_photographer_789': [
    {
      message_id: 'msg_photo_1',
      conversation_id: 'conv_vendor_photographer_789',
      sender_id: 'user_123',
      sender_type: 'user',
      content: "Hi Emma! I'd love to capture the magical moments of my daughter's jungle birthday party. Do you offer photo booth services as well?",
      message_type: 'text',
      attachments: [],
      status: 'read',
      timestamp: new Date(Date.now() - 1800000).toISOString(), // 30 minutes ago
      metadata: {}
    }
  ]
}

export const demoConversations: Conversation[] = [
  {
    conversation_id: 'conv_vendor_balloon_123',
    party_id: 'demo-party',
    vendor_id: 'vendor_balloon_123',
    vendor_type: 'balloon_artist',
    participants: ['user_123', 'vendor_balloon_123', 'festimo'],
    status: 'active',
    last_message: demoMessages['conv_vendor_balloon_123'][demoMessages['conv_vendor_balloon_123'].length - 1],
    unread_count: { 'user_123': 0, 'vendor_balloon_123': 1 },
    created_at: '2025-01-22T10:00:00Z',
    updated_at: new Date(Date.now() - 900000).toISOString(),
    metadata: {}
  },
  {
    conversation_id: 'conv_vendor_caterer_456',
    party_id: 'demo-party',
    vendor_id: 'vendor_caterer_456',
    vendor_type: 'caterer',
    participants: ['user_123', 'vendor_caterer_456', 'festimo'],
    status: 'active',
    last_message: demoMessages['conv_vendor_caterer_456'][demoMessages['conv_vendor_caterer_456'].length - 1],
    unread_count: { 'user_123': 0, 'vendor_caterer_456': 1 },
    created_at: '2025-01-22T10:15:00Z',
    updated_at: new Date(Date.now() - 1200000).toISOString(),
    metadata: {}
  },
  {
    conversation_id: 'conv_vendor_photographer_789',
    party_id: 'demo-party',
    vendor_id: 'vendor_photographer_789',
    vendor_type: 'photographer',
    participants: ['user_123', 'vendor_photographer_789', 'festimo'],
    status: 'active',
    last_message: demoMessages['conv_vendor_photographer_789'][demoMessages['conv_vendor_photographer_789'].length - 1],
    unread_count: { 'user_123': 0, 'vendor_photographer_789': 1 },
    created_at: '2025-01-22T10:30:00Z',
    updated_at: new Date(Date.now() - 1800000).toISOString(),
    metadata: {}
  }
]

// Helper function to get demo data
export function getDemoCommunicationData(partyId: string) {
  return {
    conversations: demoConversations.filter(conv => conv.party_id === partyId),
    vendors: demoVendors,
    messages: demoMessages,
  }
}
