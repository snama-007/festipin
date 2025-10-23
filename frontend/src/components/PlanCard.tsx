'use client'

import { motion } from 'framer-motion'

interface PlanCardProps {
  type: 'theme' | 'venue' | 'cake' | 'catering' | 'vendor'
  title: string
  data: any
  status: string
}

export function PlanCard({ type, title, data, status }: PlanCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800 border-green-200'
      case 'running': return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'error': return 'bg-red-100 text-red-800 border-red-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return '✅'
      case 'running': return '⏳'
      case 'error': return '❌'
      default: return '⏸️'
    }
  }

  const renderCardContent = () => {
    switch (type) {
      case 'theme':
        return (
          <div className="space-y-3">
            <div className="text-2xl font-bold text-purple-700">{data.primary_theme}</div>
            <div className="flex flex-wrap gap-2">
              {data.color_scheme?.map((color: string, index: number) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm"
                >
                  {color}
                </span>
              ))}
            </div>
            <div className="text-sm text-gray-600">
              <div className="font-medium mb-1">Decorations:</div>
              <ul className="list-disc list-inside space-y-1">
                {data.decorations?.slice(0, 3).map((decoration: string, index: number) => (
                  <li key={index}>{decoration}</li>
                ))}
              </ul>
            </div>
            <div className="text-sm">
              <span className="font-medium">Mood:</span> {data.mood}
            </div>
          </div>
        )

      case 'venue':
        const venue = data.recommended_venues?.[0]
        return (
          <div className="space-y-3">
            {venue ? (
              <>
                <div className="text-xl font-bold text-blue-700">{venue.name}</div>
                <div className="text-sm text-gray-600">
                  <div className="flex items-center gap-2 mb-1">
                    <span>📍</span>
                    <span>{venue.location}</span>
                  </div>
                  <div className="flex items-center gap-2 mb-1">
                    <span>👥</span>
                    <span>Capacity: {venue.capacity} guests</span>
                  </div>
                  <div className="flex items-center gap-2 mb-2">
                    <span>💰</span>
                    <span>{venue.price_range}</span>
                  </div>
                </div>
                <div className="text-sm">
                  <div className="font-medium mb-1">Features:</div>
                  <div className="flex flex-wrap gap-1">
                    {venue.features?.slice(0, 3).map((feature: string, index: number) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs"
                      >
                        {feature}
                      </span>
                    ))}
                  </div>
                </div>
              </>
            ) : (
              <div className="text-gray-500">No venue recommendations yet</div>
            )}
          </div>
        )

      case 'cake':
        const cake = data.cake_suggestions?.[0]
        return (
          <div className="space-y-3">
            {cake ? (
              <>
                <div className="text-xl font-bold text-pink-700">{cake.type}</div>
                <div className="text-sm text-gray-600">
                  <div className="mb-1">
                    <span className="font-medium">Flavor:</span> {cake.flavor}
                  </div>
                  <div className="mb-1">
                    <span className="font-medium">Size:</span> {cake.size}
                  </div>
                  <div className="mb-1">
                    <span className="font-medium">Price:</span> {cake.price_range}
                  </div>
                  <div>
                    <span className="font-medium">Bakery:</span> {cake.bakery}
                  </div>
                </div>
              </>
            ) : (
              <div className="text-gray-500">No cake suggestions yet</div>
            )}
          </div>
        )

      case 'catering':
        return (
          <div className="space-y-3">
            {data.menu_suggestions?.map((menu: any, index: number) => (
              <div key={index}>
                <div className="font-medium text-orange-700 mb-2">{menu.category}</div>
                <div className="text-sm text-gray-600">
                  <div className="mb-1">
                    <span className="font-medium">Items:</span>
                    <ul className="list-disc list-inside ml-2">
                      {menu.items?.slice(0, 3).map((item: string, itemIndex: number) => (
                        <li key={itemIndex}>{item}</li>
                      ))}
                    </ul>
                  </div>
                  {menu.dietary_options && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {menu.dietary_options.map((option: string, optIndex: number) => (
                        <span
                          key={optIndex}
                          className="px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs"
                        >
                          {option}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )

      case 'vendor':
        return (
          <div className="space-y-3">
            {data.vendor_suggestions?.slice(0, 2).map((vendor: any, index: number) => (
              <div key={index} className="border-l-4 border-purple-300 pl-3">
                <div className="font-medium text-purple-700">{vendor.name}</div>
                <div className="text-sm text-gray-600">
                  <div className="mb-1">
                    <span className="font-medium">Type:</span> {vendor.type}
                  </div>
                  <div className="mb-1">
                    <span className="font-medium">Services:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {vendor.services?.slice(0, 2).map((service: string, sIndex: number) => (
                        <span
                          key={sIndex}
                          className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs"
                        >
                          {service}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <span className="font-medium">Price:</span> {vendor.price_range}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )

      default:
        return <div className="text-gray-500">No data available</div>
    }
  }

  return (
    <motion.div
      whileHover={{ 
        scale: 1.05, 
        y: -10,
        transition: { duration: 0.3 }
      }}
      className="relative group bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl border border-white/50 overflow-hidden"
      style={{
        background: `
          linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%),
          radial-gradient(circle at top right, rgba(255,182,193,0.1) 0%, transparent 50%)
        `
      }}
    >
      {/* Magical shimmer effect */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
        animate={{ x: ["-100%", "100%"] }}
        transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
      />
      
      <div className="relative z-10 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            {title}
          </h3>
          <motion.span 
            className={`px-4 py-2 rounded-full text-sm font-bold border-2 ${getStatusColor(status)} shadow-lg`}
            whileHover={{ scale: 1.1 }}
          >
            {getStatusIcon(status)} {status}
          </motion.span>
        </div>
        
        <div className="min-h-[140px]">
          {renderCardContent()}
        </div>
      </div>
      
      {/* Magical border glow */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-pink-400 via-purple-400 to-blue-400 opacity-0 group-hover:opacity-20 transition-opacity duration-300" />
    </motion.div>
  )
}
