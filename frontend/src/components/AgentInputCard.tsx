'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface AgentInputCardProps {
  agentKey: string
  agentName: string
  emoji: string
  currentData?: any
  isOpen: boolean
  onClose: () => void
  onRegenerate: (newInputs: any) => void
  agentPosition: { x: number; y: number }
  cardPosition?: { x: number; y: number }
  onCardPositionChange?: (position: { x: number; y: number }) => void
}

const AgentInputCard: React.FC<AgentInputCardProps> = ({
  agentKey,
  agentName,
  emoji,
  currentData,
  isOpen,
  onClose,
  onRegenerate,
  agentPosition,
  cardPosition: propCardPosition,
  onCardPositionChange
}) => {
  const [formData, setFormData] = useState<any>({})
  const [isConnected, setIsConnected] = useState(false)
  const [isDragging, setIsDragging] = useState(false)
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 })

  // Use prop position or default position
  const defaultCardPosition = {
    x: agentPosition.x + 280, // Offset to the right of agent card
    y: agentPosition.y - 50   // Slightly above agent card
  }
  
  const cardPosition = propCardPosition || defaultCardPosition

  // Initialize form data with current data
  useEffect(() => {
    if (currentData) {
      setFormData(currentData)
    }
  }, [currentData])

  // Connection animation effect
  useEffect(() => {
    if (isOpen) {
      const timer = setTimeout(() => setIsConnected(true), 300)
      return () => clearTimeout(timer)
    } else {
      setIsConnected(false)
    }
  }, [isOpen])

  const handleInputChange = (field: string, value: any) => {
    setFormData((prev: any) => ({
      ...prev,
      [field]: value
    }))
  }

  const handleRegenerate = () => {
    onRegenerate(formData)
    onClose()
  }

  // Drag handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.target instanceof HTMLElement && e.target.closest('.no-drag')) {
      return // Don't drag if clicking on form elements
    }
    
    setIsDragging(true)
    const rect = e.currentTarget.getBoundingClientRect()
    setDragOffset({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    })
    e.preventDefault()
  }

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging) return
    
    const newX = e.clientX - dragOffset.x
    const newY = e.clientY - dragOffset.y
    
    onCardPositionChange?.({ x: newX, y: newY })
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      return () => {
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isDragging, dragOffset])

  const renderCurrentData = () => {
    if (!currentData) return null

    switch (agentKey) {
      case 'budget_agent':
        let budget = 1000;
        if (currentData.total_budget) {
          if (typeof currentData.total_budget === 'object') {
            budget = currentData.total_budget.estimated || currentData.total_budget.min || currentData.total_budget.max || 1000;
          } else if (typeof currentData.total_budget === 'number') {
            budget = currentData.total_budget;
          } else if (typeof currentData.total_budget === 'string') {
            budget = parseInt(currentData.total_budget) || 1000;
          }
        }
        return (
          <div className="space-y-2">
            <div className="text-xs text-gray-500 uppercase tracking-wide">Current Settings</div>
            <div className="bg-gray-50 rounded-lg p-3 space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Budget:</span>
                <span className="text-sm font-semibold text-green-600">${budget}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Currency:</span>
                <span className="text-sm font-semibold text-gray-800">USD</span>
              </div>
            </div>
          </div>
        )

      case 'theme_agent':
        let theme = 'Auto-detected';
        if (currentData.primary_theme) {
          if (typeof currentData.primary_theme === 'string') {
            theme = currentData.primary_theme;
          } else if (typeof currentData.primary_theme === 'object') {
            theme = currentData.primary_theme.name || currentData.primary_theme.title || 'Auto-detected';
          }
        }
        return (
          <div className="space-y-2">
            <div className="text-xs text-gray-500 uppercase tracking-wide">Current Settings</div>
            <div className="bg-gray-50 rounded-lg p-3 space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Theme:</span>
                <span className="text-sm font-semibold text-purple-600">{theme}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Colors:</span>
                <span className="text-sm font-semibold text-gray-800">Auto-selected</span>
              </div>
            </div>
          </div>
        )

      case 'venue_agent':
        return (
          <div className="space-y-2">
            <div className="text-xs text-gray-500 uppercase tracking-wide">Current Settings</div>
            <div className="bg-gray-50 rounded-lg p-3 space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Venues Found:</span>
                <span className="text-sm font-semibold text-blue-600">{currentData.recommended_venues?.length || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Location:</span>
                <span className="text-sm font-semibold text-gray-800">Auto-detected</span>
              </div>
            </div>
          </div>
        )

      default:
        return (
          <div className="space-y-2">
            <div className="text-xs text-gray-500 uppercase tracking-wide">Current Settings</div>
            <div className="bg-gray-50 rounded-lg p-3">
              <div className="text-sm text-gray-600">Status: {currentData.status || 'Completed'}</div>
            </div>
          </div>
        )
    }
  }

  const renderNewDataForm = () => {
    switch (agentKey) {
      case 'budget_agent':
        return (
          <div className="space-y-4">
            <div className="text-xs text-gray-500 uppercase tracking-wide">New Settings</div>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Budget Range</label>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <input
                      type="number"
                      placeholder="Min Budget"
                      value={formData.minBudget || ''}
                      onChange={(e) => handleInputChange('minBudget', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                    />
                  </div>
                  <div>
                    <input
                      type="number"
                      placeholder="Max Budget"
                      value={formData.maxBudget || ''}
                      onChange={(e) => handleInputChange('maxBudget', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                    />
                  </div>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Currency</label>
                <select 
                  value={formData.currency || 'USD'}
                  onChange={(e) => handleInputChange('currency', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                >
                  <option value="USD">USD ($)</option>
                  <option value="EUR">EUR (€)</option>
                  <option value="GBP">GBP (£)</option>
                </select>
              </div>
            </div>
          </div>
        )

      case 'theme_agent':
        return (
          <div className="space-y-4">
            <div className="text-xs text-gray-500 uppercase tracking-wide">New Settings</div>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Preferred Theme</label>
                <select 
                  value={formData.theme || ''}
                  onChange={(e) => handleInputChange('theme', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                >
                  <option value="">Auto-detect</option>
                  <option value="birthday">Birthday Party</option>
                  <option value="wedding">Wedding</option>
                  <option value="corporate">Corporate Event</option>
                  <option value="casual">Casual Gathering</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Color Preferences</label>
                <div className="flex gap-2 flex-wrap">
                  {['Red', 'Blue', 'Green', 'Purple', 'Pink', 'Gold'].map(color => (
                    <button
                      key={color}
                      className={`px-3 py-1 text-xs rounded-full border transition-colors ${
                        formData.colors?.includes(color) 
                          ? 'bg-blue-100 border-blue-300 text-blue-700' 
                          : 'bg-gray-100 hover:bg-gray-200 border-gray-300 text-gray-600'
                      }`}
                      onClick={() => {
                        const colors = formData.colors || []
                        const newColors = colors.includes(color) 
                          ? colors.filter((c: string) => c !== color)
                          : [...colors, color]
                        handleInputChange('colors', newColors)
                      }}
                    >
                      {color}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )

      case 'venue_agent':
        return (
          <div className="space-y-4">
            <div className="text-xs text-gray-500 uppercase tracking-wide">New Settings</div>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
                <input
                  type="text"
                  placeholder="Enter city or address"
                  value={formData.location || ''}
                  onChange={(e) => handleInputChange('location', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Venue Type</label>
                <select 
                  value={formData.venueType || ''}
                  onChange={(e) => handleInputChange('venueType', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                >
                  <option value="">Any Type</option>
                  <option value="indoor">Indoor</option>
                  <option value="outdoor">Outdoor</option>
                  <option value="hotel">Hotel</option>
                  <option value="restaurant">Restaurant</option>
                  <option value="venue">Event Venue</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Capacity</label>
                <input
                  type="number"
                  placeholder="Number of guests"
                  value={formData.capacity || ''}
                  onChange={(e) => handleInputChange('capacity', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                />
              </div>
            </div>
          </div>
        )

      default:
        return (
          <div className="space-y-4">
            <div className="text-xs text-gray-500 uppercase tracking-wide">New Settings</div>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Custom Instructions</label>
                <textarea
                  placeholder="Add specific requirements or preferences..."
                  rows={3}
                  value={formData.instructions || ''}
                  onChange={(e) => handleInputChange('instructions', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Priority Level</label>
                <select 
                  value={formData.priority || 'medium'}
                  onChange={(e) => handleInputChange('priority', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                >
                  <option value="high">High Priority</option>
                  <option value="medium">Medium Priority</option>
                  <option value="low">Low Priority</option>
                </select>
              </div>
            </div>
          </div>
        )
    }
  }

  // Calculate connection path based on positions
  const calculateConnectionPath = () => {
    const agentCenterX = agentPosition.x + 128 // Center of agent card (256/2)
    const agentCenterY = agentPosition.y + 160 // Center of agent card (320/2)
    
    const cardLeft = cardPosition.x
    const cardTop = cardPosition.y + 40 // Top of input card
    
    // Determine if input card is above or below the agent
    const isCardAbove = cardTop < agentPosition.y
    const isCardBelow = cardTop > agentPosition.y + 320
    
    // Determine connection points based on relative position
    let startX, startY, endX, endY, controlX1, controlY1, controlX2, controlY2
    
    if (isCardAbove) {
      // Card is above agent - connect from top of agent
      startX = agentCenterX
      startY = agentPosition.y // Top edge of agent
      endX = cardLeft + 160 // Center of input card (320/2)
      endY = cardTop + 200 // Bottom of input card
      controlX1 = agentCenterX
      controlY1 = agentPosition.y - 50 // Bend upward
      controlX2 = cardLeft + 160
      controlY2 = cardTop + 200 + 50 // Bend downward
    } else if (isCardBelow) {
      // Card is below agent - connect from bottom of agent
      startX = agentCenterX
      startY = agentPosition.y + 320 // Bottom edge of agent
      endX = cardLeft + 160 // Center of input card
      endY = cardTop // Top of input card
      controlX1 = agentCenterX
      controlY1 = agentPosition.y + 320 + 50 // Bend downward
      controlX2 = cardLeft + 160
      controlY2 = cardTop - 50 // Bend upward
    } else {
      // Card is at same level - use side connection
      if (cardLeft > agentCenterX) {
        // Card is to the right
        startX = agentPosition.x + 256 // Right edge of agent
        startY = agentCenterY
        endX = cardLeft // Left edge of card
        endY = cardTop + 100 // Center of card
        controlX1 = agentPosition.x + 256 + 50
        controlY1 = agentCenterY
        controlX2 = cardLeft - 50
        controlY2 = cardTop + 100
      } else {
        // Card is to the left
        startX = agentPosition.x // Left edge of agent
        startY = agentCenterY
        endX = cardLeft + 320 // Right edge of card
        endY = cardTop + 100 // Center of card
        controlX1 = agentPosition.x - 50
        controlY1 = agentCenterY
        controlX2 = cardLeft + 320 + 50
        controlY2 = cardTop + 100
      }
    }
    
    return {
      startX,
      startY,
      endX,
      endY,
      controlX1,
      controlY1,
      controlX2,
      controlY2
    }
  }

  const connectionPath = calculateConnectionPath()

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Connection Line Animation */}
          <motion.div
            className="fixed pointer-events-none z-40"
            style={{
              left: `${Math.min(connectionPath.startX, connectionPath.endX) - 50}px`,
              top: `${Math.min(connectionPath.startY, connectionPath.endY) - 50}px`,
            }}
            initial={{ opacity: 0, scaleX: 0 }}
            animate={{ 
              opacity: isConnected ? 1 : 0,
              scaleX: isConnected ? 1 : 0
            }}
            transition={{ duration: 0.6, ease: "easeOut" }}
          >
            <svg 
              width={`${Math.abs(connectionPath.endX - connectionPath.startX) + 100}`} 
              height={`${Math.abs(connectionPath.endY - connectionPath.startY) + 100}`} 
              viewBox={`0 0 ${Math.abs(connectionPath.endX - connectionPath.startX) + 100} ${Math.abs(connectionPath.endY - connectionPath.startY) + 100}`} 
              className="overflow-visible"
            >
              <defs>
                <linearGradient id="connectionGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#3B82F6" stopOpacity="0.8" />
                  <stop offset="50%" stopColor="#8B5CF6" stopOpacity="1" />
                  <stop offset="100%" stopColor="#EC4899" stopOpacity="0.8" />
                </linearGradient>
                <filter id="glow">
                  <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                  <feMerge> 
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
              </defs>
              <motion.path
                d={`M ${connectionPath.startX - Math.min(connectionPath.startX, connectionPath.endX) + 50} ${connectionPath.startY - Math.min(connectionPath.startY, connectionPath.endY) + 50} 
                    C ${connectionPath.controlX1 - Math.min(connectionPath.startX, connectionPath.endX) + 50} ${connectionPath.controlY1 - Math.min(connectionPath.startY, connectionPath.endY) + 50}
                      ${connectionPath.controlX2 - Math.min(connectionPath.startX, connectionPath.endX) + 50} ${connectionPath.controlY2 - Math.min(connectionPath.startY, connectionPath.endY) + 50}
                      ${connectionPath.endX - Math.min(connectionPath.startX, connectionPath.endX) + 50} ${connectionPath.endY - Math.min(connectionPath.startY, connectionPath.endY) + 50}`}
                stroke="url(#connectionGradient)"
                strokeWidth="3"
                fill="none"
                initial={{ pathLength: 0 }}
                animate={{ 
                  pathLength: isConnected ? 1 : 0,
                  opacity: isConnected ? [0.6, 1, 0.6] : 0
                }}
                transition={{ 
                  pathLength: { duration: 0.8, ease: "easeInOut" },
                  opacity: { duration: 1.5, repeat: isConnected ? Infinity : 0, ease: "easeInOut" }
                }}
              />
              {/* Animated dots along the curved path */}
              {[...Array(8)].map((_, i) => {
                const t = i / 7 // Parameter along the curve (0 to 1)
                const x = (1-t) * (1-t) * (1-t) * (connectionPath.startX - Math.min(connectionPath.startX, connectionPath.endX) + 50) +
                         3 * (1-t) * (1-t) * t * (connectionPath.controlX1 - Math.min(connectionPath.startX, connectionPath.endX) + 50) +
                         3 * (1-t) * t * t * (connectionPath.controlX2 - Math.min(connectionPath.startX, connectionPath.endX) + 50) +
                         t * t * t * (connectionPath.endX - Math.min(connectionPath.startX, connectionPath.endX) + 50)
                const y = (1-t) * (1-t) * (1-t) * (connectionPath.startY - Math.min(connectionPath.startY, connectionPath.endY) + 50) +
                         3 * (1-t) * (1-t) * t * (connectionPath.controlY1 - Math.min(connectionPath.startY, connectionPath.endY) + 50) +
                         3 * (1-t) * t * t * (connectionPath.controlY2 - Math.min(connectionPath.startY, connectionPath.endY) + 50) +
                         t * t * t * (connectionPath.endY - Math.min(connectionPath.startY, connectionPath.endY) + 50)
                
                return (
                  <motion.circle
                    key={i}
                    cx={x}
                    cy={y}
                    r="3"
                    fill="#3B82F6"
                    filter="url(#glow)"
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ 
                      opacity: isConnected ? [0, 1, 0] : 0,
                      scale: isConnected ? [0, 1.2, 0] : 0
                    }}
                    transition={{ 
                      duration: 2,
                      delay: i * 0.15,
                      repeat: isConnected ? Infinity : 0,
                      repeatDelay: 1
                    }}
                  />
                )
              })}
            </svg>
          </motion.div>

          {/* Input Card */}
          <motion.div
            className={`fixed bg-white/98 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/40 z-50 w-80 max-h-[70vh] overflow-y-auto ${isDragging ? 'cursor-grabbing' : 'cursor-move'}`}
            style={{
              left: `${cardPosition.x}px`,
              top: `${cardPosition.y}px`,
            }}
            initial={{ 
              opacity: 0, 
              scale: 0.8, 
              x: -50,
              rotateY: -15
            }}
            animate={{ 
              opacity: 1, 
              scale: isDragging ? 1.05 : 1, 
              x: 0,
              rotateY: 0
            }}
            exit={{ 
              opacity: 0, 
              scale: 0.8, 
              x: -50,
              rotateY: -15
            }}
            transition={{ 
              duration: 0.5,
              ease: [0.25, 0.46, 0.45, 0.94],
              type: "spring",
              stiffness: 100
            }}
            onMouseDown={handleMouseDown}
          >
            {/* Header */}
            <div className="sticky top-0 bg-white/95 backdrop-blur-sm border-b border-gray-200/50 p-4 rounded-t-2xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white text-sm">
                    {emoji}
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-gray-800">{agentName}</h3>
                    <p className="text-xs text-gray-600">Edit & Regenerate</p>
                  </div>
                </div>
                <motion.button
                  className="w-7 h-7 bg-gray-100 hover:bg-gray-200 rounded-full flex items-center justify-center text-gray-600 hover:text-gray-800 transition-colors"
                  onClick={onClose}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                  </svg>
                </motion.button>
              </div>
            </div>

            {/* Content */}
            <div className="p-4 space-y-6 no-drag">
              {/* Current Data */}
              {renderCurrentData()}

              {/* Divider */}
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-200"></div>
                </div>
                <div className="relative flex justify-center text-xs">
                  <span className="px-2 bg-white text-gray-500">vs</span>
                </div>
              </div>

              {/* New Data Form */}
              {renderNewDataForm()}
            </div>

            {/* Footer */}
            <div className="sticky bottom-0 bg-white/95 backdrop-blur-sm border-t border-gray-200/50 p-4 rounded-b-2xl no-drag">
              <div className="flex gap-3">
                <motion.button
                  className="flex-1 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors text-sm"
                  onClick={onClose}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Cancel
                </motion.button>
                <motion.button
                  className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white rounded-lg font-medium transition-all text-sm"
                  onClick={handleRegenerate}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Regenerate
                </motion.button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}

export default AgentInputCard
