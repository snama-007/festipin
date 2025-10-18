/**
 * Dynamic Input Components for Party Planning Data Collection
 * Builds forms dynamically based on missing fields from backend agent
 */

import React, { useEffect, useMemo, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ExtractedEventData } from '../services/api'

export interface DataInputProps {
  extractedData: ExtractedEventData
  missingFields: string[]
  suggestions: string[]
  onDataComplete: (data: ExtractedEventData) => void
  onSkip: () => void
}

// Simplified field configuration
const FIELD_CONFIG = {
  eventType: {
    label: "Event Type",
    type: "select",
    options: ['Birthday', 'Wedding', 'Anniversary', 'Baby Shower', 'Graduation', 'Retirement', 'Holiday Party', 'Other']
  },
  title: {
    label: "Event Title",
    type: "text",
    placeholder: "e.g., Sarah's 5th Birthday"
  },
  honoreeName: {
    label: "Who is this for?",
    type: "text",
    placeholder: "e.g., Sarah"
  },
  age: {
    label: "Age",
    type: "number",
    placeholder: "5",
    min: 0,
    max: 120
  },
  theme: {
    label: "Theme",
    type: "select",
    options: ['Princess', 'Superhero', 'Unicorn', 'Dinosaur', 'Space', 'Pirate', 'Fairy', 'Mermaid', 'Jungle', 'Circus', 'Modern', 'Vintage', 'Tropical', 'Beach', 'Garden', 'Disney', 'Other']
  },
  date: {
    label: "Date",
    type: "date"
  },
  time: {
    label: "Time",
    type: "time-range"
  },
  guestCount: {
    label: "Guests",
    type: "guest-count"
  },
  budget: {
    label: "Budget",
    type: "budget-range"
  },
  location: {
    label: "Location",
    type: "location"
  },
  foodPreference: {
    label: "Food",
    type: "select",
    options: ['Veg', 'Non-Veg', 'Mixed', 'No Preference']
  },
  activities: {
    label: "Activities",
    type: "multi-select",
    options: ['Balloon Twisting', 'Magic Show', 'Face Painting', 'Pinata', 'Bouncy Castle', 'Photo Booth', 'Dancing', 'Karaoke', 'Treasure Hunt', 'Crafts']
  }
}

const FIELD_NAME_ALIASES: Record<string, keyof typeof FIELD_CONFIG> = {
  eventtype: 'eventType',
  eventtitle: 'title',
  title: 'title',
  honoreename: 'honoreeName',
  honoree: 'honoreeName',
  hostname: 'honoreeName',
  age: 'age',
  theme: 'theme',
  themename: 'theme',
  date: 'date',
  time: 'time',
  timerange: 'time',
  timestart: 'time',
  timeend: 'time',
  guestcount: 'guestCount',
  guestcountadults: 'guestCount',
  guestcountkids: 'guestCount',
  guestcountchildren: 'guestCount',
  budget: 'budget',
  budgetrange: 'budget',
  budgetmin: 'budget',
  budgetmax: 'budget',
  location: 'location',
  locationtype: 'location',
  locationname: 'location',
  locationaddress: 'location',
  locationdetails: 'location',
  foodpreference: 'foodPreference',
  foodpreferences: 'foodPreference',
  activities: 'activities',
  activitypreferences: 'activities',
  activitieslist: 'activities',
}

const isSupportedField = (fieldName: string): fieldName is keyof typeof FIELD_CONFIG => {
  return Object.prototype.hasOwnProperty.call(FIELD_CONFIG, fieldName)
}

const toCamelCase = (value: string) => {
  if (!value) return value
  if (!/[_\s.-]/.test(value)) {
    return value.charAt(0).toLowerCase() + value.slice(1)
  }
  const sanitized = value.replace(/\./g, ' ')
  const parts = sanitized.split(/[_\s-]+/).filter(Boolean)
  return parts
    .map((part, index) => {
      if (index === 0) return part.toLowerCase()
      return part.charAt(0).toUpperCase() + part.slice(1).toLowerCase()
    })
    .join('')
}

const getAliasKey = (value: string) => value.replace(/[^a-zA-Z0-9]/g, '').toLowerCase()

const resolveAlias = (value: string): keyof typeof FIELD_CONFIG | null => {
  const alias = FIELD_NAME_ALIASES[getAliasKey(value)]
  return alias ?? null
}

