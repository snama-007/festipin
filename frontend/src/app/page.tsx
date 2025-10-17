'use client'

import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence, useMotionValue, useSpring } from 'framer-motion'
import Image from 'next/image'
import { useRouter } from 'next/navigation'
import { uploadAndAnalyzeImage, generatePlan } from '@/services/api'
import type { VisionAnalysisResponse } from '@/services/api'
import { useAgentOrchestration } from '@/components/AgentOrchestration'
import type { OrchestrationInput } from '@/services/api'
import { extractEventData, validatePartyContent, ExtractedEventData, ExtractionResponse, ValidationResponse } from '../services/api'
import { DataInputForm } from '../components/DataInputForm'
import { ConversationalDialog } from '../components/ConversationalDialog'
import { generatePartyId } from '@/lib/partyId'

const partyTags = [
  "🎉 BalloonVendor",
  "🍰 CakeArtist",
  "📸 PhotoBooth",
  "🪩 DJ",
  "👗 DressThemes"
]

const floatingImages = [
  { src: "https://images.unsplash.com/photo-1530103862676-de8c9debad1d?w=400&h=400&fit=crop", top: "15%", left: "8%" },
  { src: "https://images.unsplash.com/photo-1464047736614-af63643285bf?w=400&h=400&fit=crop", top: "20%", right: "10%" },
  { src: "https://images.unsplash.com/photo-1505236858219-8359eb29e329?w=400&h=400&fit=crop", bottom: "20%", left: "12%" },
  { src: "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=400&h=400&fit=crop", bottom: "25%", right: "8%" },
  { src: "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?w=400&h=400&fit=crop", top: "50%", left: "5%" },
  { src: "https://images.unsplash.com/photo-1478146896981-b80fe463b330?w=400&h=400&fit=crop", top: "55%", right: "5%" }
]

// Agent log types for color coding
type LogType = 'user_input' | 'agent_info' | 'agent_success' | 'agent_warning' | 'agent_error' | 'system_info'

interface AgentLog {
  id: string
  type: LogType
  message: string
  timestamp: Date
  agent?: string
  data?: any
}

// Plan building components
interface PlanComponent {
  id: string
  type: 'theme' | 'venue' | 'cake' | 'decorations' | 'catering' | 'entertainment' | 'timeline'
  title: string
  data: any
  position: { x: number, y: number }
  isComplete: boolean
}

