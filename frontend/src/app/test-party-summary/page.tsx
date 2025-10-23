'use client'

import { useState } from 'react'
import { PartySummary } from '@/components/PartySummary'
import { ErrorBoundary, DefaultErrorFallback } from '@/components/ErrorBoundary'

export default function TestPartySummary() {
  const [showSummary, setShowSummary] = useState(false)
  const [showCommunication, setShowCommunication] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
      {!showSummary && !showCommunication ? (
        // Test Landing Page
        <div className="flex items-center justify-center min-h-screen p-8">
          <div className="text-center max-w-2xl">
            <div className="text-6xl mb-6">🧪</div>
            <h1 className="text-4xl font-bold text-gray-800 mb-4">
              Party Summary UI Test
            </h1>
            <p className="text-lg text-gray-600 mb-8">
              This page demonstrates the Party Summary UI with dummy data. 
              Click the button below to see the complete party planning interface.
            </p>
            
            <div className="space-y-4">
              <button
                onClick={() => setShowSummary(true)}
                className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-4 rounded-xl text-lg font-semibold hover:from-purple-700 hover:to-pink-700 transform hover:scale-105 transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                🎊 Test Party Summary UI
              </button>
              
              <div className="text-sm text-gray-500">
                <p>✅ Uses demo data when API is unavailable</p>
                <p>✅ Fully responsive design</p>
                <p>✅ Smooth animations and transitions</p>
                <p>✅ Complete party planning showcase</p>
              </div>
            </div>
          </div>
        </div>
      ) : showSummary ? (
        // Party Summary View with Error Boundary
        <ErrorBoundary fallback={DefaultErrorFallback}>
          <PartySummary 
            partyId="test-party-123" 
            onNext={() => {
              setShowSummary(false)
              setShowCommunication(true)
            }}
          />
        </ErrorBoundary>
      ) : (
        // Communication Hub Placeholder
        <div className="flex items-center justify-center min-h-screen p-8">
          <div className="text-center max-w-2xl">
            <div className="text-6xl mb-6">💬</div>
            <h1 className="text-3xl font-bold text-gray-800 mb-4">
              Communication Hub
            </h1>
            <p className="text-lg text-gray-600 mb-8">
              This is where vendor communication will be implemented next.
            </p>
            
            <button
              onClick={() => {
                setShowCommunication(false)
                setShowSummary(true)
              }}
              className="bg-gray-600 text-white px-6 py-3 rounded-lg hover:bg-gray-700 transition-colors"
            >
              ← Back to Party Summary
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
