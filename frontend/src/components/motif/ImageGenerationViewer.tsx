'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Wand2, Download, RefreshCw, Star, X, Loader2 } from 'lucide-react'

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

  // Generate image on component mount
  useEffect(() => {
    if (prompt.trim()) {
      generateImage()
    }
  }, [prompt, style])

  const generateImage = async () => {
    setIsGenerating(true)
    setError(null)

    try {
      const requestBody = {
        prompt: prompt,
        style: style,
        user_id: 'user_' + Date.now()
      }

      const response = await fetch('http://localhost:8000/motif/generation/generate-from-prompt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      })

      if (!response.ok) {
        throw new Error('Failed to generate image')
      }

      const data = await response.json()

      if (data.success) {
        const newImage: GeneratedImage = {
          id: data.generation_id,
          imageData: data.image_data,
          prompt: data.prompt_used,
          style: data.style_applied,
          generatedAt: new Date().toISOString()
        }

        setGeneratedImages(prev => [newImage, ...prev])
        setCurrentImage(newImage)
      } else {
        throw new Error(data.error || 'Generation failed')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsGenerating(false)
    }
  }

  const generateFromInspiration = async () => {
    if (!inspirationImage) return

    setIsGenerating(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('prompt', prompt)
      if (style) formData.append('style', style)
      formData.append('user_id', 'user_' + Date.now())

      // Convert data URL to blob
      const response = await fetch(inspirationImage)
      const blob = await response.blob()
      formData.append('inspiration_image', blob, 'inspiration.jpg')

      const apiResponse = await fetch('http://localhost:8000/motif/generation/generate-from-inspiration', {
        method: 'POST',
        body: formData
      })

      if (!apiResponse.ok) {
        throw new Error('Failed to generate image from inspiration')
      }

      const data = await apiResponse.json()

      if (data.success) {
        const newImage: GeneratedImage = {
          id: data.generation_id,
          imageData: data.image_data,
          prompt: data.prompt_used,
          style: data.style_applied,
          generatedAt: new Date().toISOString()
        }

        setGeneratedImages(prev => [newImage, ...prev])
        setCurrentImage(newImage)
      } else {
        throw new Error(data.error || 'Generation failed')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsGenerating(false)
    }
  }

  const submitRating = async (imageId: string, rating: number) => {
    try {
      const response = await fetch(`http://localhost:8000/motif/generation/feedback/${imageId}`, {
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
    <div className="w-full h-[600px] rounded-2xl overflow-hidden bg-gradient-to-br from-gray-900 to-gray-800">
      {/* Header */}
      <div className="absolute top-4 left-4 bg-black/50 backdrop-blur-md rounded-lg px-4 py-2 text-white text-sm z-10">
        <p className="font-medium">🎨 AI Image Generation</p>
        <p className="text-xs text-gray-300 mt-1">Powered by Google Gemini Flash</p>
      </div>

      {/* Generation Controls */}
      <div className="absolute top-4 right-4 bg-black/50 backdrop-blur-md rounded-lg px-4 py-2 text-white text-sm z-10">
        <div className="flex gap-2">
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
          
          {inspirationImage && (
            <button
              onClick={generateFromInspiration}
              disabled={isGenerating}
              className="flex items-center gap-1 px-3 py-1 rounded bg-green-600 hover:bg-green-700 disabled:opacity-50"
            >
              <RefreshCw className="w-4 h-4" />
              From Image
            </button>
          )}
        </div>
      </div>

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
                <p className="text-gray-300">AI is creating your party decoration...</p>
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