const normalizeFieldName = (rawFieldName: string): keyof typeof FIELD_CONFIG | null => {
  if (!rawFieldName) return null

  const trimmed = rawFieldName.trim()
  if (!trimmed) return null

  const segments = trimmed.split('.')
  const baseSegment = segments[0]

  const candidates = [
    trimmed,
    trimmed.replace(/\./g, '_'),
    trimmed.replace(/\./g, ' '),
    baseSegment,
    baseSegment.replace(/_/g, ' '),
    toCamelCase(trimmed),
    toCamelCase(trimmed.replace(/\./g, '_')),
    toCamelCase(baseSegment)
  ]

  for (const candidate of candidates) {
    if (!candidate) continue
    if (isSupportedField(candidate)) {
      return candidate
    }
    const alias = resolveAlias(candidate)
    if (alias) {
      return alias
    }
  }

  return null
}

const cloneValue = (value: any) => {
  if (Array.isArray(value)) {
    return [...value]
  }
  if (value && typeof value === 'object') {
    return { ...value }
  }
  if (value === undefined || value === null) {
    return ''
  }
  return value
}

const getDefaultValue = (field: keyof typeof FIELD_CONFIG) => {
  switch (field) {
    case 'time':
      return { start: '', end: '' }
    case 'guestCount':
      return { adults: 0, kids: 0 }
    case 'budget':
      return { min: 0, max: 0 }
    case 'location':
      return { type: '', name: '', address: '' }
    case 'activities':
      return []
    default:
      return ''
  }
}

const buildInitialFormData = (
  baseData: ExtractedEventData,
  fields: (keyof typeof FIELD_CONFIG)[]
): ExtractedEventData => {
  const initialData: ExtractedEventData = { ...baseData }

  fields.forEach(field => {
    const existingValue = baseData[field as keyof ExtractedEventData]
    if (existingValue === undefined || existingValue === null) {
      initialData[field as keyof ExtractedEventData] = cloneValue(getDefaultValue(field)) as any
    } else {
      initialData[field as keyof ExtractedEventData] = cloneValue(existingValue) as any
    }
  })

  return initialData
}

