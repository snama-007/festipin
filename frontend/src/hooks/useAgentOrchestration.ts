/**
 * Frontend Integration for Agent Orchestration
 *
 * This module provides React hooks and components for integrating
 * the agent orchestration system with the frontend.
 */

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Types
interface AgentStatus {
  agent_name: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  progress: number;
  result?: any;
  error?: string;
  execution_time?: number;
}

interface WorkflowStatus {
  event_id: string;
  workflow_status: string;
  agent_results: Record<string, AgentStatus>;
  final_plan?: any;
  created_at: string;
  updated_at: string;
}

interface OrchestrationInput {
  source_type: 'image' | 'url' | 'text';
  content: string;
  tags: string[];
  metadata?: Record<string, any>;
}

// API Service
class OrchestrationAPI {
  private baseUrl: string;

  constructor(baseUrl: string = '/api/v1') {
    this.baseUrl = baseUrl;
  }

  async startOrchestration(inputs: OrchestrationInput[], metadata?: Record<string, any>) {
    const response = await fetch(`${this.baseUrl}/orchestration/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ inputs, metadata }),
    });

    if (!response.ok) {
      throw new Error(`Failed to start orchestration: ${response.statusText}`);
    }

    return response.json();
  }

  async getWorkflowStatus(eventId: string): Promise<WorkflowStatus> {
    const response = await fetch(`${this.baseUrl}/orchestration/status/${eventId}`);

    if (!response.ok) {
      throw new Error(`Failed to get workflow status: ${response.statusText}`);
    }

    return response.json();
  }

  async addUserFeedback(eventId: string, feedback: Record<string, any>) {
    const response = await fetch(`${this.baseUrl}/orchestration/feedback/${eventId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ feedback }),
    });

    if (!response.ok) {
      throw new Error(`Failed to add feedback: ${response.statusText}`);
    }

    return response.json();
  }

  async getMemoryStats() {
    const response = await fetch(`${this.baseUrl}/orchestration/stats`);

    if (!response.ok) {
      throw new Error(`Failed to get memory stats: ${response.statusText}`);
    }

    return response.json();
  }
}

// React Hook for Agent Orchestration
export const useAgentOrchestration = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentEventId, setCurrentEventId] = useState<string | null>(null);
  const [workflowStatus, setWorkflowStatus] = useState<WorkflowStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [api] = useState(() => new OrchestrationAPI());

  const startOrchestration = useCallback(async (
    inputs: OrchestrationInput[], 
    metadata?: Record<string, any>
  ) => {
    try {
      setIsProcessing(true);
      setError(null);
      setWorkflowStatus(null);

      const response = await api.startOrchestration(inputs, metadata);
      setCurrentEventId(response.event_id);

      // Start polling for status updates
      pollWorkflowStatus(response.event_id);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start orchestration');
      setIsProcessing(false);
    }
  }, [api]);

  const pollWorkflowStatus = useCallback(async (eventId: string) => {
    try {
      const status = await api.getWorkflowStatus(eventId);
      setWorkflowStatus(status);

      // Continue polling if workflow is still running
      if (status.workflow_status === 'running') {
        setTimeout(() => pollWorkflowStatus(eventId), 2000); // Poll every 2 seconds
      } else {
        setIsProcessing(false);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get workflow status');
      setIsProcessing(false);
    }
  }, [api]);

  const addFeedback = useCallback(async (feedback: Record<string, any>) => {
    if (!currentEventId) return;

    try {
      await api.addUserFeedback(currentEventId, feedback);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add feedback');
    }
  }, [api, currentEventId]);

  const reset = useCallback(() => {
    setIsProcessing(false);
    setCurrentEventId(null);
    setWorkflowStatus(null);
    setError(null);
  }, []);

  return {
    isProcessing,
    currentEventId,
    workflowStatus,
    error,
    startOrchestration,
    addFeedback,
    reset,
  };
};

export default { useAgentOrchestration };
