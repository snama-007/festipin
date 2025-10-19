import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { AgentUpdate } from './useOrchestration'
import { demoScenarios, type DemoAgentKey, type DemoScenarioKey } from '@/data/demoAgents'

interface DemoOrchestrationState {
  agentUpdates: AgentUpdate[]
  currentAgent: string | null
  completedAgents: string[]
  errors: Record<string, string>
  isConnected: boolean
  workflowStatus: 'idle' | 'connecting' | 'running' | 'completed' | 'error'
}

const initialState: DemoOrchestrationState = {
  agentUpdates: [],
  currentAgent: null,
  completedAgents: [],
  errors: {},
  isConnected: true,
  workflowStatus: 'idle'
}

export function useDemoOrchestration(scenarioKey: DemoScenarioKey) {
  const scenario = useMemo(() => demoScenarios[scenarioKey], [scenarioKey])

  const [state, setState] = useState<DemoOrchestrationState>(initialState)
  const timeoutsRef = useRef<NodeJS.Timeout[]>([])

  const clearTimeline = useCallback(() => {
    timeoutsRef.current.forEach(clearTimeout)
    timeoutsRef.current = []
  }, [])

  useEffect(() => {
    clearTimeline()
    setState(initialState)
  }, [scenarioKey, clearTimeline])

  useEffect(() => () => clearTimeline(), [clearTimeline])

  const startDemo = useCallback(() => {
    clearTimeline()
    setState(prev => ({
      ...initialState,
      workflowStatus: 'running',
      isConnected: prev.isConnected
    }))

    let cumulativeDelay = 0

    scenario.timeline.forEach(step => {
      cumulativeDelay += step.delay
      const timeout = setTimeout(() => {
        setState(prev => {
          const updates = [...prev.agentUpdates]
          const update: AgentUpdate = {
            type: 'agent_update',
            agent: step.agent,
            status: step.status,
            result: step.status === 'completed' ? scenario.agentResults[step.agent].result : undefined,
            message: scenario.agentResults[step.agent].summary,
            timestamp: new Date().toISOString()
          }

          updates.push(update)

          const completedAgents = step.status === 'completed' && step.agent
            ? Array.from(new Set([...prev.completedAgents, step.agent]))
            : prev.completedAgents

          const workflowStatus =
            step.agent === 'planner_agent' && step.status === 'completed'
              ? 'completed'
              : prev.workflowStatus

          return {
            ...prev,
            agentUpdates: updates,
            currentAgent: step.status === 'running' ? step.agent : prev.currentAgent,
            completedAgents,
            workflowStatus
          }
        })
      }, cumulativeDelay)

      timeoutsRef.current.push(timeout)
    })
  }, [clearTimeline, scenario])

  const getAgentResult = useCallback(
    (agentName: string) => scenario.agentResults[agentName as DemoAgentKey]?.result,
    [scenario]
  )

  return useMemo(
    () => ({
      ...state,
      startDemo,
      getAgentResult
    }),
    [state, startDemo, getAgentResult]
  )
}