export const DataInputForm: React.FC<DataInputProps> = ({
  extractedData,
  missingFields,
  suggestions,
  onDataComplete,
  onSkip
}) => {
  const normalizedMissingFields = useMemo(() => {
    const collected: (keyof typeof FIELD_CONFIG)[] = []
    const seen = new Set<keyof typeof FIELD_CONFIG>()

    missingFields.forEach(fieldName => {
      const normalized = normalizeFieldName(fieldName)
      if (normalized && !seen.has(normalized)) {
        seen.add(normalized)
        collected.push(normalized)
      }
    })

    return collected
  }, [missingFields])

  const [formData, setFormData] = useState<ExtractedEventData>(() =>
    buildInitialFormData(extractedData, normalizedMissingFields)
  )
  const [isSubmitting, setIsSubmitting] = useState(false)
  const previousMissingSignatureRef = useRef<string>('')
  const previousExtractedSignatureRef = useRef<string>('')

  useEffect(() => {
    const missingSignature = normalizedMissingFields.join('|')
    const extractedSignature = JSON.stringify(extractedData || {})

    if (
      previousMissingSignatureRef.current === missingSignature &&
      previousExtractedSignatureRef.current === extractedSignature
    ) {
      return
    }

    previousMissingSignatureRef.current = missingSignature
    previousExtractedSignatureRef.current = extractedSignature

    setFormData(prevData => {
      const mergedBase: ExtractedEventData = { ...extractedData }

      normalizedMissingFields.forEach(field => {
        if (prevData[field as keyof ExtractedEventData] !== undefined) {
          mergedBase[field as keyof ExtractedEventData] = cloneValue(
            prevData[field as keyof ExtractedEventData]
          ) as any
        }
      })

      return buildInitialFormData(mergedBase, normalizedMissingFields)
    })
  }, [extractedData, normalizedMissingFields])

  const updateFormData = (field: keyof ExtractedEventData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)
    await new Promise(resolve => setTimeout(resolve, 1000))
    onDataComplete(formData)
    setIsSubmitting(false)
  }

  const renderField = (fieldName: keyof typeof FIELD_CONFIG) => {
    const config = FIELD_CONFIG[fieldName]
    if (!config) return null

    const currentValue = formData[fieldName as keyof ExtractedEventData]

    switch (config.type) {
      case 'select':
        return (
          <SelectField
            config={config}
            value={currentValue as string}
            onChange={(value) => updateFormData(fieldName as keyof ExtractedEventData, value)}
          />
        )
      case 'text':
        return (
          <TextField
            config={config}
            value={currentValue as string}
            onChange={(value) => updateFormData(fieldName as keyof ExtractedEventData, value)}
          />
        )
      case 'number':
        return (
          <NumberField
            config={config}
            value={currentValue as number}
            onChange={(value) => updateFormData(fieldName as keyof ExtractedEventData, value)}
          />
        )
      case 'date':
        return (
          <DateField
            config={config}
            value={currentValue as string}
            onChange={(value) => updateFormData(fieldName as keyof ExtractedEventData, value)}
          />
        )
      case 'time-range':
        return (
          <TimeRangeField
            config={config}
            value={currentValue as { start: string; end: string }}
            onChange={(value) => updateFormData(fieldName as keyof ExtractedEventData, value)}
          />
        )
      case 'guest-count':
        return (
          <GuestCountField
            config={config}
            value={currentValue as { adults: number; kids: number }}
            onChange={(value) => updateFormData(fieldName as keyof ExtractedEventData, value)}
          />
        )
      case 'budget-range':
        return (
          <BudgetRangeField
            config={config}
            value={currentValue as { min: number; max: number }}
            onChange={(value) => updateFormData(fieldName as keyof ExtractedEventData, value)}
          />
        )
      case 'location':
        return (
          <LocationField
            config={config}
            value={currentValue as { type: string; name: string; address: string }}
            onChange={(value) => updateFormData(fieldName as keyof ExtractedEventData, value)}
          />
        )
      case 'multi-select':
        return (
          <MultiSelectField
            config={config}
            value={currentValue as string[]}
            onChange={(value) => updateFormData(fieldName as keyof ExtractedEventData, value)}
          />
        )
      default:
        return null
    }
  }

  if (normalizedMissingFields.length === 0) {
    return null
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-gradient-to-br from-purple-900/20 via-pink-900/20 to-orange-900/20 backdrop-blur-md z-[100] flex items-center justify-center p-4"
    >
      {/* Festive Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(8)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-3 h-3 rounded-full"
            style={{
              background: `linear-gradient(45deg, 
                ${['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3', '#54a0ff', '#5f27cd'][i % 8]}, 
                ${['#ff8e8e', '#6ed5d0', '#6bc5d8', '#a8d5c0', '#fed766', '#ffb3f3', '#74b0ff', '#7c3aed'][i % 8]})`,
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -30, 0],
              x: [0, Math.random() * 20 - 10, 0],
              opacity: [0.3, 0.8, 0.3],
              scale: [1, 1.2, 1],
            }}
            transition={{
              duration: 4 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
              ease: "easeInOut"
            }}
          />
        ))}
      </div>

      <motion.div
        initial={{ scale: 0.9, opacity: 0, y: 20 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        exit={{ scale: 0.9, opacity: 0, y: -20 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
        className="bg-gradient-to-br from-white via-pink-50/80 to-purple-50/80 backdrop-blur-xl rounded-3xl shadow-2xl max-w-lg w-full max-h-[85vh] overflow-hidden flex flex-col border border-white/30 relative"
        style={{
          boxShadow: `
            0 25px 50px rgba(0, 0, 0, 0.15),
            0 0 0 1px rgba(255, 255, 255, 0.8),
            inset 0 1px 0 rgba(255, 255, 255, 0.9)
          `
        }}
      >
        {/* Festive Header */}
        <div className="p-6 border-b border-gradient-to-r from-pink-200/50 to-purple-200/50 bg-gradient-to-r from-pink-50/50 to-purple-50/50">
          <div className="flex items-center justify-between">
            <div>
              <motion.h2 
                className="text-2xl font-bold bg-gradient-to-r from-pink-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                🎉 Complete Your Party Details
              </motion.h2>
              <motion.p 
                className="text-sm text-gray-600 mt-1 font-medium"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                Let's make your celebration magical! ✨
              </motion.p>
            </div>
            <motion.button
              onClick={onSkip}
              className="w-10 h-10 rounded-full bg-gradient-to-r from-gray-100 to-gray-200 hover:from-pink-100 hover:to-purple-100 flex items-center justify-center text-gray-500 hover:text-pink-600 transition-all duration-300 shadow-lg hover:shadow-xl"
              whileHover={{ scale: 1.1, rotate: 90 }}
              whileTap={{ scale: 0.95 }}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </motion.button>
          </div>
        </div>

        {/* Festive Content */}
        <div className="p-6 overflow-y-auto flex-grow bg-gradient-to-b from-transparent via-pink-50/20 to-purple-50/20">
          <div className="space-y-5">
            {normalizedMissingFields.map((fieldName, index) => (
              <motion.div
                key={fieldName}
                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ 
                  delay: index * 0.1,
                  type: "spring",
                  stiffness: 300,
                  damping: 25
                }}
                className="relative group"
              >
                {/* Festive Field Container */}
                <div className="relative p-1 rounded-2xl bg-gradient-to-r from-pink-200/30 via-purple-200/30 to-indigo-200/30 backdrop-blur-sm">
                  <div className="bg-white/90 backdrop-blur-sm rounded-xl p-4 border border-white/50 shadow-lg group-hover:shadow-xl transition-all duration-300">
                    {renderField(fieldName)}
                  </div>
                  
                  {/* Festive Glow Effect */}
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-pink-400/20 via-purple-400/20 to-indigo-400/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-sm pointer-events-none" />
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Festive Footer */}
        <div className="p-6 border-t border-gradient-to-r from-pink-200/50 to-purple-200/50 bg-gradient-to-r from-pink-50/50 to-purple-50/50">
          <div className="flex gap-4">
            <motion.button
              onClick={onSkip}
              className="flex-1 px-6 py-3 text-gray-600 border-2 border-gray-200 rounded-xl hover:border-pink-300 hover:bg-gradient-to-r hover:from-pink-50 hover:to-purple-50 transition-all duration-300 font-semibold shadow-lg hover:shadow-xl"
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
            >
              Skip for Now
            </motion.button>
            <motion.button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 text-white rounded-xl hover:from-pink-600 hover:via-purple-600 hover:to-indigo-600 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed font-semibold shadow-xl hover:shadow-2xl relative overflow-hidden"
              whileHover={{ scale: 1.02, y: -2 }}
              whileTap={{ scale: 0.98 }}
            >
              {/* Animated Background */}
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-pink-400 via-purple-400 to-indigo-400 opacity-0"
                animate={isSubmitting ? { opacity: 0.3 } : { opacity: 0 }}
                transition={{ duration: 0.3 }}
              />
              
              <span className="relative z-10 flex items-center justify-center gap-2">
                {isSubmitting ? (
                  <>
                    <motion.span
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="text-lg"
                    >
                      ✨
                    </motion.span>
                    Creating Magic...
                  </>
                ) : (
                  <>
                    🎉 Complete Party Details
                  </>
                )}
              </span>
            </motion.button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}

