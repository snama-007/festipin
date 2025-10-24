/**
 * Communication System Test Suite
 * Manual testing guide for the communication system
 */

import React from 'react'
import { CommunicationHub } from '../components/CommunicationHub'
import { MessageBubble } from '../components/MessageBubble'
import { MessageComposer } from '../components/MessageComposer'

// Test data
const testPartyId = 'test-party-123'
const testVendorRecommendations = [
  {
    type: "Balloon Artist",
    why_needed: "Create magical balloon decorations",
    budget_range: [200, 400],
    suggested_vendors: ["Sarah's Balloons", "Magic Balloons Co."]
  },
  {
    type: "Caterer", 
    why_needed: "Provide delicious party food",
    budget_range: [500, 800],
    suggested_vendors: ["Gourmet Catering", "Party Food Express"]
  }
]

const testMessage = {
  message_id: 'test_msg_1',
  conversation_id: 'test_conv_1',
  sender_id: 'vendor_123',
  sender_type: 'vendor' as const,
  content: 'Hello! I\'d love to help with your party. What kind of decorations are you looking for?',
  message_type: 'text' as const,
  attachments: [],
  status: 'delivered' as const,
  timestamp: new Date().toISOString(),
  metadata: {}
}

// Test CommunicationHub Component
export function TestCommunicationHub() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
      <CommunicationHub
        partyId={testPartyId}
        vendorRecommendations={testVendorRecommendations}
        onBack={() => console.log('Back button clicked')}
      />
    </div>
  )
}

// Test MessageBubble Component
export function TestMessageBubble() {
  return (
    <div className="p-8 bg-gray-100">
      <h2 className="text-2xl font-bold mb-4">MessageBubble Tests</h2>
      
      {/* User Message */}
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-2">User Message</h3>
        <MessageBubble
          message={{
            ...testMessage,
            sender_type: 'user',
            content: 'Hi! I\'m interested in your balloon services.'
          }}
          isOwn={true}
          showAvatar={true}
          showTimestamp={true}
        />
      </div>

      {/* Vendor Message */}
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-2">Vendor Message</h3>
        <MessageBubble
          message={testMessage}
          isOwn={false}
          showAvatar={true}
          showTimestamp={true}
        />
      </div>

      {/* Festimo Message */}
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-2">Festimo Message</h3>
        <MessageBubble
          message={{
            ...testMessage,
            sender_type: 'festimo',
            content: '✨ I\'ve found the perfect vendor for you!'
          }}
          isOwn={false}
          showAvatar={true}
          showTimestamp={true}
        />
      </div>
    </div>
  )
}

// Test MessageComposer Component
export function TestMessageComposer() {
  return (
    <div className="p-8 bg-gray-100">
      <h2 className="text-2xl font-bold mb-4">MessageComposer Tests</h2>
      
      <div className="max-w-md">
        <MessageComposer
          onSendMessage={(content) => {
            console.log('Message sent:', content)
            alert(`Message sent: "${content}"`)
          }}
          onTyping={(isTyping) => {
            console.log('Typing:', isTyping)
          }}
          placeholder="Type your test message..."
        />
      </div>
    </div>
  )
}

// Comprehensive Test Page
export function CommunicationTestPage() {
  const [testMode, setTestMode] = React.useState<'hub' | 'bubble' | 'composer'>('hub')

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
      {/* Test Navigation */}
      <div className="p-4 bg-white shadow-lg">
        <h1 className="text-3xl font-bold mb-4">🧪 Communication System Test Suite</h1>
        <div className="flex gap-4">
          <button
            onClick={() => setTestMode('hub')}
            className={`px-4 py-2 rounded-lg font-semibold ${
              testMode === 'hub' 
                ? 'bg-purple-600 text-white' 
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            Communication Hub
          </button>
          <button
            onClick={() => setTestMode('bubble')}
            className={`px-4 py-2 rounded-lg font-semibold ${
              testMode === 'bubble' 
                ? 'bg-purple-600 text-white' 
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            Message Bubble
          </button>
          <button
            onClick={() => setTestMode('composer')}
            className={`px-4 py-2 rounded-lg font-semibold ${
              testMode === 'composer' 
                ? 'bg-purple-600 text-white' 
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            Message Composer
          </button>
        </div>
      </div>

      {/* Test Content */}
      <div className="flex-1">
        {testMode === 'hub' && <TestCommunicationHub />}
        {testMode === 'bubble' && <TestMessageBubble />}
        {testMode === 'composer' && <TestMessageComposer />}
      </div>
    </div>
  )
}
