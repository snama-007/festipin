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
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/60 backdrop-blur-md z-[100] flex items-center justify-center p-4"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0, y: 20 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        exit={{ scale: 0.9, opacity: 0, y: -20 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
        className="bg-white/95 backdrop-blur-2xl rounded-3xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col border border-white/60"
        style={{
          background: `
            linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.95) 100%),
            radial-gradient(circle at 20% 80%, rgba(59, 130, 246, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(147, 51, 234, 0.05) 0%, transparent 50%)
          `,
          boxShadow: `
            0 25px 50px rgba(0, 0, 0, 0.15),
            0 0 0 1px rgba(255, 255, 255, 0.8),
            inset 0 1px 0 rgba(255, 255, 255, 0.9)
          `
        }}
      >
        {/* Animated Background Elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {/* Floating Orbs */}
          {[...Array(6)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-3 h-3 bg-gradient-to-r from-blue-400/20 to-purple-400/20 rounded-full"
              style={{
                left: `${20 + i * 15}%`,
                top: `${30 + i * 10}%`,
              }}
              animate={{
                y: [0, -30, 0],
                x: [0, Math.random() * 20 - 10, 0],
                opacity: [0.3, 0.8, 0.3],
                scale: [1, 1.5, 1],
              }}
              transition={{
                duration: 4 + Math.random() * 2,
                repeat: Infinity,
                delay: Math.random() * 2,
                ease: "easeInOut"
              }}
            />
          ))}
          
          {/* Gradient Mesh */}
          <motion.div
            className="absolute inset-0 opacity-30"
            style={{
              background: `
                radial-gradient(circle at 30% 20%, rgba(59, 130, 246, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 70% 80%, rgba(147, 51, 234, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 50% 50%, rgba(236, 72, 153, 0.05) 0%, transparent 50%)
              `
            }}
            animate={{
              backgroundPosition: ['0% 0%', '100% 100%'],
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: "linear"
            }}
          />
        </div>

        {/* Header */}
        <div className="p-8 border-b border-gray-200/50 flex-shrink-0 relative z-10">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-4">
              <motion.div
                className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center text-white text-xl shadow-lg"
                animate={{ 
                  rotate: [0, 5, -5, 0],
                  scale: [1, 1.05, 1]
                }}
                transition={{ 
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                🎉
              </motion.div>
              <div>
                <h2 className="text-3xl font-bold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
                  Party Details Found!
                </h2>
                <p className="text-gray-500 text-sm mt-1">We've analyzed your request and found some great details</p>
              </div>
            </div>
            <motion.button
              onClick={handleExit}
              className="w-10 h-10 bg-gray-100/80 hover:bg-gray-200/80 rounded-xl flex items-center justify-center text-gray-500 hover:text-gray-700 transition-all duration-200 backdrop-blur-sm border border-gray-200/50"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </motion.button>
          </div>
        </div>

        {/* Content */}
        <div className="p-8 overflow-y-auto flex-grow relative z-10">
          {/* Success Message */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8 p-6 rounded-2xl bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200/50 backdrop-blur-sm"
            style={{
              boxShadow: '0 8px 32px rgba(34, 197, 94, 0.1)'
            }}
          >
            <div className="flex items-start gap-4">
              <div className="w-8 h-8 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl flex items-center justify-center text-white text-sm font-bold">
                ✓
              </div>
              <div>
                <h3 className="text-lg font-semibold text-green-800 mb-2">Analysis Complete!</h3>
                <p className="text-green-700 leading-relaxed">
                  {extractionResult.friendly_message}
                </p>
              </div>
            </div>
          </motion.div>

          {/* Extracted Data Display */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-8"
          >
            <div className="flex items-center gap-3 mb-6">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center text-white text-sm font-bold">
                📋
              </div>
              <h3 className="text-xl font-bold text-gray-800">What We Found</h3>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {extractedData.eventType && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.2 }}
                  className="group p-5 rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200/50 hover:border-blue-300/50 transition-all duration-300 backdrop-blur-sm"
                  style={{
                    boxShadow: '0 4px 20px rgba(59, 130, 246, 0.08)'
                  }}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-6 h-6 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg flex items-center justify-center text-white text-xs">
                      🎂
                    </div>
                    <div className="text-sm font-medium text-blue-600 uppercase tracking-wide">Event Type</div>
                  </div>
                  <div className="font-semibold text-gray-800 text-lg">{extractedData.eventType}</div>
                </motion.div>
              )}
              
              {extractedData.theme && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.3 }}
                  className="group p-5 rounded-2xl bg-gradient-to-br from-purple-50 to-pink-50 border border-purple-200/50 hover:border-purple-300/50 transition-all duration-300 backdrop-blur-sm"
                  style={{
                    boxShadow: '0 4px 20px rgba(147, 51, 234, 0.08)'
                  }}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center text-white text-xs">
                      🎨
                    </div>
                    <div className="text-sm font-medium text-purple-600 uppercase tracking-wide">Theme</div>
                  </div>
                  <div className="font-semibold text-gray-800 text-lg">{extractedData.theme}</div>
                </motion.div>
              )}
              
              {extractedData.age && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.4 }}
                  className="group p-5 rounded-2xl bg-gradient-to-br from-orange-50 to-yellow-50 border border-orange-200/50 hover:border-orange-300/50 transition-all duration-300 backdrop-blur-sm"
                  style={{
                    boxShadow: '0 4px 20px rgba(251, 146, 60, 0.08)'
                  }}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-6 h-6 bg-gradient-to-r from-orange-500 to-yellow-500 rounded-lg flex items-center justify-center text-white text-xs">
                      🎈
                    </div>
                    <div className="text-sm font-medium text-orange-600 uppercase tracking-wide">Age</div>
                  </div>
                  <div className="font-semibold text-gray-800 text-lg">{extractedData.age} years old</div>
                </motion.div>
              )}
              
              {extractedData.honoreeName && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.5 }}
                  className="group p-5 rounded-2xl bg-gradient-to-br from-pink-50 to-rose-50 border border-pink-200/50 hover:border-pink-300/50 transition-all duration-300 backdrop-blur-sm"
                  style={{
                    boxShadow: '0 4px 20px rgba(236, 72, 153, 0.08)'
                  }}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-6 h-6 bg-gradient-to-r from-pink-500 to-rose-500 rounded-lg flex items-center justify-center text-white text-xs">
                      👑
                    </div>
                    <div className="text-sm font-medium text-pink-600 uppercase tracking-wide">Celebrating</div>
                  </div>
                  <div className="font-semibold text-gray-800 text-lg">{extractedData.honoreeName}</div>
                </motion.div>
              )}
              
              {extractedData.guestCount && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.6 }}
                  className="group p-5 rounded-2xl bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200/50 hover:border-emerald-300/50 transition-all duration-300 backdrop-blur-sm"
                  style={{
                    boxShadow: '0 4px 20px rgba(16, 185, 129, 0.08)'
                  }}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-6 h-6 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-lg flex items-center justify-center text-white text-xs">
                      👥
                    </div>
                    <div className="text-sm font-medium text-emerald-600 uppercase tracking-wide">Guests</div>
                  </div>
                  <div className="font-semibold text-gray-800 text-lg">
                    {extractedData.guestCount.adults + extractedData.guestCount.kids} total
                  </div>
                  <div className="text-sm text-emerald-600 mt-1">
                    ({extractedData.guestCount.adults} adults, {extractedData.guestCount.kids} kids)
                  </div>
                </motion.div>
              )}
              
              {extractedData.location && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.7 }}
                  className="group p-5 rounded-2xl bg-gradient-to-br from-cyan-50 to-blue-50 border border-cyan-200/50 hover:border-cyan-300/50 transition-all duration-300 backdrop-blur-sm"
                  style={{
                    boxShadow: '0 4px 20px rgba(6, 182, 212, 0.08)'
                  }}
                >
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-6 h-6 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg flex items-center justify-center text-white text-xs">
                      📍
                    </div>
                    <div className="text-sm font-medium text-cyan-600 uppercase tracking-wide">Location</div>
                  </div>
                  <div className="font-semibold text-gray-800 text-lg">
                    {extractedData.location.type === 'Home' ? 'At Home' : 
                     extractedData.location.name ? extractedData.location.name : 
                     extractedData.location.address ? extractedData.location.address :
                     extractedData.location.type || 'Location specified'}
                  </div>
                </motion.div>
              )}
            </div>
          </motion.div>

          {/* Missing Fields Warning */}
          {extractionResult.missing_fields.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
              className="mb-8 p-6 rounded-2xl bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200/50 backdrop-blur-sm"
              style={{
                boxShadow: '0 8px 32px rgba(245, 158, 11, 0.1)'
              }}
            >
              <div className="flex items-start gap-4">
                <div className="w-8 h-8 bg-gradient-to-r from-amber-500 to-orange-500 rounded-xl flex items-center justify-center text-white text-sm font-bold">
                  ⚠️
                </div>
                <div>
                  <h4 className="font-semibold text-amber-800 mb-2">Missing Important Details</h4>
                  <p className="text-amber-700 text-sm leading-relaxed">
                    We need: <span className="font-medium">{extractionResult.missing_fields.join(', ')}</span>
                  </p>
                </div>
              </div>
            </motion.div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="p-8 border-t border-gray-200/50 flex flex-col gap-4 flex-shrink-0 relative z-10">
          {hasMinimumData ? (
            <>
              <motion.button
                onClick={onAddDetails}
                className="w-full px-6 py-4 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white rounded-2xl transition-all duration-300 font-semibold shadow-lg hover:shadow-xl backdrop-blur-sm border border-white/20"
                style={{
                  boxShadow: '0 8px 32px rgba(59, 130, 246, 0.3)'
                }}
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.9 }}
              >
                <div className="flex items-center justify-center gap-3">
                  <span className="text-lg">✨</span>
                  <span>Add More Details</span>
                </div>
              </motion.button>
              
              <motion.button
                onClick={onBuildWithAgents}
                className="w-full px-6 py-4 bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 text-white rounded-2xl transition-all duration-300 font-semibold shadow-lg hover:shadow-xl backdrop-blur-sm border border-white/20"
                style={{
                  boxShadow: '0 8px 32px rgba(236, 72, 153, 0.3)'
                }}
                whileHover={{ scale: 1.02, y: -2 }}
                whileTap={{ scale: 0.98 }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.0 }}
              >
                <div className="flex items-center justify-center gap-3">
                  <span className="text-lg">🤖</span>
                  <span>Build with Interactive Agents</span>
                </div>
              </motion.button>
            </>
          ) : (
            <motion.button
              onClick={onAddDetails}
              className="w-full px-6 py-4 bg-gradient-to-r from-pink-500 to-rose-500 hover:from-pink-600 hover:to-rose-600 text-white rounded-2xl transition-all duration-300 font-semibold shadow-lg hover:shadow-xl backdrop-blur-sm border border-white/20"
              style={{
                boxShadow: '0 8px 32px rgba(236, 72, 153, 0.3)'
              }}
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.9 }}
            >
              <div className="flex items-center justify-center gap-3">
                <span className="text-lg">✨</span>
                <span>Add Required Details</span>
              </div>
            </motion.button>
          )}
          
          <motion.button
            onClick={handleExit}
            className="w-full px-6 py-3 text-gray-600 hover:text-gray-800 border border-gray-200/60 hover:border-gray-300/60 rounded-2xl hover:bg-gray-50/80 transition-all duration-300 backdrop-blur-sm font-medium bg-white/40"
            whileHover={{ scale: 1.02, y: -1 }}
            whileTap={{ scale: 0.98 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.1 }}
          >
            <div className="flex items-center justify-center gap-3">
              <span className="text-lg">🚪</span>
              <span>Exit & Delete Event</span>
            </div>
          </motion.button>
        </div>
      </motion.div>
    </motion.div>
  )
}
