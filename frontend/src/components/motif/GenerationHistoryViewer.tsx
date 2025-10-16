'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Heart, Star, Tag, Download, Search, Filter, Calendar, Clock, Trash2 } from 'lucide-react'
import Image from 'next/image'

interface GenerationHistory {
  id: string
  user_id: string
  prompt: string
  enhanced_prompt: string
  style?: string
  generation_type: string
  status: string
  image_data?: string
  created_at: string
  completed_at?: string
  processing_time?: number
  rating?: number
  feedback?: string
  is_favorite: boolean
  tags: string[]
  metadata?: any
}

interface GenerationHistoryProps {
  userId: string
}

export function GenerationHistoryViewer({ userId }: GenerationHistoryProps) {
  const [generations, setGenerations] = useState<GenerationHistory[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStyle, setFilterStyle] = useState<string>('')
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false)
  const [currentPage, setCurrentPage] = useState(0)
  const [hasMore, setHasMore] = useState(true)

  const fetchHistory = useCallback(async (page = 0, reset = false) => {
    setLoading(true)
    setError(null)

    try {
      const params = new URLSearchParams({
        limit: '20',
        offset: (page * 20).toString(),
        ...(searchQuery && { search_query: searchQuery }),
        ...(filterStyle && { style: filterStyle }),
        ...(showFavoritesOnly && { favorites_only: 'true' })
      })

      const response = await fetch(`http://localhost:8000/motif/history/${userId}?${params}`)
      const data = await response.json()

      if (response.ok && data.success) {
        if (reset) {
          setGenerations(data.generations)
        } else {
          setGenerations(prev => [...prev, ...data.generations])
        }
        setHasMore(data.has_more)
        setCurrentPage(page)
      } else {
        setError(data.detail || 'Failed to fetch history')
      }
    } catch (err) {
      console.error('Error fetching history:', err)
      setError('Failed to connect to backend')
    } finally {
      setLoading(false)
    }
  }, [userId, searchQuery, filterStyle, showFavoritesOnly])

  useEffect(() => {
    fetchHistory(0, true)
  }, [fetchHistory])

  const toggleFavorite = async (generationId: string, isFavorite: boolean) => {
    try {
      const response = await fetch('http://localhost:8000/motif/history/favorite', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          generation_id: generationId,
          user_id: userId,
          is_favorite: !isFavorite
        })
      })

      const data = await response.json()
      if (response.ok && data.success) {
        setGenerations(prev => 
          prev.map(gen => 
            gen.id === generationId 
              ? { ...gen, is_favorite: data.is_favorite }
              : gen
          )
        )
      }
    } catch (err) {
      console.error('Error toggling favorite:', err)
    }
  }

  const handleDownload = (imageData: string, generationId: string) => {
    const link = document.createElement('a')
    link.href = imageData
    link.download = `motif_generation_${generationId}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const loadMore = () => {
    if (!loading && hasMore) {
      fetchHistory(currentPage + 1, false)
    }
  }

  const handleSearch = () => {
    fetchHistory(0, true)
  }

  const handleFilterChange = () => {
    fetchHistory(0, true)
  }

  return (
    <div className="bg-white/90 backdrop-blur-lg rounded-3xl shadow-xl p-8 max-h-[90vh] overflow-y-auto">
      <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">
        Generation History
      </h2>

      {/* Search and Filters */}
      <div className="mb-6 space-y-4">
        <div className="flex gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search prompts..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#6b46c1] focus:border-transparent"
              />
            </div>
          </div>
          <button
            onClick={handleSearch}
            className="px-4 py-2 bg-[#6b46c1] text-white rounded-lg hover:bg-[#5a3a9a] transition-colors"
          >
            Search
          </button>
        </div>

        <div className="flex gap-4 items-center">
          <select
            value={filterStyle}
            onChange={(e) => {
              setFilterStyle(e.target.value)
              handleFilterChange()
            }}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#6b46c1] focus:border-transparent"
          >
            <option value="">All Styles</option>
            <option value="party">Party</option>
            <option value="elegant">Elegant</option>
            <option value="fun">Fun</option>
            <option value="romantic">Romantic</option>
            <option value="birthday">Birthday</option>
            <option value="wedding">Wedding</option>
            <option value="holiday">Holiday</option>
          </select>

          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={showFavoritesOnly}
              onChange={(e) => {
                setShowFavoritesOnly(e.target.checked)
                handleFilterChange()
              }}
              className="rounded"
            />
            <span className="text-sm text-gray-700">Favorites Only</span>
          </label>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-xl mb-6">
          <strong className="font-bold">Error!</strong>
          <span className="block sm:inline"> {error}</span>
        </div>
      )}

      {/* Loading State */}
      {loading && generations.length === 0 && (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#6b46c1]"></div>
        </div>
      )}

      {/* Generations Grid */}
      <AnimatePresence>
        {generations.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
          >
            {generations.map((generation) => (
              <motion.div
                key={generation.id}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="bg-gray-50 rounded-xl shadow-md overflow-hidden border border-gray-200"
              >
                {/* Image */}
                <div className="relative w-full h-48 bg-gray-200 flex items-center justify-center">
                  {generation.image_data ? (
                    <Image
                      src={generation.image_data}
                      alt={`Generated decoration ${generation.id}`}
                      layout="fill"
                      objectFit="contain"
                    />
                  ) : (
                    <span className="text-gray-500">No image data</span>
                  )}
                  
                  {/* Favorite Button */}
                  <button
                    onClick={() => toggleFavorite(generation.id, generation.is_favorite)}
                    className="absolute top-2 right-2 p-2 rounded-full bg-white/80 backdrop-blur-sm hover:bg-white transition-colors"
                  >
                    <Heart
                      className={`w-5 h-5 ${
                        generation.is_favorite ? 'text-red-500 fill-current' : 'text-gray-400'
                      }`}
                    />
                  </button>
                </div>

                {/* Content */}
                <div className="p-4">
                  <p className="text-sm text-gray-700 mb-2 line-clamp-2">
                    {generation.prompt}
                  </p>
                  
                  {generation.style && (
                    <span className="inline-block px-2 py-1 bg-[#6b46c1]/10 text-[#6b46c1] text-xs rounded-full mb-2">
                      {generation.style}
                    </span>
                  )}

                  {/* Tags */}
                  {generation.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-2">
                      {generation.tags.map((tag, index) => (
                        <span
                          key={index}
                          className="inline-flex items-center gap-1 px-2 py-1 bg-gray-200 text-gray-700 text-xs rounded-full"
                        >
                          <Tag className="w-3 h-3" />
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Rating */}
                  {generation.rating && (
                    <div className="flex items-center gap-1 mb-2">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <Star
                          key={star}
                          className={`w-4 h-4 ${
                            star <= generation.rating! ? 'text-yellow-400 fill-current' : 'text-gray-300'
                          }`}
                        />
                      ))}
                    </div>
                  )}

                  {/* Metadata */}
                  <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                    <div className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {new Date(generation.created_at).toLocaleDateString()}
                    </div>
                    {generation.processing_time && (
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {generation.processing_time.toFixed(1)}s
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center justify-between">
                    <button
                      onClick={() => handleDownload(generation.image_data!, generation.id)}
                      className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-[#6b46c1] text-white text-sm hover:bg-[#5a3a9a] transition-colors"
                    >
                      <Download className="w-4 h-4" /> Download
                    </button>
                    
                    <button
                      className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Load More Button */}
      {hasMore && generations.length > 0 && (
        <div className="text-center mt-8">
          <button
            onClick={loadMore}
            disabled={loading}
            className={`px-6 py-3 rounded-full font-medium transition-all ${
              loading
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-[#6b46c1] text-white hover:bg-[#5a3a9a]'
            }`}
          >
            {loading ? 'Loading...' : 'Load More'}
          </button>
        </div>
      )}

      {/* Empty State */}
      {!loading && generations.length === 0 && !error && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <Calendar className="w-16 h-16 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No generations found</h3>
          <p className="text-gray-600">
            {showFavoritesOnly 
              ? "You haven't marked any generations as favorites yet."
              : "Start generating images to see them here."
            }
          </p>
        </div>
      )}
    </div>
  )
}
