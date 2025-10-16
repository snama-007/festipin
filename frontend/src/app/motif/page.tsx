'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { useState, useCallback } from 'react'
import { Upload, Image as ImageIcon, Wand2, Sparkles, ArrowRight, CheckCircle2, X } from 'lucide-react'
import dynamic from 'next/dynamic'

// Dynamically import image generation components
const ImageGenerationViewer = dynamic(
  () => import('@/components/motif/ImageGenerationViewer').then(mod => mod.ImageGenerationViewer),
  { ssr: false }
)

const GenerationHistoryViewer = dynamic(
  () => import('@/components/motif/GenerationHistoryViewer').then(mod => mod.GenerationHistoryViewer),
  { ssr: false }
)

export default function MotifPage() {
  const [isDragging, setIsDragging] = useState(false)
  const [uploadedImage, setUploadedImage] = useState<string | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [processingStage, setProcessingStage] = useState('')
  const [progress, setProgress] = useState(0)
  const [showImageGeneration, setShowImageGeneration] = useState(false)
  const [prompt, setPrompt] = useState('')
  const [selectedStyle, setSelectedStyle] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'generate' | 'history'>('generate')

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const files = e.dataTransfer.files
    if (files.length > 0) {
      const file = files[0]
      if (file.type.startsWith('image/')) {
        const reader = new FileReader()
        reader.onload = (e) => {
          setUploadedImage(e.target?.result as string)
        }
        reader.readAsDataURL(file)
      }
    }
  }, [])

  const handleFileUpload = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setUploadedImage(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  }, [])

  const simulateProcessing = useCallback(async () => {
    const stages = [
      { stage: 'Analyzing image...', duration: 1000, progress: 20 },
      { stage: 'Detecting decorations...', duration: 1500, progress: 40 },
      { stage: 'Creating 3D models...', duration: 2000, progress: 70 },
      { stage: 'Building scene...', duration: 1000, progress: 90 },
      { stage: 'Complete!', duration: 500, progress: 100 }
    ]

    for (const { stage, duration, progress } of stages) {
      setProcessingStage(stage)
      setProgress(progress)
      
      if (duration > 0) {
        await new Promise(resolve => setTimeout(resolve, duration))
      } else {
        await new Promise(resolve => setTimeout(resolve, 100))
      }
    }
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100">
      {/* Subtle Pattern Overlay */}
      <div className="absolute inset-0 opacity-30">
        <div className="absolute inset-0" style={{
          backgroundImage: `radial-gradient(circle at 1px 1px, rgba(107, 70, 193, 0.15) 1px, transparent 0)`,
          backgroundSize: '20px 20px'
        }} />
      </div>

      {/* Navigation */}
      <nav className="relative z-10 p-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#6b46c1] to-[#8b5cf6] flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">Motif</h1>
          </div>
          
          <div className="flex items-center gap-4">
            <button className="px-4 py-2 rounded-full bg-white/80 backdrop-blur-sm border border-gray-200/50 text-gray-700 hover:bg-white transition-all">
              Back to Dashboard
            </button>
          </div>
        </div>
      </nav>

      <div className="relative z-10 max-w-7xl mx-auto px-6 pb-20">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[#6b46c1]/10 text-[#6b46c1] text-sm font-medium mb-6">
            <Sparkles className="w-4 h-4" />
            AI-Powered Image Generation
          </div>

          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Generate Your<br/>
            <span className="text-[#6b46c1]">Party Decorations</span>
          </h1>

          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Transform your party vision into stunning decorations with AI-powered image generation. 
            Upload inspiration images or describe your dream celebration.
          </p>

          {/* Tab Navigation */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="flex justify-center mb-8"
          >
            <div className="bg-white/70 backdrop-blur-sm border border-gray-200/50 rounded-2xl p-2">
              <div className="flex gap-2">
                <button
                  onClick={() => setActiveTab('generate')}
                  className={`px-6 py-3 rounded-xl font-medium transition-all ${
                    activeTab === 'generate'
                      ? 'bg-[#6b46c1] text-white shadow-lg'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  Generate
                </button>
                <button
                  onClick={() => setActiveTab('history')}
                  className={`px-6 py-3 rounded-xl font-medium transition-all ${
                    activeTab === 'history'
                      ? 'bg-[#6b46c1] text-white shadow-lg'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  History
                </button>
              </div>
            </div>
          </motion.div>

          {/* Tab Content */}
          <AnimatePresence mode="wait">
            {activeTab === 'generate' ? (
              <motion.div
                key="generate"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.3 }}
              >
                {/* Upload Area */}
                <AnimatePresence mode="wait">
                  {!uploadedImage ? (
                    <motion.div
                      key="upload"
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      transition={{ duration: 0.3 }}
                      className="relative"
                    >
                      <div
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                        className={`relative border-2 border-dashed rounded-3xl p-12 transition-all cursor-pointer ${
                          isDragging
                            ? 'border-[#6b46c1] bg-[#6b46c1]/5 scale-105'
                            : 'border-gray-300 hover:border-[#6b46c1] hover:bg-[#6b46c1]/5'
                        }`}
                        onClick={() => document.getElementById('file-upload')?.click()}
                      >
                        <input
                          id="file-upload"
                          type="file"
                          accept="image/*"
                          onChange={handleFileUpload}
                          className="hidden"
                        />
                        
                        <div className="text-center">
                          <div className={`w-20 h-20 mx-auto mb-6 rounded-2xl flex items-center justify-center transition-all ${
                            isDragging ? 'bg-[#6b46c1] text-white' : 'bg-gray-100 text-gray-400'
                          }`}>
                            <Upload className="w-10 h-10" />
                          </div>
                          
                          <h3 className="text-2xl font-bold text-gray-900 mb-3">
                            {isDragging ? 'Drop your image here' : 'Upload inspiration image (optional)'}
                          </h3>
                          
                          <p className="text-gray-600 mb-6">
                            Drag and drop an image, or click to browse
                          </p>
                          
                          <div className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-white border border-gray-200 text-gray-700 hover:bg-gray-50 transition-all">
                            <ImageIcon className="w-5 h-5" />
                            Choose Image
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  ) : (
                    <motion.div
                      key="preview"
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      transition={{ duration: 0.3 }}
                      className="relative"
                    >
                      <div className="relative w-full max-w-md mx-auto">
                        <img
                          src={uploadedImage}
                          alt="Uploaded inspiration"
                          className="w-full h-64 object-cover rounded-2xl shadow-lg"
                        />
                        <button
                          onClick={() => setUploadedImage(null)}
                          className="absolute -top-3 -right-3 w-8 h-8 rounded-full bg-red-500 text-white flex items-center justify-center hover:bg-red-600 transition-colors"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Prompt Input */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.3 }}
                  className="mt-8"
                >
                  <div className="max-w-2xl mx-auto">
                    <label className="block text-lg font-semibold text-gray-900 mb-4">
                      Describe your decoration vision
                    </label>
                    <textarea
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      placeholder="e.g., A beautiful balloon arch with gold and white balloons, elegant centerpieces with candles..."
                      className="w-full h-32 px-6 py-4 rounded-2xl border border-gray-200 focus:ring-2 focus:ring-[#6b46c1] focus:border-transparent resize-none text-gray-900 placeholder-gray-500"
                    />
                    
                    <div className="mt-6 flex items-center justify-center">
                      <motion.button
                        onClick={() => setShowImageGeneration(true)}
                        disabled={!prompt.trim()}
                        className={`inline-flex items-center gap-3 px-8 py-4 rounded-2xl font-semibold text-lg transition-all ${
                          prompt.trim()
                            ? 'bg-[#6b46c1] text-white hover:bg-[#5a3a9a] shadow-lg hover:shadow-xl'
                            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        }`}
                        whileHover={prompt.trim() ? { scale: 1.05 } : {}}
                        whileTap={prompt.trim() ? { scale: 0.95 } : {}}
                      >
                        <Wand2 className="w-6 h-6" />
                        Generate Decoration
                      </motion.button>
                    </div>
                  </div>
                </motion.div>
              </motion.div>
            ) : (
              <motion.div
                key="history"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                <GenerationHistoryViewer userId="test_user" />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="grid md:grid-cols-3 gap-6 mb-12"
        >
          {[
            {
              icon: '🎨',
              title: 'AI Image Generation',
              description: 'Generate beautiful party decorations using Google Gemini Flash AI'
            },
            {
              icon: '🎭',
              title: 'Style Presets',
              description: 'Choose from Party, Elegant, Fun, and Romantic style themes'
            },
            {
              icon: '✨',
              title: 'Custom Prompts',
              description: 'Describe your vision and let AI create unique decorations'
            }
          ].map((feature, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 + idx * 0.1 }}
              className="p-6 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200/50"
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">{feature.title}</h3>
              <p className="text-sm text-gray-600">{feature.description}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Image Generation Modal */}
        <AnimatePresence>
          {showImageGeneration && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-6"
              onClick={() => setShowImageGeneration(false)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                onClick={(e) => e.stopPropagation()}
                className="relative w-full max-w-6xl"
              >
                <button
                  onClick={() => setShowImageGeneration(false)}
                  className="absolute -top-12 right-0 text-white hover:text-gray-300 transition-colors"
                >
                  <X className="w-8 h-8" />
                </button>

                <ImageGenerationViewer 
                  prompt={prompt}
                  style={selectedStyle}
                  inspirationImage={uploadedImage || undefined}
                />
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* How It Works */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="text-center"
        >
          <h2 className="text-3xl font-bold text-gray-900 mb-8">How It Works</h2>
          <div className="grid md:grid-cols-4 gap-6">
            {[
              { step: '1', title: 'Describe', desc: 'Tell us your decoration vision' },
              { step: '2', title: 'Choose Style', desc: 'Select from preset themes' },
              { step: '3', title: 'AI Generation', desc: 'Gemini Flash creates your design' },
              { step: '4', title: 'Download', desc: 'Get your custom decoration' }
            ].map((item, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 + idx * 0.1 }}
                className="text-center"
              >
                <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-[#6b46c1] text-white flex items-center justify-center font-bold text-lg">
                  {item.step}
                </div>
                <h3 className="font-bold text-gray-900 mb-2">{item.title}</h3>
                <p className="text-sm text-gray-600">{item.desc}</p>
                {idx < 3 && (
                  <div className="hidden md:block absolute top-6 left-full w-full h-0.5 bg-gray-200 transform translate-x-6">
                    <div className="w-full h-full bg-[#6b46c1] rounded-full" />
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  )
}