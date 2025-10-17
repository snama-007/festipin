/**
 * Agent Progress Component
 *
 * Shows real-time progress of all agents in the orchestration workflow
 */

import React from 'react';
import { useOrchestration } from '@/hooks/useOrchestration';

interface AgentProgressProps {
  eventId: string;
}

const AGENT_DISPLAY_NAMES: Record<string, string> = {
  input_classifier: 'Input Analysis',
  theme_agent: 'Theme Detection',
  cake_agent: 'Cake Recommendations',
  venue_agent: 'Venue Search',
  catering_agent: 'Catering Options',
  budget_agent: 'Budget Calculation',
  vendor_agent: 'Vendor Recommendations',
  planner_agent: 'Final Plan Assembly',
};

const AGENT_EMOJIS: Record<string, string> = {
  input_classifier: '📋',
  theme_agent: '🎨',
  cake_agent: '🎂',
  venue_agent: '📍',
  catering_agent: '🍽️',
  budget_agent: '💰',
  vendor_agent: '🏪',
  planner_agent: '📅',
};

export function AgentProgress({ eventId }: AgentProgressProps) {
  const { agentUpdates, completedAgents, currentAgent, isConnected, workflowStatus, errors } = useOrchestration(eventId);

  const getAgentStatus = (agentName: string): 'pending' | 'running' | 'completed' | 'error' => {
    if (errors[agentName]) return 'error';
    if (completedAgents.includes(agentName)) return 'completed';
    if (currentAgent === agentName) return 'running';
    return 'pending';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return '✅';
      case 'running':
        return '⏳';
      case 'error':
        return '❌';
      default:
        return '⏸️';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'running':
        return 'text-blue-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-gray-400';
    }
  };

  const agents = Object.keys(AGENT_DISPLAY_NAMES);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Party Planning Progress</h2>
        <div className="flex items-center gap-2">
          {isConnected ? (
            <span className="flex items-center text-green-600">
              <span className="w-2 h-2 bg-green-600 rounded-full mr-2 animate-pulse"></span>
              Live
            </span>
          ) : (
            <span className="flex items-center text-gray-400">
              <span className="w-2 h-2 bg-gray-400 rounded-full mr-2"></span>
              Offline
            </span>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Overall Progress</span>
          <span>{completedAgents.length} / {agents.length} agents completed</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-500"
            style={{ width: `${(completedAgents.length / agents.length) * 100}%` }}
          ></div>
        </div>
      </div>

      {/* Agent List */}
      <div className="space-y-3">
        {agents.map((agentName) => {
          const status = getAgentStatus(agentName);
          const displayName = AGENT_DISPLAY_NAMES[agentName];
          const emoji = AGENT_EMOJIS[agentName];
          const statusIcon = getStatusIcon(status);
          const statusColor = getStatusColor(status);

          // Get latest message for this agent
          const latestUpdate = agentUpdates
            .filter((u) => u.agent === agentName)
            .pop();

          return (
            <div
              key={agentName}
              className={`p-4 rounded-lg border-2 transition-all ${
                status === 'running'
                  ? 'border-blue-500 bg-blue-50'
                  : status === 'completed'
                  ? 'border-green-500 bg-green-50'
                  : status === 'error'
                  ? 'border-red-500 bg-red-50'
                  : 'border-gray-200 bg-gray-50'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{emoji}</span>
                  <div>
                    <h3 className="font-semibold">{displayName}</h3>
                    {latestUpdate?.message && (
                      <p className="text-sm text-gray-600">{latestUpdate.message}</p>
                    )}
                    {errors[agentName] && (
                      <p className="text-sm text-red-600">{errors[agentName]}</p>
                    )}
                  </div>
                </div>
                <span className={`text-2xl ${statusColor}`}>{statusIcon}</span>
              </div>

              {status === 'running' && (
                <div className="mt-2">
                  <div className="w-full bg-gray-200 rounded-full h-1">
                    <div className="bg-blue-600 h-1 rounded-full animate-pulse w-full"></div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Workflow Status */}
      <div className="mt-6 text-center">
        {workflowStatus === 'completed' && (
          <div className="bg-green-100 border border-green-500 text-green-700 px-4 py-3 rounded">
            🎉 Planning complete! Check your recommendations below.
          </div>
        )}
        {workflowStatus === 'error' && (
          <div className="bg-red-100 border border-red-500 text-red-700 px-4 py-3 rounded">
            ❌ Some agents encountered errors. Please review and try again.
          </div>
        )}
      </div>
    </div>
  );
}
