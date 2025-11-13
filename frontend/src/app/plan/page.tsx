'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

type PlanBlock = {
  title: string
  intent: string
  highlights: string[]
  nudges: string[]
}

const PLAN_BLOCKS: PlanBlock[] = [
  {
    title: 'Celebration Narrative',
    intent: 'Honor Maya’s Sweet 16 with a luminous “Neon Bloom” ritual that feels older than confetti yet still playful.',
    highlights: [
      'Arrival runway with glow sensors → audio guestbook → lighting reveal.',
      'Emotional arc: awe on arrival, intimacy during dinner pods, catharsis on dance floor.',
      'Anchor Maya’s art-school sketches into projection textures.'
    ],
    nudges: [
      'Capture 20-second reflections from each guest for a Monday highlight reel.',
      'Script two surprise micro-moments (light wand entrance, parent toast remix).'
    ]
  },
  {
    title: 'Atmosphere Canvas',
    intent: 'Curate a sensory palette that teaches “calm intent” for every future plan.',
    highlights: [
      'Palette: ultraviolet core, champagne haze, matte midnight anchor.',
      'Materials: sheer voile drapes, chrome plinths, velvet conversation cubes.',
      'Scent cue: grapefruit + cedar diffusers triggered at check-in.'
    ],
    nudges: [
      'Label each décor zone with a verb (Glow, Drift, Bloom) so ops stay aligned.',
      'Program lighting presets tied to timeline steps to avoid panic switching.'
    ]
  },
  {
    title: 'Spatial Playbook',
    intent: 'Guide guests through discovery loops instead of parking them at a single table.',
    highlights: [
      'Flow: Arrival runway → Aura Scan booth → Dinner pods → Bloom Lab dessert studio.',
      'Projection-mapped arrows nudge traffic every 30 min.',
      'Polaroid gratitude wall doubles as favor pickup.'
    ],
    nudges: [
      'Send a QR mini-map with invites so guests anticipate the route.',
      'Assign two “energy hosts” to pulse groups without shouting instructions.'
    ]
  },
  {
    title: 'Menu & Bar Cadence',
    intent: 'Mindful indulgence—light, interactive, color-synced with light scenes.',
    highlights: [
      'Progressive bites served in three drops, each echoing palette colors.',
      'Mocktail lab unlocking flavors via NFC cards.',
      'Warm finale: molten cakes with edible neon sugar lattice.'
    ],
    nudges: [
      'Prep allergy tokens so guests can flag needs silently.',
      'Stack infusion pitchers labelled Calm / Elevate / Hype.'
    ]
  },
  {
    title: 'Experience Timeline',
    intent: '90-minute arc that rewards punctuality but feels spontaneous.',
    highlights: [
      '6:00–6:20 Arrival + Aura Scan (AI photobooth).',
      '6:20–6:40 Parent toast + lighting reveal.',
      '6:40–7:10 Dinner pods with conversation cards.',
      '7:10–8:00 Dance Bloom + dessert studio drop.'
    ],
    nudges: [
      'Text VIPs gentle reminders 10 min before each scene change.',
      'Use soft chimes instead of MC shout-outs to preserve atmosphere.'
    ]
  },
  {
    title: 'Budget Confidence',
    intent: 'Stay within $8,000 while reinforcing a sustainable planning habit.',
    highlights: [
      'Must-invest: lighting programming ($2,400) and culinary experiences ($1,900).',
      'Flexible: installation extras ($600), specialty florals ($750).',
      'DIY-friendly: conversation cards, gratitude wall, signage.'
    ],
    nudges: [
      'Log every DIY savings into a “habit bank” to visualize momentum.',
      'Schedule vendor check-ins 14 and 7 days prior to avoid rush fees.'
    ]
  }
]

const formatLatLng = (lat: number, lng: number) =>
  `${lat.toFixed(3)}, ${lng.toFixed(3)}`

