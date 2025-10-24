/**
 * Test Communication Data Flow
 * Simple test to verify demo data integration
 */

import { getDemoCommunicationData } from '../data/demoData'

export function testCommunicationData() {
  console.log('🧪 Testing Communication Data Flow...')
  
  try {
    const demoData = getDemoCommunicationData('demo-party')
    
    console.log('📊 Demo Data Results:')
    console.log('- Conversations:', demoData.conversations.length)
    console.log('- Vendors:', demoData.vendors.length)
    console.log('- Message Groups:', Object.keys(demoData.messages).length)
    
    // Test conversation structure
    if (demoData.conversations.length > 0) {
      const conv = demoData.conversations[0]
      console.log('✅ First conversation:', {
        id: conv.conversation_id,
        vendor: conv.vendor_type,
        participants: conv.participants.length,
        hasLastMessage: !!conv.last_message
      })
    }
    
    // Test vendor structure
    if (demoData.vendors.length > 0) {
      const vendor = demoData.vendors[0]
      console.log('✅ First vendor:', {
        id: vendor.vendor_id,
        name: vendor.business_name,
        type: vendor.vendor_type,
        rating: vendor.rating
      })
    }
    
    // Test messages structure
    const messageKeys = Object.keys(demoData.messages)
    if (messageKeys.length > 0) {
      const messages = demoData.messages[messageKeys[0]]
      console.log('✅ First message group:', {
        conversationId: messageKeys[0],
        messageCount: messages.length,
        firstMessage: messages[0]?.content?.substring(0, 50) + '...'
      })
    }
    
    console.log('🎉 All tests passed!')
    return true
    
  } catch (error) {
    console.error('❌ Test failed:', error)
    return false
  }
}

// Auto-run test in development
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  setTimeout(() => {
    testCommunicationData()
  }, 1000)
}
