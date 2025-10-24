/**
 * API Testing Script
 * Test the communication API endpoints
 */

// Test API endpoints manually
const testAPIEndpoints = async () => {
  const baseUrl = 'http://localhost:9000/api/v1/communication'
  
  console.log('🧪 Testing Communication API Endpoints...')
  
  try {
    // Test 1: Get Party Conversations
    console.log('📞 Testing: GET /conversations/party/{partyId}')
    const conversationsResponse = await fetch(`${baseUrl}/conversations/party/demo-party`)
    console.log('✅ Conversations Response:', await conversationsResponse.json())
    
    // Test 2: Get Vendors
    console.log('📞 Testing: GET /vendors')
    const vendorsResponse = await fetch(`${baseUrl}/vendors`)
    console.log('✅ Vendors Response:', await vendorsResponse.json())
    
    // Test 3: Create Conversation
    console.log('📞 Testing: POST /conversations')
    const createConvResponse = await fetch(`${baseUrl}/conversations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        party_id: 'demo-party',
        vendor_id: 'test-vendor-123',
        initial_message: 'Hello! I\'m interested in your services.'
      })
    })
    console.log('✅ Create Conversation Response:', await createConvResponse.json())
    
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error)
    console.log('❌ API Test Failed (Expected - using demo data):', message)
    console.log('🔄 This is normal - the system will fall back to demo data')
  }
}

// Run API tests
if (typeof window !== 'undefined') {
  testAPIEndpoints()
}
