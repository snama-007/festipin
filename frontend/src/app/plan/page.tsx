'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

type ClassicData = {
  eventType: string
  occasion: string
  honoree: string
  locationLabel: string
  adultGuests: string
  kidGuests: string
  budget: string
  date: string
  timeStart: string
  timeEnd: string
  constraints: string
  guestNotes: string
  extraIntent: string
}

const BRAND = {
  sunshine: '#FFD93D',
  lime: '#6BCF7E',
  emerald: '#2DB876',
  cream: '#FFFEF5',
  graphite: '#1F2937',
  smoke: '#6B7280'
}

const JOURNEY_MAP = [
  { time: '6:00 PM', label: 'Arrivals + Aura Scan', detail: 'Guests walk a glow runway, drop voice notes, receive AI aura keepsake.' },
  { time: '6:25 PM', label: 'Lighting Reveal', detail: 'Parents toast, room floods with “Neon Bloom” scene, Maya’s sketches projected.' },
  { time: '6:45 PM', label: 'Dinner Pods', detail: 'Conversation cards, shared plates, scent cue shifts to grapefruit cedar.' },
  { time: '7:15 PM', label: 'Dance Bloom', detail: 'DJ x sax overlay, mocktail lab opens, gratitude wall activated.' }
]

const CLASSIC_DEFAULTS: ClassicData = {
  eventType: '',
  occasion: '',
  honoree: '',
  locationLabel: '',
  adultGuests: '',
  kidGuests: '',
  budget: '',
  date: '',
  timeStart: '',
  timeEnd: '',
  constraints: '',
  guestNotes: '',
  extraIntent: ''
}

const CONFETTI_COLORS = ['#FFD93D', '#6BCF7E', '#FF9AC5', '#A5D8FF', '#F5A524']
const ACTION_ITEMS = [
  { task: 'Lock Loft Venue', owner: 'You', due: 'Apr 15', status: 'Pending' },
  { task: 'Lighting + Install Call', owner: 'Festimo Agent', due: 'Apr 02', status: 'Scheduled' },
  { task: 'Menu Mood Board', owner: 'Catering Lead', due: 'Mar 28', status: 'Draft' }
]

const DECISIONS = [
  {
    title: 'Atmosphere',
    options: [
      'Palette: Sunshine yellow + emerald anchoring tones',
      'Materials: Sheer voile, chrome plinths, velvet lounge pads',
      'Lighting: Pre-programmed scenes for each journey moment'
    ]
  },
  {
    title: 'Menu & Bar',
    options: [
      'Progressive bites (3 drops) color-matched to lighting',
      'Mocktail lab with NFC unlock cards',
      'Comfort finale: molten cakes + neon sugar lattice'
    ]
  },
  {
    title: 'Guest Touchpoints',
    options: [
      'Aura Scan keepsake photos on arrival',
      'Audio guestbook + gratitude wall',
      'Energy hosts rotating groups between zones'
    ]
  }
]

