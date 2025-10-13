/**
 * Dynamic Input Components for Party Planning Data Collection
 * Builds forms dynamically based on missing fields from backend agent
 */

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ExtractedEventData } from '../services/api'

export interface DataInputProps {
  extractedData: ExtractedEventData
  missingFields: string[]
  suggestions: string[]
  onDataComplete: (data: ExtractedEventData) => void
  onSkip: () => void
}

// Field configuration for dynamic form generation
const FIELD_CONFIG = {
  eventType: {
    label: "What type of event is this?",
    type: "select",
    options: ['Birthday', 'Wedding', 'Anniversary', 'Baby Shower', 'Graduation', 'Retirement', 'Holiday Party', 'Other'],
    placeholder: "Select event type"
  },
  title: {
    label: "Event Title",
    type: "text",
    placeholder: "e.g., Sarah's 5th Birthday Party"
  },
  honoreeName: {
    label: "Who is this event for?",
    type: "text",
    placeholder: "e.g., Sarah, John, etc."
  },
  age: {
    label: "Age",
    type: "number",
    placeholder: "e.g., 5, 25, etc.",
    min: 0,
    max: 120
  },
  gender: {
    label: "Gender",
    type: "select",
    options: ['Male', 'Female', 'Other', 'Prefer not to say'],
    placeholder: "Select gender"
  },
  theme: {
    label: "Choose a theme",
    type: "select",
    options: ['Princess', 'Superhero', 'Unicorn', 'Dinosaur', 'Space', 'Pirate', 'Fairy', 'Mermaid', 'Jungle', 'Circus', 'Vintage', 'Modern', 'Tropical', 'Beach', 'Garden', 'Disney', 'Frozen', 'Cars', 'Other'],
    placeholder: "Select theme"
  },
  date: {
    label: "Event Date",
    type: "date",
    placeholder: "Select date"
  },
  time: {
    label: "Event Time",
    type: "time-range",
    placeholder: "Select time range"
  },
  guestCount: {
    label: "Guest Count",
    type: "guest-count",
    placeholder: "Number of guests"
  },
  budget: {
    label: "Budget Range",
    type: "budget-range",
    placeholder: "Budget range"
  },
  location: {
    label: "Event Location",
    type: "location",
    placeholder: "Event location details"
  },
  foodPreference: {
    label: "Food Preference",
    type: "select",
    options: ['Veg', 'Non-Veg', 'Mixed', 'No Preference'],
    placeholder: "Select food preference"
  },
  activities: {
    label: "Activities",
    type: "multi-select",
    options: ['Balloon Twisting', 'Magic Show', 'Face Painting', 'Pinata', 'Bouncy Castle', 'Photo Booth', 'Dancing', 'Karaoke', 'Treasure Hunt', 'Crafts'],
    placeholder: "Select activities"
  },
  rsvpDeadline: {
    label: "RSVP Deadline",
    type: "date",
    placeholder: "RSVP deadline"
  },
  contactInfo: {
    label: "Contact Information",
    type: "email",
    placeholder: "Email address"
  }
}

