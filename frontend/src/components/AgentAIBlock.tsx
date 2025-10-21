'use client'

import React, { useState, useEffect } from 'react'
import Image, { StaticImageData } from 'next/image'
import { motion, AnimatePresence } from 'framer-motion'
import { createPortal } from 'react-dom'
import defaultThemeImage from '@/app/assets/theme_2.jpg'
import defaultCakeImage from '@/app/assets/cake_1.jpg'

interface AgentAIBlockProps {
  agentKey: string
  agentName: string
  emoji: string
  status: 'idle' | 'running' | 'completed' | 'error'
  data?: any
  onInteraction?: (action: string, value?: any) => void
  onPositionChange?: (x: number, y: number) => void
  onAgentAction?: (action: 'pause' | 'restart' | 'delete') => void
  onPlayClick?: (agentKey: string) => void
  isActive?: boolean
  className?: string
  borderColor?: string
  initialX?: number
  initialY?: number
  variant?: 'floating' | 'focus' | 'secondary'
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
  onPlayClick,
  isActive = false,
  className = '',
  borderColor,
  initialX = 0,
  initialY = 0,
  variant = 'floating'
}) => {
  const isFocus = variant === 'focus'
  const isSecondary = variant === 'secondary'
  const [isHovered, setIsHovered] = useState(false)
  const [localData, setLocalData] = useState(data)
  const [isDragging, setIsDragging] = useState(false)
  const [position, setPosition] = useState({ x: initialX, y: initialY })
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 })
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [zoomedImage, setZoomedImage] = useState<{ src: StaticImageData; alt: string } | null>(null)
  const [portalTarget, setPortalTarget] = useState<HTMLElement | null>(null)
  const isFloating = variant === 'floating'

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
  const isVisualAgent = agentKey === 'cake_agent' || agentKey === 'theme_agent'
  const imageHeightClass = isVisualAgent
    ? (isFocus ? 'h-64' : isSecondary ? 'h-40' : 'h-48')
    : (isFocus ? 'h-40' : isSecondary ? 'h-28' : 'h-36')
  const emojiSizeClass = isFocus ? 'text-6xl' : isSecondary ? 'text-4xl' : 'text-5xl'
  const cardSizeClass = isFocus
    ? 'w-full max-w-4xl min-h-[26rem]'
    : isSecondary
      ? 'w-80 min-h-[20rem]'
      : 'w-72 h-[22rem]'
  const standardImageWrapper = isFocus ? 'px-8 pt-8' : isSecondary ? 'px-5 pt-5' : 'px-5 pt-5'
  const visualImageWrapper = isFocus ? 'px-6 pt-6' : isSecondary ? 'px-4 pt-4' : 'px-4 pt-4'
  const imageWrapperClass = `relative ${isVisualAgent ? visualImageWrapper : standardImageWrapper}`
  const dataSectionClass = isFocus
    ? 'flex-1 px-8 pb-8 pt-6 flex flex-col justify-end gap-8'
    : isSecondary
      ? 'flex-1 p-5 flex flex-col justify-between'
      : 'flex-1 p-6 flex flex-col justify-between'

  useEffect(() => {
    setLocalData(data)
  }, [data])

  // Drag and drop handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    if (!isFloating) return
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
    if (isFloating && isDragging) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      return () => {
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isFloating, isDragging, dragOffset])

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

  useEffect(() => {
    if (!zoomedImage) return

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setZoomedImage(null)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    const originalOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = originalOverflow
    }
  }, [zoomedImage])

  useEffect(() => {
    if (typeof document !== 'undefined') {
      setPortalTarget(document.body)
    }
  }, [])

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


  const renderStatusIndicator = () => (
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
  )

  const renderAgentImage = () => {
    if (isVisualAgent) {
      const imageSrc = agentKey === 'cake_agent' ? defaultCakeImage : defaultThemeImage
      const altText = agentKey === 'cake_agent' ? 'Signature cake inspiration' : 'Default theme inspiration'
      return (
        <button
          type="button"
          onMouseDown={(e) => e.stopPropagation()}
          onClick={(e) => {
            e.stopPropagation()
            setZoomedImage({ src: imageSrc, alt: altText })
          }}
          className={`group relative z-10 w-full ${imageHeightClass} rounded-3xl overflow-hidden shadow-2xl cursor-zoom-in focus:outline-none focus:ring-4 focus:ring-blue-400/30`}
          aria-label="Zoom preview"
          title="Zoom preview"
        >
          <Image
            src={imageSrc}
            alt={altText}
            fill
            sizes={isFocus ? '(min-width: 1024px) 480px, 360px' : '(min-width: 1024px) 320px, 260px'}
            className="object-contain transition-transform duration-700 ease-out group-hover:scale-105"
            priority={isFocus}
          />
          <div className="absolute bottom-3 right-3 rounded-full bg-black/55 text-white text-xs font-medium px-3 py-1.5 flex items-center gap-1 shadow-lg backdrop-blur-sm">
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="opacity-90"
            >
              <rect x="3" y="3" width="7" height="7" rx="1" />
              <rect x="14" y="3" width="7" height="7" rx="1" />
              <rect x="14" y="14" width="7" height="7" rx="1" />
              <rect x="3" y="14" width="7" height="7" rx="1" />
            </svg>
            <span>Zoom</span>
          </div>
        </button>
      )
    }

    return (
      <div className={`relative w-full ${imageHeightClass} bg-gradient-to-br from-white/90 to-gray-100/90 rounded-2xl overflow-hidden`}>
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.div
            className={`${emojiSizeClass} filter drop-shadow-lg`}
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

  // Helper function to safely render values
  const safeRender = (value: any): string => {
    if (value === null || value === undefined) return '';
    if (typeof value === 'string' || typeof value === 'number') return String(value);
    if (typeof value === 'object') {
      // If it's an object, try to extract a meaningful string value
      if (value.name) return String(value.name);
      if (value.title) return String(value.title);
      if (value.estimated) return String(value.estimated);
      if (value.min && value.max) return `${value.min}-${value.max}`;
      return JSON.stringify(value);
    }
    return String(value);
  };

  const renderDynamicData = () => {
    if (!localData) return null

    // Debug logging to help identify the issue
    console.log(`AgentAIBlock ${agentKey} data:`, localData);
    const summaryWrapper = isFocus ? 'space-y-5 text-center' : 'space-y-3'
    const badgeClass = isFocus ? 'text-xs tracking-[0.35em] uppercase text-gray-400' : 'text-xs text-gray-500 uppercase tracking-wide'
    const statRow = isFocus ? 'flex flex-col items-center gap-1' : 'flex items-center justify-between'
    const labelClass = isFocus ? 'text-sm text-gray-500' : 'text-sm text-gray-600'

    switch (agentKey) {
      case 'budget_agent':
        let budgetValue = 1000; // Default value
        if (localData.total_budget) {
          if (typeof localData.total_budget === 'object') {
            // Handle object with min/max properties
            budgetValue = localData.total_budget.estimated || localData.total_budget.min || localData.total_budget.max || 1000;
          } else if (typeof localData.total_budget === 'number') {
            budgetValue = localData.total_budget;
          } else if (typeof localData.total_budget === 'string') {
            budgetValue = parseInt(localData.total_budget) || 1000;
          }
        }
        
        return (
          <div className={summaryWrapper}>
            <div className={badgeClass}>Budget Controls</div>
            <div className={statRow}>
              <span className={labelClass}>Current Budget</span>
              <span className={isFocus ? 'text-3xl font-bold text-green-600' : 'text-sm font-bold text-green-600'}>
                ${budgetValue}
              </span>
            </div>
            <div className={isFocus ? 'relative max-w-md mx-auto w-full' : 'relative'}>
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
            {isFocus && (
              <div className="text-xs text-gray-400">Drag the slider to fine-tune the party budget estimates.</div>
            )}
          </div>
        )

      case 'cake_agent':
        return (
          <div className={summaryWrapper}>
            <div className={badgeClass}>Sweet Selections</div>
            <div className={statRow}>
              <span className={labelClass}>Bakeries Suggested</span>
              <span className={isFocus ? 'text-3xl font-semibold text-purple-500' : 'text-sm font-semibold text-purple-600'}>
                {localData.recommended_bakeries?.length || 0}
              </span>
            </div>
            {isFocus && (
              <div className="text-sm text-gray-500">
                We’ve gathered top cake artists that match your theme and budget.
              </div>
            )}
          </div>
        )

      case 'decor_agent':
        return (
          <div className={summaryWrapper}>
            <div className={badgeClass}>Hero Décor Plan</div>
            <div className={statRow}>
              <span className={labelClass}>Focal Elements</span>
              <span className={isFocus ? 'text-3xl font-semibold text-indigo-500' : 'text-sm font-semibold text-indigo-500'}>
                {localData.focal_elements?.length || 0}
              </span>
            </div>
            {localData.focal_elements && (
              <div className={isFocus ? 'space-y-2 text-sm text-gray-600' : 'text-sm text-gray-500'}>
                {localData.focal_elements.slice(0, isFocus ? 3 : 2).map((item: string) => (
                  <div key={item} className="flex items-start gap-2 justify-center">
                    <span className="mt-1 text-indigo-400">✦</span>
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            )}
            {isFocus && localData.diy_tips && (
              <div className="text-xs text-gray-400">
                DIY boost: {localData.diy_tips[0]}
              </div>
            )}
          </div>
        )

      case 'balloon_agent':
        return (
          <div className={summaryWrapper}>
            <div className={badgeClass}>Balloon Stylists</div>
            <div className={statRow}>
              <span className={labelClass}>Recommended Artists</span>
              <span className={isFocus ? 'text-3xl font-semibold text-rose-500' : 'text-sm font-semibold text-rose-500'}>
                {localData.recommended_artists?.length || 0}
              </span>
            </div>
            {localData.recommended_artists && (
              <div className={isFocus ? 'space-y-2 text-sm text-gray-600' : 'text-sm text-gray-500'}>
                {localData.recommended_artists.slice(0, isFocus ? 2 : 1).map((artist: any) => (
                  <div key={artist.name} className="flex flex-col items-center">
                    <span className="font-medium text-gray-700">{artist.name}</span>
                    <span className="text-xs text-gray-500">{artist.specialty}</span>
                  </div>
                ))}
              </div>
            )}
            {isFocus && localData.quick_win && (
              <div className="text-xs text-gray-400">
                Quick win: {localData.quick_win}
              </div>
            )}
          </div>
        )

      case 'venue_agent':
        return (
          <div className={summaryWrapper}>
            <div className={badgeClass}>Venues</div>
            <div className={statRow}>
              <span className={labelClass}>Matching Venues</span>
              <span className={isFocus ? 'text-3xl font-semibold text-blue-600' : 'text-sm font-semibold text-blue-600'}>
                {localData.recommended_venues?.length || 0}
              </span>
            </div>
            {isFocus && (
              <div className="text-sm text-gray-500">
                Filtered to suit capacity, style, and location preferences.
              </div>
            )}
          </div>
        )

      case 'theme_agent':
        let themeValue = 'Detecting...';
        if (localData.primary_theme) {
          if (typeof localData.primary_theme === 'string') {
            themeValue = localData.primary_theme;
          } else if (typeof localData.primary_theme === 'object') {
            themeValue = localData.primary_theme.name || localData.primary_theme.title || 'Detecting...';
          }
        }
        return (
          <div className={summaryWrapper}>
            <div className={badgeClass}>Primary Theme</div>
            <div className={statRow}>
              <span className={isFocus ? 'text-3xl font-semibold text-indigo-600' : 'text-sm font-medium text-gray-600'}>
                {safeRender(themeValue)}
              </span>
            </div>
            {isFocus && (
              <div className="flex justify-center gap-2 text-xs text-gray-400">
                <span>Palette synced ·</span>
                <span>Decor plan aligned</span>
              </div>
            )}
          </div>
        )

      case 'vendor_agent':
        return (
          <div className={summaryWrapper}>
            <div className={badgeClass}>Vendor Coverage</div>
            <div className={statRow}>
              <span className={labelClass}>Categories Covered</span>
              <span className={isFocus ? 'text-3xl font-semibold text-emerald-500' : 'text-sm font-semibold text-emerald-500'}>
                {Object.keys(localData.vendors_by_category || {}).length}
              </span>
            </div>
            {isFocus && (
              <div className="text-sm text-gray-500">
                Includes entertainment, décor, food, and specialty services ready for quotes.
              </div>
            )}
          </div>
        )

      case 'catering_agent':
        return (
          <div className={summaryWrapper}>
            <div className={badgeClass}>Catering Options</div>
            <div className={statRow}>
              <span className={labelClass}>Curated Caterers</span>
              <span className={isFocus ? 'text-3xl font-semibold text-rose-500' : 'text-sm font-semibold text-rose-500'}>
                {localData.recommended_caterers?.length || 0}
              </span>
            </div>
            {isFocus && (
              <div className="text-sm text-gray-500">
                Menu pairings balance dietary preferences, service style, and budget targets.
              </div>
            )}
          </div>
        )

      default:
        return (
          <div className={summaryWrapper}>
            <div className={badgeClass}>Status</div>
            <div className={isFocus ? 'text-2xl font-semibold text-gray-700' : 'text-sm font-medium text-gray-600'}>
              {status === 'running' ? 'Processing...' : 
               status === 'completed' ? 'Complete' :
               status === 'error' ? 'Needs Attention' : 'Ready'}
            </div>
            {isFocus && (
              <div className="text-sm text-gray-500">
                {agentName} is standing by for your inputs or regenerating fresh results.
              </div>
            )}
          </div>
        )
    }
  }

  const zoomOverlay = portalTarget
    ? createPortal(
        <AnimatePresence>
          {zoomedImage && (
            <motion.div
              className="fixed inset-0 z-[200] flex items-center justify-center bg-black/70 backdrop-blur-sm p-6"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setZoomedImage(null)}
            >
            <motion.div
              className="relative w-full max-w-5xl"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              transition={{ type: 'spring', stiffness: 160, damping: 22 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="relative w-full max-w-5xl h-[80vh] rounded-[32px] overflow-hidden shadow-[0_40px_120px_rgba(0,0,0,0.45)] bg-gradient-to-b from-black via-black to-black">
                <Image
                  src={zoomedImage.src}
                  alt={zoomedImage.alt}
                  fill
                  sizes="100vw"
                  className="object-contain"
                  priority
                />
              </div>
              <button
                type="button"
                className="absolute top-4 right-4 w-10 h-10 rounded-full bg-black/60 text-white hover:bg-black/80 transition flex items-center justify-center shadow-lg focus:outline-none focus:ring-2 focus:ring-white/60"
                aria-label="Close zoomed image"
                onClick={() => setZoomedImage(null)}
              >
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>,
        portalTarget
      )
    : null

  return (
    <>
      {zoomOverlay}
      <motion.div
        className={`group relative bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl overflow-visible ${cardSizeClass} ${className} ${isFloating ? (isDragging ? 'cursor-grabbing' : 'cursor-move') : 'cursor-default'} ${isActive ? 'ring-4 ring-blue-400/50' : ''}`}
        style={{
          border: `3px solid transparent`,
          background: `linear-gradient(white, white) padding-box, linear-gradient(135deg, ${borderGradient}) border-box`,
          ...(isFloating ? { transform: `translate(${position.x}px, ${position.y}px)` } : {}),
          zIndex: isFloating ? (isDragging ? 1000 : (isActive ? 20 : 5)) : undefined,
          opacity: variant === 'focus' ? 1 : (isActive ? 1 : 0.75)
        }}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        onMouseDown={handleMouseDown}
        whileHover={isFloating ? { 
          scale: isDragging ? 1 : (isActive ? 1.1 : 1.05),
          y: isDragging ? 0 : (isActive ? -12 : -6),
          rotateY: isDragging ? 0 : (isActive ? 8 : 3),
          boxShadow: isActive 
            ? `0 25px 50px ${getStatusGlow()}, 0 0 40px rgba(59, 130, 246, 0.4), 0 0 80px rgba(147, 51, 234, 0.2)`
            : `0 25px 50px ${getStatusGlow()}, 0 0 30px rgba(59, 130, 246, 0.3), 0 0 60px rgba(147, 51, 234, 0.15)`
        } : (
          variant === 'focus'
            ? { scale: isActive ? 1.01 : 1, boxShadow: isActive ? `0 25px 50px ${getStatusGlow()}` : undefined }
            : { scale: 1.02 }
        )}
        initial={isFloating ? { opacity: 0, y: 30, scale: 0.8, rotateX: -15 } : { opacity: 0, y: 20, scale: 0.95 }}
        animate={isFloating ? { 
          opacity: isActive ? 1 : 0.6, 
          y: 0, 
          scale: isDragging ? 1.05 : (isActive ? 1.05 : 1), 
          rotateX: 0,
          rotateZ: isDragging ? 2 : 0
        } : { 
          opacity: 1,
          y: 0,
          scale: isActive ? 1.01 : 1,
          rotateX: 0,
          rotateZ: 0
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
            className={`absolute inset-0 bg-gradient-to-br ${borderGradient} opacity-10 pointer-events-none`}
            animate={isActive ? { opacity: 0.4 } : (isHovered ? { opacity: 0.25 } : { opacity: 0.05 })}
            transition={{ duration: 0.3 }}
          />

          {/* Vibrant hover gradient overlay */}
          <AnimatePresence>
            {isHovered && (
              <motion.div
                className="absolute inset-0 bg-gradient-to-br from-blue-400/30 via-purple-400/20 to-pink-400/30 rounded-3xl pointer-events-none"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
              />
            )}
          </AnimatePresence>

          {/* Radiance effect on hover */}
          <AnimatePresence>
            {isHovered && (
              <motion.div
                className="absolute inset-0 rounded-3xl pointer-events-none"
                style={{
                  background: `radial-gradient(circle at center, 
                    rgba(59, 130, 246, 0.15) 0%, 
                    rgba(147, 51, 234, 0.1) 30%, 
                    rgba(236, 72, 153, 0.08) 60%, 
                    transparent 100%)`
                }}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ duration: 0.4, ease: "easeOut" }}
              />
            )}
          </AnimatePresence>

      {/* Active Agent Blue Overlay */}
      {isActive && (
        <motion.div
          className="absolute inset-0 bg-gradient-to-br from-blue-400/20 to-cyan-400/20 rounded-3xl pointer-events-none"
          initial={{ opacity: 0 }}
          animate={{ 
            opacity: [0.2, 0.4, 0.2],
            scale: [1, 1.02, 1]
          }}
          transition={{ 
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      )}
      
      {/* Agent Image Section (40%) */}
      <div className={imageWrapperClass}>
        {renderAgentImage()}
        <div className="absolute -top-2 -right-2 flex items-center justify-center pointer-events-none">
          {renderStatusIndicator()}
        </div>
      </div>

      {/* Data Section (60%) */}
      <div className={dataSectionClass}>
        <div className={isFocus ? 'flex-1 flex items-end justify-center w-full' : 'flex-1'}>
          <div className={isFocus ? 'w-full max-w-2xl mx-auto' : ''}>
            {renderDynamicData()}
          </div>
        </div>
        
        {/* Agent name with menu */}
        <div className={`relative ${isFocus ? 'pt-2' : ''}`}>
          <motion.div 
            className={`${isFocus ? 'text-lg' : 'text-sm'} font-semibold text-gray-700 text-center truncate pr-8 pl-8`}
            animate={isHovered ? { scale: 1.05 } : { scale: 1 }}
            transition={{ duration: 0.2 }}
          >
            {agentName}
          </motion.div>
          
          {/* Edit Agent Button - Bottom Left Corner */}
          <motion.button
            className="absolute left-[-4px] bottom-[-4px] w-9 h-9 bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-500 hover:from-blue-600 hover:via-indigo-600 hover:to-purple-600 rounded-full flex items-center justify-center text-white shadow-xl backdrop-blur-sm border border-white/60 cursor-pointer z-20 focus:outline-none focus:ring-2 focus:ring-blue-300"
            onClick={(e) => {
              e.stopPropagation()
              onPlayClick?.(agentKey)
            }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            title="Edit Agent"
            animate={isActive ? { 
              scale: [1, 1.1, 1],
              rotate: [0, 5, -5, 0]
            } : {}}
            transition={{ 
              duration: 2,
              repeat: isActive ? Infinity : 0,
              ease: "easeInOut"
            }}
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
              <path d="M4 20h3.6l10.9-10.9a1 1 0 0 0 0-1.4L15.4 4.6a1 1 0 0 0-1.4 0L3.1 15.5V19a1 1 0 0 0 1 1zm11.9-12.9 1.4 1.4-1.6 1.6-1.4-1.4 1.6-1.6zM5.1 18l8.2-8.2 1.4 1.4L6.5 19H5.1V18z" />
            </svg>
          </motion.button>
          
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

      {/* Enhanced hover glow effect */}
      <AnimatePresence>
        {isHovered && !isActive && (
          <motion.div
            className="absolute inset-0 rounded-3xl"
            style={{
              background: `linear-gradient(135deg, 
                rgba(59, 130, 246, 0.1) 0%, 
                rgba(147, 51, 234, 0.08) 50%, 
                rgba(236, 72, 153, 0.1) 100%)`,
              boxShadow: `0 0 30px rgba(59, 130, 246, 0.3), 
                          0 0 60px rgba(147, 51, 234, 0.2), 
                          0 0 90px rgba(236, 72, 153, 0.1)`
            }}
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
      {isFloating && isDragging && (
        <motion.div
          className="absolute inset-0 border-2 border-dashed border-blue-400 rounded-3xl bg-blue-50/20"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        />
      )}
    </motion.div>
    </>
  )
}

export default AgentAIBlock
