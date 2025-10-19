'use client'

import { useEffect, useMemo, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import Link from 'next/link'
import { useDemoOrchestration } from '@/hooks/useDemoOrchestration'
import { demoScenarios, type DemoAgentKey, type DemoScenarioKey } from '@/data/demoAgents'

type WorkflowStatus = 'available' | 'soon'

type WorkflowConfig = {
  id: string
  name: string
  tagline: string
  description: string
  status: WorkflowStatus
  highlights: { title: string; content: string }[]
  badges: string[]
  defaultPrimary: string
  defaultSecondary: string[]
}

const WORKFLOWS: WorkflowConfig[] = [
  {
    id: 'birthday',
    name: 'Birthday Glow Blueprint',
    tagline: 'Instagram sparkle reel → tween birthday master plan',
    description:
      'Paste the reel link or type the glittery prompt and watch the agents spin up a shimmer-forward birthday kit in seconds.',
    status: 'available',
    highlights: [
      { title: 'Start from Inspiration', content: 'Drop an Instagram link or typed prompt — we auto-classify the vibe.' },
      { title: 'Tween-Centric Flow', content: 'Balance shimmer décor, pizza parade, and parent logistics in one pass.' },
      { title: 'Budget Guardrails', content: 'See how loft rentals, balloons, and sweet reveals ladder into budget ranges.' }
    ],
    badges: ['Mock Data', 'Birthday', '≈ 60 sec'],
    defaultPrimary: 'theme_agent',
    defaultSecondary: ['cake_agent', 'balloon_agent']
  },
  {
    id: 'baby_shower',
    name: 'Boho Baby Shower Brunch',
    tagline: 'Prompt typing → golden-hour shower orchestration',
    description:
      'Type the brunch vision or share the board and let agents co-create a pampas-filled baby shower with bilingual hospitality.',
    status: 'available',
    highlights: [
      { title: 'Prompt-to-Plan', content: 'Typed request becomes theme, florals, and keepsake stations automatically.' },
      { title: 'Hospitality Sync', content: 'Coordinate brunch caterers, spritz bar, and bouquet station down to rentals.' },
      { title: 'Hybrid Friendly', content: 'Livestream-ready upgrades and bilingual signage included in the draft.' }
    ],
    badges: ['Mock Data', 'Baby Shower', 'Brunch Ready'],
    defaultPrimary: 'catering_agent',
    defaultSecondary: ['decor_agent', 'planner_agent']
  },
  {
    id: 'graduation',
    name: 'Graduation Festival Flow',
    tagline: 'Backyard reel → grad-night festival timeline',
    description:
      'Share the grad-night Instagram reel or typed notes and turn them into a taco-truck-lined celebration board.',
    status: 'available',
    highlights: [
      { title: 'Reel-to-Rundown', content: 'Stage, donor lounge, and sparkler cues auto-fill from the inspiration link.' },
      { title: 'Vendor Mission', content: 'Food trucks, balloon tunnels, and AV come pre-synced with parking ops.' },
      { title: 'Scholarship Ready', content: 'Callouts for scholarship donors, reveal moments, and bilingual signage baked in.' }
    ],
    badges: ['Mock Data', 'Graduation', 'Backyard'],
    defaultPrimary: 'venue_agent',
    defaultSecondary: ['vendor_agent', 'budget_agent']
  },
  {
    id: 'milestone_escape',
    name: '40th Muse Escape',
    tagline: 'Instagram moodboard → luxe Cabo weekend',
    description:
      'Hand over the Instagram moodboard or typed vibe and agents will choreograph villas, catamaran, and spa rituals.',
    status: 'available',
    highlights: [
      { title: 'Inspo to Itinerary', content: 'Reel + prompt instantly map to a three-day Cabo celebration for 12 women.' },
      { title: 'Concierge Coordination', content: 'Transfers, catamaran sail, chefs, and daily digests planned up front.' },
      { title: 'Wellness & Nightlife', content: 'Sunrise rituals and nightlife glam share the same timeline effortlessly.' }
    ],
    badges: ['Mock Data', '40th Escape', '3-Day Flow'],
    defaultPrimary: 'planner_agent',
    defaultSecondary: ['venue_agent', 'vendor_agent']
  }
]

const agentDefinitions = [
  { key: 'input_classifier', name: 'Inspiration Capture', emoji: '🔗' },
  { key: 'theme_agent', name: 'Theme Vision', emoji: '🌈' },
  { key: 'cake_agent', name: 'Cake Studio', emoji: '🎂' },
  { key: 'decor_agent', name: 'Décor Direction', emoji: '✨' },
  { key: 'balloon_agent', name: 'Balloon Artists', emoji: '🎈' },
  { key: 'venue_agent', name: 'Venue Search', emoji: '📍' },
  { key: 'catering_agent', name: 'Culinary Flow', emoji: '🍕' },
  { key: 'budget_agent', name: 'Budget Pulse', emoji: '💰' },
  { key: 'vendor_agent', name: 'Vendor Roster', emoji: '🛠️' },
  { key: 'planner_agent', name: 'Final Plan', emoji: '🗓️' }
] as const

const shortenLink = (value?: string) => {
  if (!value) return 'Not provided'
  try {
    const url = new URL(value)
    return url.hostname.replace(/^www\./, '')
  } catch {
    return value.length > 32 ? `${value.slice(0, 29)}…` : value
  }
}

const formatCurrencyRange = (range?: { min?: number; max?: number; estimated?: number }) => {
  if (!range) return 'Unknown'
  const min = range.min ?? range.estimated
  const max = range.max ?? range.estimated
  if (min != null && max != null) {
    return `$${min.toLocaleString()} – $${max.toLocaleString()}`
  }
  if (min != null) return `$${min.toLocaleString()}`
  return 'TBD'
}

const buildAgentHighlights = (agentKey: DemoAgentKey, result: Record<string, any>) => {
  const arr = (value: any) => (Array.isArray(value) ? value.length : 0)
  const safeString = (value?: string) => (value ? (value.length > 36 ? `${value.slice(0, 33)}…` : value) : '—')

  switch (agentKey) {
    case 'input_classifier':
      return [
        { label: 'Source', value: shortenLink(result?.source) },
        { label: 'Insights', value: `${arr(result?.highlights)} key visuals` }
      ]
    case 'theme_agent':
      return [
        { label: 'Palette', value: `${arr(result?.palette)} colors` },
        { label: 'Alternatives', value: `${arr(result?.alternative_themes)} options` }
      ]
    case 'cake_agent':
      return [
        { label: 'Bakeries', value: `${arr(result?.recommended_bakeries)} curated` },
        { label: 'Flavors', value: `${arr(result?.flavor_profile)} notes` }
      ]
    case 'decor_agent':
      return [
        { label: 'Focal Elements', value: `${arr(result?.focal_elements)} hero moments` },
        { label: 'DIY Tips', value: `${arr(result?.diy_tips)} quick wins` }
      ]
    case 'balloon_agent':
      return [
        { label: 'Artists', value: `${arr(result?.recommended_artists)} specialists` },
        { label: 'Signature Idea', value: safeString(result?.quick_win) }
      ]
    case 'venue_agent':
      return [
        { label: 'Venues', value: `${arr(result?.recommended_venues)} matches` },
        { label: 'Virtual Tour', value: shortenLink(result?.virtual_tour) }
      ]
    case 'catering_agent':
      return [
        { label: 'Caterers', value: `${arr(result?.recommended_caterers)} options` },
        { label: 'Menu Pairings', value: `${arr(result?.menu_pairings)} highlights` }
      ]
    case 'budget_agent':
      return [
        { label: 'Total Budget', value: formatCurrencyRange(result?.total_budget) },
        { label: 'Categories', value: `${arr(result?.allocation)} allocations` }
      ]
    case 'vendor_agent':
      return [
        { label: 'Categories', value: `${Object.keys(result?.vendors_by_category ?? {}).length} covered` },
        { label: 'Strategy', value: safeString(result?.contact_strategy) }
      ]
    case 'planner_agent':
      return [
        { label: 'Agenda', value: `${arr(result?.final_plan?.agenda)} beats` },
        { label: 'Checklist', value: `${arr(result?.final_plan?.checklist)} tasks` }
      ]
    default:
      return []
  }
}

export default function DemoPage() {
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<string>(WORKFLOWS[0].id)
  const selectedWorkflow = useMemo(
    () => WORKFLOWS.find(workflow => workflow.id === selectedWorkflowId) ?? WORKFLOWS[0],
    [selectedWorkflowId]
  )

  const scenarioKey = selectedWorkflow.id as DemoScenarioKey
  const currentScenario = demoScenarios[scenarioKey]
  const demoAgentResults = useMemo(() => currentScenario.agentResults, [currentScenario])
  const { currentAgent, completedAgents, workflowStatus, getAgentResult, startDemo } = useDemoOrchestration(scenarioKey)

  const [showOverview, setShowOverview] = useState(false)
  const timelineRefs = useRef<Record<string, HTMLDivElement | null>>({})

  useEffect(() => {
    setShowOverview(false)
  }, [selectedWorkflowId])

  const getAgentPresentation = (agentKey: string) => {
    const index = agentDefinitions.findIndex(def => def.key === agentKey)
    const isCompleted = completedAgents.includes(agentKey)
    const isRunning = currentAgent === agentKey

    let status: 'idle' | 'running' | 'completed' | 'error' = 'idle'
    if (isCompleted) status = 'completed'
    else if (isRunning) status = 'running'

    const borderPalette = [
      'from-blue-400 to-indigo-400',
      'from-purple-400 to-pink-400',
      'from-teal-400 to-emerald-400',
      'from-orange-400 to-red-400'
    ]
    const borderColor = borderPalette[index % borderPalette.length]

    return {
      status,
      borderColor,
      data: getAgentResult(agentKey)
    }
  }

  const isPlayable = selectedWorkflow.status === 'available'

  const handlePlayWorkflow = () => {
    if (!isPlayable) return
    startDemo()
    setShowOverview(true)
  }

  const totalAgents = agentDefinitions.length
  const completedCount = completedAgents.length
  const progressPercent = Math.min(100, Math.round((completedCount / totalAgents) * 100))

  const activeAgentKey = useMemo<DemoAgentKey | null>(() => {
    const fallback = currentAgent ?? completedAgents.slice(-1)[0] ?? 'theme_agent'
    if (!fallback) return null
    const key = fallback as DemoAgentKey
    return demoAgentResults[key] ? key : null
  }, [currentAgent, completedAgents, demoAgentResults])

  const activeAgentDefinition = activeAgentKey ? agentDefinitions.find(def => def.key === activeAgentKey) : null
  const activeDemoData = activeAgentKey ? demoAgentResults[activeAgentKey] : undefined
  const activeHighlights = useMemo(() => {
    if (!activeAgentKey || !activeDemoData) return []
    return buildAgentHighlights(activeAgentKey, activeDemoData.result).filter(item => item && item.value).slice(0, 4)
  }, [activeAgentKey, activeDemoData])

  const vendorCity =
    activeDemoData?.result?.final_plan?.contact_sheet?.[0]?.city ?? currentScenario.metadata.city
  const vendorHeading = vendorCity ? `Lead Vendors — ${vendorCity}` : 'Lead Vendors'

  useEffect(() => {
    if (!showOverview || !activeAgentKey) return
    const node = timelineRefs.current[activeAgentKey]
    if (node && typeof node.scrollIntoView === 'function') {
      node.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }, [activeAgentKey, showOverview]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#fdf7ff] via-[#edf3ff] to-[#e6fffb] text-gray-800 relative">
      <motion.div
        aria-hidden="true"
        className="pointer-events-none absolute -top-24 right-10 h-72 w-72 rounded-full bg-gradient-to-br from-blue-500/40 via-purple-400/30 to-transparent blur-3xl"
        animate={{ y: [0, -20, 10, 0], opacity: [0.55, 0.75, 0.6, 0.55] }}
        transition={{ duration: 14, repeat: Infinity, repeatType: 'mirror', ease: 'easeInOut' }}
      />
      <motion.div
        aria-hidden="true"
        className="pointer-events-none absolute bottom-10 left-[-6rem] h-64 w-64 rounded-full bg-gradient-to-br from-pink-400/35 via-orange-300/25 to-transparent blur-3xl"
        animate={{ y: [0, 15, -10, 0], x: [0, 10, -5, 0], opacity: [0.4, 0.55, 0.45, 0.4] }}
        transition={{ duration: 18, repeat: Infinity, repeatType: 'mirror', ease: 'easeInOut' }}
      />
      <div className="max-w-6xl mx-auto px-6 pt-16 pb-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          className="relative mb-10 flex flex-col gap-6 overflow-hidden rounded-4xl border border-white/60 bg-white/80 px-6 py-6 shadow-[0_25px_80px_rgba(126,139,255,0.18)] backdrop-blur-xl md:px-10 md:py-8"
        >
          <motion.span
            aria-hidden="true"
            className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(59,130,246,0.18),_transparent_55%)]"
            initial={{ opacity: 0.5 }}
            animate={{ opacity: [0.45, 0.7, 0.5] }}
            transition={{ duration: 8, repeat: Infinity, repeatType: 'mirror' }}
          />
          <motion.span
            aria-hidden="true"
            className="pointer-events-none absolute -bottom-16 right-16 h-40 w-40 rounded-full bg-gradient-to-br from-indigo-500/20 via-purple-400/20 to-transparent blur-2xl"
            animate={{ x: [0, 12, -8, 0], y: [0, -10, 6, 0], opacity: [0.4, 0.6, 0.45, 0.4] }}
            transition={{ duration: 12, repeat: Infinity, repeatType: 'mirror' }}
          />
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <Link href="/" className="group flex items-center gap-3">
              <span className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 text-2xl font-semibold text-white shadow-lg shadow-blue-500/30 transition-transform duration-300 group-hover:scale-105">
                F
              </span>
              <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-2xl font-semibold text-transparent">
                Festimo Demo Studio
              </span>
            </Link>
            <span className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.3em] text-blue-500/80">
              Mock Workflows
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-blue-500" />
            </span>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="group relative">
              <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-blue-500/20 via-indigo-500/10 to-purple-500/10 opacity-0 blur-lg transition-opacity duration-300 group-hover:opacity-100" />
              <div className="relative rounded-2xl border border-white/60 bg-white/75 px-4 py-3 shadow-[0_12px_35px_rgba(59,113,202,0.12)] transition-all duration-300 group-hover:-translate-y-1">
                <div className="text-xs font-semibold uppercase tracking-[0.2em] text-gray-400">Start Any Flow</div>
                <p className="mt-1.5 text-sm text-gray-600">
                  Paste an Instagram link or type a party prompt and watch agents choreograph the plan in seconds.
                </p>
              </div>
            </div>
            <div className="group relative">
              <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-purple-500/20 via-pink-500/10 to-orange-500/10 opacity-0 blur-lg transition-opacity duration-300 group-hover:opacity-100" />
              <div className="relative rounded-2xl border border-white/60 bg-white/75 px-4 py-3 shadow-[0_12px_35px_rgba(192,88,243,0.12)] transition-all duration-300 group-hover:-translate-y-1">
                <div className="text-xs font-semibold uppercase tracking-[0.2em] text-gray-400">Scenario Variety</div>
                <p className="mt-1.5 text-sm text-gray-600">
                  Birthday, baby shower, graduation, and milestone escapes showcase different agent combinations.
                </p>
              </div>
            </div>
            <div className="group relative">
              <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-teal-500/20 via-blue-500/10 to-purple-500/10 opacity-0 blur-lg transition-opacity duration-300 group-hover:opacity-100" />
              <div className="relative rounded-2xl border border-white/60 bg-white/75 px-4 py-3 shadow-[0_12px_35px_rgba(16,185,129,0.12)] transition-all duration-300 group-hover:-translate-y-1">
                <div className="text-xs font-semibold uppercase tracking-[0.2em] text-gray-400">Mock Data Only</div>
                <p className="mt-1.5 text-sm text-gray-600">
                  Every response is curated sample output so you can preview the orchestration before going live.
                </p>
              </div>
            </div>
          </div>
          <motion.div
            aria-hidden="true"
            className="mx-auto mt-2 h-px w-3/4 bg-gradient-to-r from-transparent via-blue-500/40 to-transparent"
            initial={{ scaleX: 0.6, opacity: 0 }}
            animate={{ scaleX: [0.6, 1, 0.9], opacity: [0, 1, 1] }}
            transition={{ duration: 2, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
          />
        </motion.div>

        <div className="overflow-x-auto pb-5 no-scrollbar">
          <div className="flex gap-4 min-w-max">
            {WORKFLOWS.map(workflow => {
              const isSelected = workflow.id === selectedWorkflow.id
              return (
                <motion.button
                  key={workflow.id}
                  onClick={() => setSelectedWorkflowId(workflow.id)}
                  type="button"
                  className={`relative rounded-3xl px-6 py-5 text-left transition-all duration-300 border ${
                    isSelected
                      ? 'bg-white/90 border-white shadow-[0_20px_45px_rgba(125,137,255,0.25)]'
                      : 'bg-white/60 border-white/60 hover:bg-white/80 hover:shadow-lg'
                  }`}
                  whileHover={{ y: -6, scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="flex items-center gap-2 text-xs uppercase tracking-[0.3em] text-gray-400 mb-2">
                    <span>{workflow.status === 'available' ? 'LIVE DEMO' : 'COMING SOON'}</span>
                    {isSelected && <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />}
                  </div>
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="text-lg font-semibold text-gray-800">{workflow.name}</div>
                      <div className="text-sm text-gray-500 mt-1 max-w-xs">{workflow.tagline}</div>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        workflow.status === 'available'
                          ? 'bg-blue-500/15 text-blue-600'
                          : 'bg-gray-200 text-gray-600'
                      }`}
                    >
                      {workflow.status === 'available' ? 'Play' : 'Soon'}
                    </span>
                  </div>
                </motion.button>
              )
            })}
          </div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          className="rounded-4xl bg-white/80 backdrop-blur-2xl border border-white/60 shadow-[0_35px_120px_rgba(126,139,255,0.18)] overflow-hidden relative"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-pink-500/10 pointer-events-none" />
          <div className="relative px-8 py-10 lg:px-16 lg:py-14 flex flex-col gap-8 lg:gap-10">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
              <div className="space-y-5">
                <motion.span
                  className="inline-flex items-center gap-2 text-xs tracking-[0.35em] uppercase text-gray-500"
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1, duration: 0.5 }}
                >
                  {selectedWorkflow.status === 'available' ? 'DEMO WORKFLOW' : 'COMING SOON'}
                </motion.span>
                <motion.h1
                  className="text-3xl lg:text-4xl xl:text-5xl font-semibold text-gray-900 leading-tight"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2, duration: 0.6 }}
                >
                  {selectedWorkflow.tagline}
                </motion.h1>
                <motion.p
                  className="text-base lg:text-lg text-gray-600 max-w-2xl"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3, duration: 0.6 }}
                >
                  {selectedWorkflow.description}
                </motion.p>
                <motion.div
                  className="flex flex-wrap items-center gap-3"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4, duration: 0.6 }}
                >
                  <button
                    type="button"
                    onClick={handlePlayWorkflow}
                    disabled={!isPlayable}
                    className={`px-5 py-3 rounded-full font-semibold transition-all duration-300 ${
                      isPlayable
                        ? 'bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 text-white shadow-lg shadow-blue-500/30 hover:shadow-xl hover:shadow-blue-500/40'
                        : 'bg-gray-200 text-gray-500 cursor-not-allowed'
                    }`}
                  >
                    {isPlayable ? `Play “${selectedWorkflow.name}”` : 'Workflow arriving soon'}
                  </button>
                  <Link
                    href="/"
                    className="px-5 py-3 rounded-full border border-blue-500/30 text-blue-600 font-semibold hover:bg-blue-500/10 transition-colors duration-200"
                  >
                    Back to main app
                  </Link>
                </motion.div>
                <motion.div
                  className="flex flex-wrap gap-2"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5, duration: 0.6 }}
                >
                  {selectedWorkflow.badges.map(badge => (
                    <span
                      key={badge}
                      className="px-3 py-1 rounded-full bg-white/70 border border-white/60 text-xs font-semibold text-gray-600"
                    >
                      {badge}
                    </span>
                  ))}
                </motion.div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>

      <AnimatePresence>
        {showOverview && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm px-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="relative w-full max-w-6xl max-h-[90vh] bg-white/95 backdrop-blur-xl border border-white/70 rounded-[2.5rem] shadow-[0_55px_150px_rgba(59,113,202,0.35)] overflow-hidden flex flex-col"
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 30 }}
              transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
            >
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-purple-500/10 to-pink-500/10 pointer-events-none" />
              <div className="relative flex-1 overflow-y-auto">
                <div className="p-8 lg:p-11 xl:p-12 space-y-10">
                  <div className="space-y-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-xs uppercase tracking-[0.3em] text-gray-500">
                        Workflow Overview
                        <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse" />
                      </div>
                      <button
                        type="button"
                        onClick={() => setShowOverview(false)}
                        className="w-10 h-10 rounded-full bg-white text-gray-600 border border-white/70 shadow hover:shadow-lg hover:text-gray-800 transition-all flex items-center justify-center"
                        aria-label="Close overview"
                        title="Close overview"
                      >
                        ×
                      </button>
                    </div>
                    <div>
                      <div className="text-2xl font-semibold text-gray-900">{selectedWorkflow.name}</div>
                      <div className="mt-2 text-sm text-gray-500 leading-relaxed">{selectedWorkflow.description}</div>
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-xs font-semibold text-gray-500 uppercase tracking-wide">
                        <span>Progress</span>
                        <span>{progressPercent}%</span>
                      </div>
                      <div className="w-full h-2 rounded-full bg-gray-200/60 overflow-hidden">
                        <motion.div
                          className="h-full bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 rounded-full"
                          animate={{ width: `${progressPercent}%` }}
                          transition={{ duration: 0.5 }}
                          style={{ width: `${progressPercent}%` }}
                        />
                      </div>
                      <div className="flex items-center gap-3 text-xs text-gray-500">
                        <span className="px-2 py-1 rounded-full bg-blue-500/10 text-blue-600 font-semibold">
                          {completedCount}/{totalAgents} agents done
                        </span>
                        <span>
                          {workflowStatus === 'completed'
                            ? 'Workflow completed — explore the final plan below.'
                            : workflowStatus === 'running'
                              ? 'Agents are collaborating — watch each milestone update in real-time.'
                              : 'Press play to watch the inspiration flow.'}
                        </span>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={handlePlayWorkflow}
                      className="w-full px-4 py-3 rounded-2xl bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 text-white font-semibold shadow-lg shadow-blue-500/20 hover:shadow-xl hover:shadow-blue-500/30 transition-all duration-300"
                    >
                      Replay Workflow
                    </button>
                  </div>
                  <div className="grid lg:grid-cols-[1.3fr,1.7fr] gap-8 items-start">
                    <div className="space-y-5">
                      <div className="text-sm font-semibold text-gray-600 uppercase tracking-wide">Agent Timeline</div>
                      <div className="max-h-[420px] overflow-y-auto pr-2 space-y-3 scroll-smooth">
                        {agentDefinitions.map(agent => {
                          const presentation = getAgentPresentation(agent.key)
                          const isCompleted = presentation.status === 'completed'
                          const isRunning = presentation.status === 'running'
                          const isActive = agent.key === activeAgentKey
                          const statusLabel = isCompleted ? 'Completed' : isRunning ? 'In Progress' : 'Queued'
                          const demoData = demoAgentResults[agent.key as DemoAgentKey]
                          const timelineHighlights = demoData
                            ? buildAgentHighlights(agent.key as DemoAgentKey, demoData.result).slice(0, 2)
                            : []

                          return (
                            <div
                              key={agent.key}
                              ref={node => {
                                timelineRefs.current[agent.key as DemoAgentKey] = node
                              }}
                              className={`rounded-2xl border p-4 transition-all duration-300 ${
                                isActive
                                  ? 'border-blue-400/70 bg-blue-50/80 shadow-lg shadow-blue-200/60'
                                  : isCompleted
                                    ? 'border-emerald-300/60 bg-emerald-50/60'
                                    : isRunning
                                      ? 'border-blue-200/60 bg-blue-50/60'
                                      : 'border-white/70 bg-white/70'
                              }`}
                            >
                              <div className="flex items-center justify-between gap-3">
                                <div className="flex items-center gap-3">
                                  <span className="text-lg">{agent.emoji}</span>
                                  <div>
                                    <div className="font-semibold text-gray-800">{agent.name}</div>
                                    <div className="text-xs text-gray-500">
                                      Agent {agentDefinitions.indexOf(agent) + 1} of {totalAgents}
                                    </div>
                                  </div>
                                </div>
                                <span
                                  className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wide ${
                                    isActive
                                      ? 'bg-blue-500/10 text-blue-600'
                                      : isCompleted
                                        ? 'bg-emerald-500/10 text-emerald-600'
                                        : isRunning
                                          ? 'bg-blue-500/10 text-blue-600'
                                          : 'bg-gray-200 text-gray-600'
                                  }`}
                                >
                                  {statusLabel}
                                </span>
                              </div>
                              {demoData?.summary && (
                                <div className="mt-3 text-sm leading-relaxed text-gray-600">{demoData.summary}</div>
                              )}
                              {timelineHighlights.length > 0 && (
                                <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2">
                                  {timelineHighlights.map(item => (
                                    <div
                                      key={item.label}
                                      className="rounded-xl border border-white/70 bg-white/70 px-3 py-2"
                                    >
                                      <div className="text-[11px] uppercase tracking-[0.2em] text-gray-400">
                                        {item.label}
                                      </div>
                                      <div className="text-sm font-medium text-gray-700 mt-0.5">{item.value}</div>
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                          )
                        })}
                      </div>
                    </div>
                    <div className="rounded-2xl bg-white/80 border border-white/60 p-5 space-y-4">
                      {activeDemoData?.result?.final_plan?.budget?.estimated && (
                        <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-600 text-sm font-semibold">
                          Est. Budget ${activeDemoData.result.final_plan.budget.estimated.toLocaleString()}
                        </span>
                      )}
                      {activeDemoData?.result?.final_plan?.agenda && (
                        <div>
                          <div className="text-xs uppercase tracking-[0.2em] text-gray-400 mb-2">Agenda Highlights</div>
                          <div className="space-y-2 text-sm text-gray-600">
                            {activeDemoData.result.final_plan.agenda.map((item: any, idx: number) => (
                              <div key={`${item.time}-${idx}`} className="flex gap-3">
                                <span className="text-xs font-semibold text-blue-500 min-w-[60px]">{item.time}</span>
                                <span>{item.activity}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      {activeDemoData?.result?.final_plan?.budget?.allocation && (
                        <div>
                          <div className="text-xs uppercase tracking-[0.2em] text-gray-400 mb-2">Budget Allocation</div>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-gray-600">
                            {activeDemoData.result.final_plan.budget.allocation.map((item: any) => (
                              <div
                                key={item.category}
                                className="rounded-xl border border-white/60 bg-white/60 px-3 py-2 flex items-center justify-between"
                              >
                                <span>{item.category}</span>
                                <span className="font-semibold text-gray-800">${item.amount.toLocaleString()}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      {activeDemoData?.result?.final_plan?.contact_sheet && (
                        <div>
                          <div className="text-xs uppercase tracking-[0.2em] text-gray-400 mb-2">{vendorHeading}</div>
                          <div className="space-y-2 text-sm text-gray-600">
                            {activeDemoData.result.final_plan.contact_sheet.map((vendor: any) => (
                              <div
                                key={vendor.name}
                                className="rounded-xl border border-white/60 bg-white/60 px-3 py-2 flex items-center justify-between"
                              >
                                <div>
                                  <div className="font-semibold text-gray-800">{vendor.name}</div>
                                  <div className="text-xs text-gray-500">
                                    {vendor.role} · {vendor.city}
                                  </div>
                                </div>
                                <span className="text-xs text-blue-500">{vendor.contact}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      {activeDemoData?.result?.final_plan?.checklist && (
                        <div>
                          <div className="text-xs uppercase tracking-[0.2em] text-gray-400 mb-2">Checklist</div>
                          <ul className="space-y-1 text-sm text-gray-600 list-disc list-inside">
                            {activeDemoData.result.final_plan.checklist.map((item: string) => (
                              <li key={item}>{item}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      <div className="pt-2 flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
                        <span className="text-xs text-gray-500">
                          This recap is auto-generated from the demo dataset. Swap in real agents to receive
                          production-ready plans.
                        </span>
                        <button
                          type="button"
                          className="w-full sm:w-auto px-4 py-2 rounded-xl bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-500 text-white text-sm font-semibold shadow shadow-blue-500/20 hover:shadow-lg hover:shadow-blue-500/30 transition-all"
                        >
                          Proceed to Checkout
                        </button>
                        <button
                          type="button"
                          className="w-full sm:w-auto px-4 py-2 rounded-xl border border-blue-500/30 text-blue-600 text-sm font-semibold hover:bg-blue-50 transition-colors"
                        >
                          Save & Checkout Later
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
