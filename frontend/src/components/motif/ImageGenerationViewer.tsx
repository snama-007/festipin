'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Wand2, Download, RefreshCw, Star, X, Loader2, ChevronRight, CheckCircle, AlertCircle, Clock } from 'lucide-react'

interface ImageGenerationViewerProps {
  prompt: string
  style?: string | null
  inspirationImage?: string | null
}

interface GeneratedImage {
  id: string
  imageData: string
  prompt: string
  style?: string
  rating?: number
  generatedAt: string
  providerUsed?: string
  processingTime?: number
  cost?: number
}

interface ProcessStep {
  id: string
  title: string
  description: string
  status: 'pending' | 'running' | 'completed' | 'error'
  timestamp?: Date
  duration?: number
}

export function ImageGenerationViewer({ 
  prompt, 
  style, 
  inspirationImage 
}: ImageGenerationViewerProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedImages, setGeneratedImages] = useState<GeneratedImage[]>([])
  const [currentImage, setCurrentImage] = useState<GeneratedImage | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [rating, setRating] = useState<number>(0)
  const [showProcessLog, setShowProcessLog] = useState(false)
  const [processSteps, setProcessSteps] = useState<ProcessStep[]>([])
  const [currentProvider, setCurrentProvider] = useState<string>('')

  // Initialize process steps
  const initializeProcessSteps = () => {
    const steps: ProcessStep[] = [
      {
        id: 'validate',
        title: 'Validating Request',
        description: 'Checking prompt and parameters',
        status: 'pending'
      },
      {
        id: 'provider',
        title: 'Selecting Provider',
        description: 'Choosing optimal AI service',
        status: 'pending'
      },
      {
        id: 'enhance',
        title: 'Enhancing Prompt',
        description: 'Optimizing prompt for better results',
        status: 'pending'
      },
      {
        id: 'generate',
        title: 'Generating Image',
        description: 'AI is creating your decoration',
        status: 'pending'
      },
      {
        id: 'process',
        title: 'Processing Result',
        description: 'Finalizing and optimizing image',
        status: 'pending'
      }
    ]
    setProcessSteps(steps)
  }

  // Update process step
  const updateProcessStep = (stepId: string, status: ProcessStep['status'], description?: string) => {
    setProcessSteps(prev => prev.map(step => {
      if (step.id === stepId) {
        return {
          ...step,
          status,
          description: description || step.description,
          timestamp: status === 'running' ? new Date() : step.timestamp,
          duration: status === 'completed' ? Date.now() - (step.timestamp?.getTime() || Date.now()) : step.duration
        }
      }
      return step
    }))
  }

  // Generate image on component mount
  useEffect(() => {
    // Only generate if we have at least a prompt or inspiration image
    if (prompt.trim() || inspirationImage) {
      generateImage()
    }
  }, [prompt, style])

  const generateImage = async () => {
    setIsGenerating(true)
    setError(null)
    setShowProcessLog(true)
    initializeProcessSteps()

    try {
      // Validate that at least one input is provided
      const hasPrompt = prompt && prompt.trim().length > 0
      const hasImage = inspirationImage && inspirationImage.length > 0

      if (!hasPrompt && !hasImage) {
        throw new Error('Please provide a prompt or upload an inspiration image')
      }

      // Step 1: Validate Request
      updateProcessStep('validate', 'running')
      await new Promise(resolve => setTimeout(resolve, 300))
      updateProcessStep('validate', 'completed')

      // Step 2: Select Provider
      updateProcessStep('provider', 'running')
      await new Promise(resolve => setTimeout(resolve, 200))
      updateProcessStep('provider', 'completed', 'Selected optimal AI provider')

      // Step 3: Enhance Prompt
      updateProcessStep('enhance', 'running')
      await new Promise(resolve => setTimeout(resolve, 400))
      updateProcessStep('enhance', 'completed')

      // Step 4: Generate Image
      updateProcessStep('generate', 'running')

      // Use the unified endpoint that handles both prompt and image
      const formData = new FormData()

      // Add prompt if provided
      if (hasPrompt) {
        formData.append('prompt', prompt)
      }

      // Add style if provided
      if (style) {
        formData.append('style', style)
      }

      // Add user ID
      formData.append('user_id', 'user_' + Date.now())

      // Add inspiration image if provided
      if (hasImage) {
        const response = await fetch(inspirationImage)
        const blob = await response.blob()
        formData.append('inspiration_image', blob, 'inspiration.jpg')
      }

      const response = await fetch('http://localhost:9000/motif/generation/generate-from-inspiration', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to generate image')
      }

      const data = await response.json()

      if (data.success) {
        updateProcessStep('generate', 'completed')
        
        // Step 5: Process Result
        updateProcessStep('process', 'running')
        await new Promise(resolve => setTimeout(resolve, 500))
        updateProcessStep('process', 'completed')

        const newImage: GeneratedImage = {
          id: data.generation_id,
          imageData: data.image_data,
          prompt: data.prompt_used,
          style: data.style_applied,
          generatedAt: new Date().toISOString(),
          providerUsed: data.provider_used,
          processingTime: data.processing_time,
          cost: data.cost
        }

        setGeneratedImages(prev => [newImage, ...prev])
        setCurrentImage(newImage)
        setCurrentProvider(data.provider_used || 'Unknown')
      } else {
        updateProcessStep('generate', 'error')
        throw new Error(data.error || 'Generation failed')
      }
    } catch (err) {
      updateProcessStep('generate', 'error')
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsGenerating(false)
    }
  }

  const generateFromInspiration = async () => {
    if (!inspirationImage) return

    setIsGenerating(true)
    setError(null)
    setShowProcessLog(true)
    initializeProcessSteps()

    try {
      // Step 1: Validate Request
      updateProcessStep('validate', 'running')
      await new Promise(resolve => setTimeout(resolve, 300))
      updateProcessStep('validate', 'completed')

      // Step 2: Select Provider
      updateProcessStep('provider', 'running')
      await new Promise(resolve => setTimeout(resolve, 200))
      updateProcessStep('provider', 'completed', 'Selected optimal AI provider')

      // Step 3: Enhance Prompt
      updateProcessStep('enhance', 'running')
      await new Promise(resolve => setTimeout(resolve, 400))
      updateProcessStep('enhance', 'completed')

      // Step 4: Generate Image
      updateProcessStep('generate', 'running')

      const formData = new FormData()
      formData.append('prompt', prompt)
      if (style) formData.append('style', style)
      formData.append('user_id', 'user_' + Date.now())

      // Convert data URL to blob
      const response = await fetch(inspirationImage)
      const blob = await response.blob()
      formData.append('inspiration_image', blob, 'inspiration.jpg')

      const apiResponse = await fetch('http://localhost:9000/motif/generation/generate-from-inspiration', {
        method: 'POST',
        body: formData
      })

      if (!apiResponse.ok) {
        throw new Error('Failed to generate image from inspiration')
      }

      const data = await apiResponse.json()

      if (data.success) {
        updateProcessStep('generate', 'completed')
        
        // Step 5: Process Result
        updateProcessStep('process', 'running')
        await new Promise(resolve => setTimeout(resolve, 500))
        updateProcessStep('process', 'completed')

        const newImage: GeneratedImage = {
          id: data.generation_id,
          imageData: data.image_data,
          prompt: data.prompt_used,
          style: data.style_applied,
          generatedAt: new Date().toISOString(),
          providerUsed: data.provider_used,
          processingTime: data.processing_time,
          cost: data.cost
        }

        setGeneratedImages(prev => [newImage, ...prev])
        setCurrentImage(newImage)
        setCurrentProvider(data.provider_used || 'Unknown')
      } else {
        updateProcessStep('generate', 'error')
        throw new Error(data.error || 'Generation failed')
      }
    } catch (err) {
      updateProcessStep('generate', 'error')
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsGenerating(false)
    }
  }

  const submitRating = async (imageId: string, rating: number) => {
    try {
      const response = await fetch(`http://localhost:9000/motif/generation/feedback/${imageId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          rating: rating.toString(),
          feedback: `User rated ${rating}/5`
        })
      })

      if (response.ok) {
        setGeneratedImages(prev => 
          prev.map(img => 
            img.id === imageId ? { ...img, rating } : img
          )
        )
        setRating(rating)
      }
    } catch (err) {
      console.error('Failed to submit rating:', err)
    }
  }

  const downloadImage = (image: GeneratedImage) => {
    const link = document.createElement('a')
    link.href = image.imageData
    link.download = `motif-decoration-${image.id}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div className="w-full h-[600px] rounded-2xl overflow-hidden bg-gradient-to-br from-gray-900 to-gray-800 relative">
      {/* Header */}
      <div className="absolute top-4 left-4 bg-black/50 backdrop-blur-md rounded-lg px-4 py-2 text-white text-sm z-10">
        <p className="font-medium">🎨 AI Image Generation</p>
        <p className="text-xs text-gray-300 mt-1">
          {currentProvider ? `Powered by ${currentProvider}` : 'Intelligent AI Service'}
        </p>
      </div>

      {/* Generation Controls */}
      <div className="absolute top-4 right-4 bg-black/50 backdrop-blur-md rounded-lg px-4 py-2 text-white text-sm z-10">
        <button
          onClick={generateImage}
          disabled={isGenerating}
          className="flex items-center gap-1 px-3 py-1 rounded bg-[#6b46c1] hover:bg-[#5a3a9a] disabled:opacity-50"
        >
          {isGenerating ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Wand2 className="w-4 h-4" />
          )}
          Generate
        </button>
      </div>

      {/* Process Log Toggle */}
      {isGenerating && (
        <div className="absolute top-16 right-4 bg-black/50 backdrop-blur-md rounded-lg px-4 py-2 text-white text-sm z-10">
          <button
            onClick={() => setShowProcessLog(!showProcessLog)}
            className="flex items-center gap-1 px-3 py-1 rounded bg-blue-600 hover:bg-blue-700"
          >
            <Clock className="w-4 h-4" />
            {showProcessLog ? 'Hide' : 'Show'} Process
          </button>
        </div>
      )}

      {/* Main Content */}
      <div className="flex h-full">
        {/* Image Display */}
        <div className="flex-1 flex items-center justify-center p-8">
          <AnimatePresence mode="wait">
            {isGenerating ? (
              <motion.div
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-center text-white"
              >
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  className="w-16 h-16 mx-auto mb-4"
                >
                  <Wand2 className="w-16 h-16" />
                </motion.div>
                <h3 className="text-xl font-bold mb-2">Generating Your Decoration</h3>
                <p className="text-gray-300 mb-4">AI is creating your party decoration...</p>
                
                {/* Current Step Indicator */}
                {processSteps.length > 0 && (
                  <div className="text-sm text-gray-400">
                    {processSteps.find(step => step.status === 'running')?.title || 'Processing...'}
                  </div>
                )}
              </motion.div>
            ) : error ? (
              <motion.div
                key="error"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-center text-white"
              >
                <div className="text-6xl mb-4">❌</div>
                <h3 className="text-xl font-bold mb-2">Generation Failed</h3>
                <p className="text-gray-300 mb-4">{error}</p>
                <button
                  onClick={generateImage}
                  className="px-4 py-2 rounded bg-[#6b46c1] hover:bg-[#5a3a9a]"
                >
                  Try Again
                </button>
              </motion.div>
            ) : currentImage ? (
              <motion.div
                key="image"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="relative"
              >
                <img
                  src={currentImage.imageData}
                  alt="Generated decoration"
                  className="max-w-full max-h-96 rounded-lg shadow-2xl"
                />
                
                {/* Image Actions */}
                <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex gap-2">
                  <button
                    onClick={() => downloadImage(currentImage)}
                    className="p-2 rounded-full bg-black/50 backdrop-blur-md text-white hover:bg-black/70"
                    title="Download"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                </div>
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-center text-white"
              >
                <div className="text-6xl mb-4">🎨</div>
                <h3 className="text-xl font-bold mb-2">Ready to Generate</h3>
                <p className="text-gray-300">Click generate to create your decoration</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Sidebar */}
        <div className="w-80 bg-black/30 backdrop-blur-md p-4 overflow-y-auto">
          <h3 className="text-white font-bold mb-4">Generated Images</h3>
          
          {generatedImages.length === 0 ? (
            <p className="text-gray-400 text-sm">No images generated yet</p>
          ) : (
            <div className="space-y-3">
              {generatedImages.map((image) => (
                <motion.div
                  key={image.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`p-3 rounded-lg border-2 cursor-pointer transition-all ${
                    currentImage?.id === image.id
                      ? 'border-[#6b46c1] bg-[#6b46c1]/20'
                      : 'border-gray-600 hover:border-gray-500'
                  }`}
                  onClick={() => setCurrentImage(image)}
                >
                  <img
                    src={image.imageData}
                    alt="Generated decoration"
                    className="w-full h-20 object-cover rounded mb-2"
                  />
                  <p className="text-white text-xs truncate mb-2">
                    {image.prompt.substring(0, 50)}...
                  </p>
                  
                  {/* Rating */}
                  <div className="flex items-center gap-1">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        onClick={(e) => {
                          e.stopPropagation()
                          submitRating(image.id, star)
                        }}
                        className={`text-sm ${
                          star <= (image.rating || 0)
                            ? 'text-yellow-400'
                            : 'text-gray-400 hover:text-yellow-400'
                        }`}
                      >
                        <Star className="w-3 h-3 fill-current" />
                      </button>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Process Log Panel */}
      <AnimatePresence>
        {showProcessLog && (
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            className="absolute top-0 right-0 w-80 h-full bg-black/80 backdrop-blur-md border-l border-gray-700 z-20"
          >
            <div className="p-4 h-full flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-white font-bold text-lg">Process Log</h3>
                <button
                  onClick={() => setShowProcessLog(false)}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              
              <div className="flex-1 overflow-y-auto space-y-3">
                {processSteps.map((step, index) => (
                  <motion.div
                    key={step.id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className={`p-3 rounded-lg border ${
                      step.status === 'completed' 
                        ? 'border-green-500 bg-green-500/10' 
                        : step.status === 'running'
                        ? 'border-blue-500 bg-blue-500/10'
                        : step.status === 'error'
                        ? 'border-red-500 bg-red-500/10'
                        : 'border-gray-600 bg-gray-600/10'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      {step.status === 'completed' ? (
                        <CheckCircle className="w-4 h-4 text-green-400" />
                      ) : step.status === 'running' ? (
                        <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                      ) : step.status === 'error' ? (
                        <AlertCircle className="w-4 h-4 text-red-400" />
                      ) : (
                        <Clock className="w-4 h-4 text-gray-400" />
                      )}
                      <span className={`text-sm font-medium ${
                        step.status === 'completed' 
                          ? 'text-green-400' 
                          : step.status === 'running'
                          ? 'text-blue-400'
                          : step.status === 'error'
                          ? 'text-red-400'
                          : 'text-gray-400'
                      }`}>
                        {step.title}
                      </span>
                    </div>
                    <p className="text-xs text-gray-300 mb-1">{step.description}</p>
                    {step.duration && (
                      <p className="text-xs text-gray-500">
                        Completed in {step.duration}ms
                      </p>
                    )}
                  </motion.div>
                ))}
              </div>
              
              {/* Summary */}
              <div className="mt-4 p-3 rounded-lg bg-gray-800/50">
                <div className="text-sm text-gray-300">
                  <div className="flex justify-between mb-1">
                    <span>Provider:</span>
                    <span className="text-white">{currentProvider || 'Selecting...'}</span>
                  </div>
                  <div className="flex justify-between mb-1">
                    <span>Status:</span>
                    <span className={`${
                      isGenerating ? 'text-blue-400' : error ? 'text-red-400' : 'text-green-400'
                    }`}>
                      {isGenerating ? 'Generating' : error ? 'Error' : 'Completed'}
                    </span>
                  </div>
                  {currentImage && (
                    <>
                      <div className="flex justify-between mb-1">
                        <span>Time:</span>
                        <span className="text-white">{currentImage.processingTime?.toFixed(2)}s</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Cost:</span>
                        <span className="text-white">${currentImage.cost?.toFixed(4) || '0.0000'}</span>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Bottom Info */}
      <div className="absolute bottom-4 left-4 bg-black/50 backdrop-blur-md rounded-lg px-4 py-2 text-white text-sm">
        <p className="font-medium">{generatedImages.length} Images Generated</p>
        <p className="text-xs text-gray-300 mt-1">
          {currentImage ? `Style: ${currentImage.style || 'None'}` : 'No image selected'}
        </p>
      </div>
    </div>
  )
}
