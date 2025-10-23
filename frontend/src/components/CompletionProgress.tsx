'use client'

import { motion } from 'framer-motion'

interface CompletionProgressProps {
  completionPercent: number
  totalBudget: number
  usedBudget: number
}

export function CompletionProgress({ completionPercent, totalBudget, usedBudget }: CompletionProgressProps) {
  const getCompletionColor = (percent: number) => {
    if (percent >= 90) return 'text-green-600'
    if (percent >= 70) return 'text-blue-600'
    if (percent >= 50) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getCompletionIcon = (percent: number) => {
    if (percent >= 90) return '🎉'
    if (percent >= 70) return '⚡'
    if (percent >= 50) return '🔄'
    return '⏳'
  }

  const getCompletionMessage = (percent: number) => {
    if (percent >= 90) return 'Almost Ready!'
    if (percent >= 70) return 'Looking Great!'
    if (percent >= 50) return 'Good Progress!'
    return 'Getting Started'
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      className="text-center relative"
    >
      {/* Magical sparkles around the progress */}
      {[...Array(6)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-2 h-2 bg-gradient-to-r from-pink-400 to-purple-400 rounded-full"
          style={{
            left: `${50 + Math.cos((i * 60) * Math.PI / 180) * 60}%`,
            top: `${50 + Math.sin((i * 60) * Math.PI / 180) * 60}%`,
          }}
          animate={{
            opacity: [0, 1, 0],
            scale: [0, 1, 0],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            delay: i * 0.3,
          }}
        />
      ))}
      
      <div className="relative">
        {/* Magical Circular Progress */}
        <div className="relative w-32 h-32 mx-auto mb-6">
          <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 36 36">
            {/* Background circle with glow */}
            <path
              d="M18 2.0845
                a 15.9155 15.9155 0 0 1 0 31.831
                a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none"
              stroke="rgba(255,182,193,0.3)"
              strokeWidth="3"
            />
            {/* Progress circle with gradient */}
            <motion.path
              d="M18 2.0845
                a 15.9155 15.9155 0 0 1 0 31.831
                a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none"
              stroke="url(#gradient)"
              strokeWidth="4"
              strokeLinecap="round"
              strokeDasharray={`${completionPercent}, 100`}
              initial={{ strokeDasharray: "0, 100" }}
              animate={{ strokeDasharray: `${completionPercent}, 100` }}
              transition={{ duration: 2, ease: "easeOut" }}
            />
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#ec4899" />
                <stop offset="50%" stopColor="#8b5cf6" />
                <stop offset="100%" stopColor="#3b82f6" />
              </linearGradient>
            </defs>
          </svg>
          
          {/* Center content with magical effects */}
          <div className="absolute inset-0 flex items-center justify-center">
            <motion.div 
              className="text-center"
              animate={{ 
                scale: [1, 1.1, 1],
              }}
              transition={{ 
                duration: 2, 
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              <motion.div 
                className="text-4xl mb-2"
                animate={{ rotate: [0, 360] }}
                transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
              >
                {getCompletionIcon(completionPercent)}
              </motion.div>
              <div className="text-2xl font-bold bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
                {completionPercent}%
              </div>
            </motion.div>
          </div>
        </div>

        {/* Magical Status Text */}
        <div className="space-y-2">
          <motion.div 
            className="text-2xl font-bold bg-gradient-to-r from-pink-600 via-purple-600 to-blue-600 bg-clip-text text-transparent"
            animate={{ 
              backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"] 
            }}
            transition={{ 
              duration: 3, 
              repeat: Infinity, 
              ease: "linear" 
            }}
            style={{ backgroundSize: "200% 100%" }}
          >
            {getCompletionMessage(completionPercent)}
          </motion.div>
          <div className="text-lg text-gray-600 font-medium">
            ✨ Magical Party Plan Complete ✨
          </div>
        </div>
      </div>
    </motion.div>
  )
}
