'use client'

import { motion } from 'framer-motion'

interface RecommendationsListProps {
  recommendations: string[]
}

export function RecommendationsList({ recommendations }: RecommendationsListProps) {
  const getRecommendationIcon = (recommendation: string) => {
    if (recommendation.toLowerCase().includes('budget')) return '💰'
    if (recommendation.toLowerCase().includes('venue')) return '🏢'
    if (recommendation.toLowerCase().includes('cake')) return '🍰'
    if (recommendation.toLowerCase().includes('catering')) return '🍽️'
    if (recommendation.toLowerCase().includes('vendor')) return '🎈'
    if (recommendation.toLowerCase().includes('theme')) return '🎨'
    if (recommendation.toLowerCase().includes('timeline')) return '⏰'
    if (recommendation.toLowerCase().includes('guest')) return '👥'
    return '💡'
  }

  return (
    <div 
      className="relative bg-white/90 backdrop-blur-sm rounded-2xl shadow-2xl border border-white/50 p-8 overflow-hidden"
      style={{
        background: `
          linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%),
          radial-gradient(circle at bottom right, rgba(255,182,193,0.1) 0%, transparent 50%)
        `
      }}
    >
      {/* Magical sparkles */}
      {[...Array(12)].map((_, i) => (
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
        <div className="flex items-center gap-4 mb-8">
          <motion.div 
            className="text-5xl"
            animate={{ rotate: [0, 360] }}
            transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
          >
            ✨
          </motion.div>
          <div>
            <h2 className="text-3xl font-bold bg-gradient-to-r from-pink-600 via-purple-600 to-blue-600 bg-clip-text text-transparent">
              AI Magic Recommendations
            </h2>
            <p className="text-gray-600 mt-1">Our wizards have some amazing ideas for you!</p>
          </div>
        </div>

        <div className="space-y-6">
          {recommendations.map((recommendation, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -30, scale: 0.9 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              transition={{ delay: index * 0.2, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
              whileHover={{ 
                scale: 1.02,
                y: -5,
                transition: { duration: 0.3 }
              }}
              className="relative group flex items-start gap-6 p-6 bg-gradient-to-r from-pink-50/80 via-purple-50/80 to-blue-50/80 rounded-xl border border-pink-200/50 hover:shadow-lg transition-all duration-300"
            >
              {/* Magical shimmer */}
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent rounded-xl"
                animate={{ x: ["-100%", "100%"] }}
                transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
              />
              
              <motion.div 
                className="text-3xl flex-shrink-0 mt-1"
                whileHover={{ scale: 1.2, rotate: 10 }}
                transition={{ duration: 0.3 }}
              >
                {getRecommendationIcon(recommendation)}
              </motion.div>
              <div className="flex-1">
                <p className="text-gray-800 leading-relaxed text-lg font-medium">{recommendation}</p>
              </div>
              <motion.div 
                className="flex-shrink-0"
                animate={{ 
                  scale: [1, 1.2, 1],
                  opacity: [0.7, 1, 0.7]
                }}
                transition={{ 
                  duration: 2, 
                  repeat: Infinity,
                  delay: index * 0.3
                }}
              >
                <div className="w-3 h-3 bg-gradient-to-r from-pink-400 to-purple-400 rounded-full"></div>
              </motion.div>
            </motion.div>
          ))}
        </div>

        <motion.div 
          className="mt-8 p-6 bg-gradient-to-r from-green-50/80 via-blue-50/80 to-purple-50/80 rounded-xl border border-green-200/50"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
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
              🎯
            </motion.div>
            <div>
              <div className="text-xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
                ✨ Magical Planning Complete! ✨
              </div>
              <div className="text-gray-600 mt-1">
                Our AI wizards have crafted the perfect celebration plan. You're ready for an unforgettable party!
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
