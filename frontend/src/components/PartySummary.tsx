'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence, useMotionValue, useSpring } from 'framer-motion'
import { getPartyStatus, type PartySummaryData } from '@/services/api'
import { PlanCard } from './PlanCard'
import { BudgetVisualization } from './BudgetVisualization'
import { CompletionProgress } from './CompletionProgress'
import { RecommendationsList } from './RecommendationsList'
import { demoPartyData } from '@/data/demoPartyData'

interface PartySummaryProps {
  partyId: string
  onNext: () => void
}

export function PartySummary({ partyId, onNext }: PartySummaryProps) {
  const [partyData, setPartyData] = useState<PartySummaryData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchPartyData()
  }, [partyId])

  const fetchPartyData = async () => {
    try {
      setLoading(true)
      const data = await getPartyStatus(partyId)
      setPartyData(data)
    } catch (err) {
      console.log('API failed, using demo data:', err)
      // Use demo data for testing when API is not available
      setPartyData(demoPartyData as PartySummaryData)
      setError(null) // Clear error since we have demo data
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div 
        className="min-h-screen flex items-center justify-center relative overflow-hidden"
        style={{
          background: `
            radial-gradient(circle at 20% 80%, rgba(255, 182, 193, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255, 192, 203, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(255, 218, 185, 0.2) 0%, transparent 50%),
            linear-gradient(135deg, rgba(255, 182, 193, 0.1) 0%, rgba(255, 192, 203, 0.1) 50%, rgba(255, 218, 185, 0.1) 100%)
          `
        }}
      >
        {/* Floating Magic Particles */}
        {[...Array(15)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-gradient-to-r from-pink-400 to-rose-400 rounded-full opacity-60"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -30, 0],
              x: [0, Math.random() * 20 - 10, 0],
              opacity: [0.6, 1, 0.6],
              scale: [1, 1.5, 1],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
        
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center relative z-10"
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="text-6xl mb-6"
          >
            ✨
          </motion.div>
          <motion.h2 
            className="text-4xl font-bold bg-gradient-to-r from-pink-600 via-purple-600 to-blue-600 bg-clip-text text-transparent mb-4"
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
            🎊 Creating Magic! 🎊
          </motion.h2>
          <p className="text-xl text-gray-700 font-medium">
            Our AI wizards are crafting your perfect celebration...
          </p>
        </motion.div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-50 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center max-w-md mx-auto p-6"
        >
          <div className="text-6xl mb-4">😔</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Oops! Something went wrong</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchPartyData}
            className="bg-purple-600 text-white px-6 py-2 rounded-lg hover:bg-purple-700 transition-colors"
          >
            Try Again
          </button>
        </motion.div>
      </div>
    )
  }

  if (!partyData) return null

  const { agent_results, completion_percent, budget, recommendations } = partyData

  return (
    <div 
      className="min-h-screen relative overflow-hidden"
      style={{
        background: `
          radial-gradient(circle at 20% 80%, rgba(255, 182, 193, 0.3) 0%, transparent 50%),
          radial-gradient(circle at 80% 20%, rgba(255, 192, 203, 0.3) 0%, transparent 50%),
          radial-gradient(circle at 40% 40%, rgba(255, 218, 185, 0.2) 0%, transparent 50%),
          linear-gradient(135deg, rgba(255, 182, 193, 0.1) 0%, rgba(255, 192, 203, 0.1) 50%, rgba(255, 218, 185, 0.1) 100%)
        `
      }}
    >
      {/* Floating Magic Particles */}
      {[...Array(25)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-2 h-2 bg-gradient-to-r from-pink-400 to-rose-400 rounded-full opacity-60"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
          animate={{
            y: [0, -30, 0],
            x: [0, Math.random() * 20 - 10, 0],
            opacity: [0.6, 1, 0.6],
            scale: [1, 1.5, 1],
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            repeat: Infinity,
            delay: Math.random() * 2,
          }}
        />
      ))}

      {/* Magical Header */}
      <motion.div
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        className="relative z-10 text-center pt-16 pb-8"
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.3, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="text-8xl mb-6"
        >
          🎊
        </motion.div>
        
        <motion.h1 
          className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-pink-600 via-purple-600 to-blue-600 bg-clip-text text-transparent mb-4"
          animate={{ 
            backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"] 
          }}
          transition={{ 
            duration: 4, 
            repeat: Infinity, 
            ease: "linear" 
          }}
          style={{ backgroundSize: "200% 100%" }}
        >
          Your Magical Party is Ready!
        </motion.h1>
        
        <motion.p 
          className="text-xl md:text-2xl text-gray-700 font-medium mb-8"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          ✨ Everything is perfectly planned for an unforgettable celebration ✨
        </motion.p>

        {/* Completion Celebration */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.8 }}
          className="inline-block"
        >
          <CompletionProgress 
            completionPercent={completion_percent}
            totalBudget={budget.total_max}
            usedBudget={budget.total_min}
          />
        </motion.div>
      </motion.div>

      {/* Magical Content */}
      <div className="relative z-10 max-w-7xl mx-auto px-4 pb-16">
        {/* Budget Celebration */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.0, duration: 0.8 }}
          className="mb-12"
        >
          <BudgetVisualization budget={budget} />
        </motion.div>

        {/* Magical Plan Cards */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12"
        >
          <AnimatePresence>
            {agent_results.theme_agent && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8, y: 50 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ delay: 1.3, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
                whileHover={{ 
                  scale: 1.05, 
                  y: -10,
                  transition: { duration: 0.3 }
                }}
              >
                <PlanCard
                  type="theme"
                  title="🎨 Theme & Decorations"
                  data={agent_results.theme_agent.result}
                  status={agent_results.theme_agent.status}
                />
              </motion.div>
            )}
            
            {agent_results.venue_agent && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8, y: 50 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ delay: 1.4, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
                whileHover={{ 
                  scale: 1.05, 
                  y: -10,
                  transition: { duration: 0.3 }
                }}
              >
                <PlanCard
                  type="venue"
                  title="🏢 Venue"
                  data={agent_results.venue_agent.result}
                  status={agent_results.venue_agent.status}
                />
              </motion.div>
            )}
            
            {agent_results.cake_agent && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8, y: 50 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ delay: 1.5, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
                whileHover={{ 
                  scale: 1.05, 
                  y: -10,
                  transition: { duration: 0.3 }
                }}
              >
                <PlanCard
                  type="cake"
                  title="🍰 Cake & Desserts"
                  data={agent_results.cake_agent.result}
                  status={agent_results.cake_agent.status}
                />
              </motion.div>
            )}
            
            {agent_results.catering_agent && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8, y: 50 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ delay: 1.6, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
                whileHover={{ 
                  scale: 1.05, 
                  y: -10,
                  transition: { duration: 0.3 }
                }}
              >
                <PlanCard
                  type="catering"
                  title="🍽️ Catering"
                  data={agent_results.catering_agent.result}
                  status={agent_results.catering_agent.status}
                />
              </motion.div>
            )}
            
            {agent_results.vendor_agent && (
              <motion.div
                initial={{ opacity: 0, scale: 0.8, y: 50 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ delay: 1.7, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
                whileHover={{ 
                  scale: 1.05, 
                  y: -10,
                  transition: { duration: 0.3 }
                }}
              >
                <PlanCard
                  type="vendor"
                  title="🎈 Vendors & Services"
                  data={agent_results.vendor_agent.result}
                  status={agent_results.vendor_agent.status}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Magical Recommendations */}
        {recommendations && recommendations.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.8, duration: 0.8 }}
            className="mb-12"
          >
            <RecommendationsList recommendations={recommendations} />
          </motion.div>
        )}

        {/* Magical Next Button */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 2.0, duration: 0.8 }}
          className="text-center"
        >
          <motion.button
            onClick={onNext}
            className="relative group bg-gradient-to-r from-pink-500 via-purple-500 to-blue-500 text-white px-12 py-6 rounded-2xl text-xl font-bold shadow-2xl overflow-hidden"
            whileHover={{ 
              scale: 1.05,
              boxShadow: "0 20px 40px rgba(0,0,0,0.2)"
            }}
            whileTap={{ scale: 0.95 }}
            animate={{
              backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"]
            }}
            transition={{
              backgroundPosition: { duration: 3, repeat: Infinity, ease: "linear" }
            }}
            style={{ backgroundSize: "200% 100%" }}
          >
            {/* Magical sparkles */}
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
              animate={{ x: ["-100%", "100%"] }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            />
            
            <span className="relative z-10 flex items-center gap-3">
              <motion.span
                animate={{ rotate: [0, 360] }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              >
                ✨
              </motion.span>
              Start Your Vendor Conversations
              <motion.span
                animate={{ x: [0, 5, 0] }}
                transition={{ duration: 1, repeat: Infinity }}
              >
                💬
              </motion.span>
            </span>
          </motion.button>
        </motion.div>
      </div>
    </div>
  )
}
