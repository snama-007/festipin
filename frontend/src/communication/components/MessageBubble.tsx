'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { MessageBubbleProps } from '../types/communication'

export function MessageBubble({ 
  message, 
  isOwn, 
  showAvatar, 
  showTimestamp, 
  onReply 
}: MessageBubbleProps) {
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  const getSenderIcon = (senderType: string) => {
    switch (senderType) {
      case 'user':
        return '👤'
      case 'vendor':
        return '🏢'
      case 'festimo':
        return '✨'
      default:
        return '👤'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'sent':
        return '✓'
      case 'delivered':
        return '✓✓'
      case 'read':
        return '✓✓'
      default:
        return ''
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
      className={`flex ${isOwn ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div className={`flex items-end gap-2 max-w-xs lg:max-w-md ${isOwn ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        {showAvatar && !isOwn && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.1 }}
            className="w-8 h-8 bg-gradient-to-r from-pink-400 to-purple-400 rounded-full flex items-center justify-center text-white text-sm font-bold flex-shrink-0"
          >
            {getSenderIcon(message.sender_type)}
          </motion.div>
        )}

        {/* Message Content */}
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.1, duration: 0.2 }}
          className={`relative group ${
            isOwn 
              ? 'bg-gradient-to-r from-pink-500 to-purple-500 text-white' 
              : 'bg-white/90 backdrop-blur-sm text-gray-800 border border-gray-200/50'
          } rounded-2xl px-4 py-3 shadow-lg hover:shadow-xl transition-all duration-200`}
        >
          {/* Message Text */}
          <div className="relative">
            <p className="text-sm leading-relaxed break-words">
              {message.content}
            </p>

            {/* Reply Reference */}
            {message.reply_to && (
              <div className={`mt-2 p-2 rounded-lg border-l-4 ${
                isOwn 
                  ? 'bg-white/20 border-white/50' 
                  : 'bg-gray-100 border-gray-300'
              }`}>
                <p className="text-xs opacity-75">
                  Replying to message...
                </p>
              </div>
            )}

            {/* Attachments */}
            {message.attachments && message.attachments.length > 0 && (
              <div className="mt-2 space-y-2">
                {message.attachments.map((attachment) => (
                  <motion.div
                    key={attachment.attachment_id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.2 }}
                    className="relative"
                  >
                    {attachment.file_type === 'image' ? (
                      <img
                        src={attachment.file_url}
                        alt={attachment.filename}
                        className="max-w-full h-auto rounded-lg shadow-md"
                        loading="lazy"
                      />
                    ) : (
                      <div className={`p-3 rounded-lg border ${
                        isOwn 
                          ? 'bg-white/20 border-white/50' 
                          : 'bg-gray-100 border-gray-300'
                      }`}>
                        <div className="flex items-center gap-2">
                          <div className="text-lg">
                            {attachment.file_type === 'document' ? '📄' : '📎'}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-xs font-medium truncate">
                              {attachment.filename}
                            </p>
                            <p className="text-xs opacity-75">
                              {(attachment.file_size / 1024).toFixed(1)} KB
                            </p>
                          </div>
                        </div>
                      </div>
                    )}
                  </motion.div>
                ))}
              </div>
            )}
          </div>

          {/* Message Footer */}
          <div className={`flex items-center justify-between mt-2 ${
            isOwn ? 'text-pink-100' : 'text-gray-500'
          }`}>
            <div className="flex items-center gap-1 text-xs">
              {showTimestamp && (
                <span>{formatTime(message.timestamp)}</span>
              )}
              {isOwn && (
                <span className="ml-1">
                  {getStatusIcon(message.status)}
                </span>
              )}
            </div>

            {/* Reply Button */}
            {onReply && !isOwn && (
              <motion.button
                onClick={() => onReply(message)}
                className="opacity-0 group-hover:opacity-100 transition-opacity duration-200 p-1 hover:bg-white/20 rounded"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <svg
                  width="12"
                  height="12"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                  <path d="M8 9h8" />
                  <path d="M8 13h6" />
                </svg>
              </motion.button>
            )}
          </div>

          {/* Magical Sparkle Effect for Festimo Messages */}
          {message.sender_type === 'festimo' && (
            <motion.div
              className="absolute -top-1 -right-1 text-yellow-400"
              animate={{ 
                rotate: [0, 360],
                scale: [1, 1.2, 1]
              }}
              transition={{ 
                duration: 2, 
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              ✨
            </motion.div>
          )}
        </motion.div>

        {/* Avatar for own messages */}
        {showAvatar && isOwn && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.1 }}
            className="w-8 h-8 bg-gradient-to-r from-pink-500 to-purple-500 rounded-full flex items-center justify-center text-white text-sm font-bold flex-shrink-0"
          >
            👤
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}
