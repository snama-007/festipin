/**
 * Conversational Data Collection Dialog
 * Shows extracted data and asks user if they want to add more details
 */

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ExtractedEventData, ExtractionResponse } from '../services/api'

export interface ConversationalDialogProps {
  extractionResult: ExtractionResponse
  onAddDetails: () => void
  onBuildWithAgents: () => void
  onExit: () => void
}

export const ConversationalDialog: React.FC<ConversationalDialogProps> = ({
  extractionResult,
  onAddDetails,
  onBuildWithAgents,
  onExit
}) => {
  const [isExiting, setIsExiting] = useState(false)

  const handleExit = () => {
    setIsExiting(true)
    setTimeout(() => {
      onExit()
    }, 300)
  }

  const extractedData = extractionResult.extracted_data
  const hasMinimumData = extractionResult.missing_fields.length === 0 || 
    (extractedData.eventType && extractedData.theme && extractedData.location)

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100] flex items-center justify-center p-4"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white/20 backdrop-blur-2xl rounded-3xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col border border-white/30"
        style={{
          background: `
            linear-gradient(135deg, rgba(255, 182, 193, 0.3) 0%, rgba(255, 192, 203, 0.25) 50%, rgba(255, 218, 185, 0.2) 100%),
            radial-gradient(circle at 30% 20%, rgba(255, 182, 193, 0.4) 0%, transparent 50%)
          `,
          boxShadow: `
            0 8px 32px rgba(255, 182, 193, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.4),
            0 0 0 1px rgba(255, 255, 255, 0.2)
          `
        }}
      >
        {/* Animated Background Particles */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {[...Array(12)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-2 h-2 bg-gradient-to-r from-pink-400 to-rose-400 rounded-full opacity-60"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
              }}
              animate={{
                y: [0, -20, 0],
                x: [0, Math.random() * 10 - 5, 0],
                opacity: [0.6, 1, 0.6],
                scale: [1, 1.2, 1],
              }}
              transition={{
                duration: 3 + Math.random() * 2,
                repeat: Infinity,
                delay: Math.random() * 2,
              }}
            />
          ))}
        </div>

        {/* Liquid Glass Overlay */}
        <motion.div
          className="absolute inset-0 rounded-3xl opacity-40 pointer-events-none"
          style={{
            background: `
              linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.2) 50%, transparent 70%),
              radial-gradient(circle at 50% 50%, rgba(255, 182, 193, 0.15) 0%, transparent 70%)
            `
          }}
          animate={{
            backgroundPosition: ['0% 0%', '100% 100%'],
          }}
          transition={{
            duration: 6,
            repeat: Infinity,
            ease: 'linear'
          }}
        />

        {/* Header */}
        <div className="p-6 border-b border-white/20 flex-shrink-0 relative z-10">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-800 bg-gradient-to-r from-pink-600 to-rose-600 bg-clip-text text-transparent">
              🎉 Party Details Found!
            </h2>
            <button
              onClick={handleExit}
              className="text-gray-400 hover:text-gray-600 transition-colors p-2 rounded-full hover:bg-white/20"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto flex-grow relative z-10">
          {/* Friendly Message */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-6 rounded-2xl backdrop-blur-sm border border-white/40"
            style={{
              background: `
                linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.2) 100%)
              `,
              boxShadow: `
                0 8px 32px rgba(255, 182, 193, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.4)
              `
            }}
          >
            <p className="text-lg text-gray-800 leading-relaxed">
              {extractionResult.friendly_message}
            </p>
          </motion.div>

          {/* Extracted Data Display */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-6"
          >
            <h3 className="text-lg font-semibold text-gray-800 mb-4 bg-gradient-to-r from-pink-600 to-rose-600 bg-clip-text text-transparent">
              📋 What We Found:
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {extractedData.eventType && (
                <div className="p-4 rounded-xl bg-white/30 backdrop-blur-sm border border-white/40">
                  <div className="text-sm text-gray-600 mb-1">Event Type</div>
                  <div className="font-medium text-gray-800">{extractedData.eventType}</div>
                </div>
              )}
              
              {extractedData.theme && (
                <div className="p-4 rounded-xl bg-white/30 backdrop-blur-sm border border-white/40">
                  <div className="text-sm text-gray-600 mb-1">Theme</div>
                  <div className="font-medium text-gray-800">{extractedData.theme}</div>
                </div>
              )}
              
              {extractedData.age && (
                <div className="p-4 rounded-xl bg-white/30 backdrop-blur-sm border border-white/40">
                  <div className="text-sm text-gray-600 mb-1">Age</div>
                  <div className="font-medium text-gray-800">{extractedData.age} years old</div>
                </div>
              )}
              
              {extractedData.honoreeName && (
                <div className="p-4 rounded-xl bg-white/30 backdrop-blur-sm border border-white/40">
                  <div className="text-sm text-gray-600 mb-1">Celebrating</div>
                  <div className="font-medium text-gray-800">{extractedData.honoreeName}</div>
                </div>
              )}
              
              {extractedData.guestCount && (
                <div className="p-4 rounded-xl bg-white/30 backdrop-blur-sm border border-white/40">
                  <div className="text-sm text-gray-600 mb-1">Guests</div>
                  <div className="font-medium text-gray-800">
                    {extractedData.guestCount.adults + extractedData.guestCount.kids} total
                    ({extractedData.guestCount.adults} adults, {extractedData.guestCount.kids} kids)
                  </div>
                </div>
              )}
              
              {extractedData.location && (
                <div className="p-4 rounded-xl bg-white/30 backdrop-blur-sm border border-white/40">
                  <div className="text-sm text-gray-600 mb-1">Location</div>
                  <div className="font-medium text-gray-800">
                    {extractedData.location.type === 'Home' ? 'At Home' : extractedData.location.name}
                  </div>
                </div>
              )}
            </div>
          </motion.div>

          {/* Missing Fields Warning */}
          {extractionResult.missing_fields.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="mb-6 p-4 rounded-xl bg-yellow-50/80 backdrop-blur-sm border border-yellow-200"
            >
              <div className="flex items-start gap-3">
                <div className="text-yellow-600 text-xl">⚠️</div>
                <div>
                  <div className="font-medium text-yellow-800 mb-1">Missing Important Details</div>
                  <div className="text-sm text-yellow-700">
                    We need: {extractionResult.missing_fields.join(', ')}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="p-6 border-t border-white/20 flex flex-col gap-3 flex-shrink-0 relative z-10">
          {hasMinimumData ? (
            <>
              <motion.button
                onClick={onAddDetails}
                className="w-full px-6 py-4 bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-xl hover:from-blue-600 hover:to-purple-600 transition-all duration-300 font-medium shadow-lg hover:shadow-xl"
                style={{
                  boxShadow: '0 8px 32px rgba(59, 130, 246, 0.4)'
                }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                ✨ Add More Details
              </motion.button>
              
              <motion.button
                onClick={onBuildWithAgents}
                className="w-full px-6 py-4 bg-gradient-to-r from-pink-500 to-rose-500 text-white rounded-xl hover:from-pink-600 hover:to-rose-600 transition-all duration-300 font-medium shadow-lg hover:shadow-xl"
                style={{
                  boxShadow: '0 8px 32px rgba(255, 182, 193, 0.4)'
                }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                🤖 Build with Interactive Agents
              </motion.button>
            </>
          ) : (
            <motion.button
              onClick={onAddDetails}
              className="w-full px-6 py-4 bg-gradient-to-r from-pink-500 to-rose-500 text-white rounded-xl hover:from-pink-600 hover:to-rose-600 transition-all duration-300 font-medium shadow-lg hover:shadow-xl"
              style={{
                boxShadow: '0 8px 32px rgba(255, 182, 193, 0.4)'
              }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              ✨ Add Required Details
            </motion.button>
          )}
          
          <motion.button
            onClick={handleExit}
            className="w-full px-6 py-3 text-gray-600 border border-white/30 rounded-xl hover:bg-white/20 transition-all duration-300 backdrop-blur-sm font-medium"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            🚪 Exit & Delete Event
          </motion.button>
        </div>
      </motion.div>
    </motion.div>
  )
}
