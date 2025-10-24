'use client'

import React, { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { MessageComposerProps } from '../types/communication'

export function MessageComposer({ 
  onSendMessage, 
  onTyping, 
  disabled = false,
  placeholder = "Type your message..."
}: MessageComposerProps) {
  const [message, setMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [message])

  // Handle typing indicators
  useEffect(() => {
    if (message.trim() && !isTyping) {
      setIsTyping(true)
      onTyping(true)
    } else if (!message.trim() && isTyping) {
      setIsTyping(false)
      onTyping(false)
    }

    // Clear typing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current)
    }

    // Set timeout to stop typing indicator
    if (message.trim()) {
      typingTimeoutRef.current = setTimeout(() => {
        setIsTyping(false)
        onTyping(false)
      }, 2000)
    }

    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current)
      }
    }
  }, [message, isTyping, onTyping])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (message.trim() && !disabled) {
      onSendMessage(message.trim())
      setMessage('')
      
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
      }
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleSendClick = () => {
    if (message.trim() && !disabled) {
      onSendMessage(message.trim())
      setMessage('')
      
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
      }
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative"
    >
      <form onSubmit={handleSubmit} className="flex items-end gap-3 p-4 bg-white/90 backdrop-blur-sm rounded-2xl border border-white/50 shadow-lg">
        {/* Message Input */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            disabled={disabled}
            className="w-full resize-none border-0 outline-none bg-transparent text-gray-800 placeholder-gray-500 text-sm leading-relaxed max-h-32"
            rows={1}
            style={{ minHeight: '20px' }}
          />
          
          {/* Character Count */}
          {message.length > 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="absolute -bottom-6 right-0 text-xs text-gray-400"
            >
              {message.length}/1000
            </motion.div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          {/* Attachment Button */}
          <motion.button
            type="button"
            disabled={disabled}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66L9.64 16.2a2 2 0 0 1-2.83-2.83l8.49-8.49" />
            </svg>
          </motion.button>

          {/* Emoji Button */}
          <motion.button
            type="button"
            disabled={disabled}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="12" cy="12" r="10" />
              <path d="M8 14s1.5 2 4 2 4-2 4-2" />
              <line x1="9" y1="9" x2="9.01" y2="9" />
              <line x1="15" y1="9" x2="15.01" y2="9" />
            </svg>
          </motion.button>

          {/* Send Button */}
          <motion.button
            type="button"
            onClick={handleSendClick}
            disabled={disabled || !message.trim()}
            className={`px-4 py-2 rounded-xl font-semibold text-sm transition-all duration-200 ${
              message.trim() && !disabled
                ? 'bg-gradient-to-r from-pink-500 to-purple-500 text-white shadow-lg hover:shadow-xl hover:from-pink-600 hover:to-purple-600'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
            }`}
            whileHover={message.trim() && !disabled ? { scale: 1.05 } : {}}
            whileTap={message.trim() && !disabled ? { scale: 0.95 } : {}}
          >
            <div className="flex items-center gap-2">
              <span>Send</span>
              <motion.div
                animate={message.trim() && !disabled ? { 
                  rotate: [0, 10, -10, 0],
                  scale: [1, 1.1, 1]
                } : {}}
                transition={{ 
                  duration: 0.5, 
                  repeat: Infinity,
                  repeatDelay: 2
                }}
              >
                ✨
              </motion.div>
            </div>
          </motion.button>
        </div>
      </form>

      {/* Typing Indicator */}
      {isTyping && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
          className="absolute -top-8 left-4 bg-gray-100 text-gray-600 text-xs px-3 py-1 rounded-full shadow-sm"
        >
          <div className="flex items-center gap-1">
            <motion.div
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1, repeat: Infinity }}
              className="w-1 h-1 bg-gray-400 rounded-full"
            />
            <motion.div
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
              className="w-1 h-1 bg-gray-400 rounded-full"
            />
            <motion.div
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
              className="w-1 h-1 bg-gray-400 rounded-full"
            />
            <span className="ml-1">Typing...</span>
          </div>
        </motion.div>
      )}

      {/* Magical Sparkles */}
      {message.trim() && !disabled && (
        <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-2xl">
          {[...Array(3)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-gradient-to-r from-pink-400 to-purple-400 rounded-full"
              style={{
                left: `${20 + Math.random() * 60}%`,
                top: `${20 + Math.random() * 60}%`,
              }}
              animate={{
                opacity: [0, 1, 0],
                scale: [0, 1, 0],
                y: [0, -20, 0],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: Math.random() * 2,
              }}
            />
          ))}
        </div>
      )}
    </motion.div>
  )
}
