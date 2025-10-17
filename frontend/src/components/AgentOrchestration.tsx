'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  startOrchestration, 
  getWorkflowStatus, 
  addUserFeedback,
  type OrchestrationInput,
  type WorkflowStatus,
  type AgentStatus
} from '@/services/api'

interface AgentStatusPanelProps {
  workflowStatus: WorkflowStatus | null
  isProcessing: boolean
}

const AgentStatusPanel: React.FC<AgentStatusPanelProps> = ({ workflowStatus, isProcessing }) => {
  const agentOrder = [
    'input_classifier',
    'theme_agent',
    'cake_agent',
    'venue_agent',
    'catering_agent',
    'budget_agent',
    'vendor_agent',
    'planner_agent'
  ]

  const getAgentDisplayName = (agentName: string) => {
    const displayNames: Record<string, string> = {
      'input_classifier': '🔍 Input Analysis',
      'theme_agent': '🎨 Theme Detection',
      'cake_agent': '🍰 Cake Planning',
      'venue_agent': '🏠 Venue Selection',
      'catering_agent': '🍽️ Catering Planning',
      'budget_agent': '💰 Budget Estimation',
      'vendor_agent': '📞 Vendor Matching',
      'planner_agent': '📋 Final Assembly'
    }
    return displayNames[agentName] || agentName
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-500'
      case 'running': return 'bg-blue-500'
      case 'error': return 'bg-red-500'
      default: return 'bg-gray-300'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white/40 backdrop-blur-xl rounded-2xl p-6 border border-white/50"
    >
      <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
        🤖 Agent Progress
        {isProcessing && (
          <motion.div
            className="w-2 h-2 bg-blue-500 rounded-full"
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
          />
        )}
      </h3>

      <div className="space-y-3">
        {agentOrder.map((agentName, index) => {
          const agentResult = workflowStatus?.agent_results[agentName]
          const status = agentResult?.status || 'pending'
          const isActive = status === 'running'
          const isCompleted = status === 'completed'
          const hasError = status === 'error'

          return (
            <motion.div
              key={agentName}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`flex items-center gap-3 p-3 rounded-xl transition-all duration-300 ${
                isActive ? 'bg-blue-50/80 border border-blue-200' :
                isCompleted ? 'bg-green-50/80 border border-green-200' :
                hasError ? 'bg-red-50/80 border border-red-200' :
                'bg-white/30'
              }`}
            >
              {/* Status Indicator */}
              <div className="flex-shrink-0">
                <div className={`w-3 h-3 rounded-full ${getStatusColor(status)} ${
                  isActive ? 'animate-pulse' : ''
                }`} />
              </div>

              {/* Agent Name */}
              <span className="font-medium text-gray-800 flex-1">
                {getAgentDisplayName(agentName)}
              </span>

              {/* Progress Bar for Running Agents */}
              {isActive && (
                <div className="ml-auto">
                  <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-blue-500"
                      initial={{ width: 0 }}
                      animate={{ width: '100%' }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                  </div>
                </div>
              )}

              {/* Execution Time for Completed Agents */}
              {isCompleted && agentResult?.execution_time && (
                <span className="text-xs text-gray-500 ml-auto">
                  {agentResult.execution_time.toFixed(1)}s
                </span>
              )}

              {/* Error Indicator */}
              {hasError && (
                <span className="text-red-500 text-xs ml-auto">❌</span>
              )}
            </motion.div>
          )
        })}
      </div>

      {/* Workflow Status Summary */}
      {workflowStatus && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 p-3 rounded-xl bg-white/50 border border-white/50"
        >
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium text-gray-700">
              Workflow Status: 
              <span className={`ml-2 px-2 py-1 rounded-full text-xs ${
                workflowStatus.workflow_status === 'completed' ? 'bg-green-100 text-green-700' :
                workflowStatus.workflow_status === 'running' ? 'bg-blue-100 text-blue-700' :
                workflowStatus.workflow_status === 'error' ? 'bg-red-100 text-red-700' :
                'bg-gray-100 text-gray-700'
              }`}>
                {workflowStatus.workflow_status}
              </span>
            </span>
            <span className="text-gray-500">
              {new Date(workflowStatus.updated_at).toLocaleTimeString()}
            </span>
          </div>
        </motion.div>
      )}
    </motion.div>
  )
}

interface FinalPlanDisplayProps {
  finalPlan: any
  onFeedback?: (feedback: Record<string, any>) => void
}

