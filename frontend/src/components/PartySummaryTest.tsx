'use client'

import { useState } from 'react'
import { PartySummary } from '@/components/PartySummary'

/**
 * Standalone test component for Party Summary UI
 * Use this to test the Party Summary component anywhere in your app
 */
export function PartySummaryTest() {
  const [showSummary, setShowSummary] = useState(false)

  if (!showSummary) {
    return (
      <div className="p-8 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border border-purple-200">
        <div className="text-center">
          <div className="text-4xl mb-4">🧪</div>
          <h3 className="text-xl font-bold text-gray-800 mb-2">
            Party Summary UI Test
          </h3>
          <p className="text-gray-600 mb-4">
            Click to test the Party Summary component with dummy data
          </p>
          <button
            onClick={() => setShowSummary(true)}
            className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 transition-all duration-200"
          >
            🎊 Test Party Summary
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 z-50 bg-white">
      <div className="absolute top-4 left-4 z-10">
        <button
          onClick={() => setShowSummary(false)}
          className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
        >
          ← Back to Test
        </button>
      </div>
      <PartySummary 
        partyId="test-party-123" 
        onNext={() => {
          alert('Next step: Communication Hub (coming soon!)')
          setShowSummary(false)
        }}
      />
    </div>
  )
}