export default function PlanPage() {
  const [prompt, setPrompt] = useState('')
  const [location, setLocation] = useState('')
  const [isFetchingLocation, setIsFetchingLocation] = useState(false)
  const [showClassic, setShowClassic] = useState(false)

  const fetchLocation = useCallback(() => {
    if (typeof navigator === 'undefined' || !navigator.geolocation) return
    setIsFetchingLocation(true)
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLocation(formatLatLng(pos.coords.latitude, pos.coords.longitude))
        setIsFetchingLocation(false)
      },
      () => setIsFetchingLocation(false),
      { timeout: 5000, maximumAge: 60000 }
    )
  }, [])

  useEffect(() => {
    if (!location) {
      fetchLocation()
    }
  }, [fetchLocation, location])

  const intentChips = useMemo(
    () => [
      { label: 'Intent', value: 'High-touch neon celebration for Sweet 16' },
      { label: 'Guest Mix', value: '40 adults · 12 teens' },
      { label: 'Budget', value: '$8,000' },
      { label: 'Location', value: location || (isFetchingLocation ? 'Detecting...' : 'Tap to auto-detect') },
      { label: 'Date', value: 'Saturday · April 19 · 6-10pm' }
    ],
    [location, isFetchingLocation]
  )

  const heroBlock = PLAN_BLOCKS[0]

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#fdf8ff] via-[#f0f2ff] to-[#fef5f0] text-gray-900">
      <header className="sticky top-0 z-40 backdrop-blur-2xl bg-white/75 border-b border-white/70">
        <div className="max-w-6xl mx-auto px-6 py-5 flex items-center justify-between">
          <div>
            <p className="text-[11px] uppercase tracking-[0.35em] text-purple-500 font-semibold">Plan Habit</p>
            <h1 className="text-2xl font-bold text-gray-900">Designer Planning Canvas</h1>
          </div>
          <div className="flex gap-3">
            <button className="px-4 py-2 rounded-full border border-gray-200 bg-white/80 text-sm font-semibold shadow-sm">Save Snapshot</button>
            <button className="px-4 py-2 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 text-white text-sm font-semibold shadow">Share Plan</button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-12 space-y-10">
        <section className="grid lg:grid-cols-2 gap-6">
          <motion.div
            className="rounded-3xl border border-white/70 bg-white/90 shadow-[0_25px_60px_rgba(81,56,237,0.08)] p-6 space-y-5"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <p className="text-xs uppercase tracking-[0.3em] text-purple-500 font-semibold">Tell us the vibe</p>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the celebration, desired feelings, constraints..."
              className="w-full min-h-[120px] rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-200"
            />
            <div className="grid gap-3 sm:grid-cols-[1fr_auto]">
              <button className="rounded-2xl bg-gray-900 text-white py-3 text-sm font-semibold">
                Generate Intent Plan
              </button>
              <button
                onClick={() => setShowClassic(true)}
                className="rounded-2xl border border-gray-200 bg-white/80 text-sm font-semibold text-purple-700 px-4 py-3"
              >
                Classic Form
              </button>
            </div>
            <p className="text-xs text-gray-500">
              Tip: include venue vibe, guest expectations, sensory cues, non-negotiables.
            </p>
          </motion.div>

          <motion.div
            className="rounded-3xl border border-white/70 bg-gradient-to-br from-white to-[#f4ecff] p-6 shadow-[0_25px_60px_rgba(111,63,203,0.12)] space-y-4"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <p className="text-xs uppercase tracking-[0.3em] text-rose-500 font-semibold">Intent snapshot</p>
            <div className="grid sm:grid-cols-2 gap-3">
              {intentChips.map((chip) => (
                <div key={chip.label} className="rounded-2xl border border-white/70 bg-white/90 p-3">
                  <p className="text-[11px] uppercase tracking-wide text-gray-500">{chip.label}</p>
                  <p className="text-sm font-semibold text-gray-900 mt-1">{chip.value}</p>
                </div>
              ))}
            </div>
            <div className="rounded-2xl border border-white/70 bg-white p-3 flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-500">Habit cue</p>
                <p className="text-sm font-semibold text-gray-900">
                  Pin one micro win per block → unlock “Calm Planner” badge.
                </p>
              </div>
              <button className="px-3 py-2 rounded-xl bg-gray-900 text-white text-xs font-semibold">View log</button>
            </div>
          </motion.div>
        </section>

        <section className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-purple-500 font-semibold">Design philosophy</p>
              <h2 className="text-2xl font-bold text-gray-900">Choreography overview</h2>
              <p className="text-sm text-gray-500 mt-1">
                Each block links intent → sensory cues → habit nudges. Scan the capsules, then deep dive below.
              </p>
            </div>
            <button className="px-4 py-2 rounded-full border border-gray-200 bg-white/80 text-sm font-semibold text-gray-700">
              Export Summary
            </button>
          </div>

          <div className="overflow-x-auto -mx-1 px-1 pb-2">
            <div className="flex gap-3 min-w-max">
              {PLAN_BLOCKS.map((block, idx) => (
                <div
                  key={`stage-chip-${block.title}`}
                  className="flex items-center gap-3 rounded-2xl border border-white/70 bg-gradient-to-r from-white to-[#f6f2ff] px-4 py-3 shadow-[0_10px_30px_rgba(60,41,120,0.08)]"
                >
                  <div className="flex flex-col items-center">
                    <span className="text-[10px] uppercase tracking-[0.4em] text-purple-400">Stage</span>
                    <span className="text-lg font-bold text-gray-900">{(idx + 1).toString().padStart(2, '0')}</span>
                  </div>
                  <div className="text-sm text-gray-700 font-semibold max-w-[180px]">
                    {block.title}
                    <p className="text-[11px] text-gray-500 font-normal">
                      {block.intent.split('.').slice(0, 1).join('.')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <motion.article
            className="rounded-[32px] border border-white/80 bg-gradient-to-br from-white via-[#fdfafd] to-[#f4ecff] p-6 shadow-[0_35px_90px_rgba(50,23,112,0.12)] grid gap-6 lg:grid-cols-[1.2fr_0.8fr]"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.4em] text-purple-500 font-semibold">Celebration Narrative</p>
                  <h3 className="text-2xl font-bold text-gray-900">Block 1</h3>
                </div>
                <span className="text-sm font-semibold text-rose-400">Ritual Layer</span>
              </div>
              <p className="text-lg font-semibold text-gray-900">{heroBlock.intent}</p>
              <div className="space-y-2">
                {heroBlock.highlights.map((highlight) => (
                  <p key={`hero-highlight-${highlight}`} className="flex gap-2 text-sm text-gray-700">
                    <span className="text-purple-300 font-bold">•</span>
                    <span>{highlight}</span>
                  </p>
                ))}
              </div>
            </div>
            <div className="rounded-3xl border border-white bg-white/80 p-5 space-y-3">
              <p className="text-xs uppercase tracking-wide text-gray-500 font-semibold">Why it matters</p>
              <p className="text-sm text-gray-700">
                This block sets the emotional grammar of the entire night. Getting Maya’s “Neon Bloom” moment right makes every downstream vendor decision easier.
              </p>
              <div className="rounded-2xl border border-purple-100 bg-purple-50/60 p-4 space-y-2">
                <p className="text-xs uppercase tracking-wide text-purple-500 font-semibold">Habit nudges</p>
                {heroBlock.nudges.map((nudge) => (
                  <p key={`hero-nudge-${nudge}`} className="text-sm text-gray-700 flex gap-2">
                    <span className="text-purple-400 font-bold">✶</span>
                    <span>{nudge}</span>
                  </p>
                ))}
              </div>
            </div>
          </motion.article>

          <div className="space-y-4">
            {PLAN_BLOCKS.slice(1).map((block, index) => (
              <motion.article
                key={block.title}
                className="rounded-3xl border border-white/70 bg-white/92 shadow-[0_15px_45px_rgba(26,26,67,0.05)] p-6 grid gap-4 lg:grid-cols-[1fr_260px]"
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xl font-semibold text-gray-900">{block.title}</h3>
                    <span className="text-xs uppercase text-gray-400 tracking-widest">Block {index + 2}</span>
                  </div>
                  <p className="text-sm text-purple-600 font-medium">{block.intent}</p>
                  <ul className="space-y-2">
                    {block.highlights.map((highlight) => (
                      <li key={highlight} className="text-sm text-gray-700 flex gap-2">
                        <span className="text-purple-300 mt-1">•</span>
                        <span>{highlight}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="rounded-2xl border border-gray-100 bg-gray-50/85 p-4 space-y-2">
                  <p className="text-xs uppercase tracking-wide text-gray-500 font-semibold">Micro nudges</p>
                  {block.nudges.map((nudge) => (
                    <p key={nudge} className="text-sm text-gray-700 border-l-2 border-purple-200 pl-3">
                      {nudge}
                    </p>
                  ))}
                  <button className="mt-3 w-full rounded-xl bg-white border border-gray-200 text-sm font-semibold text-gray-800 py-2">
                    Pin to Habit Tray
                  </button>
                </div>
              </motion.article>
            ))}
          </div>
        </section>
      </main>

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
              className="w-full max-w-xl bg-white rounded-3xl border border-white/70 p-6 space-y-4 shadow-2xl"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.3em] text-purple-500">Classic inputs</p>
                  <h3 className="text-xl font-semibold text-gray-900">Structured intent form</h3>
                </div>
                <button className="text-sm font-semibold text-gray-500 hover:text-gray-700" onClick={() => setShowClassic(false)}>
                  Close
                </button>
              </div>
              <div className="grid grid-cols-1 gap-3">
                {['Event Type', 'Occasion Name', 'Honoree', 'Location / City / Zip'].map((label) => (
                  <label key={label} className="text-xs font-semibold text-gray-600 flex flex-col gap-1">
                    {label}
                    <input
                      type="text"
                      className="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-200"
                      placeholder={label === 'Location / City / Zip' ? location || 'Auto or type location' : `Enter ${label.toLowerCase()}`}
                      value={label === 'Location / City / Zip' ? location : undefined}
                      readOnly={label === 'Location / City / Zip' && !!location}
                      onFocus={label === 'Location / City / Zip' && !location ? fetchLocation : undefined}
                    />
                  </label>
                ))}
                <label className="text-xs font-semibold text-gray-600 flex flex-col gap-1">
                  Extra Intent
                  <textarea
                    className="rounded-2xl border border-gray-200 bg-gray-50 px-4 py-2 text-sm min-h-[90px] focus:outline-none focus:ring-2 focus:ring-purple-200"
                    placeholder="Add traditions, taboos, scheduling constraints..."
                  />
                </label>
              </div>
              <button className="w-full rounded-2xl bg-gray-900 text-white py-3 font-semibold text-sm">
                Apply to Plan
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