// Festive Field Components
const SelectField: React.FC<{ config: any; value: string; onChange: (value: string) => void }> = ({ config, value, onChange }) => (
  <div>
    <label className="block text-sm font-bold text-gray-800 mb-3 bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
      {config.label}
    </label>
    <select
      value={value || ''}
      onChange={(e) => onChange(e.target.value)}
      className="w-full p-4 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-pink-200 focus:border-pink-400 bg-white text-gray-900 font-medium transition-all duration-300 hover:border-pink-300 shadow-lg hover:shadow-xl"
    >
      <option value="">✨ Choose {config.label}</option>
      {config.options.map((option: string) => (
        <option key={option} value={option}>{option}</option>
      ))}
    </select>
  </div>
)

const TextField: React.FC<{ config: any; value: string; onChange: (value: string) => void }> = ({ config, value, onChange }) => (
  <div>
    <label className="block text-sm font-bold text-gray-800 mb-3 bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
      {config.label}
    </label>
    <input
      type="text"
      value={value || ''}
      onChange={(e) => onChange(e.target.value)}
      placeholder={config.placeholder}
      className="w-full p-4 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-pink-200 focus:border-pink-400 bg-white text-gray-900 placeholder-gray-400 font-medium transition-all duration-300 hover:border-pink-300 shadow-lg hover:shadow-xl"
    />
  </div>
)

