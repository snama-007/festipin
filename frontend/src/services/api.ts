// API Service for Festimo Backend Integration

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9000'

export interface VisionAnalysisResponse {
  scene_data: {
    occasion_type: string
    theme: string
    color_palette: string[]
    objects: Array<{
      name: string
      category: string
      confidence: number
    }>
    mood: string
    layout: {
      style: string
      arrangement: string
      background: string
    }
  }
  image_url: string
  processing_time: number
}

export interface PlanGenerationResponse {
  plan: {
    title: string
    description: string
    theme: string
    budget_estimate: string
    checklist: Array<{
      category: string
      items: string[]
      priority: string
    }>
    vendor_suggestions: Array<{
      type: string
      description: string
      estimated_cost: string
    }>
    timeline: Array<{
      phase: string
      tasks: string[]
      duration: string
    }>
  }
}

export interface ExtractedEventData {
  eventType?: string
  title?: string
  hostName?: string
  honoreeName?: string
  age?: number
  gender?: string
  theme?: string
  date?: string
  time?: { start: string; end: string }
  guestCount?: { adults: number; kids: number }
  location?: {
    type: string
    name: string
    address: string
  }
  budget?: {
    min: number
    max: number
  }
  foodPreference?: string
  activities?: string[]
  rsvpDeadline?: string
  contactInfo?: string
}

export interface ExtractionResponse {
  extracted_data: ExtractedEventData
  confidence: number
  missing_fields: string[]
  suggestions: string[]
  friendly_message: string
  needs_user_input: boolean
  error?: string
}

export interface ValidationResponse {
  is_party_related: boolean
  confidence: number
  suggestions: string[]
}

// ===== AGENT ORCHESTRATION API =====

export interface OrchestrationInput {
  source_type: 'image' | 'url' | 'text'
  content: string
  tags: string[]
  metadata?: Record<string, any>
}

export interface AgentStatus {
  agent_name: string
  status: 'pending' | 'running' | 'completed' | 'error'
  progress: number
  result?: any
  error?: string
  execution_time?: number
}

export interface WorkflowStatus {
  event_id: string
  workflow_status: string
  agent_results: Record<string, AgentStatus>
  final_plan?: any
  created_at: string
  updated_at: string
}

export interface OrchestrationResponse {
  success: boolean
  event_id: string
  message: string
}

/**
 * Upload and analyze image file
 */
export async function uploadAndAnalyzeImage(file: File): Promise<VisionAnalysisResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_URL}/api/v1/vision/upload`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to analyze image')
  }

  return response.json()
}

/**
 * Extract structured event data from text and image description
 */
export async function extractEventData(
  inputText: string,
  imageDescription?: string
): Promise<ExtractionResponse> {
  const response = await fetch(`${API_URL}/api/v1/extraction/extract`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      input_text: inputText,
      image_description: imageDescription,
    }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to extract event data')
  }

  return response.json()
}

/**
 * Validate if content is party-related
 */
export async function validatePartyContent(
  inputText: string,
  imageDescription?: string
): Promise<ValidationResponse> {
  const response = await fetch(`${API_URL}/api/v1/extraction/validate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      input_text: inputText,
      image_description: imageDescription,
    }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to validate content')
  }

  return response.json()
}

/**
 * Generate party plan from vision analysis and user prompt
 */
export async function generatePlan(
  sceneData: any,
  eventDetails: {
    event_type?: string
    guest_count?: number
    budget_range?: string
    location?: string
    date?: string
    special_requirements?: string
  }
): Promise<PlanGenerationResponse> {
  const response = await fetch(`${API_URL}/api/v1/plan/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      scene_data: sceneData,
      event_details: eventDetails,
    }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to generate plan')
  }

  return response.json()
}

/**
 * Process chat message with AI
 */
export async function processChatMessage(message: string): Promise<any> {
  const response = await fetch(`${API_URL}/api/v1/chat/process`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to process message')
  }

  return response.json()
}

/**
 * Get sample images
 */
export async function getSampleImages(): Promise<string[]> {
  const response = await fetch(`${API_URL}/api/v1/samples`)

  if (!response.ok) {
    throw new Error('Failed to fetch sample images')
  }

  const data = await response.json()
  return data.samples
}

/**
 * Health check
 */
export async function healthCheck(): Promise<{ status: string }> {
  const response = await fetch(`${API_URL}/health`)
  return response.json()
}

/**
 * Start agent orchestration workflow
 */
export async function startOrchestration(
  inputs: OrchestrationInput[], 
  metadata?: Record<string, any>
): Promise<OrchestrationResponse> {
  const response = await fetch(`${API_URL}/api/v1/orchestration/start`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ inputs, metadata }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to start orchestration')
  }

  return response.json()
}

/**
 * Get workflow status
 */
export async function getWorkflowStatus(eventId: string): Promise<WorkflowStatus> {
  const response = await fetch(`${API_URL}/api/v1/orchestration/status/${eventId}`)

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to get workflow status')
  }

  return response.json()
}

/**
 * Add user feedback to workflow
 */
export async function addUserFeedback(
  eventId: string, 
  feedback: Record<string, any>
): Promise<{ success: boolean; message: string }> {
  const response = await fetch(`${API_URL}/api/v1/orchestration/feedback/${eventId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ feedback }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to add feedback')
  }

  return response.json()
}

/**
 * Get memory store statistics
 */
export async function getMemoryStats(): Promise<{ success: boolean; stats: any }> {
  const response = await fetch(`${API_URL}/api/v1/orchestration/stats`)

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to get memory stats')
  }

  return response.json()
}

/**
 * List active events
 */
export async function listActiveEvents(): Promise<{ success: boolean; events: any[]; count: number }> {
  const response = await fetch(`${API_URL}/api/v1/orchestration/events`)

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Failed to list events')
  }

  return response.json()
}