export default function PartyPlanOS() {
  const router = useRouter()
  // Generate unique ID
  const generateUniqueId = () => {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}-${performance.now().toString(36)}`
  }
  const [mode, setMode] = useState<'search' | 'build'>('search')
  const [tab, setTab] = useState("url")
  const [showPage, setShowPage] = useState(false)
  const [ripples, setRipples] = useState<{ x: number; y: number; id: string }[]>([])
  const cardRef = useRef<HTMLDivElement>(null)
  const urlInputRef = useRef<HTMLInputElement>(null)
  const promptTextareaRef = useRef<HTMLTextAreaElement>(null)
  
  // Focus input when tab changes
  useEffect(() => {
    const timer = setTimeout(() => {
      if (tab === 'url' && urlInputRef.current) {
        urlInputRef.current.focus()
      } else if (tab === 'prompt' && promptTextareaRef.current) {
        promptTextareaRef.current.focus()
      }
    }, 100) // Reduced delay for faster focus
    
    return () => clearTimeout(timer)
  }, [tab])
  
  // Data extraction states
  const [validationResult, setValidationResult] = useState<ValidationResponse | null>(null)
  const [extractionResult, setExtractionResult] = useState<ExtractionResponse | null>(null)
  const [showConversationalDialog, setShowConversationalDialog] = useState(false)
  const [showDataInput, setShowDataInput] = useState(false)
  const [extractedEventData, setExtractedEventData] = useState<ExtractedEventData>({})
  
  // Progress feedback states
  const [progressStep, setProgressStep] = useState<string>('')
  const [progressMessage, setProgressMessage] = useState<string>('')
  
  // Form state
  const [pinterestUrl, setPinterestUrl] = useState('')
  const [chatMessage, setChatMessage] = useState('Create a magical unicorn-themed birthday party for a 5-year-old with rainbow decorations, unicorn cake, and pony rides')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  
  // Location state
  const [location, setLocation] = useState('')
  const [isLocationValid, setIsLocationValid] = useState(false)
  const [isFetchingLocation, setIsFetchingLocation] = useState(false)
  const [locationError, setLocationError] = useState('')
  
  // API state
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const errorTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const [analysisResult, setAnalysisResult] = useState<VisionAnalysisResponse | null>(null)
  const [generatedPlan, setGeneratedPlan] = useState<any | null>(null)
  const [hoveredChip, setHoveredChip] = useState<string | null>(null)
  
  // Agent orchestration
  const {
    isProcessing: isAgentProcessing,
    currentEventId,
    workflowStatus,
    error: agentError,
    startOrchestrationWorkflow,
    addFeedback,
    reset: resetOrchestration
  } = useAgentOrchestration()
  
  // Build mode state
  const [agentLogs, setAgentLogs] = useState<AgentLog[]>([])
  const [planComponents, setPlanComponents] = useState<PlanComponent[]>([])
  const [chatInput, setChatInput] = useState('')
  const [isTransitioning, setIsTransitioning] = useState(false)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  
  
  // Voice input state
  const [isListening, setIsListening] = useState(false)
  const [isSupported, setIsSupported] = useState(true)
  const [recognition, setRecognition] = useState<any>(null)
  const [interimTranscript, setInterimTranscript] = useState('')
  const [isRecognitionReady, setIsRecognitionReady] = useState(false)
  const interimTextRef = useRef<HTMLSpanElement>(null)
  
  // Location validation (zip code or city name)
  const validateLocation = (loc: string) => {
    if (!loc.trim()) return false
    
    // US zip code: 5 digits or 5+4 format
    const usZipRegex = /^\d{5}(-\d{4})?$/
    if (usZipRegex.test(loc.trim())) return true
    
    // City name: at least 2 characters, letters and spaces
    const cityRegex = /^[a-zA-Z\s]{2,}$/
    if (cityRegex.test(loc.trim())) return true
    
    // City, State format
    const cityStateRegex = /^[a-zA-Z\s]+,\s*[a-zA-Z\s]+$/
    if (cityStateRegex.test(loc.trim())) return true
    
    return false
  }
  
  // Handle location change
  const handleLocationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setLocation(value)
    setIsLocationValid(validateLocation(value))
    setLocationError('')
  }
  
  // Fetch location from browser
  const fetchBrowserLocation = async () => {
    if (!navigator.geolocation) {
      setLocationError('Geolocation is not supported by your browser')
      return
    }
    
    setIsFetchingLocation(true)
    setLocationError('')
    
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const { latitude, longitude } = position.coords
          
          // Reverse geocoding using OpenStreetMap Nominatim API (free)
          const response = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=10&addressdetails=1`,
            {
              headers: {
                'User-Agent': 'Festimo Party Planning App'
              }
            }
          )
          
          if (!response.ok) throw new Error('Failed to fetch location')
          
          const data = await response.json()
          const address = data.address
          
          // Extract city and state/zip
          const city = address.city || address.town || address.village || address.county
          const state = address.state
          const zipCode = address.postcode
          
          let locationString = ''
          if (zipCode) {
            locationString = zipCode
          } else if (city && state) {
            locationString = `${city}, ${state}`
          } else if (city) {
            locationString = city
          }
          
          if (locationString) {
            setLocation(locationString)
            setIsLocationValid(true)
          } else {
            setLocationError('Could not determine your location')
          }
        } catch (error) {
          console.error('Error fetching location:', error)
          setLocationError('Failed to fetch location details')
        } finally {
          setIsFetchingLocation(false)
        }
      },
      (error) => {
        console.error('Geolocation error:', error)
        setIsFetchingLocation(false)
        
        switch (error.code) {
          case error.PERMISSION_DENIED:
            setLocationError('Location permission denied')
            break
          case error.POSITION_UNAVAILABLE:
            setLocationError('Location information unavailable')
            break
          case error.TIMEOUT:
            setLocationError('Location request timed out')
            break
          default:
            setLocationError('An unknown error occurred')
        }
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    )
  }
  
  // Real-time URL validation
  const validateUrl = (url: string) => {
    if (!url.trim()) return { isValid: false, canType: true, isInvalid: false }
    
    const urlLower = url.trim().toLowerCase()
    const supportedDomains = [
      'pinterest.com', 'pin.it', 
      'tiktok.com', 'vm.tiktok.com', 'vt.tiktok.com',
      'lemon8.com', 
      'instagram.com', 'instagr.am'
    ]
    
    const hasDot = urlLower.includes('.')
    
    if (hasDot) {
      const parts = urlLower.split('.')
      if (parts.length >= 2) {
        const domainPart = parts.slice(-2).join('.')
        const isSupportedDomain = supportedDomains.some(domain => domainPart === domain || domainPart.includes(domain))
        
        if (isSupportedDomain) {
          return { isValid: true, canType: true, isInvalid: false }
        } else {
          return { isValid: false, canType: true, isInvalid: true }
        }
      }
    }
    
    return { isValid: false, canType: true, isInvalid: false }
  }

  const urlValidation = validateUrl(pinterestUrl)

  // Set error with auto-dismissal
  const setErrorWithAutoDismiss = (errorMessage: string, duration: number = 4000) => {
    setError(errorMessage)
    
    if (errorTimeoutRef.current) {
      clearTimeout(errorTimeoutRef.current)
    }
    
    errorTimeoutRef.current = setTimeout(() => {
      setError(null)
    }, duration)
  }

  // Handle URL input with validation
  const handleUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value
    setPinterestUrl(newValue)
  }

  useEffect(() => {
    const timeout = setTimeout(() => setShowPage(true), 300)
    
    // Auto-fetch location on page load if user has granted permission
    const autoFetchLocation = async () => {
      if (navigator.geolocation && !location) {
        // Check if we have permission to access location
        try {
          const permission = await navigator.permissions.query({ name: 'geolocation' as PermissionName })
          if (permission.state === 'granted') {
            // User has already granted permission, fetch location automatically
            setTimeout(() => {
              fetchBrowserLocation()
            }, 1000) // Small delay to let the page load
          }
        } catch (error) {
          // Permission API not supported, try to fetch anyway
          setTimeout(() => {
            fetchBrowserLocation()
          }, 1000)
        }
      }
    }
    
    autoFetchLocation()
    
    return () => clearTimeout(timeout)
  }, [])

  // Cleanup error timeout on unmount
  useEffect(() => {
    return () => {
      if (errorTimeoutRef.current) {
        clearTimeout(errorTimeoutRef.current)
      }
    }
  }, [])

  // Initialize voice recognition
  useEffect(() => {
    if (typeof window !== 'undefined') {
      console.log('Initializing voice recognition...')
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
      console.log('SpeechRecognition available:', !!SpeechRecognition)
      
      if (SpeechRecognition) {
        try {
          const recognitionInstance = new SpeechRecognition()
          recognitionInstance.continuous = false
          recognitionInstance.interimResults = true
          recognitionInstance.lang = 'en-US'
          
          recognitionInstance.onstart = () => {
            console.log('Voice recognition started')
            setIsListening(true)
            setIsRecognitionReady(false)
          }
          
        recognitionInstance.onresult = (event: any) => {
          let interimTranscript = ''
          let finalTranscript = ''
          
          for (let i = 0; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript
            if (event.results[i].isFinal) {
              finalTranscript += transcript
            } else {
              interimTranscript += transcript
            }
          }
          
          if (interimTranscript) {
            setInterimTranscript(interimTranscript)
            
            if (interimTextRef.current) {
              interimTextRef.current.textContent = interimTranscript
            }
            
            console.log('Interim transcript (instant):', interimTranscript)
          }
          
          if (finalTranscript) {
            console.log('Final transcript:', finalTranscript)
            setChatMessage(finalTranscript)
            setInterimTranscript('')
            setIsListening(false)
            setTimeout(() => {
              setIsRecognitionReady(true)
              console.log('Recognition ready for next use')
            }, 500)
            console.log('Voice input completed, ready for manual submission')
          }
        }
          
          recognitionInstance.onerror = (event: any) => {
            console.error('Speech recognition error:', event.error)
            setIsListening(false)
            setInterimTranscript('')
            setTimeout(() => {
              setIsRecognitionReady(true)
              console.log('Recognition ready after error')
            }, 1000)
          }
          
          recognitionInstance.onend = () => {
            console.log('Voice recognition ended')
            setIsListening(false)
            setInterimTranscript('')
            setTimeout(() => {
              setIsRecognitionReady(true)
              console.log('Recognition ready after end')
            }, 500)
          }
          
          setRecognition(recognitionInstance)
          setIsSupported(true)
          setIsRecognitionReady(true)
          console.log('Voice recognition initialized successfully')
        } catch (error) {
          console.error('Error initializing voice recognition:', error)
          setIsSupported(false)
        }
      } else {
        console.log('Speech recognition not supported')
        setIsSupported(false)
      }
    }
    
    return () => {
      if (recognition) {
        recognition.stop()
      }
    }
  }, [])

  const createRipple = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return
    const rect = cardRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    const id = generateUniqueId()
    setRipples(prev => [...prev, { x, y, id }])
    setTimeout(() => {
      setRipples(prev => prev.filter(ripple => ripple.id !== id))
    }, 1000)
  }

  // Voice input handlers
  const startListening = () => {
    if (recognition && !isListening && isRecognitionReady) {
      console.log('Starting voice recognition...')
      setInterimTranscript('')
      setIsRecognitionReady(false)
      try {
        recognition.start()
      } catch (error) {
        console.error('Error starting recognition:', error)
        setIsRecognitionReady(true)
      }
    }
  }

  const stopListening = () => {
    if (recognition && isListening) {
      console.log('Stopping voice recognition...')
      try {
        recognition.stop()
      } catch (error) {
        console.error('Error stopping recognition:', error)
        setIsRecognitionReady(true)
      }
    }
  }

  // Add agent log
  const addAgentLog = (type: LogType, message: string, agent?: string, data?: any) => {
    const log: AgentLog = {
      id: generateUniqueId(),
      type,
      message,
      timestamp: new Date(),
      agent,
      data
    }
    setAgentLogs(prev => [...prev, log])
  }

  // Transition to build mode
  const transitionToBuildMode = async () => {
    setIsTransitioning(true)
    
    // Clear any existing logs before transition
    setAgentLogs([])
    
    // Clear search mode hover states
    setHoveredChip(null)
    
    // Add initial logs before sending request
    addAgentLog('system_info', '🎉 Starting party plan generation...')
    addAgentLog('user_input', `User request: ${pinterestUrl || chatMessage}`, undefined, {
      type: tab,
      hasImage: !!selectedFile
    })
    
    try {
      // Create orchestration inputs based on party data
      const inputs: OrchestrationInput[] = [
        {
          source_type: tab === 'url' ? 'url' : 'text',
          content: pinterestUrl || chatMessage,
          tags: [
            'party_planning',
            extractedEventData?.eventType || 'general',
            extractedEventData?.theme || 'unknown'
          ],
          metadata: {
            extracted_data: extractedEventData,
            validation_result: validationResult,
            extraction_result: extractionResult,
            has_image: !!selectedFile,
            timestamp: new Date().toISOString()
          }
        }
      ]

      const metadata = {
        user_agent: navigator.userAgent,
        timestamp: new Date().toISOString(),
        source_data: {
          extractedEventData,
          validationResult,
          extractionResult,
          pinterestUrl,
          chatMessage,
          selectedFile: selectedFile ? {
            name: selectedFile.name,
            size: selectedFile.size,
            type: selectedFile.type
          } : null,
          tab
        }
      }

      console.log('📤 Sending orchestration request to backend...')
      
      // Start orchestration and get party ID from backend
      const response = await startOrchestrationWorkflow(inputs, metadata)
      const partyId = response.event_id
      
      if (!partyId) {
        throw new Error('Failed to get party ID from backend')
      }
      
      console.log('✅ Received party ID from backend:', partyId)
      
      // Store extracted data in localStorage for the build page
      const partyData = {
        partyId,
        extractedEventData,
        validationResult,
        extractionResult,
        pinterestUrl,
        chatMessage,
        selectedFile: selectedFile ? {
          name: selectedFile.name,
          size: selectedFile.size,
          type: selectedFile.type
        } : null,
        tab,
        timestamp: new Date().toISOString()
      }
      
      localStorage.setItem(`party_${partyId}`, JSON.stringify(partyData))
      
      // Navigate to build page with backend-generated party ID
      router.push(`/build/${partyId}`)
      
    } catch (error) {
      console.error('❌ Failed to start orchestration:', error)
      setError('Failed to start party planning. Please try again.')
      setIsTransitioning(false)
    }
  }

  // Clear search state when exiting build mode
  const clearSearchState = () => {
    setPinterestUrl('')
    setChatMessage('')
    setSelectedFile(null)
    setImagePreview(null)
    setError(null)
    setHoveredChip(null)
    setAgentLogs([])
  }

  // Start orchestration
  const startOrchestration = async () => {
    addAgentLog('system_info', '🤖 Initializing agent orchestration...')
    
    try {
      const inputs: OrchestrationInput[] = []
      
      if (tab === 'url' && pinterestUrl.trim()) {
        inputs.push({
          source_type: 'url',
          content: pinterestUrl,
          tags: ['pinterest', 'url', 'party', 'inspiration'],
          metadata: {
            original_url: pinterestUrl,
            platform: 'pinterest'
          }
        })
      } else if (tab === 'prompt') {
        if (chatMessage.trim()) {
          inputs.push({
            source_type: 'text',
            content: chatMessage,
            tags: ['prompt', 'text', 'description'],
            metadata: {
              original_prompt: chatMessage,
              timestamp: new Date().toISOString()
            }
          })
        }
        
        if (selectedFile) {
          inputs.push({
            source_type: 'image',
            content: selectedFile.name,
            tags: ['image', 'upload', 'visual'],
            metadata: {
              file_name: selectedFile.name,
              file_size: selectedFile.size,
              file_type: selectedFile.type,
              timestamp: new Date().toISOString()
            }
          })
        }
      }

      if (inputs.length === 0) {
        addAgentLog('agent_error', 'No valid inputs provided')
        return
      }

      addAgentLog('agent_info', `Processing ${inputs.length} input(s)...`)
      
      await startOrchestrationWorkflow(inputs, {
        event_type: 'party',
        source: tab,
        timestamp: new Date().toISOString()
      })

    } catch (err: any) {
      addAgentLog('agent_error', `Orchestration failed: ${err.message}`)
      setErrorWithAutoDismiss(err.message || 'Failed to start orchestration')
    }
  }

  // Handle URL submission
  const handleUrlSubmit = async () => {
    if (!pinterestUrl.trim()) {
      setErrorWithAutoDismiss('Please enter a URL from Pinterest, TikTok, Lemon8, or Instagram')
      return
    }

    const url = pinterestUrl.trim().toLowerCase()
    const supportedDomains = [
      'pinterest.com', 'pin.it', 
      'tiktok.com', 'vm.tiktok.com', 'vt.tiktok.com',
      'lemon8.com', 
      'instagram.com', 'instagr.am'
    ]
    
    const isValidUrl = supportedDomains.some(domain => url.includes(domain))
    
    if (!isValidUrl) {
      setErrorWithAutoDismiss('❌ Invalid URL! Please enter a valid URL from Pinterest, TikTok, Lemon8, or Instagram')
      return
    }

    try {
      new URL(url.startsWith('http') ? url : `https://${url}`)
    } catch {
      setErrorWithAutoDismiss('❌ Invalid URL format! Please enter a complete URL')
      return
    }

    setLoading(true)
    setError(null)
    resetOrchestration()
    
    await transitionToBuildMode()
      setLoading(false)
  }

  // Handle file upload
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!file.type.startsWith('image/') || (!file.type.includes('png') && !file.type.includes('jpeg') && !file.type.includes('jpg'))) {
      setErrorWithAutoDismiss('Please upload a PNG or JPG image file')
      return
    }

    setSelectedFile(file)
    setError(null)
    
    // Create image preview
    const reader = new FileReader()
    reader.onload = (e) => {
      setImagePreview(e.target?.result as string)
    }
    reader.readAsDataURL(file)
  }

  // Handle prompt submission
  const handlePromptSubmit = async () => {
    if (!selectedFile && !chatMessage.trim()) {
      setErrorWithAutoDismiss('Please upload an image, add a description, or both')
      return
    }

    setLoading(true)
    setError(null)
    resetOrchestration()

    await transitionToBuildMode()
      setLoading(false)
  }

  // Unified submission handler with validation
  const handleGeneratePlan = async () => {
    setError(null)
    setLoading(true)
    setProgressStep('')
    setProgressMessage('')
    
    try {
      let validationResult: ValidationResponse
      let extractionResult: ExtractionResponse
      
      // Step 1: Analyzing input
      setProgressStep('analyzing')
      setProgressMessage('🔍 Analyzing your input...')
      await new Promise(resolve => setTimeout(resolve, 800))
      
      if (tab === 'url') {
        // Step 2: Validating URL content
        setProgressStep('validating')
        setProgressMessage('✅ Validating party content...')
        validationResult = await validatePartyContent(pinterestUrl)
        if (!validationResult.is_party_related) {
          setError(`This doesn't seem to be party-related content. ${validationResult.suggestions.join(' ')}`)
          setLoading(false)
      return
    }

        // Step 3: Extracting data from URL
        setProgressStep('extracting')
        setProgressMessage('📊 Extracting event details...')
        extractionResult = await extractEventData(pinterestUrl)
      } else {
        // Step 2: Validating prompt content
        setProgressStep('validating')
        setProgressMessage('✅ Validating party content...')
        
        let imageDescription = ''
      if (selectedFile) {
          setProgressStep('analyzing_image')
          setProgressMessage('🖼️ Analyzing uploaded image...')
          // Get image description from vision analysis
          const imageAnalysis = await uploadAndAnalyzeImage(selectedFile)
          imageDescription = `${imageAnalysis.scene_data.occasion_type} ${imageAnalysis.scene_data.theme} ${imageAnalysis.scene_data.mood} ${imageAnalysis.scene_data.objects.map(obj => obj.name).join(' ')}`
        }
        
        validationResult = await validatePartyContent(chatMessage, imageDescription)
        if (!validationResult.is_party_related) {
          setError(`This doesn't seem to be party-related content. ${validationResult.suggestions.join(' ')}`)
          setLoading(false)
          return
        }
        
        // Step 3: Extracting data from prompt/image
        setProgressStep('extracting')
        setProgressMessage('📊 Extracting event details...')
        extractionResult = await extractEventData(chatMessage, imageDescription)
      }
      
      setValidationResult(validationResult)
      setExtractionResult(extractionResult)
      setExtractedEventData(extractionResult.extracted_data)
      
      // Step 4: Checking if user input is needed
      setProgressStep('checking')
      setProgressMessage('🔍 Checking for missing details...')
      await new Promise(resolve => setTimeout(resolve, 500))
      
      if (extractionResult.needs_user_input) {
        setProgressStep('form_ready')
        setProgressMessage('📝 Ready to collect missing details')
        setShowConversationalDialog(true)
      setLoading(false)
        return
      }
      
      // Step 5: Ready to build
      setProgressStep('ready')
      setProgressMessage('🎉 Ready to build your party plan!')
      await new Promise(resolve => setTimeout(resolve, 300))
      
      // Proceed to build mode
      await transitionToBuildMode()
      
    } catch (error) {
      console.error('Error in handleGeneratePlan:', error)
      setError('Failed to process your request. Please try again.')
    } finally {
      setLoading(false)
      setProgressStep('')
      setProgressMessage('')
    }
  }

  // Conversational dialog handlers
  const handleAddDetails = () => {
    setShowConversationalDialog(false)
    setShowDataInput(true)
  }
  
  const handleBuildWithAgents = () => {
    setShowConversationalDialog(false)
    // Show data input form even for building with agents
    setShowDataInput(true)
  }
  
  const handleExitAndDelete = () => {
    setShowConversationalDialog(false)
    setExtractionResult(null)
    setExtractedEventData({})
    // Clear any stored event data
    console.log('Event deleted and cleared')
  }
  
  // Data input form handlers
  const handleDataComplete = async (completeData: ExtractedEventData) => {
    setExtractedEventData(completeData)
    setShowDataInput(false)
    
    // Proceed to build mode with complete data
    await transitionToBuildMode()
  }
  
  const handleDataSkip = () => {
    setShowDataInput(false)
    
    // Check if we have minimum required data to build a party plan
    const hasMinimumData = checkMinimumDataRequirements(extractedEventData)
    
    if (!hasMinimumData) {
      setError('Inadequate details to build a party plan. Please provide at least: Event Type, Theme, and Location.')
      return
    }
    
    // Proceed to build mode with partial data
    transitionToBuildMode()
  }
  
  const checkMinimumDataRequirements = (data: ExtractedEventData): boolean => {
    const requiredFields = ['eventType', 'theme', 'location']
    return requiredFields.some(field => data[field as keyof ExtractedEventData] != null)
  }

  // Check if button should be enabled
  const canSubmit = () => {
    if (loading) return false
    switch (tab) {
      case 'url':
        return urlValidation.isValid
      case 'prompt':
        return selectedFile !== null || chatMessage.trim().length > 0
      default:
        return false
    }
  }

  // Handle feedback submission
  const handleFeedback = async (feedback: Record<string, any>) => {
    try {
      await addFeedback(feedback)
      addAgentLog('user_input', `Feedback submitted: ${JSON.stringify(feedback)}`)
      console.log('Feedback submitted:', feedback)
    } catch (err) {
      console.error('Failed to submit feedback:', err)
    }
  }

  // Handle chat in build mode
  const handleBuildModeChat = async () => {
    if (!chatInput.trim()) return
    
    addAgentLog('user_input', chatInput)
    setChatInput('')
    
    // Here you would process the chat input and update the plan
    // For now, just add a system response
    setTimeout(() => {
      addAgentLog('agent_info', 'Processing your request...')
    }, 500)
  }


  // Infinite canvas handlers


  // Drag and drop handlers









  // Get log color based on type
  const getLogColor = (type: LogType) => {
    switch (type) {
      case 'user_input': return 'text-blue-600 bg-blue-50 border-blue-200'
      case 'agent_success': return 'text-green-600 bg-green-50 border-green-200'
      case 'agent_warning': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'agent_error': return 'text-red-600 bg-red-50 border-red-200'
      case 'agent_info': return 'text-purple-600 bg-purple-50 border-purple-200'
      case 'system_info': return 'text-gray-600 bg-gray-50 border-gray-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  // Get log icon based on type
  const getLogIcon = (type: LogType) => {
    switch (type) {
      case 'user_input': return '👤'
      case 'agent_success': return '✅'
      case 'agent_warning': return '⚠️'
      case 'agent_error': return '❌'
      case 'agent_info': return '🤖'
      case 'system_info': return '⚙️'
      default: return '📝'
    }
  }

  return (
    <>
      {/* Navigation Header */}
      <motion.nav
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        className="fixed top-0 left-0 right-0 z-[100] backdrop-blur-xl bg-white/70 border-b border-white/40 shadow-lg"
      >
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          {/* Logo */}
          <motion.div
            className="flex items-center gap-2 cursor-pointer"
            whileHover={{ scale: 1.05 }}
            transition={{ duration: 0.2 }}
            onClick={() => window.location.href = '/'}
          >
            <span className="text-2xl font-bold bg-gradient-to-r from-pink-500 to-purple-600 bg-clip-text text-transparent">
              Festimo
            </span>
          </motion.div>

          {/* Neon Button */}
          <motion.a
            href="/neon"
            className="relative overflow-hidden px-6 py-2.5 rounded-full font-bold text-white transition-all duration-300"
            style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              boxShadow: '0 0 20px rgba(102, 126, 234, 0.5), 0 0 40px rgba(118, 75, 162, 0.3)'
            }}
            whileHover={{ 
              scale: 1.05,
              boxShadow: '0 0 30px rgba(102, 126, 234, 0.8), 0 0 60px rgba(118, 75, 162, 0.5)'
            }}
            whileTap={{ scale: 0.95 }}
          >
            {/* Neon glow effect */}
            <motion.div
              className="absolute inset-0 rounded-full"
              style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                filter: 'blur(10px)',
                opacity: 0.6
              }}
              animate={{
                opacity: [0.6, 0.8, 0.6],
                scale: [1, 1.1, 1]
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            />
            
            {/* Animated shine */}
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
              initial={{ x: "-100%" }}
              animate={{ x: "200%" }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut"
              }}
            />
            
            <span className="relative z-10 flex items-center gap-2">
              <svg 
                width="18" 
                height="18" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2.5" 
                strokeLinecap="round" 
                strokeLinejoin="round"
              >
                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
              </svg>
              Neon
            </span>
          </motion.a>
        </div>
      </motion.nav>

      {/* Conversational Dialog */}
      {showConversationalDialog && extractionResult && (
        <ConversationalDialog
          extractionResult={extractionResult}
          onAddDetails={handleAddDetails}
          onBuildWithAgents={handleBuildWithAgents}
          onExit={handleExitAndDelete}
        />
      )}

      {/* Data Input Form */}
      {showDataInput && extractionResult && (
        <DataInputForm
          extractedData={extractedEventData}
          missingFields={extractionResult.missing_fields}
          suggestions={extractionResult.suggestions}
          onDataComplete={handleDataComplete}
          onSkip={handleDataSkip}
        />
      )}
      
    <AnimatePresence mode="wait">
      {showPage && (
        <motion.div
          key="page"
          className="relative min-h-screen overflow-hidden bg-gradient-to-br from-[#fef9ff] via-[#e5eaf5] to-[#d0e0f5] pt-20"
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 50 }}
          transition={{ duration: 0.8 }}
        >
          {/* Floating Party Images - Hidden in build mode */}
          <AnimatePresence>
            {mode === 'search' && !isTransitioning && (
              <div className="hidden lg:block">
                {floatingImages.map((img, idx) => (
                  <motion.div
                    key={`floating-${idx}-${img}`}
                    className="absolute w-28 h-28 xl:w-32 xl:h-32 rounded-2xl shadow-2xl overflow-hidden border-2 border-white/40"
                    initial={{ opacity: 0, scale: 0.8, y: 10 }}
                    animate={{ 
                      opacity: 0.9, 
                      scale: 1, 
                      y: [10, -5, 10] 
                    }}
                    exit={{ opacity: 0, scale: 0, y: -20 }}
                    transition={{ 
                      duration: 5 + idx * 0.5, 
                      repeat: Infinity, 
                      ease: "easeInOut", 
                      delay: idx * 0.3 
                    }}
                    style={{ 
                      top: img.top, 
                      left: img.left, 
                      right: img.right, 
                      bottom: img.bottom 
                    }}
                  >
                    <Image
                      src={img.src}
                      alt={`party-${idx}`}
                      fill
                      className="object-cover"
                      sizes="128px"
                    />
                  </motion.div>
                ))}
              </div>
            )}
          </AnimatePresence>

              {/* Animated Background Elements for Chips */}
              <AnimatePresence>
            {mode === 'search' && hoveredChip === "🎉 BalloonVendor" && (
                  <div className="absolute inset-0 pointer-events-none">
                    {[...Array(8)].map((_, i) => (
                      <motion.div
                        key={`glass-particle-${i}`}
                        className="absolute text-4xl"
                        initial={{ 
                          opacity: 0, 
                          scale: 0,
                          x: Math.random() * window.innerWidth,
                          y: Math.random() * window.innerHeight
                        }}
                        animate={{ 
                          opacity: [0, 1, 0],
                          scale: [0, 1.2, 0],
                          x: Math.random() * window.innerWidth,
                          y: Math.random() * window.innerHeight,
                          rotate: [0, 360, 720]
                        }}
                        exit={{ opacity: 0, scale: 0 }}
                        transition={{ 
                          duration: 3,
                          repeat: Infinity,
                          delay: i * 0.2,
                          ease: "easeInOut"
                        }}
                        style={{
                          color: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F'][i % 8]
                        }}
                      >
                        🎈
                      </motion.div>
                    ))}
                  </div>
                )}
                
            {mode === 'search' && hoveredChip === "🍰 CakeArtist" && (
                  <div className="absolute inset-0 pointer-events-none">
                    {[...Array(6)].map((_, i) => (
                      <motion.div
                        key={`glass-particle-6-${i}`}
                        className="absolute text-3xl"
                        initial={{ 
                          opacity: 0, 
                          scale: 0,
                          x: Math.random() * window.innerWidth,
                          y: Math.random() * window.innerHeight
                        }}
                        animate={{ 
                          opacity: [0, 1, 0],
                          scale: [0, 1.5, 0],
                          y: [Math.random() * window.innerHeight, Math.random() * window.innerHeight - 100],
                          rotate: [0, 180, 360]
                        }}
                        exit={{ opacity: 0, scale: 0 }}
                        transition={{ 
                          duration: 4,
                          repeat: Infinity,
                          delay: i * 0.3,
                          ease: "easeInOut"
                        }}
                      >
                        🍰
                      </motion.div>
                    ))}
                  </div>
                )}
                
            {mode === 'search' && hoveredChip === "📸 PhotoBooth" && (
                  <div className="absolute inset-0 pointer-events-none">
                    {[...Array(5)].map((_, i) => (
                      <motion.div
                        key={`glass-particle-5-${i}`}
                        className="absolute text-2xl"
                        initial={{ 
                          opacity: 0, 
                          scale: 0,
                          x: Math.random() * window.innerWidth,
                          y: Math.random() * window.innerHeight
                        }}
                        animate={{ 
                          opacity: [0, 1, 0],
                          scale: [0, 1.3, 0],
                          x: [Math.random() * window.innerWidth, Math.random() * window.innerWidth],
                          y: [Math.random() * window.innerHeight, Math.random() * window.innerHeight]
                        }}
                        exit={{ opacity: 0, scale: 0 }}
                        transition={{ 
                          duration: 2.5,
                          repeat: Infinity,
                          delay: i * 0.4,
                          ease: "easeInOut"
                        }}
                      >
                        📸
                      </motion.div>
                    ))}
                  </div>
                )}
                
            {mode === 'search' && hoveredChip === "🪩 DJ" && (
                  <div className="absolute inset-0 pointer-events-none">
                    {[...Array(7)].map((_, i) => (
                      <motion.div
                        key={`glass-particle-7-${i}`}
                        className="absolute text-3xl"
                        initial={{ 
                          opacity: 0, 
                          scale: 0,
                          x: Math.random() * window.innerWidth,
                          y: Math.random() * window.innerHeight
                        }}
                        animate={{ 
                          opacity: [0, 1, 0],
                          scale: [0, 1.4, 0],
                          rotate: [0, 360, 720],
                          x: [Math.random() * window.innerWidth, Math.random() * window.innerWidth],
                          y: [Math.random() * window.innerHeight, Math.random() * window.innerHeight]
                        }}
                        exit={{ opacity: 0, scale: 0 }}
                        transition={{ 
                          duration: 2,
                          repeat: Infinity,
                          delay: i * 0.15,
                          ease: "easeInOut"
                        }}
                      >
                        🎵
                      </motion.div>
                    ))}
                  </div>
                )}
                
            {mode === 'search' && hoveredChip === "👗 DressThemes" && (
                  <div className="absolute inset-0 pointer-events-none">
                    {[...Array(6)].map((_, i) => (
                      <motion.div
                        key={`glass-particle-6-${i}`}
                        className="absolute text-2xl"
                        initial={{ 
                          opacity: 0, 
                          scale: 0,
                          x: Math.random() * window.innerWidth,
                          y: Math.random() * window.innerHeight
                        }}
                        animate={{ 
                          opacity: [0, 1, 0],
                          scale: [0, 1.2, 0],
                          y: [Math.random() * window.innerHeight, Math.random() * window.innerHeight - 150],
                          rotate: [0, 90, 180, 270, 360]
                        }}
                        exit={{ opacity: 0, scale: 0 }}
                        transition={{ 
                          duration: 3.5,
                          repeat: Infinity,
                          delay: i * 0.25,
                          ease: "easeInOut"
                        }}
                      >
                        👗
                      </motion.div>
                    ))}
                  </div>
                )}
              </AnimatePresence>

          {/* Mode-based layout */}
          {mode === 'search' ? (
            // SEARCH MODE
              <motion.div
              className="min-h-screen flex items-center justify-center p-4"
              initial={{ opacity: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.8 }}
            >
              {/* Festimo Logo */}
              <motion.div
                className="absolute top-[-20px] left-[39%] transform -translate-x-1/2 z-50 overflow-hidden h-60 sm:h-72 md:h-84 lg:h-96 w-auto"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1, duration: 0.4 }}
              >
            <Image
              src="/festimo-logo.png"
              alt="Festimo"
              width={1200}
              height={390}
              priority
              className="h-full w-auto drop-shadow-2xl"
            />
          </motion.div>

              {/* Main Card */}
            <motion.div
              ref={cardRef}
              className="relative z-10 backdrop-blur-3xl bg-white/20 border border-white/50 shadow-2xl p-6 sm:p-8 md:p-10 rounded-3xl w-full max-w-2xl overflow-hidden"
              initial={{ y: 40, opacity: 0, scale: 0.98 }}
              animate={{ y: 0, opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
              onClick={createRipple}
            >
              {/* Ripple effects */}
              {ripples.map((ripple) => (
                <motion.span
                  key={ripple.id}
                  className="absolute rounded-full bg-white/30 pointer-events-none"
                  style={{
                    left: ripple.x,
                    top: ripple.y,
                    width: 0,
                    height: 0,
                  }}
                  initial={{ width: 0, height: 0, opacity: 0.6 }}
                  animate={{ width: 500, height: 500, opacity: 0 }}
                  transition={{ duration: 1, ease: "easeOut" }}
                />
              ))}
              
              {/* Liquid glass gradient overlay */}
              <motion.div
                className="absolute inset-0 rounded-3xl opacity-50 pointer-events-none"
                style={{
                  background: "radial-gradient(circle at 50% 50%, rgba(255,255,255,0.3), transparent 70%)",
                }}
                animate={{
                  background: [
                    "radial-gradient(circle at 20% 30%, rgba(255,255,255,0.3), transparent 70%)",
                    "radial-gradient(circle at 80% 70%, rgba(255,255,255,0.3), transparent 70%)",
                    "radial-gradient(circle at 20% 30%, rgba(255,255,255,0.3), transparent 70%)",
                  ],
                }}
                transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
              />
            
            <div className="relative z-10">

                {/* Location Input - First */}
                <motion.div
                  className="mb-5"
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.35, duration: 0.4 }}
                >
                  <div className="relative">
                    <motion.div
                      className="relative overflow-hidden rounded-2xl backdrop-blur-xl border-2 transition-all duration-300"
                      style={{
                        background: isLocationValid
                          ? 'linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(22, 163, 74, 0.1) 100%)'
                          : 'linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.15) 100%)',
                        borderColor: isLocationValid ? 'rgba(34, 197, 94, 0.5)' : 'rgba(255, 255, 255, 0.4)',
                        boxShadow: isLocationValid
                          ? '0 8px 32px rgba(34, 197, 94, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.4)'
                          : '0 4px 16px rgba(0, 0, 0, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.4)'
                      }}
                    >
                      {/* Icon */}
                      <div className="absolute left-4 top-1/2 transform -translate-y-1/2 z-10">
                        <motion.div
                          animate={{
                            scale: isLocationValid ? [1, 1.2, 1] : isFetchingLocation ? [1, 1.1, 1] : 1,
                            rotate: isLocationValid ? [0, 10, -10, 0] : isFetchingLocation ? [0, 360] : 0
                          }}
                          transition={{ 
                            duration: isFetchingLocation ? 1.5 : 0.5,
                            repeat: isFetchingLocation ? Infinity : 0,
                            ease: isFetchingLocation ? "linear" : "easeInOut"
                          }}
                        >
                          {isLocationValid ? (
                            <svg 
                              width="20" 
                              height="20" 
                              viewBox="0 0 24 24" 
                              fill="none" 
                              stroke="currentColor" 
                              strokeWidth="2.5" 
                              strokeLinecap="round" 
                              strokeLinejoin="round"
                              className="text-green-600"
                            >
                              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                              <polyline points="22 4 12 14.01 9 11.01"/>
                            </svg>
                          ) : (
                            <svg 
                              width="20" 
                              height="20" 
                              viewBox="0 0 24 24" 
                              fill="none" 
                              stroke="currentColor" 
                              strokeWidth="2" 
                              strokeLinecap="round" 
                              strokeLinejoin="round"
                              className={isFetchingLocation ? "text-blue-500" : "text-pink-500"}
                            >
                              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                              <circle cx="12" cy="10" r="3"/>
                            </svg>
                          )}
                        </motion.div>
                      </div>

                      {/* Input */}
                      <input
                        type="text"
                        value={location}
                        onChange={handleLocationChange}
                        placeholder="Enter zip code or city (e.g., 95110 or San Jose, CA)"
                        className="w-full pl-14 pr-24 py-3.5 bg-transparent focus:outline-none text-gray-900 placeholder-gray-500 font-medium tracking-wide"
                        style={{
                          textShadow: '0 1px 2px rgba(255, 255, 255, 0.8)'
                        }}
                        disabled={isFetchingLocation}
                      />

                      {/* Buttons */}
                      <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center gap-2">
                        {/* GPS Button */}
                        <motion.button
                          onClick={fetchBrowserLocation}
                          disabled={isFetchingLocation}
                          className="p-2 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 border border-white/40 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.95 }}
                          title={isFetchingLocation ? "Fetching location..." : "Use my current location"}
                        >
                          <svg 
                            width="14" 
                            height="14" 
                            viewBox="0 0 24 24" 
                            fill="none" 
                            stroke="currentColor" 
                            strokeWidth="2.5" 
                            strokeLinecap="round" 
                            strokeLinejoin="round"
                            className="text-white"
                          >
                            <circle cx="12" cy="12" r="10"/>
                            <circle cx="12" cy="12" r="2"/>
                            <line x1="12" y1="2" x2="12" y2="4"/>
                            <line x1="12" y1="20" x2="12" y2="22"/>
                            <line x1="2" y1="12" x2="4" y2="12"/>
                            <line x1="20" y1="12" x2="22" y2="12"/>
                          </svg>
                        </motion.button>
                        
                        {/* Clear Button */}
                        {location && !isFetchingLocation && (
                          <motion.button
                            onClick={() => {
                              setLocation('')
                              setIsLocationValid(false)
                              setLocationError('')
                            }}
                            className="p-1.5 rounded-full bg-white/60 hover:bg-white/80 border border-white/40 transition-all duration-200"
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.95 }}
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            title="Clear location"
                          >
                            <svg 
                              width="12" 
                              height="12" 
                              viewBox="0 0 24 24" 
                              fill="none" 
                              stroke="currentColor" 
                              strokeWidth="2.5" 
                              strokeLinecap="round" 
                              strokeLinejoin="round"
                              className="text-gray-600"
                            >
                              <line x1="18" y1="6" x2="6" y2="18"/>
                              <line x1="6" y1="6" x2="18" y2="18"/>
                            </svg>
                          </motion.button>
                        )}
                        
                        {/* Floating particles */}
                        {isLocationValid && (
                          <>
                            {[...Array(3)].map((_, i) => (
                              <motion.div
                                key={`location-particle-${i}`}
                                className="absolute w-1 h-1 rounded-full bg-green-400"
                                initial={{ opacity: 0, x: 0, y: 0 }}
                                animate={{
                                  opacity: [0, 1, 0],
                                  x: [0, (i - 1) * 20],
                                  y: [0, -20 - i * 5],
                                }}
                                transition={{
                                  duration: 1.5,
                                  repeat: Infinity,
                                  delay: i * 0.2,
                                }}
                                style={{
                                  right: `${25 + i * 5}px`,
                                }}
                              />
                            ))}
                          </>
                        )}
                      </div>
                    </motion.div>

                    {/* Helper text or Error */}
                    <motion.p
                      className={`mt-2 text-xs text-center ${locationError ? 'text-red-600' : 'text-gray-600'}`}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.4 }}
                    >
                      <span className="inline-flex items-center gap-1">
                        {locationError ? (
                          <>
                            <svg 
                              width="12" 
                              height="12" 
                              viewBox="0 0 24 24" 
                              fill="none" 
                              stroke="currentColor" 
                              strokeWidth="2" 
                              strokeLinecap="round" 
                              strokeLinejoin="round"
                              className="text-red-500"
                            >
                              <circle cx="12" cy="12" r="10"/>
                              <line x1="12" y1="8" x2="12" y2="12"/>
                              <line x1="12" y1="16" x2="12.01" y2="16"/>
                            </svg>
                            {locationError}
                          </>
                        ) : isLocationValid ? (
                          <>
                            <svg 
                              width="12" 
                              height="12" 
                              viewBox="0 0 24 24" 
                              fill="none" 
                              stroke="currentColor" 
                              strokeWidth="2.5" 
                              strokeLinecap="round" 
                              strokeLinejoin="round"
                              className="text-green-600"
                            >
                              <polyline points="20 6 9 17 4 12"/>
                            </svg>
                            Perfect! We'll find vendors near you
                          </>
                        ) : isFetchingLocation ? (
                          <>
                            <svg 
                              width="12" 
                              height="12" 
                              viewBox="0 0 24 24" 
                              fill="none" 
                              stroke="currentColor" 
                              strokeWidth="2" 
                              strokeLinecap="round" 
                              strokeLinejoin="round"
                              className="text-blue-500 animate-spin"
                            >
                              <circle cx="12" cy="12" r="10"/>
                            </svg>
                            Auto-fetching your location...
                          </>
                        ) : (
                          <>
                            <svg 
                              width="12" 
                              height="12" 
                              viewBox="0 0 24 24" 
                              fill="none" 
                              stroke="currentColor" 
                              strokeWidth="2" 
                              strokeLinecap="round" 
                              strokeLinejoin="round"
                              className="text-pink-500"
                            >
                              <circle cx="12" cy="12" r="10"/>
                              <line x1="12" y1="16" x2="12" y2="12"/>
                              <line x1="12" y1="8" x2="12.01" y2="8"/>
                            </svg>
                            Enter location or click 📍 to use GPS
                          </>
                        )}
                      </span>
                    </motion.p>
                  </div>
                </motion.div>

                {/* Tabs - After Location Input */}
                <div className="flex justify-center gap-3 sm:gap-4 mb-6 relative z-[60]">
                  {["url", "prompt"].map((key, idx) => (
                <motion.button
                  key={key}
                  onClick={() => {
                    setTab(key)
                    // Immediately focus the input after tab change
                    setTimeout(() => {
                      if (key === 'url' && urlInputRef.current) {
                        urlInputRef.current.focus()
                      } else if (key === 'prompt' && promptTextareaRef.current) {
                        promptTextareaRef.current.focus()
                      }
                    }, 50)
                  }}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ 
                    opacity: 1,
                    y: 0,
                    transition: { delay: 0.4 + idx * 0.05, duration: 0.3 }
                  }}
                  whileTap={{ scale: 0.95 }}
                  className={`relative overflow-hidden px-5 sm:px-6 py-2.5 sm:py-3 rounded-full font-semibold transition-all duration-200 z-[70] pointer-events-auto ${
                    tab === key 
                      ? 'bg-gradient-to-r from-pink-500 to-rose-500 text-white shadow-lg' 
                      : 'bg-white/40 text-gray-800 hover:bg-white/60'
                  } backdrop-blur-xl border border-white/40`}
                >
                  <span className="relative z-10">{key === "url" ? "🔗 Inspiration" : "💬 Imagination"}</span>
                </motion.button>
              ))}
            </div>

                {/* Tab Panels */}
                <AnimatePresence mode="wait">
                  <motion.div
                    key={tab}
                    initial={{ opacity: 0, scale: 0.95, y: 10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: -10 }}
                    transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
                    className="mb-6"
                  >
                    {tab === "url" && (
                      <div className="relative">
                        <motion.input 
                          ref={urlInputRef}
                          type="text"
                          value={pinterestUrl}
                          onChange={handleUrlChange}
                          onKeyPress={(e) => e.key === 'Enter' && urlValidation.isValid && handleGeneratePlan()}
                          placeholder="Pinterest, TikTok, Lemon8, or Instagram URL (Currently Disabled)" 
                          className="w-full p-4 pr-12 rounded-2xl border-2 shadow-inner focus:outline-none text-gray-500 placeholder-gray-400 transition-all duration-300 backdrop-blur-xl bg-gray-100/50 border-gray-300 cursor-not-allowed"
                          disabled={true}
                        />
                        
                        {/* Clear Button */}
                        {false && pinterestUrl && (
                          <motion.button
                            onClick={() => setPinterestUrl('')}
                            className="absolute right-3 top-2.5 px-1.5 pt-2 pb-1.5 rounded-full bg-gray-200/80 hover:bg-gray-300/80 border border-gray-300/50 shadow-sm transition-all duration-200"
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.95 }}
                            initial={{ opacity: 0, scale: 0.8 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.8 }}
                            title="Clear URL"
                          >
                            <svg 
                              width="12" 
                              height="12" 
                              viewBox="0 0 24 24" 
                              fill="none" 
                              stroke="currentColor" 
                              strokeWidth="2" 
                              strokeLinecap="round" 
                              strokeLinejoin="round"
                              className="text-gray-600"
                            >
                              <line x1="18" y1="6" x2="6" y2="18"></line>
                              <line x1="6" y1="6" x2="18" y2="18"></line>
                            </svg>
                          </motion.button>
                        )}
                      </div>
                    )}
                    {tab === "prompt" && (
                  <div className="space-y-4">
                    {/* Text Input Section */}
                    <div className="relative">
                      <motion.textarea
                        ref={promptTextareaRef}
                        value={chatMessage}
                        onChange={(e) => setChatMessage(e.target.value)}
                        placeholder="Write your party theme, attach design of decor, cake, etc..." 
                        className="w-full h-32 p-4 pt-12 pr-20 rounded-2xl bg-white/50 border-2 border-white/40 shadow-inner focus:outline-none focus:ring-2 focus:ring-pink-400 focus:border-pink-300 text-gray-900 placeholder-gray-500 resize-none transition-all duration-300 backdrop-blur-xl" 
                        disabled={loading}
                      />
                      
                      {/* Clear Button */}
                      {chatMessage && (
                        <motion.button
                          onClick={() => setChatMessage('')}
                          className="absolute right-3 top-3 p-1.5 rounded-full bg-gray-200/80 hover:bg-gray-300/80 border border-gray-300/50 shadow-sm transition-all duration-200"
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.95 }}
                          initial={{ opacity: 0, scale: 0.8 }}
                          animate={{ opacity: 1, scale: 1 }}
                          exit={{ opacity: 0, scale: 0.8 }}
                          title="Clear text"
                        >
                          <svg 
                            width="12" 
                            height="12" 
                            viewBox="0 0 24 24" 
                            fill="none" 
                            stroke="currentColor" 
                            strokeWidth="2" 
                            strokeLinecap="round" 
                            strokeLinejoin="round"
                            className="text-gray-600"
                          >
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                          </svg>
                        </motion.button>
                      )}
                      
                      {/* Image Upload Icon with Tooltip */}
                      <div className="absolute right-16 bottom-3 group">
                        <label htmlFor="combined-file-upload" className="cursor-pointer">
                          <motion.div 
                            className={`p-2 rounded-full border transition-all duration-200 ${
                              selectedFile 
                                ? 'bg-green-100/80 hover:bg-green-200/80 text-green-600 border-green-300/50' 
                                : 'bg-gray-100/80 hover:bg-gray-200/80 text-gray-600 border-gray-300/50'
                            }`}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            title={selectedFile ? `Selected: ${selectedFile.name}` : "Upload PNG/JPG • Max 10MB"}
                          >
                            {selectedFile ? (
                              <svg 
                                width="16" 
                                height="16" 
                                viewBox="0 0 24 24" 
                                fill="none" 
                                stroke="currentColor" 
                                strokeWidth="2" 
                                strokeLinecap="round" 
                                strokeLinejoin="round"
                              >
                                <path d="M9 12l2 2 4-4"/>
                                <path d="M21 12c0 4.97-4.03 9-9 9s-9-4.03-9-9 4.03-9 9-9 9 4.03 9 9z"/>
                              </svg>
                            ) : (
                              <svg 
                                width="16" 
                                height="16" 
                                viewBox="0 0 24 24" 
                                fill="none" 
                                stroke="currentColor" 
                                strokeWidth="2" 
                                strokeLinecap="round" 
                                strokeLinejoin="round"
                              >
                                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                                <circle cx="8.5" cy="8.5" r="1.5"/>
                                <polyline points="21,15 16,10 5,21"/>
                              </svg>
                            )}
                          </motion.div>
                        </label>
                        <input 
                          type="file"
                          accept="image/png,image/jpeg,image/jpg"
                          onChange={handleFileUpload}
                          className="hidden" 
                          id="combined-file-upload"
                          disabled={loading}
                        />
                        
                        {/* Tooltip */}
                        <div className="absolute bottom-full right-0 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
                          {selectedFile ? `Selected: ${selectedFile.name}` : "PNG/JPG • Max 10MB"}
                          <div className="absolute top-full right-4 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
                        </div>
                      </div>
                      
                      {/* Voice Input Button - Half Size */}
                      <motion.button
                        onClick={isListening ? stopListening : startListening}
                        className={`absolute right-3 bottom-3 p-1.5 rounded-full shadow-lg transition-all duration-300 ${
                          isSupported && isRecognitionReady
                            ? 'bg-gradient-to-br from-pink-200 to-purple-200 hover:from-pink-300 hover:to-purple-300 border border-pink-300/50' 
                            : 'bg-gray-200 hover:bg-gray-300 border border-gray-300'
                        }`}
                        whileHover={isSupported && isRecognitionReady ? { scale: 1.1, y: -2 } : {}}
                        whileTap={isSupported && isRecognitionReady ? { scale: 0.95 } : {}}
                        disabled={loading || !isSupported || !isRecognitionReady}
                        title={
                          !isSupported 
                            ? 'Voice input not supported' 
                            : !isRecognitionReady 
                            ? 'Voice recognition not ready' 
                            : isListening 
                            ? 'Click to stop' 
                            : 'Click to speak'
                        }
                      >
                        {isListening ? (
                          <motion.div
                            className="w-3.5 h-3.5 bg-gradient-to-br from-red-400 to-pink-500 rounded-full flex items-center justify-center"
                            animate={{ 
                              scale: [1, 1.2, 1],
                              boxShadow: [
                                "0 0 0 0 rgba(239, 68, 68, 0.4)",
                                "0 0 0 10px rgba(239, 68, 68, 0.1)",
                                "0 0 0 0 rgba(239, 68, 68, 0.4)"
                              ]
                            }}
                            transition={{ duration: 1.5, repeat: Infinity }}
                          >
                            <div className="w-1.5 h-1.5 bg-white rounded-full"></div>
                          </motion.div>
                        ) : !isRecognitionReady ? (
                          <motion.div
                            className="w-3.5 h-3.5 flex items-center justify-center text-gray-400"
                            animate={{ rotate: [0, 360] }}
                            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                          >
                            <div className="w-2 h-2 border-2 border-gray-400 border-t-transparent rounded-full"></div>
                          </motion.div>
                        ) : (
                          <motion.div
                            className={`w-3.5 h-3.5 flex items-center justify-center ${isSupported ? 'text-pink-600' : 'text-gray-400'}`}
                            whileHover={{ scale: 1.1, rotate: 5 }}
                          >
                            <svg 
                              width="14" 
                              height="14" 
                              viewBox="0 0 24 24" 
                              fill="currentColor"
                              className="drop-shadow-sm"
                            >
                              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                              <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                            </svg>
                          </motion.div>
                        )}
                      </motion.button>
                      
                      {/* Voice Status Indicator */}
                      {isListening && (
                        <motion.div
                          className="absolute right-20 bottom-3 px-3 py-2 bg-gradient-to-r from-pink-100 to-purple-100 text-pink-700 text-xs rounded-lg border border-pink-300/50 shadow-md max-w-xs"
                          initial={{ opacity: 0, scale: 0.8, y: 10 }}
                          animate={{ opacity: 1, scale: 1, y: 0 }}
                          exit={{ opacity: 0, scale: 0.8, y: 10 }}
                        >
                          <motion.div
                            className="flex items-center gap-2"
                            animate={{ opacity: [1, 0.5, 1] }}
                            transition={{ duration: 1, repeat: Infinity }}
                          >
                            <div className="w-2 h-2 bg-pink-500 rounded-full animate-pulse flex-shrink-0"></div>
                            <span className="font-medium">Listening...</span>
                          </motion.div>
                          
                          {/* Real-time transcript display */}
                          {interimTranscript && (
                            <motion.div
                              className="mt-2 text-gray-600 italic max-h-16 overflow-y-auto"
                              initial={{ opacity: 0, y: 5 }}
                              animate={{ opacity: 1, y: 0 }}
                              transition={{ duration: 0.1 }}
                              key={interimTranscript}
                            >
                              <div className="flex items-start gap-1">
                                <span className="text-pink-400">"</span>
                                <span 
                                  ref={interimTextRef}
                                  className="flex-1 break-words whitespace-pre-wrap"
                                >
                                  {interimTranscript}
                                </span>
                                <span className="text-pink-400">"</span>
                              </div>
                            </motion.div>
                          )}
                        </motion.div>
                      )}
                    </div>
                    
                    {/* Instructions */}
                    <motion.p
                      className="text-xs text-gray-500 text-center"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.5 }}
                    >
                      💡 Add a prompt or click the image icon to upload!
                    </motion.p>
                  </div>
                )}
              </motion.div>
            </AnimatePresence>

            {/* Unified Generate Button */}
            <motion.button
              onClick={handleGeneratePlan}
              disabled={!canSubmit()}
              className="w-full py-4 mb-6 rounded-2xl bg-gradient-to-r from-pink-500 via-rose-500 to-pink-500 text-white text-lg font-bold shadow-lg disabled:opacity-50 disabled:cursor-not-allowed backdrop-blur-xl transition-all duration-300"
              style={{
                backgroundSize: "200% 100%",
              }}
              animate={!loading && canSubmit() ? {
                backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"],
              } : {}}
              transition={{
                backgroundPosition: { duration: 3, repeat: Infinity, ease: "linear" }
              }}
              whileTap={canSubmit() ? { scale: 0.98 } : {}}
            >
                  {loading ? (
                    <span className="flex flex-col items-center justify-center gap-2">
                      <motion.span
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      >
                        ✨
                      </motion.span>
                      <span className="text-sm font-medium">
                        {progressMessage || 'Building Your Party Plan...'}
                      </span>
                      {progressStep && (
                        <div className="w-full bg-white/20 rounded-full h-1 mt-1">
                          <motion.div
                            className="bg-white h-1 rounded-full"
                            initial={{ width: "0%" }}
                            animate={{ 
                              width: progressStep === 'analyzing' ? "20%" :
                                     progressStep === 'validating' ? "40%" :
                                     progressStep === 'analyzing_image' ? "50%" :
                                     progressStep === 'extracting' ? "70%" :
                                     progressStep === 'checking' ? "85%" :
                                     progressStep === 'form_ready' ? "95%" :
                                     progressStep === 'ready' ? "100%" : "0%"
                            }}
                            transition={{ duration: 0.5 }}
                          />
                        </div>
                      )}
                    </span>
                  ) : (
                    <span className="flex items-center justify-center gap-2">
                      🎉 Generate Party Plan
                    </span>
                  )}
            </motion.button>

            {/* Error Display */}
            {(error || agentError) && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-4 p-4 rounded-2xl bg-red-50/80 border border-red-200 text-red-700 backdrop-blur-xl"
              >
                <p className="font-medium">❌ {error || agentError}</p>
              </motion.div>
            )}


                {/* Tags */}
                <motion.div
                  className="flex flex-wrap justify-center gap-1.5 sm:gap-2"
                  initial="hidden"
                  animate="visible"
                  variants={{
                    hidden: {},
                    visible: {
                      transition: { staggerChildren: 0.08, delayChildren: 0.8 }
                    }
                  }}
                >
                  {partyTags.map((tag, idx) => {
                    const chipStyles = [
                      "px-2 py-1 text-xs rounded-full bg-gradient-to-r from-pink-100 to-rose-100 border border-pink-200 text-pink-700 shadow-sm",
                      "px-2 py-1 text-xs rounded-full bg-gradient-to-r from-blue-100 to-cyan-100 border border-blue-200 text-blue-700 shadow-sm",
                      "px-2 py-1 text-xs rounded-full bg-gradient-to-r from-purple-100 to-violet-100 border border-purple-200 text-purple-700 shadow-sm",
                      "px-2 py-1 text-xs rounded-full bg-gradient-to-r from-green-100 to-emerald-100 border border-green-200 text-green-700 shadow-sm",
                      "px-2 py-1 text-xs rounded-full bg-gradient-to-r from-yellow-100 to-amber-100 border border-yellow-200 text-yellow-700 shadow-sm"
                    ]
                    
                    return (
                      <motion.span
                        key={`tag-${tag}-${idx}`}
                        className={`relative overflow-hidden font-medium cursor-pointer ${chipStyles[idx % chipStyles.length]}`}
                        initial={{ opacity: 0, y: 10, scale: 0.9 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                        whileHover={{ 
                          scale: 1.1,
                          y: -3,
                          boxShadow: "0 8px 25px -5px rgba(0, 0, 0, 0.2)",
                          transition: { duration: 0.3 }
                        }}
                        whileTap={{ scale: 0.95 }}
                        onHoverStart={() => setHoveredChip(tag)}
                        onHoverEnd={() => setHoveredChip(null)}
                      >
                        <motion.span
                          className="absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent"
                          initial={{ x: "-100%" }}
                          whileHover={{ x: "100%" }}
                          transition={{ duration: 0.6 }}
                        />
                        <span className="relative z-10">{tag}</span>
                      </motion.span>
                    )
                  })}
                </motion.div>

            {/* Legacy Results Display - Fallback */}
            {generatedPlan && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="mt-8 p-6 rounded-2xl bg-white/40 border border-white/50 backdrop-blur-xl"
              >
                <h3 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                  🎊 Your Party Plan
                </h3>
                {generatedPlan.plan && (
                  <div className="space-y-4 text-left">
                    <div>
                      <h4 className="font-semibold text-lg text-gray-800 mb-2">📋 {generatedPlan.plan.title}</h4>
                      <p className="text-gray-700">{generatedPlan.plan.description}</p>
                    </div>
                    {generatedPlan.plan.theme && (
                      <div className="p-3 rounded-xl bg-white/50">
                        <span className="font-semibold">🎨 Theme:</span> {generatedPlan.plan.theme}
                      </div>
                    )}
                    {generatedPlan.plan.budget_estimate && (
                      <div className="p-3 rounded-xl bg-white/50">
                        <span className="font-semibold">💰 Budget:</span> {generatedPlan.plan.budget_estimate}
                      </div>
                    )}
                  </div>
                )}
              </motion.div>
            )}
            </div>
          </motion.div>
          </motion.div>
          ) : (
            // BUILD MODE
            <motion.div
              className="min-h-screen flex relative overflow-hidden"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
              style={{
                background: `
                  radial-gradient(circle at 20% 80%, rgba(255, 182, 193, 0.3) 0%, transparent 50%),
                  radial-gradient(circle at 80% 20%, rgba(255, 192, 203, 0.3) 0%, transparent 50%),
                  radial-gradient(circle at 40% 40%, rgba(255, 218, 185, 0.2) 0%, transparent 50%),
                  linear-gradient(135deg, rgba(255, 182, 193, 0.1) 0%, rgba(255, 192, 203, 0.1) 50%, rgba(255, 218, 185, 0.1) 100%)
                `
              }}
            >
              {/* Animated Background Particles */}
              <div className="absolute inset-0 overflow-hidden pointer-events-none">
                {[...Array(20)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="absolute w-2 h-2 bg-gradient-to-r from-pink-400 to-rose-400 rounded-full opacity-60"
                    style={{
                      left: `${Math.random() * 100}%`,
                      top: `${Math.random() * 100}%`,
                    }}
                    animate={{
                      y: [0, -20, 0],
                      x: [0, Math.random() * 10 - 5, 0],
                      opacity: [0.6, 1, 0.6],
                      scale: [1, 1.2, 1],
                    }}
                    transition={{
                      duration: 3 + Math.random() * 2,
                      repeat: Infinity,
                      delay: Math.random() * 2,
                    }}
                  />
                ))}
          </div>


              {/* Festimo Logo - Bottom Right */}
              <motion.div
                className="absolute bottom-4 right-4 z-30"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 1.0 }}
              >
                <img 
                  src="/festimo-logo.png" 
                  alt="Festimo" 
                  className="w-24 h-24 opacity-60 hover:opacity-80 transition-opacity duration-300"
                />
              </motion.div>
            </motion.div>
          )}
        </motion.div>
      )}
    </AnimatePresence>
    </>
  )
}