const NumberField: React.FC<{ config: any; value: number; onChange: (value: number) => void }> = ({ config, value, onChange }) => (
  <div>
    <label className="block text-sm font-bold text-gray-800 mb-3 bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
      {config.label}
    </label>
    <input
      type="number"
      value={value || ''}
      onChange={(e) => onChange(parseInt(e.target.value) || 0)}
      placeholder={config.placeholder}
      min={config.min}
      max={config.max}
      className="w-full p-4 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-pink-200 focus:border-pink-400 bg-white text-gray-900 placeholder-gray-400 font-medium transition-all duration-300 hover:border-pink-300 shadow-lg hover:shadow-xl"
    />
  </div>
)

const DateField: React.FC<{ config: any; value: string; onChange: (value: string) => void }> = ({ config, value, onChange }) => (
  <div>
    <label className="block text-sm font-bold text-gray-800 mb-3 bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
      {config.label}
    </label>
    <input
      type="date"
      value={value || ''}
      onChange={(e) => onChange(e.target.value)}
      className="w-full p-4 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-pink-200 focus:border-pink-400 bg-white text-gray-900 font-medium transition-all duration-300 hover:border-pink-300 shadow-lg hover:shadow-xl"
    />
  </div>
)

const TimeRangeField: React.FC<{ config: any; value: { start: string; end: string }; onChange: (value: { start: string; end: string }) => void }> = ({ config, value, onChange }) => {
  const safeValue = value || { start: '', end: '' };
  
  return (
    <div>
      <label className="block text-sm font-bold text-gray-800 mb-3 bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
        {config.label}
      </label>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-2">🕐 Start Time</label>
          <input
            type="time"
            value={safeValue.start}
            onChange={(e) => onChange({ ...safeValue, start: e.target.value })}
            className="w-full p-4 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-pink-200 focus:border-pink-400 bg-white text-gray-900 font-medium transition-all duration-300 hover:border-pink-300 shadow-lg hover:shadow-xl"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-2">🕕 End Time</label>
          <input
            type="time"
            value={safeValue.end}
            onChange={(e) => onChange({ ...safeValue, end: e.target.value })}
            className="w-full p-4 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-pink-200 focus:border-pink-400 bg-white text-gray-900 font-medium transition-all duration-300 hover:border-pink-300 shadow-lg hover:shadow-xl"
          />
        </div>
      </div>
    </div>
  )
}

const GuestCountField: React.FC<{ config: any; value: { adults: number; kids: number }; onChange: (value: { adults: number; kids: number }) => void }> = ({ config, value, onChange }) => {
  const safeValue = value || { adults: 0, kids: 0 };
  
  return (
    <div>
      <label className="block text-sm font-bold text-gray-800 mb-3 bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
        {config.label}
      </label>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-2">👥 Adults</label>
          <input
            type="number"
            value={safeValue.adults || ''}
            onChange={(e) => onChange({ ...safeValue, adults: parseInt(e.target.value) || 0 })}
            className="w-full p-4 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-pink-200 focus:border-pink-400 bg-white text-gray-900 font-medium transition-all duration-300 hover:border-pink-300 shadow-lg hover:shadow-xl"
            min="0"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-2">🧒 Kids</label>
          <input
            type="number"
            value={safeValue.kids || ''}
            onChange={(e) => onChange({ ...safeValue, kids: parseInt(e.target.value) || 0 })}
            className="w-full p-4 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-pink-200 focus:border-pink-400 bg-white text-gray-900 font-medium transition-all duration-300 hover:border-pink-300 shadow-lg hover:shadow-xl"
            min="0"
          />
        </div>
      </div>
    </div>
  )
}

