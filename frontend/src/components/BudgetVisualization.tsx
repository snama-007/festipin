'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'

interface BudgetVisualizationProps {
  budget: {
    total_min: number
    total_max: number
    breakdown: Array<{
      category: string
      amount: number
      percentage: number
    }>
  }
}

export function BudgetVisualization({ budget }: BudgetVisualizationProps) {
  const { total_min, total_max, breakdown } = budget
  const budgetUsed = total_min
  const budgetTotal = total_max
  const usagePercentage = (budgetUsed / budgetTotal) * 100
  const [isExpanded, setIsExpanded] = useState(false)

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      'venue': 'bg-blue-500',
      'catering': 'bg-orange-500',
      'cake': 'bg-pink-500',
      'decorations': 'bg-purple-500',
      'vendors': 'bg-green-500',
      'entertainment': 'bg-yellow-500',
      'photography': 'bg-indigo-500',
      'other': 'bg-gray-500'
    }
    return colors[category.toLowerCase()] || 'bg-gray-500'
  }

  const getCategoryIcon = (category: string) => {
    const icons: Record<string, string> = {
      'venue': '🏢',
      'catering': '🍽️',
      'cake': '🍰',
      'decorations': '🎨',
      'vendors': '🎈',
      'entertainment': '🎪',
      'photography': '📸',
      'other': '💰'
    }
    return icons[category.toLowerCase()] || '💰'
  }

  return (
    <div 
      className="relative bg-white/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-white/50 p-8 overflow-hidden"
      style={{
        background: `
          linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%),
          radial-gradient(circle at top left, rgba(255,182,193,0.1) 0%, transparent 50%)
        `
      }}
    >
      {/* Magical sparkles */}
      {[...Array(8)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-1 h-1 bg-gradient-to-r from-pink-400 to-purple-400 rounded-full"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
          animate={{
            opacity: [0, 1, 0],
            scale: [0, 1, 0],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            delay: Math.random() * 2,
          }}
        />
      ))}
      
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-3xl font-bold bg-gradient-to-r from-pink-600 via-purple-600 to-blue-600 bg-clip-text text-transparent">
              💰 Budget Celebration
            </h2>
            <p className="text-gray-600 mt-2">Your magical budget breakdown</p>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold bg-gradient-to-r from-green-500 to-emerald-500 bg-clip-text text-transparent">
              ${budgetUsed.toLocaleString()}
            </div>
            <div className="text-lg text-gray-600">of ${budgetTotal.toLocaleString()}</div>
          </div>
        </div>

        {/* Budget Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-lg text-gray-600 mb-3">
            <span className="font-semibold">Budget Usage</span>
            <span className="font-bold">{usagePercentage.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-4">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(usagePercentage, 100)}%` }}
              transition={{ duration: 1.5, ease: "easeOut" }}
              className={`h-4 rounded-full ${
                usagePercentage > 90 ? 'bg-gradient-to-r from-red-500 to-pink-500' : 
                usagePercentage > 75 ? 'bg-gradient-to-r from-yellow-500 to-orange-500' : 
                'bg-gradient-to-r from-green-500 to-emerald-500'
              }`}
            />
          </div>
        </div>

        {/* Magical Budget Breakdown - Expandable */}
        <div>
          <motion.div 
            className="flex items-center justify-between mb-6 cursor-pointer group"
            onClick={() => setIsExpanded(!isExpanded)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <h3 className="text-2xl font-bold bg-gradient-to-r from-pink-600 via-purple-600 to-blue-600 bg-clip-text text-transparent">
              ✨ Magical Budget Breakdown ✨
            </h3>
            <motion.div
              animate={{ 
                rotate: isExpanded ? 180 : 0,
                scale: isExpanded ? 1.1 : 1
              }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
              className="text-2xl group-hover:scale-110 transition-transform duration-200"
            >
              <motion.span
                animate={{ 
                  rotate: [0, 10, -10, 0],
                  scale: [1, 1.2, 1]
                }}
                transition={{ 
                  duration: 2, 
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                {isExpanded ? '🔽' : '🔼'}
              </motion.span>
            </motion.div>
          </motion.div>

          {/* Summary Cards - Always Visible */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {breakdown.slice(0, 4).map((item, index) => (
              <motion.div
                key={item.category}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="p-4 bg-gradient-to-br from-white/80 to-gray-50/80 rounded-xl border border-gray-200/50 hover:shadow-lg transition-all duration-300 text-center"
              >
                <div className="text-2xl mb-2">{getCategoryIcon(item.category)}</div>
                <div className="font-bold text-gray-800 text-sm capitalize">{item.category}</div>
                <div className="text-lg font-bold text-purple-600">${item.amount.toLocaleString()}</div>
                <div className="text-xs text-gray-500">{item.percentage.toFixed(1)}%</div>
              </motion.div>
            ))}
          </div>

          {/* Detailed Breakdown - Expandable */}
          <AnimatePresence>
            {isExpanded && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.4, ease: "easeInOut" }}
                className="overflow-hidden"
              >
                <div className="space-y-3">
                  <div className="text-lg font-semibold text-gray-700 mb-4 text-center">
                    📊 Detailed Breakdown
                  </div>
                  {breakdown.map((item, index) => (
                    <motion.div
                      key={item.category}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50/80 to-white/80 rounded-xl border border-gray-200/50 hover:shadow-lg transition-all duration-300 group"
                    >
                      <div className="flex items-center gap-4">
                        <motion.span 
                          className="text-3xl"
                          whileHover={{ scale: 1.2, rotate: 5 }}
                          transition={{ duration: 0.2 }}
                        >
                          {getCategoryIcon(item.category)}
                        </motion.span>
                        <div>
                          <div className="font-bold text-gray-800 capitalize text-lg">{item.category}</div>
                          <div className="text-sm text-gray-500">{item.percentage.toFixed(1)}% of total budget</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-gray-800 text-lg">${item.amount.toLocaleString()}</div>
                        <div className="text-sm text-gray-500">
                          {((item.amount / budgetTotal) * 100).toFixed(1)}% of total
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Expand/Collapse Hint */}
          <motion.div 
            className="text-center mt-4"
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <span className="text-sm text-gray-500">
              {isExpanded ? 'Click to collapse details' : 'Click to see detailed breakdown'}
            </span>
          </motion.div>
        </div>

        {/* Budget Status */}
        <motion.div 
          className="mt-8 p-6 bg-gradient-to-r from-green-50/80 via-blue-50/80 to-purple-50/80 rounded-xl border border-green-200/50"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <div className="flex items-center gap-4">
            <motion.div 
              className="text-4xl"
              animate={{ 
                scale: [1, 1.2, 1],
                rotate: [0, 10, -10, 0]
              }}
              transition={{ 
                duration: 2, 
                repeat: Infinity,
                ease: "easeInOut"
              }}
            >
              {usagePercentage > 90 ? '⚠️' : usagePercentage > 75 ? '⚡' : '✅'}
            </motion.div>
            <div>
              <div className="text-xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
                {usagePercentage > 90 ? 'Budget Nearly Full' : 
                 usagePercentage > 75 ? 'Good Budget Usage' : 'Excellent Budget Management'}
              </div>
              <div className="text-gray-600 mt-1">
                {usagePercentage > 90 ? 'Consider optimizing some expenses' :
                 usagePercentage > 75 ? 'You have room for additional items' :
                 'You have plenty of budget remaining for extras'}
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}