const FinalPlanDisplay: React.FC<FinalPlanDisplayProps> = ({ finalPlan, onFeedback }) => {
  if (!finalPlan) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-8 p-6 rounded-2xl bg-white/40 border border-white/50 backdrop-blur-xl"
    >
      <h3 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
        🎊 Your Party Plan
      </h3>

      {/* Event Summary */}
      {finalPlan.event_summary && (
        <div className="mb-6 p-4 rounded-xl bg-white/50">
          <h4 className="font-semibold text-lg text-gray-800 mb-2">
            📋 Event Summary
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {finalPlan.event_summary.theme && (
              <div className="flex items-center gap-2">
                <span className="font-medium">🎨 Theme:</span>
                <span className="text-gray-700">{finalPlan.event_summary.theme}</span>
              </div>
            )}
            {finalPlan.event_summary.total_budget && (
              <div className="flex items-center gap-2">
                <span className="font-medium">💰 Budget:</span>
                <span className="text-gray-700">
                  ${finalPlan.event_summary.total_budget.min} - ${finalPlan.event_summary.total_budget.max}
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {finalPlan.recommendations && finalPlan.recommendations.length > 0 && (
        <div className="mb-6 p-4 rounded-xl bg-white/50">
          <h4 className="font-semibold text-lg text-gray-800 mb-2">
            💡 Recommendations
          </h4>
          <ul className="space-y-2">
            {finalPlan.recommendations.map((rec: string, index: number) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-blue-500 mt-1">•</span>
                <span className="text-gray-700">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Next Steps */}
      {finalPlan.next_steps && finalPlan.next_steps.length > 0 && (
        <div className="mb-6 p-4 rounded-xl bg-white/50">
          <h4 className="font-semibold text-lg text-gray-800 mb-2">
            📝 Next Steps
          </h4>
          <ol className="space-y-2">
            {finalPlan.next_steps.map((step: string, index: number) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-green-500 mt-1 font-bold">{index + 1}.</span>
                <span className="text-gray-700">{step}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* Feedback Section */}
      {onFeedback && (
        <div className="mt-6 p-4 rounded-xl bg-gradient-to-r from-pink-50 to-purple-50 border border-pink-200">
          <h4 className="font-semibold text-lg text-gray-800 mb-2">
            💬 How was your experience?
          </h4>
          <p className="text-gray-600 text-sm mb-3">
            Help us improve by sharing your feedback
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => onFeedback({ rating: 5, comment: 'Excellent!' })}
              className="px-3 py-1 bg-green-100 hover:bg-green-200 text-green-700 rounded-full text-sm transition-colors"
            >
              😍 Love it!
            </button>
            <button
              onClick={() => onFeedback({ rating: 3, comment: 'Good' })}
              className="px-3 py-1 bg-yellow-100 hover:bg-yellow-200 text-yellow-700 rounded-full text-sm transition-colors"
            >
              😊 Good
            </button>
            <button
              onClick={() => onFeedback({ rating: 1, comment: 'Needs improvement' })}
              className="px-3 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded-full text-sm transition-colors"
            >
              😕 Needs work
            </button>
          </div>
        </div>
      )}
    </motion.div>
  )
}

// Custom hook for agent orchestration
export const useAgentOrchestration = () => {
  const [isProcessing, setIsProcessing] = useState(false)
  const [currentEventId, setCurrentEventId] = useState<string | null>(null)
  const [workflowStatus, setWorkflowStatus] = useState<WorkflowStatus | null>(null)
  const [error, setError] = useState<string | null>(null)

  const startOrchestrationWorkflow = useCallback(async (
    inputs: OrchestrationInput[], 
    metadata?: Record<string, any>
  ) => {
    try {
      setIsProcessing(true)
      setError(null)
      setWorkflowStatus(null)

      const response = await startOrchestration(inputs, metadata)
      setCurrentEventId(response.event_id)

      // Start polling for status updates
      pollWorkflowStatus(response.event_id)
      
      // Return the response so caller can get the event_id immediately
      return response

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start orchestration')
      setIsProcessing(false)
      throw err
    }
  }, [])

  const pollWorkflowStatus = useCallback(async (eventId: string) => {
    try {
      const status = await getWorkflowStatus(eventId)
      setWorkflowStatus(status)

      // Continue polling if workflow is still running
      if (status.workflow_status === 'running') {
        setTimeout(() => pollWorkflowStatus(eventId), 2000) // Poll every 2 seconds
      } else {
        setIsProcessing(false)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get workflow status')
      setIsProcessing(false)
    }
  }, [])

  const addFeedback = useCallback(async (feedback: Record<string, any>) => {
    if (!currentEventId) return

    try {
      await addUserFeedback(currentEventId, feedback)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add feedback')
    }
  }, [currentEventId])

  const reset = useCallback(() => {
    setIsProcessing(false)
    setCurrentEventId(null)
    setWorkflowStatus(null)
    setError(null)
  }, [])

  return {
    isProcessing,
    currentEventId,
    workflowStatus,
    error,
    startOrchestrationWorkflow,
    addFeedback,
    reset,
  }
}

export { AgentStatusPanel, FinalPlanDisplay }