const BudgetRangeField: React.FC<{ config: any; value: { min: number; max: number }; onChange: (value: { min: number; max: number }) => void }> = ({ config, value, onChange }) => {
  const safeValue = value || { min: 0, max: 0 };
  
  return (
    <div>
      <label className="block text-sm font-bold text-gray-800 mb-3 bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
        {config.label}
      </label>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-2">💰 Min Budget</label>
          <input
            type="number"
            value={safeValue.min || ''}
            onChange={(e) => onChange({ ...safeValue, min: parseInt(e.target.value) || 0 })}
            className="w-full p-4 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-pink-200 focus:border-pink-400 bg-white text-gray-900 font-medium transition-all duration-300 hover:border-pink-300 shadow-lg hover:shadow-xl"
            min="0"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-gray-600 mb-2">💎 Max Budget</label>
          <input
            type="number"
            value={safeValue.max || ''}
            onChange={(e) => onChange({ ...safeValue, max: parseInt(e.target.value) || 0 })}
            className="w-full p-4 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-pink-200 focus:border-pink-400 bg-white text-gray-900 font-medium transition-all duration-300 hover:border-pink-300 shadow-lg hover:shadow-xl"
            min="0"
          />
        </div>
      </div>
    </div>
  )
}

const LocationField: React.FC<{ config: any; value: { type: string; name: string; address: string }; onChange: (value: { type: string; name: string; address: string }) => void }> = ({ config, value, onChange }) => {
  const locationTypes = ['Home', 'Backyard', 'Park', 'Restaurant', 'Banquet Hall', 'Community Center', 'Other']
  const safeValue = value || { type: '', name: '', address: '' };
  
  return (
    <div className="space-y-5">
      <div>
        <label className="block text-sm font-bold text-gray-800 mb-3 bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
          🏠 Location Type
        </label>
        <select
          value={safeValue.type}
          onChange={(e) => onChange({ ...safeValue, type: e.target.value })}
          className="w-full p-4 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-pink-200 focus:border-pink-400 bg-white text-gray-900 font-medium transition-all duration-300 hover:border-pink-300 shadow-lg hover:shadow-xl"
        >
          <option value="">🏠 Choose Location Type</option>
          {locationTypes.map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </div>
      
      {safeValue.type && safeValue.type !== 'Home' && (
        <>
          <div>
            <label className="block text-sm font-bold text-gray-800 mb-3 bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
              🏢 Venue Name <span className="text-gray-400 text-xs font-normal">(Optional)</span>
            </label>
            <input
              type="text"
              value={safeValue.name || ''}
              onChange={(e) => onChange({ ...safeValue, name: e.target.value })}
              placeholder="Leave empty to auto-fetch"
              className="w-full p-4 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-pink-200 focus:border-pink-400 bg-white text-gray-900 placeholder-gray-400 font-medium transition-all duration-300 hover:border-pink-300 shadow-lg hover:shadow-xl"
            />
          </div>
          <div>
            <label className="block text-sm font-bold text-gray-800 mb-3 bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
              📍 Address <span className="text-gray-400 text-xs font-normal">(Optional)</span>
            </label>
            <input
              type="text"
              value={safeValue.address || ''}
              onChange={(e) => onChange({ ...safeValue, address: e.target.value })}
              placeholder="Leave empty to auto-fetch"
              className="w-full p-4 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-pink-200 focus:border-pink-400 bg-white text-gray-900 placeholder-gray-400 font-medium transition-all duration-300 hover:border-pink-300 shadow-lg hover:shadow-xl"
            />
          </div>
        </>
      )}
    </div>
  )
}

const MultiSelectField: React.FC<{ config: any; value: string[]; onChange: (value: string[]) => void }> = ({ config, value, onChange }) => {
  const safeValue = value || [];
  
  const toggleOption = (option: string) => {
    if (safeValue.includes(option)) {
      onChange(safeValue.filter(item => item !== option))
    } else {
      onChange([...safeValue, option])
    }
  }

  return (
    <div>
      <label className="block text-sm font-bold text-gray-800 mb-3 bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent">
        🎪 {config.label}
      </label>
      <div className="grid grid-cols-2 gap-3 max-h-40 overflow-y-auto">
        {config.options.map((option: string) => (
          <button
            key={option}
            onClick={() => toggleOption(option)}
            className={`p-3 rounded-xl border-2 text-sm font-medium transition-all duration-300 ${
              safeValue.includes(option)
                ? 'border-pink-400 bg-gradient-to-r from-pink-100 to-purple-100 text-pink-700 shadow-lg'
                : 'border-gray-200 bg-white text-gray-700 hover:border-pink-300 hover:bg-gradient-to-r hover:from-pink-50 hover:to-purple-50 shadow-md hover:shadow-lg'
            }`}
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  )
}