export default function PlanPage() {
  const [prompt, setPrompt] = useState('')
  const [location, setLocation] = useState('')
  const [locationError, setLocationError] = useState<string | null>(null)
  const [isFetchingLocation, setIsFetchingLocation] = useState(false)
  const [activeMode, setActiveMode] = useState<'prompt' | 'classic'>('prompt')
  const [showClassic, setShowClassic] = useState(false)
  const [classicData, setClassicData] = useState<ClassicData>(CLASSIC_DEFAULTS)
  const [formErrors, setFormErrors] = useState<Record<string, string>>({})
  const [formStatus, setFormStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null)

  const infoTips: Record<string, string> = {
    eventType: 'Select the celebration archetype to set tone and vendors.',
    occasion: 'Name of the experience or internal codename.',
    honoree: 'Who is being celebrated or hosting?',
    location: 'City, neighborhood, or venue zip. Tap Detect for GPS.',
    guestAdults: 'Number of adult guests (18+).',
    guestKids: 'Kids/teens (0-17). Enter 0 if none.',
    budget: 'Total spend ceiling. Numbers only; $ is added.',
    date: 'Calendar date for the celebration.',
    timeStart: 'Guest arrival or experience start.',
    timeEnd: 'Wrap time or handover.',
    constraints: 'Anything to exclude so AI avoids misfires.',
    guestNotes: 'Dietary needs, VIP notes, accessibility.',
    extraNotes: 'Traditions, rituals, or feelings to honor.'
  }

  const updateClassicField = (key: keyof ClassicData, value: string) => {
    setClassicData((prev) => ({
      ...prev,
      [key]:
        key === 'budget'
          ? value.trim()
            ? value.trim().startsWith('$')
              ? value.trim()
              : `$${value.trim().replace(/^\$/, '')}`
            : ''
          : value
    }))
  }

  const validateClassicForm = useCallback(() => {
    const errors: Record<string, string> = {}

    if (!classicData.eventType) errors.eventType = 'Pick an event type.'
    if (!classicData.occasion.trim()) errors.occasion = 'Occasion name required.'
    if (!(classicData.locationLabel || location)) errors.location = 'Provide a city/zip.'

    const adults = Number(classicData.adultGuests)
    if (!classicData.adultGuests || Number.isNaN(adults) || adults <= 0) {
      errors.guestAdults = 'Need at least one adult.'
    }
    if (classicData.kidGuests) {
      const kids = Number(classicData.kidGuests)
      if (Number.isNaN(kids) || kids < 0) errors.guestKids = 'Use a positive number.'
    }

    if (!classicData.budget.trim()) errors.budget = 'Budget keeps vendors aligned.'
    if (!classicData.date) errors.date = 'Select a date.'
    else {
      const selected = new Date(classicData.date)
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      if (selected < today) errors.date = 'Date cannot be in the past.'
    }

    if (!classicData.timeStart) errors.timeStart = 'Start time required.'
    if (!classicData.timeEnd) errors.timeEnd = 'End time required.'
    if (classicData.timeStart && classicData.timeEnd && classicData.timeStart >= classicData.timeEnd) {
      errors.timeEnd = 'End must be later than start.'
    }

    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }, [classicData, location])

  const fetchLocation = useCallback(() => {
    if (typeof navigator === 'undefined' || !navigator.geolocation) {
      setLocationError('Geolocation is not supported in this environment.')
      return
    }

    const requestPosition = () => {
      setIsFetchingLocation(true)
      setLocationError(null)
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const { latitude, longitude } = pos.coords
          const fallback = `${latitude.toFixed(3)}, ${longitude.toFixed(3)}`

          const resolveLabel = async () => {
            try {
              const response = await fetch(
                `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=12&addressdetails=1`
              )
              if (!response.ok) throw new Error('reverse geocode failed')
              const data = await response.json()
              const address = data.address || {}
              const city = address.city || address.town || address.village || address.county
              const state = address.state
              const postal = address.postcode
              const label = postal || [city, state].filter(Boolean).join(', ') || fallback
              setLocation(label)
              updateClassicField('locationLabel', label)
              setLocationError(null)
            } catch {
              setLocation(fallback)
              updateClassicField('locationLabel', fallback)
              setLocationError('Using coordinates fallback. You can edit manually.')
            } finally {
              setIsFetchingLocation(false)
            }
          }

          resolveLabel()
        },
        (error) => {
          setIsFetchingLocation(false)
          if (error.code === error.PERMISSION_DENIED) {
            setLocationError('Please allow location permissions in your browser to auto-detect your city.')
          } else {
            setLocationError('Unable to fetch location. Try again or enter it manually.')
          }
        },
        { timeout: 5000, maximumAge: 60000 }
      )
    }

    if (navigator.permissions?.query) {
      navigator.permissions
        .query({ name: 'geolocation' as PermissionName })
        .then((result) => {
          if (result.state === 'denied') {
            setLocationError('Location permission is blocked. Enable it in your browser settings to auto-detect.')
          } else {
            requestPosition()
          }
        })
        .catch(() => {
          requestPosition()
        })
    } else {
      requestPosition()
    }
  }, [updateClassicField])

  useEffect(() => {
    if (!location) fetchLocation()
  }, [fetchLocation, location])

  const overview = useMemo(
    () => [
      { label: 'Intent', value: 'Luminous Sweet 16 ritual' },
      { label: 'Budget', value: '$8,000 (must-invest lighting + culinary)' },
      { label: 'Guests', value: '40 adults · 12 teens' },
      { label: 'Location', value: location || (isFetchingLocation ? 'Detecting…' : 'Tap to detect') }
    ],
    [location, isFetchingLocation]
  )

  const promptSnippet = prompt ? `${prompt.slice(0, 80)}${prompt.length > 80 ? '…' : ''}` : 'Awaiting prompt'
  const generatedPrompt = useMemo(() => {
    if (!classicData.eventType && !classicData.occasion) return null
    const parts = [
      classicData.eventType ? `Plan a ${classicData.eventType}` : 'Plan a celebration',
      classicData.occasion ? `called "${classicData.occasion}"` : '',
      classicData.locationLabel ? `in ${classicData.locationLabel}` : '',
      classicData.adultGuests ? `for ${classicData.adultGuests} adults` : '',
      classicData.kidGuests ? `and ${classicData.kidGuests} teens/kids` : '',
      classicData.budget ? `within ${classicData.budget}` : '',
      classicData.date ? `on ${classicData.date}` : '',
      classicData.timeStart && classicData.timeEnd ? `from ${classicData.timeStart} to ${classicData.timeEnd}` : ''
    ]
    return parts.filter(Boolean).join(' ') || null
  }, [classicData])

  const handlePlanSubmit = () => {
    if (validateClassicForm()) {
      setFormStatus({
        type: 'success',
        message: generatedPrompt ? `Prompt ready: ${generatedPrompt}` : 'Inputs captured. You can now plan.'
      })
    } else {
      setFormStatus({
        type: 'error',
        message: 'Please fix the highlighted fields.'
      })
    }
  }

  const handleResetForm = () => {
    setClassicData({ ...CLASSIC_DEFAULTS })
    setFormErrors({})
    setFormStatus(null)
  }

  const InfoIcon = ({ tip }: { tip: string }) => (
    <span className="relative inline-flex group">
      <button
        type="button"
        className="inline-flex h-4 w-4 items-center justify-center rounded-full border border-[#E8EDE5] text-[10px] font-semibold text-gray-500 bg-white focus:outline-none focus:ring-2 focus:ring-[#FFD93D]"
        aria-label="Field help"
      >
        i
      </button>
      <span
        className="pointer-events-none absolute left-1/2 top-full z-20 mt-2 w-48 -translate-x-1/2 rounded-xl bg-gray-900/95 px-3 py-2 text-[11px] font-medium text-white opacity-0 shadow-lg transition group-hover:opacity-100 group-focus-within:opacity-100"
      >
        {tip}
      </span>
    </span>
  )

  type FieldConfig = {
    key: string
    dataKey: keyof ClassicData
    label: string
    placeholder: string
    type?: 'text' | 'number' | 'date' | 'time' | 'select'
    options?: string[]
    infoKey: keyof typeof infoTips
    errorKey?: string
    auto?: boolean
    showButton?: boolean
    fullWidth?: boolean
  }

  const classicFields: FieldConfig[] = [
    {
      key: 'eventType',
      dataKey: 'eventType',
      label: 'Event Type',
      placeholder: 'Select type',
      type: 'select',
      options: [
        'Sweet 16',
        'Birthday Bash',
        'Anniversary Dinner',
        'Baby Shower',
        'Bridal Shower',
        'Engagement Party',
        'Corporate Social',
        'Pop-Up Launch',
        'Holiday Party',
        'Graduation',
        'Cocktail Soirée',
        'Family Reunion',
        'Other'
      ],
      infoKey: 'eventType',
      errorKey: 'eventType'
    },
    { key: 'occasion', dataKey: 'occasion', label: 'Occasion Name', placeholder: 'Maya’s Neon Bloom', infoKey: 'occasion', errorKey: 'occasion' },
    { key: 'honoree', dataKey: 'honoree', label: 'Honoree', placeholder: 'Maya Johnson', infoKey: 'honoree' },
    {
      key: 'location',
      dataKey: 'locationLabel',
      label: 'Location / City / Zip',
      placeholder: 'Auto or type location',
      infoKey: 'location',
      errorKey: 'location',
      auto: true,
      showButton: true,
      fullWidth: true
    },
    { key: 'guestAdults', dataKey: 'adultGuests', label: 'Adult Guests (18+)', placeholder: '40 adults', type: 'number', infoKey: 'guestAdults', errorKey: 'guestAdults' },
    { key: 'guestKids', dataKey: 'kidGuests', label: 'Kids / Teens (0-17)', placeholder: '12 teens', type: 'number', infoKey: 'guestKids', errorKey: 'guestKids' },
    { key: 'budget', dataKey: 'budget', label: 'Budget Range', placeholder: '$8,000 cap', infoKey: 'budget', errorKey: 'budget' },
    { key: 'date', dataKey: 'date', label: 'Event Date', placeholder: 'Select date', type: 'date', infoKey: 'date', errorKey: 'date' },
    { key: 'timeStart', dataKey: 'timeStart', label: 'Start Time', placeholder: '6:00 PM', type: 'time', infoKey: 'timeStart', errorKey: 'timeStart' },
    { key: 'timeEnd', dataKey: 'timeEnd', label: 'End Time', placeholder: '10:00 PM', type: 'time', infoKey: 'timeEnd', errorKey: 'timeEnd' },
    { key: 'constraints', dataKey: 'constraints', label: 'Exclude / Constraints', placeholder: 'No clowns, must protect reveal', infoKey: 'constraints' }
  ]

  return (
    <div className="min-h-screen" style={{ background: BRAND.cream, color: BRAND.graphite }}>
      <header className="sticky top-0 z-30 backdrop-blur-xl border-b border-white/60" style={{ background: 'rgba(255,255,245,0.95)' }}>
        <div className="max-w-5xl mx-auto px-6 py-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between relative">
          <div>
            <p className="text-[11px] uppercase tracking-[0.35em]" style={{ color: BRAND.lime }}>Plan</p>
            <motion.h1
              className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent"
              style={{
                backgroundImage: 'linear-gradient(120deg, #FFD93D, #FF9AC5, #6BCF7E, #A5D8FF)',
                backgroundSize: '200% 200%'
              }}
              animate={{
                backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
                textShadow: [
                  '0 0 12px rgba(255,217,61,0.35)',
                  '0 0 18px rgba(107,207,126,0.45)',
                  '0 0 12px rgba(255,217,61,0.35)'
                ],
                y: [0, -2, 0],
                scale: [1, 1.015, 1]
              }}
              transition={{ repeat: Infinity, duration: 6, ease: 'easeInOut' }}
            >
              Celebration begins..
            </motion.h1>
          </div>
          <div className="flex gap-2">
            <button className="px-4 py-2 rounded-full text-sm font-semibold shadow" style={{ border: '1px solid #E8EDE5', background: 'white' }}>
              Save
            </button>
            <button className="px-4 py-2 rounded-full text-sm font-semibold text-white shadow"
              style={{ background: 'linear-gradient(135deg, #FFD93D, #2DB876)' }}>
              Share
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-10 space-y-10">
        <section className="rounded-[28px] border border-white/70 shadow-[0_20px_60px_rgba(107,207,126,0.2)] p-6"
          style={{ background: 'rgba(255,255,255,0.95)' }}>
          <div className="flex flex-col gap-4">
            <div className="flex flex-col gap-1 text-xs font-semibold uppercase tracking-[0.2em]" style={{ color: BRAND.smoke }}>
              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  onClick={fetchLocation}
                  className="inline-flex items-center gap-2 rounded-full border border-[#E8EDE5] bg-white px-3 py-1 text-[11px] normal-case font-normal tracking-normal text-gray-600 hover:border-[#C2D4C6] disabled:opacity-60"
                  disabled={isFetchingLocation}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" stroke="currentColor" fill="none" strokeWidth="2" className="text-emerald-500">
                    <path d="M12 2C8 2 5 5 5 9c0 4.2 5.6 10.4 6.3 11.2.4.5 1.1.5 1.5 0C13.4 19.4 19 13.2 19 9c0-4-3-7-7-7z" />
                    <circle cx="12" cy="9" r="2.5" />
                  </svg>
                  {isFetchingLocation ? 'Locating…' : location || 'Location not fetched — tap to detect'}
                </button>
              </div>
              {locationError && (
                <p className="text-[11px] font-medium text-red-500 normal-case tracking-normal">{locationError}</p>
              )}
            </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setActiveMode('prompt')}
                  className="flex-1 rounded-full px-4 py-3 text-sm font-semibold transition shadow-sm"
                  style={{
                    border: activeMode === 'prompt' ? 'none' : '1px solid #E8EDE5',
                    color: BRAND.graphite,
                    background:
                      activeMode === 'prompt' ? 'linear-gradient(135deg, #FFD93D, #6BCF7E)' : 'rgba(255,255,255,0.9)'
                  }}
                >
                  Tell us the vibe
                </button>
                <button
                  onClick={() => {
                    setActiveMode('classic')
                    setShowClassic(true)
                  }}
                  className="flex-1 rounded-full px-4 py-3 text-sm font-semibold transition shadow-sm"
                  style={{
                    border: activeMode === 'classic' ? 'none' : '1px solid #E8EDE5',
                    color: BRAND.graphite,
                    background:
                      activeMode === 'classic' ? 'linear-gradient(135deg, #FFD93D, #6BCF7E)' : 'rgba(255,255,255,0.9)'
                  }}
                >
                  Classic form
                </button>
              </div>

            {activeMode === 'prompt' ? (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-3">
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Describe the celebration, desired feelings, constraints..."
                  className="w-full rounded-3xl border border-[#E8EDE5] bg-white px-4 py-4 text-sm focus:outline-none focus:ring-2"
                  style={{ boxShadow: '0 8px 24px rgba(107, 207, 126, 0.15)' }}
                />
                <div className="flex justify-center">
                  <button
                    className="rounded-2xl px-10 text-white py-3 text-sm font-semibold shadow-lg transition"
                    style={{ background: 'linear-gradient(135deg, #FFD93D, #2DB876)' }}
                  >
                    Generate
                  </button>
                </div>
                <p className="text-xs" style={{ color: BRAND.smoke }}>
                  Tip: include vibe words, location hints, headcount, and any taboos.
                </p>
              </motion.div>
            ) : (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <p className="text-sm" style={{ color: BRAND.smoke }}>
                  Classic form is active. Fill the structured fields to continue.
                </p>
              </motion.div>
            )}
          </div>
        </section>

      </main>

      <footer className="border-t border-white/60" style={{ background: 'rgba(255,255,245,0.95)' }}>
        <div className="max-w-5xl mx-auto px-6 py-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.35em]" style={{ color: BRAND.lime }}>Delivery summary</p>
            <p className="text-sm text-gray-700">
              Primary intent: luminous Sweet 16 ritual. Must-do next: {ACTION_ITEMS[0].task}. Confidence:{' '}
              <span className="font-semibold text-emerald-600">82%</span>
            </p>
          </div>
          <div className="flex gap-3 flex-wrap">
            <button className="px-4 py-2 rounded-full border border-[#E8EDE5] bg-white text-sm font-semibold text-gray-700">
              Export PDF (Locked)
            </button>
            <button className="px-4 py-2 rounded-full text-white text-sm font-semibold shadow"
              style={{ background: BRAND.graphite }}>
              Share link
            </button>
          </div>
        </div>
      </footer>

      <AnimatePresence>
        {showClassic && (
          <motion.div
            className="fixed inset-0 z-40 bg-black/30 backdrop-blur-sm flex items-center justify-center px-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setShowClassic(false)}
          >
            <motion.div
              className="w-full max-w-3xl rounded-[32px] border border-white/70 bg-white p-6 space-y-4 shadow-2xl"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-xs uppercase tracking-[0.35em]" style={{ color: BRAND.lime }}>Celebration Planning Form</p>
                  <h3 className="text-xl font-semibold text-gray-900">Classic details capture</h3>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleResetForm}
                    className="px-3 py-1.5 rounded-full border border-[#E8EDE5] text-xs font-semibold text-gray-600 hover:border-[#C2D4C6]"
                  >
                    Reset
                  </button>
                  <button className="text-sm font-semibold text-gray-500 hover:text-gray-700" onClick={() => setShowClassic(false)}>
                    Close
                  </button>
                </div>
              </div>
              <div
                className="rounded-2xl border border-[#E8EDE5] bg-gradient-to-r from-[#FFFDEB] to-[#F2FFFB] p-3 text-xs text-gray-600 shadow-inner"
              >
                {generatedPrompt
                  ? <>Auto prompt preview: <span className="font-semibold text-gray-900">{generatedPrompt}</span></>
                  : 'Fill the form to auto-generate a backend prompt.'}
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {classicFields.map((field) => {
                  const value = field.key === 'location' ? classicData.locationLabel || location : classicData[field.dataKey]
                  const errorMsg = field.errorKey ? formErrors[field.errorKey] : undefined
                  const inputClasses = [
                    'rounded-2xl',
                    'px-4',
                    'py-2.5',
                    'text-sm',
                    'flex-1',
                    'transition',
                    'focus:outline-none',
                    'focus:ring-2',
                    errorMsg ? 'border-red-400 bg-red-50 focus:ring-red-200' : 'border-[#E8EDE5] bg-gray-50 focus:ring-[#FFD93D]'
                  ].join(' ')
                  return (
                    <label
                      key={field.key}
                      className={`flex flex-col gap-1 text-[13px] font-semibold ${field.fullWidth ? 'sm:col-span-2' : ''}`}
                      style={{ color: BRAND.graphite }}
                    >
                      <span className="flex items-center gap-1 text-[12px]" style={{ color: BRAND.emerald }}>
                        {field.label}
                        <InfoIcon tip={infoTips[field.infoKey]} />
                      </span>
                      {field.type === 'select' ? (
                        <select
                          className={`${inputClasses} appearance-none bg-gradient-to-r from-white to-[#F9FFF7]`}
                          value={classicData.eventType}
                          onChange={(e) => updateClassicField('eventType', e.target.value)}
                        >
                          <option value="" disabled hidden>
                            Choose an event type
                          </option>
                          {field.options?.map((option) => (
                            <option key={option} value={option}>
                              {option}
                            </option>
                          ))}
                        </select>
                      ) : (
                        <div className={`flex gap-2 ${field.fullWidth ? 'flex-col sm:flex-row sm:items-center' : ''}`}>
                          <input
                            type={field.type || 'text'}
                            min={field.type === 'number' ? 0 : undefined}
                            className={inputClasses}
                            placeholder={field.placeholder}
                            value={value}
                            onChange={(e) => updateClassicField(field.dataKey, e.target.value)}
                            onFocus={field.auto && !classicData.locationLabel ? fetchLocation : undefined}
                          />
                          {field.showButton && (
                            <button
                              type="button"
                              onClick={fetchLocation}
                              className="px-4 py-2 rounded-2xl border border-[#E8EDE5] text-xs font-semibold text-gray-600 bg-white shadow-sm"
                            >
                              {isFetchingLocation ? 'Locating…' : 'Use GPS'}
                            </button>
                          )}
                        </div>
                      )}
                      {errorMsg && <p className="text-[11px] font-medium text-red-500">{errorMsg}</p>}
                    </label>
                  )
                })}
                <label className="flex flex-col gap-1 text-[13px] font-semibold" style={{ color: BRAND.graphite }}>
                  <span className="flex items-center gap-1 text-[12px]" style={{ color: BRAND.emerald }}>
                    Guest Notes / Dietary
                    <InfoIcon tip={infoTips.guestNotes} />
                  </span>
                  <textarea
                    className="rounded-2xl border border-[#E8EDE5] bg-gray-50 px-4 py-2 text-sm min-h-[70px] focus:outline-none focus:ring-2 focus:ring-[#FFD93D]"
                    placeholder="e.g., 3 vegan teens, 2 gluten-free adults."
                    value={classicData.guestNotes}
                    onChange={(e) => updateClassicField('guestNotes', e.target.value)}
                  />
                </label>
                <label className="flex flex-col gap-1 text-[13px] font-semibold sm:col-span-2" style={{ color: BRAND.graphite }}>
                  <span className="flex items-center gap-1 text-[12px]" style={{ color: BRAND.emerald }}>
                    Extra Notes
                    <InfoIcon tip={infoTips.extraNotes} />
                  </span>
                  <textarea
                    className="rounded-2xl border border-[#E8EDE5] bg-gray-50 px-4 py-3 text-sm min-h-[120px] focus:outline-none focus:ring-2 focus:ring-[#FFD93D]"
                    placeholder="Add traditions, taboos, scheduling constraints..."
                    value={classicData.extraIntent}
                    onChange={(e) => updateClassicField('extraIntent', e.target.value)}
                  />
                </label>
              </div>
              <div className="space-y-3">
                <button
                  onClick={handlePlanSubmit}
                  className="w-full rounded-2xl text-white py-3 font-semibold text-sm shadow-lg transition hover:shadow-xl"
                  style={{ background: 'linear-gradient(135deg, #FFD93D, #2DB876)' }}
                >
                  Plan
                </button>
                {formStatus && (
                  <p
                    className={`text-sm text-center font-medium ${
                      formStatus.type === 'error' ? 'text-red-500' : 'text-emerald-600'
                    }`}
                  >
                    {formStatus.message}
                  </p>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
