'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface AgentAIBlockProps {
  agentKey: string
  agentName: string
  emoji: string
  status: 'idle' | 'running' | 'completed' | 'error'
  data?: any
  onInteraction?: (action: string, value?: any) => void
  onPositionChange?: (x: number, y: number) => void
  onAgentAction?: (action: 'pause' | 'restart' | 'delete') => void
  className?: string
  borderColor?: string
  initialX?: number
  initialY?: number
}

const AgentAIBlock: React.FC<AgentAIBlockProps> = ({
  agentKey,
  agentName,
  emoji,
  status,
  data,
  onInteraction,
  onPositionChange,
  onAgentAction,
  className = '',
  borderColor,
  initialX = 0,
  initialY = 0
}) => {
  const [isHovered, setIsHovered] = useState(false)
  const [localData, setLocalData] = useState(data)
  const [isDragging, setIsDragging] = useState(false)
  const [position, setPosition] = useState({ x: initialX, y: initialY })
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 })
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  // Generate random vibrant border colors
  const getRandomBorderColor = () => {
    const colors = [
      'from-purple-400 to-pink-400',
      'from-blue-400 to-cyan-400', 
      'from-green-400 to-emerald-400',
      'from-orange-400 to-red-400',
      'from-indigo-400 to-purple-400',
      'from-pink-400 to-rose-400',
      'from-teal-400 to-green-400',
      'from-yellow-400 to-orange-400'
    ]
    return colors[Math.floor(Math.random() * colors.length)]
  }

  const borderGradient = borderColor || getRandomBorderColor()

  useEffect(() => {
    setLocalData(data)
  }, [data])

  // Drag and drop handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.target instanceof HTMLElement && (e.target.closest('.agent-menu-button') || e.target.closest('.agent-dropdown-menu'))) {
      return // Don't drag if clicking on menu or dropdown
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
    
    setPosition({ x: newX, y: newY })
    onPositionChange?.(newX, newY)
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

  // Click outside to close menu
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (isMenuOpen && event.target instanceof HTMLElement) {
        if (!event.target.closest('.agent-menu-button') && !event.target.closest('.agent-dropdown-menu')) {
          setIsMenuOpen(false)
        }
      }
    }

    if (isMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isMenuOpen])

  const getStatusColor = () => {
    switch (status) {
      case 'running': return 'from-blue-500 to-cyan-500'
      case 'completed': return 'from-green-500 to-emerald-500'
      case 'error': return 'from-red-500 to-pink-500'
      default: return 'from-gray-400 to-gray-500'
    }
  }

  const getStatusGlow = () => {
    switch (status) {
      case 'running': return 'shadow-blue-500/30'
      case 'completed': return 'shadow-green-500/30'
      case 'error': return 'shadow-red-500/30'
      default: return 'shadow-gray-500/20'
    }
  }


  const renderAgentImage = () => {
    return (
      <div className="relative w-full h-32 bg-gradient-to-br from-white/90 to-gray-100/90 rounded-2xl overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.div
            className="text-5xl filter drop-shadow-lg"
            animate={status === 'running' ? { 
              scale: [1, 1.2, 1],
              rotate: [0, 10, -10, 0],
              filter: ['drop-shadow(0 0 0px rgba(59, 130, 246, 0))', 'drop-shadow(0 0 20px rgba(59, 130, 246, 0.8))', 'drop-shadow(0 0 0px rgba(59, 130, 246, 0))']
            } : {}}
            transition={{ 
              duration: 2.5,
              repeat: status === 'running' ? Infinity : 0,
              ease: "easeInOut"
            }}
            style={{
              filter: status === 'completed' ? 'drop-shadow(0 0 15px rgba(34, 197, 94, 0.6))' : 
                     status === 'error' ? 'drop-shadow(0 0 15px rgba(239, 68, 68, 0.6))' :
                     'drop-shadow(0 0 5px rgba(0, 0, 0, 0.1))'
            }}
          >
            {emoji}
          </motion.div>
        </div>
        
        {/* Enhanced status indicator overlay */}
        <div className="absolute top-3 right-3">
          <motion.div 
            className={`w-5 h-5 rounded-full bg-gradient-to-r ${getStatusColor()} shadow-lg`}
            animate={status === 'running' ? { 
              scale: [1, 1.3, 1],
              opacity: [0.8, 1, 0.8]
            } : {}}
            transition={{ 
              duration: 1.5,
              repeat: status === 'running' ? Infinity : 0
            }}
          />
        </div>

        {/* Animated pattern overlay */}
        <motion.div 
          className="absolute inset-0 opacity-20"
          animate={{
            background: [
              'linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.3) 50%, transparent 70%)',
              'linear-gradient(225deg, transparent 30%, rgba(255,255,255,0.3) 50%, transparent 70%)',
              'linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.3) 50%, transparent 70%)'
            ]
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />

        {/* Glow effect for running agents */}
        {status === 'running' && (
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-blue-400/20 to-purple-400/20 rounded-2xl"
            animate={{
              opacity: [0.3, 0.7, 0.3]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
        )}
      </div>
    )
  }

  const renderDynamicData = () => {
    if (!localData) return null

    switch (agentKey) {
      case 'budget_agent':
        const budgetValue = typeof localData.total_budget === 'object' 
          ? (localData.total_budget?.estimated || localData.total_budget?.min || 1000)
          : (localData.total_budget || 1000);
        
        return (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">Budget</span>
              <span className="text-sm font-bold text-green-600">
                ${budgetValue}
              </span>
            </div>
            <div className="relative">
              <input
                type="range"
                min="500"
                max="5000"
                value={budgetValue}
                onChange={(e) => onInteraction?.('budget_change', parseInt(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                style={{
                  background: `linear-gradient(to right, #10b981 0%, #10b981 ${(budgetValue - 500) / 45}%, #e5e7eb ${(budgetValue - 500) / 45}%, #e5e7eb 100%)`
                }}
              />
            </div>
          </div>
        )

      case 'cake_agent':
        return (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-lg">🎂</span>
              <span className="text-sm font-medium text-gray-600">Cake</span>
            </div>
            <div className="text-sm text-gray-500">
              {localData.recommended_bakeries?.length || 0} options
            </div>
          </div>
        )

      case 'venue_agent':
        return (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-lg">📍</span>
              <span className="text-sm font-medium text-gray-600">Venue</span>
            </div>
            <div className="text-sm text-gray-500">
              {localData.recommended_venues?.length || 0} venues
            </div>
          </div>
        )

      case 'theme_agent':
        const themeValue = typeof localData.primary_theme === 'string' 
          ? localData.primary_theme 
          : (localData.primary_theme?.name || 'Detecting...');
        
        return (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-lg">🎨</span>
              <span className="text-sm font-medium text-gray-600">Theme</span>
            </div>
            <div className="text-sm text-gray-500 truncate">
              {themeValue}
            </div>
          </div>
        )

      case 'vendor_agent':
        return (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-lg">🏪</span>
              <span className="text-sm font-medium text-gray-600">Vendors</span>
            </div>
            <div className="text-sm text-gray-500">
              {Object.keys(localData.vendors_by_category || {}).length} categories
            </div>
          </div>
        )

      case 'catering_agent':
        return (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-lg">🍽️</span>
              <span className="text-sm font-medium text-gray-600">Catering</span>
            </div>
            <div className="text-sm text-gray-500">
              {localData.recommended_caterers?.length || 0} options
            </div>
          </div>
        )

      default:
        return (
          <div className="space-y-3">
            <div className="text-sm font-medium text-gray-600">{agentName}</div>
            <div className="text-sm text-gray-500">
              {status === 'running' ? 'Processing...' : 
               status === 'completed' ? 'Complete' :
               status === 'error' ? 'Error' : 'Ready'}
            </div>
          </div>
        )
    }
  }

  return (
    <motion.div
      className={`group relative w-64 h-80 bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl overflow-visible ${isDragging ? 'cursor-grabbing' : 'cursor-move'} ${className}`}
      style={{
        border: `3px solid transparent`,
        background: `linear-gradient(white, white) padding-box, linear-gradient(135deg, ${borderGradient}) border-box`,
        transform: `translate(${position.x}px, ${position.y}px)`,
        zIndex: isDragging ? 1000 : 5
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onMouseDown={handleMouseDown}
      whileHover={{ 
        scale: isDragging ? 1 : 1.08,
        y: isDragging ? 0 : -8,
        rotateY: isDragging ? 0 : 5,
        boxShadow: `0 25px 50px ${getStatusGlow()}`
      }}
      initial={{ opacity: 0, y: 30, scale: 0.8, rotateX: -15 }}
      animate={{ 
        opacity: 1, 
        y: 0, 
        scale: isDragging ? 1.05 : 1, 
        rotateX: 0,
        rotateZ: isDragging ? 2 : 0
      }}
      transition={{ 
        duration: 0.8,
        ease: [0.25, 0.46, 0.45, 0.94],
        type: "spring",
        stiffness: 100
      }}
    >

      {/* Animated background gradient */}
      <motion.div 
        className={`absolute inset-0 bg-gradient-to-br ${borderGradient} opacity-10`}
        animate={isHovered ? { opacity: 0.15 } : { opacity: 0.05 }}
        transition={{ duration: 0.3 }}
      />
      
      {/* Agent Image Section (40%) */}
      <div className="h-32 p-4">
        {renderAgentImage()}
      </div>

      {/* Data Section (60%) */}
      <div className="h-48 p-6 flex flex-col justify-between">
        <div className="flex-1">
          {renderDynamicData()}
        </div>
        
        {/* Agent name with menu */}
        <div className="relative">
          <motion.div 
            className="text-sm font-semibold text-gray-700 text-center truncate pr-8"
            animate={isHovered ? { scale: 1.05 } : { scale: 1 }}
            transition={{ duration: 0.2 }}
          >
            {agentName}
          </motion.div>
          
          {/* 3-Dots Menu Button - Absolute positioned */}
          <motion.button
            className="agent-menu-button absolute bottom-0 right-0 w-6 h-6 bg-white/90 hover:bg-white rounded-full flex items-center justify-center text-gray-600 hover:text-gray-800 shadow-lg backdrop-blur-sm border border-gray-200/50 cursor-pointer z-10"
            onClick={(e) => {
              e.stopPropagation()
              console.log('Menu button clicked, current state:', isMenuOpen)
              setIsMenuOpen(!isMenuOpen)
            }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            title="Agent Options"
            style={{ 
              cursor: 'pointer',
              border: '2px solid blue' // Debug border to make it visible
            }}
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="12" cy="5" r="2"/>
              <circle cx="12" cy="12" r="2"/>
              <circle cx="12" cy="19" r="2"/>
            </svg>
          </motion.button>
          
          {/* Dropdown Menu */}
          <AnimatePresence>
            {isMenuOpen && (
              <motion.div
                className="agent-dropdown-menu absolute bottom-8 right-0 bg-white/98 backdrop-blur-xl rounded-lg shadow-xl border border-gray-200/60 py-1 min-w-[100px] z-[9999]"
                initial={{ opacity: 0, scale: 0.95, y: 8 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 8 }}
                transition={{ duration: 0.15, ease: "easeOut" }}
                style={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.98)',
                  border: '1px solid rgba(229, 231, 235, 0.8)'
                }}
              >
                {/* Pause Option */}
                <motion.button
                  className="w-full px-3 py-1.5 text-left text-xs text-gray-600 hover:bg-yellow-50 hover:text-yellow-700 flex items-center gap-1.5 transition-colors duration-100"
                  onClick={(e) => {
                    e.stopPropagation()
                    onAgentAction?.('pause')
                    setIsMenuOpen(false)
                  }}
                  whileHover={{ x: 2 }}
                >
                  <span className="text-sm">⏸️</span>
                  <span>Pause</span>
                </motion.button>

                {/* Restart Option */}
                <motion.button
                  className="w-full px-3 py-1.5 text-left text-xs text-gray-600 hover:bg-blue-50 hover:text-blue-700 flex items-center gap-1.5 transition-colors duration-100"
                  onClick={(e) => {
                    e.stopPropagation()
                    onAgentAction?.('restart')
                    setIsMenuOpen(false)
                  }}
                  whileHover={{ x: 2 }}
                >
                  <span className="text-sm">🔄</span>
                  <span>Restart</span>
                </motion.button>

                {/* Divider */}
                <div className="h-px bg-gray-200/40 mx-2 my-0.5"></div>

                {/* Delete Option */}
                <motion.button
                  className="w-full px-3 py-1.5 text-left text-xs text-gray-600 hover:bg-red-50 hover:text-red-700 flex items-center gap-1.5 transition-colors duration-100"
                  onClick={(e) => {
                    e.stopPropagation()
                    onAgentAction?.('delete')
                    setIsMenuOpen(false)
                  }}
                  whileHover={{ x: 2 }}
                >
                  <span className="text-sm">🗑️</span>
                  <span>Delete</span>
                </motion.button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Enhanced hover overlay */}
      <AnimatePresence>
        {isHovered && (
          <motion.div
            className="absolute inset-0 bg-gradient-to-br from-white/30 to-transparent"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          />
        )}
      </AnimatePresence>

      {/* Enhanced status pulse effect */}
      {status === 'running' && (
        <motion.div
          className="absolute inset-0 border-3 border-blue-400 rounded-3xl"
          animate={{ 
            scale: [1, 1.02, 1],
            opacity: [0.3, 0.7, 0.3],
            rotate: [0, 1, -1, 0]
          }}
          transition={{ 
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      )}

      {/* Floating particles effect */}
      {status === 'running' && (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {[...Array(6)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-blue-400 rounded-full"
              style={{
                left: `${20 + i * 15}%`,
                top: `${30 + i * 10}%`
              }}
              animate={{
                y: [-20, -40, -20],
                opacity: [0, 1, 0],
                scale: [0.5, 1, 0.5]
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                delay: i * 0.5,
                ease: "easeInOut"
              }}
            />
          ))}
        </div>
      )}

      {/* Drag indicator */}
      {isDragging && (
        <motion.div
          className="absolute inset-0 border-2 border-dashed border-blue-400 rounded-3xl bg-blue-50/20"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        />
      )}
    </motion.div>
  )
}

export default AgentAIBlock