export const DataInputForm: React.FC<DataInputProps> = ({
  extractedData,
  missingFields,
  suggestions,
  onDataComplete,
  onSkip
}) => {
  const [formData, setFormData] = useState<ExtractedEventData>(extractedData)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const updateFormData = (field: keyof ExtractedEventData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    onDataComplete(formData)
    setIsSubmitting(false)
  }

  const renderDynamicField = (fieldName: string) => {
    const config = FIELD_CONFIG[fieldName as keyof typeof FIELD_CONFIG]
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
      case 'email':
        return (
          <EmailField
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

  if (missingFields.length === 0) {
    return null
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100] flex items-center justify-center p-4"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="bg-white/20 backdrop-blur-2xl rounded-3xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden flex flex-col border border-white/30"
        style={{
          background: `
            linear-gradient(135deg, rgba(255, 182, 193, 0.3) 0%, rgba(255, 192, 203, 0.25) 50%, rgba(255, 218, 185, 0.2) 100%),
            radial-gradient(circle at 30% 20%, rgba(255, 182, 193, 0.4) 0%, transparent 50%)
          `,
          boxShadow: `
            0 8px 32px rgba(255, 182, 193, 0.5),
            inset 0 1px 0 rgba(255, 255, 255, 0.4),
            0 0 0 1px rgba(255, 255, 255, 0.2)
          `
        }}
      >
        {/* Animated Background Particles */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {[...Array(15)].map((_, i) => (
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

        {/* Liquid Glass Overlay */}
        <motion.div
          className="absolute inset-0 rounded-3xl opacity-40 pointer-events-none"
          style={{
            background: `
              linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.2) 50%, transparent 70%),
              radial-gradient(circle at 50% 50%, rgba(255, 182, 193, 0.15) 0%, transparent 70%)
            `
          }}
          animate={{
            backgroundPosition: ['0% 0%', '100% 100%'],
          }}
          transition={{
            duration: 6,
            repeat: Infinity,
            ease: 'linear'
          }}
        />

        {/* Header */}
        <div className="p-6 border-b border-white/20 flex-shrink-0 relative z-10">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-800 bg-gradient-to-r from-pink-600 to-rose-600 bg-clip-text text-transparent">
              ✨ Complete Party Details
            </h2>
            <button
              onClick={onSkip}
              className="text-gray-400 hover:text-gray-600 transition-colors p-2 rounded-full hover:bg-white/20"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <p className="text-sm text-gray-600">
            🎉 Please fill in the missing details for your amazing party
          </p>
        </div>

        {/* Content - All fields at once */}
        <div className="p-6 overflow-y-auto flex-grow relative z-10">
          <div className="space-y-8">
            {missingFields.map((fieldName, index) => (
              <motion.div
                key={fieldName}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="relative"
              >
                    {/* Field Container with Glass Effect */}
                    <div 
                      className="p-6 rounded-2xl backdrop-blur-sm border border-white/40 relative overflow-hidden"
                      style={{
                        background: `
                          linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.2) 100%)
                        `,
                        boxShadow: `
                          0 8px 32px rgba(255, 182, 193, 0.3),
                          inset 0 1px 0 rgba(255, 255, 255, 0.4)
                        `
                      }}
                    >
                  {/* Glowing Edge Effect */}
                  <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-pink-400/10 via-transparent to-rose-400/10 opacity-0 hover:opacity-100 transition-opacity duration-500" />
                  
                  {/* Liquid Glass Overlay */}
                  <motion.div
                    className="absolute inset-0 rounded-2xl opacity-20 pointer-events-none"
                    style={{
                      background: `
                        linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.2) 50%, transparent 70%)
                      `
                    }}
                    animate={{
                      backgroundPosition: ['0% 0%', '100% 100%'],
                    }}
                    transition={{
                      duration: 4,
                      repeat: Infinity,
                      ease: 'linear'
                    }}
                  />
                  
                  <div className="relative z-10">
                    {renderDynamicField(fieldName)}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-white/20 flex gap-3 flex-shrink-0 relative z-10">
              <button
                onClick={onSkip}
                className="flex-1 px-6 py-3 text-gray-600 border border-white/40 rounded-xl hover:bg-white/30 transition-all duration-300 backdrop-blur-sm font-medium"
              >
                Skip for now
              </button>
              <button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-pink-500 to-rose-500 text-white rounded-xl hover:from-pink-600 hover:to-rose-600 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-lg hover:shadow-xl"
                style={{
                  boxShadow: '0 8px 32px rgba(255, 182, 193, 0.5)'
                }}
              >
            {isSubmitting ? (
              <span className="flex items-center justify-center gap-2">
                <motion.span
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                >
                  ✨
                </motion.span>
                Processing...
              </span>
            ) : (
              '🎉 Complete'
            )}
          </button>
        </div>
      </motion.div>
    </motion.div>
  )
}

// Dynamic Field Components
const SelectField: React.FC<{ config: any; value: string; onChange: (value: string) => void }> = ({ config, value, onChange }) => (
  <div>
    <label className="block text-lg font-semibold text-gray-800 mb-4 bg-gradient-to-r from-pink-600 to-rose-600 bg-clip-text text-transparent">
      {config.label}
    </label>
    <div className="grid grid-cols-2 gap-3">
      {config.options.map((option: string) => (
        <motion.button
          key={option}
          onClick={() => onChange(option)}
        className={`p-4 rounded-xl border-2 transition-all duration-300 font-medium backdrop-blur-sm relative overflow-hidden ${
          value === option
            ? 'border-pink-500 bg-gradient-to-r from-pink-500/30 to-rose-500/30 text-pink-700 shadow-lg'
            : 'border-white/40 bg-white/20 hover:border-pink-300 hover:bg-white/30 text-gray-700'
        }`}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          style={{
            boxShadow: value === option ? '0 8px 32px rgba(255, 182, 193, 0.3)' : '0 4px 16px rgba(255, 182, 193, 0.1)'
          }}
        >
          {/* Glowing Edge Effect */}
          <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-pink-400/10 via-transparent to-rose-400/10 opacity-0 hover:opacity-100 transition-opacity duration-300" />
          
          {/* Liquid Glass Overlay */}
          <motion.div
            className="absolute inset-0 rounded-xl opacity-20 pointer-events-none"
            style={{
              background: `
                linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.2) 50%, transparent 70%)
              `
            }}
            animate={{
              backgroundPosition: ['0% 0%', '100% 100%'],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: 'linear'
            }}
          />
          
          <span className="relative z-10">{option}</span>
        </motion.button>
      ))}
    </div>
  </div>
)

const TextField: React.FC<{ config: any; value: string; onChange: (value: string) => void }> = ({ config, value, onChange }) => (
  <div>
    <label className="block text-lg font-semibold text-gray-800 mb-4 bg-gradient-to-r from-pink-600 to-rose-600 bg-clip-text text-transparent">
      {config.label}
    </label>
    <div className="relative">
      <input
        type="text"
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        placeholder={config.placeholder}
        className="w-full p-4 border-2 border-white/40 rounded-xl focus:ring-2 focus:ring-pink-400 focus:border-pink-300 bg-white/20 backdrop-blur-sm text-gray-800 placeholder-gray-500 transition-all duration-300 relative overflow-hidden"
        style={{
          boxShadow: '0 4px 16px rgba(255, 182, 193, 0.2)'
        }}
      />
      {/* Glowing Edge Effect */}
      <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-pink-400/10 via-transparent to-rose-400/10 opacity-0 focus-within:opacity-100 transition-opacity duration-300 pointer-events-none" />
    </div>
  </div>
)

const NumberField: React.FC<{ config: any; value: number; onChange: (value: number) => void }> = ({ config, value, onChange }) => (
  <div>
    <label className="block text-lg font-semibold text-gray-800 mb-4 bg-gradient-to-r from-pink-600 to-rose-600 bg-clip-text text-transparent">
      {config.label}
    </label>
    <div className="relative">
      <input
        type="number"
        value={value || ''}
        onChange={(e) => onChange(parseInt(e.target.value) || 0)}
        placeholder={config.placeholder}
        min={config.min}
        max={config.max}
        className="w-full p-4 border-2 border-white/40 rounded-xl focus:ring-2 focus:ring-pink-400 focus:border-pink-300 bg-white/20 backdrop-blur-sm text-gray-800 placeholder-gray-500 transition-all duration-300 relative overflow-hidden"
        style={{
          boxShadow: '0 4px 16px rgba(255, 182, 193, 0.2)'
        }}
      />
      {/* Glowing Edge Effect */}
      <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-pink-400/10 via-transparent to-rose-400/10 opacity-0 focus-within:opacity-100 transition-opacity duration-300 pointer-events-none" />
    </div>
  </div>
)

const DateField: React.FC<{ config: any; value: string; onChange: (value: string) => void }> = ({ config, value, onChange }) => (
  <div>
    <label className="block text-lg font-semibold text-gray-800 mb-4 bg-gradient-to-r from-pink-600 to-rose-600 bg-clip-text text-transparent">
      {config.label}
    </label>
    <div className="relative">
      <input
        type="date"
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        className="w-full p-4 border-2 border-white/40 rounded-xl focus:ring-2 focus:ring-pink-400 focus:border-pink-300 bg-white/20 backdrop-blur-sm text-gray-800 transition-all duration-300 relative overflow-hidden"
        style={{
          boxShadow: '0 4px 16px rgba(255, 182, 193, 0.2)'
        }}
      />
      {/* Glowing Edge Effect */}
      <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-pink-400/10 via-transparent to-rose-400/10 opacity-0 focus-within:opacity-100 transition-opacity duration-300 pointer-events-none" />
    </div>
  </div>
)

const EmailField: React.FC<{ config: any; value: string; onChange: (value: string) => void }> = ({ config, value, onChange }) => (
  <div>
    <label className="block text-lg font-semibold text-gray-800 mb-4 bg-gradient-to-r from-pink-600 to-rose-600 bg-clip-text text-transparent">
      {config.label}
    </label>
    <div className="relative">
      <input
        type="email"
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        placeholder={config.placeholder}
        className="w-full p-4 border-2 border-white/40 rounded-xl focus:ring-2 focus:ring-pink-400 focus:border-pink-300 bg-white/20 backdrop-blur-sm text-gray-800 placeholder-gray-500 transition-all duration-300 relative overflow-hidden"
        style={{
          boxShadow: '0 4px 16px rgba(255, 182, 193, 0.2)'
        }}
      />
      {/* Glowing Edge Effect */}
      <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-pink-400/10 via-transparent to-rose-400/10 opacity-0 focus-within:opacity-100 transition-opacity duration-300 pointer-events-none" />
    </div>
  </div>
)

const TimeRangeField: React.FC<{ config: any; value: { start: string; end: string }; onChange: (value: { start: string; end: string }) => void }> = ({ config, value, onChange }) => (
  <div>
    <label className="block text-lg font-semibold text-gray-800 mb-4 bg-gradient-to-r from-pink-600 to-rose-600 bg-clip-text text-transparent">
      {config.label}
    </label>
    <div className="space-y-4">
      <div>
        <label className="block text-sm text-gray-600 mb-2">Start Time</label>
        <div className="relative">
          <input
            type="time"
            value={value?.start || ''}
            onChange={(e) => onChange({ ...value, start: e.target.value })}
            className="w-full p-4 border-2 border-white/30 rounded-xl focus:ring-2 focus:ring-pink-400 focus:border-pink-300 bg-white/10 backdrop-blur-sm text-gray-800 transition-all duration-300 relative overflow-hidden"
            style={{
              boxShadow: '0 4px 16px rgba(255, 182, 193, 0.1)'
            }}
          />
          {/* Glowing Edge Effect */}
          <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-pink-400/10 via-transparent to-rose-400/10 opacity-0 focus-within:opacity-100 transition-opacity duration-300 pointer-events-none" />
        </div>
      </div>
      <div>
        <label className="block text-sm text-gray-600 mb-2">End Time</label>
        <div className="relative">
          <input
            type="time"
            value={value?.end || ''}
            onChange={(e) => onChange({ ...value, end: e.target.value })}
            className="w-full p-4 border-2 border-white/30 rounded-xl focus:ring-2 focus:ring-pink-400 focus:border-pink-300 bg-white/10 backdrop-blur-sm text-gray-800 transition-all duration-300 relative overflow-hidden"
            style={{
              boxShadow: '0 4px 16px rgba(255, 182, 193, 0.1)'
            }}
          />
          {/* Glowing Edge Effect */}
          <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-pink-400/10 via-transparent to-rose-400/10 opacity-0 focus-within:opacity-100 transition-opacity duration-300 pointer-events-none" />
        </div>
      </div>
    </div>
  </div>
)

const GuestCountField: React.FC<{ config: any; value: { adults: number; kids: number }; onChange: (value: { adults: number; kids: number }) => void }> = ({ config, value, onChange }) => (
  <div>
    <label className="block text-lg font-semibold text-gray-800 mb-4 bg-gradient-to-r from-pink-600 to-rose-600 bg-clip-text text-transparent">
      {config.label}
    </label>
    <div className="space-y-4">
      <div>
        <label className="block text-sm text-gray-600 mb-2">Adults</label>
        <div className="relative">
          <input
            type="number"
            value={value?.adults || ''}
            onChange={(e) => onChange({ ...value, adults: parseInt(e.target.value) || 0 })}
            className="w-full p-4 border-2 border-white/30 rounded-xl focus:ring-2 focus:ring-pink-400 focus:border-pink-300 bg-white/10 backdrop-blur-sm text-gray-800 transition-all duration-300 relative overflow-hidden"
            min="0"
            style={{
              boxShadow: '0 4px 16px rgba(255, 182, 193, 0.1)'
            }}
          />
          {/* Glowing Edge Effect */}
          <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-pink-400/10 via-transparent to-rose-400/10 opacity-0 focus-within:opacity-100 transition-opacity duration-300 pointer-events-none" />
        </div>
      </div>
      <div>
        <label className="block text-sm text-gray-600 mb-2">Kids</label>
        <div className="relative">
          <input
            type="number"
            value={value?.kids || ''}
            onChange={(e) => onChange({ ...value, kids: parseInt(e.target.value) || 0 })}
            className="w-full p-4 border-2 border-white/30 rounded-xl focus:ring-2 focus:ring-pink-400 focus:border-pink-300 bg-white/10 backdrop-blur-sm text-gray-800 transition-all duration-300 relative overflow-hidden"
            min="0"
            style={{
              boxShadow: '0 4px 16px rgba(255, 182, 193, 0.1)'
            }}
          />
          {/* Glowing Edge Effect */}
          <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-pink-400/10 via-transparent to-rose-400/10 opacity-0 focus-within:opacity-100 transition-opacity duration-300 pointer-events-none" />
        </div>
      </div>
    </div>
  </div>
)

const BudgetRangeField: React.FC<{ config: any; value: { min: number; max: number }; onChange: (value: { min: number; max: number }) => void }> = ({ config, value, onChange }) => (
  <div>
    <label className="block text-lg font-semibold text-gray-800 mb-4 bg-gradient-to-r from-pink-600 to-rose-600 bg-clip-text text-transparent">
      {config.label}
    </label>
    <div className="space-y-4">
      <div>
        <label className="block text-sm text-gray-600 mb-2">Minimum ($)</label>
        <div className="relative">
          <input
            type="number"
            value={value?.min || ''}
            onChange={(e) => onChange({ ...value, min: parseInt(e.target.value) || 0 })}
            placeholder="Min amount"
            className="w-full p-4 border-2 border-white/30 rounded-xl focus:ring-2 focus:ring-pink-400 focus:border-pink-300 bg-white/10 backdrop-blur-sm text-gray-800 placeholder-gray-500 transition-all duration-300 relative overflow-hidden"
            min="0"
            style={{
              boxShadow: '0 4px 16px rgba(255, 182, 193, 0.1)'
            }}
          />
          {/* Glowing Edge Effect */}
          <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-pink-400/10 via-transparent to-rose-400/10 opacity-0 focus-within:opacity-100 transition-opacity duration-300 pointer-events-none" />
        </div>
      </div>
      <div>
        <label className="block text-sm text-gray-600 mb-2">Maximum ($)</label>
        <div className="relative">
          <input
            type="number"
            value={value?.max || ''}
            onChange={(e) => onChange({ ...value, max: parseInt(e.target.value) || 0 })}
            placeholder="Max amount"
            className="w-full p-4 border-2 border-white/30 rounded-xl focus:ring-2 focus:ring-pink-400 focus:border-pink-300 bg-white/10 backdrop-blur-sm text-gray-800 placeholder-gray-500 transition-all duration-300 relative overflow-hidden"
            min="0"
            style={{
              boxShadow: '0 4px 16px rgba(255, 182, 193, 0.1)'
            }}
          />
          {/* Glowing Edge Effect */}
          <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-pink-400/10 via-transparent to-rose-400/10 opacity-0 focus-within:opacity-100 transition-opacity duration-300 pointer-events-none" />
        </div>
      </div>
    </div>
  </div>
)

const LocationField: React.FC<{ config: any; value: { type: string; name: string; address: string }; onChange: (value: { type: string; name: string; address: string }) => void }> = ({ config, value, onChange }) => {
  const locationTypes = ['Home', 'Backyard', 'Park', 'Restaurant', 'Banquet Hall', 'Community Center', 'Other']
  
  return (
    <div className="space-y-4">
      <div>
        <label className="block text-lg font-semibold text-gray-800 mb-4 bg-gradient-to-r from-pink-600 to-rose-600 bg-clip-text text-transparent">
          Location Type
        </label>
        <div className="grid grid-cols-2 gap-3">
          {locationTypes.map(type => (
            <motion.button
              key={type}
              onClick={() => onChange({ ...value, type })}
              className={`p-4 rounded-xl border-2 transition-all duration-300 font-medium backdrop-blur-sm text-sm relative overflow-hidden ${
                value?.type === type
                  ? 'border-pink-500 bg-gradient-to-r from-pink-500/30 to-rose-500/30 text-pink-700 shadow-lg'
                  : 'border-white/40 bg-white/20 hover:border-pink-300 hover:bg-white/30 text-gray-700'
              }`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              style={{
                boxShadow: value?.type === type ? '0 8px 32px rgba(255, 182, 193, 0.3)' : '0 4px 16px rgba(255, 182, 193, 0.1)'
              }}
            >
              {/* Glowing Edge Effect */}
              <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-pink-400/10 via-transparent to-rose-400/10 opacity-0 hover:opacity-100 transition-opacity duration-300" />
              
              {/* Liquid Glass Overlay */}
              <motion.div
                className="absolute inset-0 rounded-xl opacity-20 pointer-events-none"
                style={{
                  background: `
                    linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.2) 50%, transparent 70%)
                  `
                }}
                animate={{
                  backgroundPosition: ['0% 0%', '100% 100%'],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: 'linear'
                }}
              />
              
              <span className="relative z-10">{type}</span>
            </motion.button>
          ))}
        </div>
      </div>
      <div>
        <label className="block text-sm text-gray-600 mb-2">Venue Name</label>
        <div className="relative">
          <input
            type="text"
            value={value?.name || ''}
            onChange={(e) => onChange({ ...value, name: e.target.value })}
            placeholder="e.g., FunZone Hall"
            className="w-full p-4 border-2 border-white/30 rounded-xl focus:ring-2 focus:ring-pink-400 focus:border-pink-300 bg-white/10 backdrop-blur-sm text-gray-800 placeholder-gray-500 transition-all duration-300 relative overflow-hidden"
            style={{
              boxShadow: '0 4px 16px rgba(255, 182, 193, 0.1)'
            }}
          />
          {/* Glowing Edge Effect */}
          <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-pink-400/10 via-transparent to-rose-400/10 opacity-0 focus-within:opacity-100 transition-opacity duration-300 pointer-events-none" />
        </div>
      </div>
      <div>
        <label className="block text-sm text-gray-600 mb-2">Address</label>
        <div className="relative">
          <input
            type="text"
            value={value?.address || ''}
            onChange={(e) => onChange({ ...value, address: e.target.value })}
            placeholder="e.g., 123 Main St, City, State"
            className="w-full p-4 border-2 border-white/30 rounded-xl focus:ring-2 focus:ring-pink-400 focus:border-pink-300 bg-white/10 backdrop-blur-sm text-gray-800 placeholder-gray-500 transition-all duration-300 relative overflow-hidden"
            style={{
              boxShadow: '0 4px 16px rgba(255, 182, 193, 0.1)'
            }}
          />
          {/* Glowing Edge Effect */}
          <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-pink-400/10 via-transparent to-rose-400/10 opacity-0 focus-within:opacity-100 transition-opacity duration-300 pointer-events-none" />
        </div>
      </div>
    </div>
  )
}

const MultiSelectField: React.FC<{ config: any; value: string[]; onChange: (value: string[]) => void }> = ({ config, value, onChange }) => {
  const toggleOption = (option: string) => {
    const currentValue = value || []
    if (currentValue.includes(option)) {
      onChange(currentValue.filter(item => item !== option))
    } else {
      onChange([...currentValue, option])
    }
  }

  return (
    <div>
      <label className="block text-lg font-semibold text-gray-800 mb-4 bg-gradient-to-r from-pink-600 to-rose-600 bg-clip-text text-transparent">
        {config.label}
      </label>
      <div className="grid grid-cols-2 gap-3 max-h-48 overflow-y-auto">
        {config.options.map((option: string) => (
          <motion.button
            key={option}
            onClick={() => toggleOption(option)}
            className={`p-4 rounded-xl border-2 transition-all duration-300 font-medium backdrop-blur-sm text-sm relative overflow-hidden ${
              value?.includes(option)
                ? 'border-pink-500 bg-gradient-to-r from-pink-500/30 to-rose-500/30 text-pink-700 shadow-lg'
                : 'border-white/40 bg-white/20 hover:border-pink-300 hover:bg-white/30 text-gray-700'
            }`}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            style={{
              boxShadow: value?.includes(option) ? '0 8px 32px rgba(255, 182, 193, 0.3)' : '0 4px 16px rgba(255, 182, 193, 0.1)'
            }}
          >
            {/* Glowing Edge Effect */}
            <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-pink-400/10 via-transparent to-rose-400/10 opacity-0 hover:opacity-100 transition-opacity duration-300" />
            
            {/* Liquid Glass Overlay */}
            <motion.div
              className="absolute inset-0 rounded-xl opacity-20 pointer-events-none"
              style={{
                background: `
                  linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.2) 50%, transparent 70%)
                `
              }}
              animate={{
                backgroundPosition: ['0% 0%', '100% 100%'],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: 'linear'
              }}
            />
            
            <span className="relative z-10">{option}</span>
          </motion.button>
        ))}
      </div>
    </div>
  )
}