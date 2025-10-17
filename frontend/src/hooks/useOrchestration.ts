/**
 * React Hook for Orchestration WebSocket Connection
 *
 * Provides real-time agent updates via WebSocket
 */

import { useEffect, useState, useCallback, useRef } from 'react';

export interface AgentUpdate {
  type: 'agent_update' | 'connection' | 'status_response' | 'pong';
  agent?: string;
  status?: 'running' | 'completed' | 'error';
  result?: any;
  message?: string;
  error?: string;
  timestamp?: string;
}

export interface OrchestrationState {
  agentUpdates: AgentUpdate[];
  currentAgent: string | null;
  completedAgents: string[];
  errors: Record<string, string>;
  isConnected: boolean;
  workflowStatus: 'idle' | 'connecting' | 'running' | 'completed' | 'error';
}

export function useOrchestration(eventId: string | null) {
  const [state, setState] = useState<OrchestrationState>({
    agentUpdates: [],
    currentAgent: null,
    completedAgents: [],
    errors: {},
    isConnected: false,
    workflowStatus: 'idle',
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  const connect = useCallback(() => {
    if (!eventId) return;

    const wsUrl = `ws://localhost:9000/ws/orchestration/${eventId}`;
    console.log('🔌 Connecting to WebSocket:', wsUrl);

    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('✅ WebSocket connected');
      setState((prev) => ({
        ...prev,
        isConnected: true,
        workflowStatus: 'running',
      }));

      // Send heartbeat every 30 seconds
      const heartbeat = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }));
        }
      }, 30000);

      ws.addEventListener('close', () => clearInterval(heartbeat));
    };

    ws.onmessage = (event) => {
      try {
        const update: AgentUpdate = JSON.parse(event.data);
        console.log('📨 Received update:', update);

        setState((prev) => {
          const newState = { ...prev };

          if (update.type === 'agent_update') {
            // Add to updates list
            newState.agentUpdates = [...prev.agentUpdates, update];

            // Update current agent
            if (update.status === 'running') {
              newState.currentAgent = update.agent || null;
            }

            // Track completed agents
            if (update.status === 'completed' && update.agent) {
              if (!prev.completedAgents.includes(update.agent)) {
                newState.completedAgents = [...prev.completedAgents, update.agent];
              }
              // Check if all agents completed
              if (update.agent === 'planner_agent') {
                newState.workflowStatus = 'completed';
              }
            }

            // Track errors
            if (update.status === 'error' && update.agent && update.error) {
              newState.errors = {
                ...prev.errors,
                [update.agent]: update.error,
              };
              newState.workflowStatus = 'error';
            }
          }

          return newState;
        });
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      setState((prev) => ({
        ...prev,
        isConnected: false,
        workflowStatus: 'error',
      }));
    };

    ws.onclose = () => {
      console.log('🔌 WebSocket disconnected');
      setState((prev) => ({
        ...prev,
        isConnected: false,
      }));

      // Attempt reconnect after 3 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        console.log('🔄 Attempting reconnect...');
        connect();
      }, 3000);
    };

    wsRef.current = ws;
  }, [eventId]);

  useEffect(() => {
    if (eventId) {
      connect();
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [eventId, connect]);

  const requestStatus = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'status' }));
    }
  }, []);

  const getAgentResult = useCallback((agentName: string) => {
    const update = state.agentUpdates
      .filter((u) => u.agent === agentName && u.status === 'completed')
      .pop();
    return update?.result || null;
  }, [state.agentUpdates]);

  return {
    ...state,
    requestStatus,
    getAgentResult,
  };
}
