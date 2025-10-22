'use client'

import React, { useState, useEffect, useMemo } from 'react'
import Image, { StaticImageData } from 'next/image'
import { motion, AnimatePresence } from 'framer-motion'
import { createPortal } from 'react-dom'
import defaultThemeImage from '@/app/assets/theme_2.jpg'
import defaultCakeImage from '@/app/assets/cake_1.jpg'
import AgentDataItems, { AgentDataItem } from './AgentDataItems'

const cityIcon = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M12 21c4-4.2 6-7.2 6-10a6 6 0 1 0-12 0c0 2.8 2 5.8 6 10z" />
    <circle cx="12" cy="11" r="2.5" />
  </svg>
)

const pinIcon = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <rect x="4" y="4" width="16" height="12" rx="2" />
    <path d="M4 10h16" />
    <path d="M8 14h4" />
  </svg>
)

const calendarIcon = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <rect x="3" y="5" width="18" height="16" rx="2" />
    <path d="M16 3v4" />
    <path d="M8 3v4" />
    <path d="M3 11h18" />
  </svg>
)

const clockIcon = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <circle cx="12" cy="12" r="9" />
    <path d="M12 7v5l3 2" />
  </svg>
)

const budgetIcon = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M12 3v18" />
    <path d="M8 7a4 4 0 0 1 4-4c2.2 0 4 1.8 4 4s-1.8 4-4 4" />
    <path d="M16 17a4 4 0 0 1-4 4c-2.2 0-4-1.8-4-4s1.8-4 4-4" />
  </svg>
)

const paletteIcon = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M12 3a9 9 0 0 0-9 9 5 5 0 0 0 5 5h1a2 2 0 1 1 0 4 9 9 0 1 0 3-18z" />
    <circle cx="7.5" cy="10.5" r="1" />
    <circle cx="12" cy="7.5" r="1" />
    <circle cx="16.5" cy="10.5" r="1" />
  </svg>
)

const sparkleIcon = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="m12 3 1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5L12 3z" />
  </svg>
)

const venueIcon = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M4 22V9l8-6 8 6v13" />
    <path d="M9 22v-6h6v6" />
    <path d="M3 10h18" />
  </svg>
)

const chefIcon = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M4 20v-3a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v3" />
    <path d="M9 7V5a3 3 0 0 1 6 0v2" />
    <path d="M5 10h14" />
  </svg>
)

const balloonIcon = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M12 3c4 0 7 3 7 7 0 3.3-2.3 6.4-5 7l1 4H9l1-4c-2.7-.6-5-3.7-5-7 0-4 3-7 7-7z" />
  </svg>
)

const vendorIcon = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M4 7h16v13H4z" />
    <path d="M9 4h6l1 3H8l1-3z" />
    <path d="M9 10v4" />
    <path d="M15 10v4" />
  </svg>
)

const checklistIcon = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M9 11l3 3L22 4" />
    <path d="M3 6h3" />
    <path d="M3 12h3" />
    <path d="M3 18h3" />
  </svg>
)

const bakeryIcon = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M4 6h16v4H4z" />
    <path d="M5 6c0-2.2 2-4 4-4h6c2 0 4 1.8 4 4" />
    <path d="M6 10v10h12V10" />
    <path d="M10 14h4" />
  </svg>
)

const pickString = (...values: any[]): string | undefined => {
  for (const value of values) {
    if (!value) continue
    if (typeof value === 'string') {
      const trimmed = value.trim()
      if (trimmed) return trimmed
    }
    if (typeof value === 'number' && !Number.isNaN(value)) {
      return String(value)
    }
    if (typeof value === 'object') {
      if (typeof value.label === 'string' && value.label.trim()) return value.label.trim()
      if (typeof value.value === 'string' && value.value.trim()) return value.value.trim()
      if (typeof value.text === 'string' && value.text.trim()) return value.text.trim()
    }
  }
  return undefined
}

const parseAmount = (input: any): number | undefined => {
  if (typeof input === 'number' && !Number.isNaN(input)) return input
  if (typeof input === 'string') {
    const numeric = Number(input.replace(/[^0-9.-]+/g, ''))
    return Number.isNaN(numeric) ? undefined : numeric
  }
  return undefined
}

const formatDateValue = (value: any): string | undefined => {
  if (!value) return undefined
  if (typeof value === 'string') {
    const parsed = new Date(value)
    if (!Number.isNaN(parsed.getTime())) {
      return parsed.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      })
    }
    return value
  }
  if (typeof value === 'number') {
    return String(value)
  }
  if (typeof value === 'object') {
    if (value.date) return formatDateValue(value.date)
    if (value.start || value.end) {
      const start = formatDateValue(value.start)
      const end = formatDateValue(value.end)
      return [start, end].filter(Boolean).join(' – ')
    }
    if (value.label) return formatDateValue(value.label)
  }
  return undefined
}

const formatTimeValue = (value: any): string | undefined => {
  if (!value) return undefined
  if (typeof value === 'string') return value
  if (typeof value === 'object') {
    const start = pickString(value.start, value.begin, value.from)
    const end = pickString(value.end, value.finish, value.to)
    if (start || end) {
      return [start, end].filter(Boolean).join(' – ')
    }
    if (value.label) return value.label
  }
  return undefined
}

const formatBudgetRange = (value: any): string | undefined => {
  if (!value) return undefined
  if (typeof value === 'string') return value
  if (typeof value === 'number') {
    return new Intl.NumberFormat(undefined, {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(value)
  }
  if (typeof value === 'object') {
    const currency = typeof value.currency === 'string' && value.currency.trim()
      ? value.currency.trim().toUpperCase()
      : 'USD'
    const formatter = new Intl.NumberFormat(undefined, {
      style: 'currency',
      currency,
      maximumFractionDigits: 0
    })
    const estimated = parseAmount(value.estimated)
    if (estimated) return formatter.format(estimated)
    const min = parseAmount(value.min)
    const max = parseAmount(value.max)
    if (min && max) return `${formatter.format(min)} – ${formatter.format(max)}`
    if (min) return `From ${formatter.format(min)}`
    if (max) return `Up to ${formatter.format(max)}`
  }
  return undefined
}

const safeArray = <T,>(value: any): T[] => {
  return Array.isArray(value) ? value.filter(Boolean) : []
}

const linkIcon = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M10.59 13.41a1.996 1.996 0 0 0 2.82 0l5.59-5.59a1.996 1.996 0 0 0-2.82-2.82l-1.53 1.53" />
    <path d="M13.41 10.59a1.996 1.996 0 0 0-2.82 0l-5.59 5.59a1.996 1.996 0 0 0 2.82 2.82l1.53-1.53" />
  </svg>
)

const shortenLink = (value: string) => {
  try {
    const url = new URL(value)
    return url.hostname.replace(/^www\./, '')
  } catch {
    return value.length > 28 ? `${value.slice(0, 25)}…` : value
  }
}

const buildInputClassifierDetails = (
  data: any,
  onInteraction?: (action: string, value?: any) => void
): { items: AgentDataItem[]; highlights: string[]; nextMove?: string; confidence?: number } => {
  if (!data) {
    return { items: [], highlights: [] }
  }

  const buildAction = (action: string, value?: any) =>
    onInteraction ? () => onInteraction(action, value) : undefined

  const candidateSources = [
    data.party_summary,
    data.summary?.party,
    data.summary,
    data.extracted_event_data,
    data.extractedEventData,
    data.metadata?.extractedEventData,
    data.metadata?.party_data,
    data.metadata?.event_details,
    data.metadata?.source_data?.extractedEventData,
    data.metadata?.source_data?.extractionResult?.extracted_data,
    data.metadata?.source_data?.extraction_result?.extracted_data,
    data.metadata?.source_data?.extractionResult?.event_data,
    data.metadata?.source_data?.extraction_result?.event_data,
    data.metadata?.extraction_result?.extracted_data,
    data.metadata?.latest_inputs,
    data.metadata?.session?.extracted_event_data,
    data.party,
    data.data
  ]

  const summarySource = candidateSources.reduce<Record<string, any>>((acc, entry) => {
    if (entry && typeof entry === 'object' && !Array.isArray(entry)) {
      return { ...acc, ...entry }
    }
    return acc
  }, {})

  const locationInfo =
    summarySource.location ||
    summarySource.venue ||
    summarySource.event_location ||
    summarySource.destination ||
    data.location ||
    data.metadata?.location ||
    {}

  const locationName = pickString(
    locationInfo.name,
    summarySource.location_name,
    summarySource.venue_name,
    summarySource.destination_name,
    summarySource.location_description,
    summarySource.venue_description
  )

  const cityValue = pickString(
    summarySource.city,
    locationInfo.city,
    summarySource.region,
    summarySource.metro,
    data.city,
    data.metadata?.city
  )

  const addressValue = pickString(
    locationInfo.address,
    summarySource.location_address,
    summarySource.address
  )

  const locationType = pickString(
    locationInfo.type,
    summarySource.location_type,
    summarySource.venue_type,
    summarySource.location_category,
    data.location?.type
  )

  const locationParts = [locationType, locationName, cityValue].filter(Boolean)
  const locationDisplay = locationParts.length
    ? locationParts.join(' · ')
    : addressValue

  const dateValue = formatDateValue(
    summarySource.date ||
    summarySource.event_date ||
    summarySource.celebration_date ||
    summarySource.schedule?.date ||
    summarySource.calendar_date ||
    summarySource.timeline?.date ||
    summarySource.when ||
    summarySource.calendar ||
    data.date ||
    data.metadata?.date
  )

  const timeValue = formatTimeValue(
    summarySource.time ||
    summarySource.time_window ||
    summarySource.timeframe ||
    summarySource.schedule ||
    summarySource.schedule_window ||
    summarySource.hours ||
    summarySource.timeline?.time ||
    summarySource.event_time ||
    summarySource.time_range ||
    data.time
  )

  const budgetValue = formatBudgetRange(
    summarySource.budget ||
    summarySource.estimated_budget ||
    summarySource.total_budget ||
    summarySource.budget_range ||
    summarySource.investment ||
    data.budget ||
    data.extracted_event_data?.budget
  )

  const eventType = pickString(
    summarySource.eventType,
    summarySource.event_type,
    summarySource.occasion_type,
    summarySource.celebration_type,
    data.eventType
  )

  const guestInfo = summarySource.guestCount ||
    summarySource.guest_count ||
    summarySource.guest_counts ||
    summarySource.guests ||
    data.guestCount

  let guestValue: string | undefined
  if (guestInfo) {
    if (typeof guestInfo === 'number') {
      guestValue = `${guestInfo} guests`
    } else if (typeof guestInfo === 'string') {
      guestValue = guestInfo
    } else if (typeof guestInfo === 'object') {
      const adults = pickString(guestInfo.adults, guestInfo.adult)
      const kids = pickString(guestInfo.kids, guestInfo.children, guestInfo.kid)
      const total = pickString(guestInfo.total, guestInfo.count)
      if (total) {
        guestValue = `${total} guests`
      } else {
        const parts = [
          adults ? `${adults} adults` : null,
          kids ? `${kids} kids` : null
        ].filter(Boolean)
        guestValue = parts.join(' · ')
      }
    }
  }

  const highlightCandidates = [
    data.highlights,
    data.summary?.highlights,
    data.summary_points,
    data.top_insights,
    data.key_takeaways,
    data.insights,
    data.metadata?.highlights
  ]

  const highlights = highlightCandidates
    .filter((entry): entry is string[] => Array.isArray(entry))
    .flat()
    .filter((item): item is string => typeof item === 'string' && item.trim().length > 0)

  const uniqueHighlights = Array.from(new Set(highlights))

  const nextMove = pickString(
    data.recommended_next_step,
    data.next_best_step,
    data.next_step,
    data.summary?.next_step,
    data.action_item,
    data.recommendations?.[0]
  )

  const confidence =
    typeof data.confidence === 'number' && data.confidence > 0 && data.confidence <= 1
      ? Math.round(data.confidence * 100)
      : typeof data.confidence === 'number'
        ? Math.round(data.confidence)
        : undefined

  const sourceLink = pickString(
    data.source,
    data.source_url,
    data.metadata?.source_url,
    data.metadata?.original_url,
    data.metadata?.inputs?.[0]?.content
  )

  const items: AgentDataItem[] = []

  if (sourceLink) {
    items.push({
      key: 'source',
      label: 'Source',
      value: shortenLink(sourceLink),
      icon: linkIcon,
      tone: 'slate',
      actionLabel: 'Open',
      onAction: () => {
        if (typeof window !== 'undefined') {
          window.open(sourceLink, '_blank', 'noopener,noreferrer')
        }
      }
    })
  }

  items.push({
    key: 'location',
    label: 'Location',
    value: locationDisplay,
    hint: locationDisplay ? undefined : 'Add the celebration location to align vendors.',
    icon: venueIcon,
    tone: 'indigo',
    actionLabel: onInteraction ? 'Edit' : undefined,
    onAction: buildAction('edit_location')
  })

  items.push({
    key: 'date',
    label: 'Event Date',
    value: dateValue,
    hint: dateValue ? undefined : 'Set the event date to sync timelines.',
    icon: calendarIcon,
    tone: 'purple',
    actionLabel: onInteraction ? 'Schedule' : undefined,
    onAction: buildAction('edit_date')
  })

  items.push({
    key: 'time',
    label: 'Event Time',
    value: timeValue,
    hint: timeValue ? undefined : 'Add timing details to pace the experience.',
    icon: clockIcon,
    tone: 'amber',
    actionLabel: onInteraction ? 'Edit' : undefined,
    onAction: buildAction('edit_time')
  })

  items.push({
    key: 'budget',
    label: 'Budget Target',
    value: budgetValue,
    hint: budgetValue ? 'Recommendations will stay within this range.' : 'Drop a range to frame recommendations.',
    icon: budgetIcon,
    tone: 'emerald',
    actionLabel: onInteraction ? 'Adjust' : undefined,
    onAction: buildAction('edit_budget')
  })

  items.push({
    key: 'event-type',
    label: 'Event Type',
    value: eventType,
    hint: eventType ? undefined : 'Tell us the occasion to activate the right agents.',
    icon: sparkleIcon,
    tone: 'blue',
    actionLabel: onInteraction ? 'Edit' : undefined,
    onAction: buildAction('edit_event_type')
  })

  items.push({
    key: 'guest-count',
    label: 'Guest Count',
    value: guestValue,
    hint: guestValue ? undefined : 'Add a guest estimate to size venues and catering.',
    icon: balloonIcon,
    tone: 'rose',
    actionLabel: onInteraction ? 'Edit' : undefined,
    onAction: buildAction('edit_guest_count')
  })

  return {
    items,
    highlights: uniqueHighlights,
    nextMove,
    confidence
  }
}

const buildGenericHighlights = (
  agentKey: string,
  data: any,
  onInteraction?: (action: string, value?: any) => void
): AgentDataItem[] => {
  if (!data) return []

  const buildAction = (action: string) => onInteraction ? () => onInteraction(action) : undefined
  const items: AgentDataItem[] = []

  switch (agentKey) {
    case 'budget_agent': {
      let budgetValue = 1000
      if (data.total_budget) {
        if (typeof data.total_budget === 'object') {
          budgetValue = data.total_budget.estimated || data.total_budget.min || data.total_budget.max || 1000
        } else if (typeof data.total_budget === 'number') {
          budgetValue = data.total_budget
        } else if (typeof data.total_budget === 'string') {
          budgetValue = parseInt(data.total_budget) || 1000
        }
      }

      const currency = data.currency || data.total_budget?.currency || 'USD'
      const formattedBudget = new Intl.NumberFormat(undefined, {
        style: 'currency',
        currency,
        maximumFractionDigits: 0
      }).format(budgetValue)

      items.push({
        key: 'budget-total',
        label: 'Total Budget',
        value: formattedBudget,
        icon: budgetIcon,
        tone: 'emerald',
        actionLabel: onInteraction ? 'Adjust' : undefined,
        onAction: buildAction('adjust_budget')
      })

      const allocationCount = safeArray<any>(data.allocation).length
      items.push({
        key: 'budget-allocation',
        label: 'Categories',
        value: allocationCount ? `${allocationCount} allocated` : undefined,
        hint: allocationCount ? undefined : 'Allocate categories to balance spend.',
        icon: checklistIcon,
        tone: 'slate',
        actionLabel: allocationCount ? undefined : (onInteraction ? 'Add' : undefined),
        onAction: allocationCount ? undefined : buildAction('add_allocation')
      })
      break
    }

    case 'theme_agent': {
      const primaryTheme = pickString(data.primary_theme, data.theme, data.hero_descriptor)
      const paletteSize = safeArray<string>(data.palette).length
      items.push({
        key: 'theme-primary',
        label: 'Primary Theme',
        value: primaryTheme,
        icon: sparkleIcon,
        tone: 'purple',
        actionLabel: onInteraction ? 'Swap' : undefined,
        onAction: buildAction('change_theme')
      })
      items.push({
        key: 'theme-palette',
        label: 'Palette',
        value: paletteSize ? `${paletteSize} colors` : undefined,
        icon: paletteIcon,
        tone: 'indigo',
        hint: paletteSize ? undefined : 'Pick colors to guide decor + lighting.'
      })
      break
    }

    case 'cake_agent': {
      const bakeries = safeArray<any>(data.recommended_bakeries)
      const highlightBakery = bakeries[0]
      items.push({
        key: 'cake-count',
        label: 'Bakeries',
        value: bakeries.length ? `${bakeries.length} curated` : undefined,
        icon: bakeryIcon,
        tone: 'rose',
        hint: bakeries.length ? undefined : 'Need tastings? Add a bakery to start.'
      })
      if (highlightBakery) {
        items.push({
          key: 'cake-signature',
          label: highlightBakery.name || 'Signature Dessert',
          value: pickString(highlightBakery.signature, highlightBakery.estimate),
          icon: sparkleIcon,
          tone: 'purple'
        })
      }
      break
    }

    case 'decor_agent': {
      const focalCount = safeArray<string>(data.focal_elements).length
      items.push({
        key: 'decor-hero',
        label: 'Focal Elements',
        value: focalCount ? `${focalCount} hero moments` : undefined,
        icon: sparkleIcon,
        tone: 'purple',
        hint: focalCount ? undefined : 'Highlight the wow moments to shape decor.'
      })
      const diyTips = safeArray<string>(data.diy_tips)
      if (diyTips[0]) {
        items.push({
          key: 'decor-diy',
          label: 'DIY Boost',
          value: diyTips[0],
          icon: checklistIcon,
          tone: 'emerald'
        })
      }
      break
    }

    case 'balloon_agent': {
      const artists = safeArray<any>(data.recommended_artists)
      items.push({
        key: 'balloon-artists',
        label: 'Balloon Artists',
        value: artists.length ? `${artists.length} stylists` : undefined,
        icon: balloonIcon,
        tone: 'rose',
        hint: artists.length ? undefined : 'Bring in a balloon crew to frame entrances.'
      })
      if (artists[0]?.package) {
        items.push({
          key: 'balloon-package',
          label: artists[0].name || 'Signature Package',
          value: artists[0].package,
          icon: sparkleIcon,
          tone: 'blue'
        })
      }
      break
    }

    case 'venue_agent': {
      const venues = safeArray<any>(data.recommended_venues)
      items.push({
        key: 'venue-count',
        label: 'Matching Venues',
        value: venues.length ? `${venues.length} scouted` : undefined,
        icon: venueIcon,
        tone: 'blue',
        hint: venues.length ? undefined : 'Add capacity + neighborhood to sharpen matches.',
        actionLabel: venues.length ? undefined : (onInteraction ? 'Add' : undefined),
        onAction: venues.length ? undefined : buildAction('add_venue_filters')
      })
      const lead = venues[0]
      if (lead?.neighborhood || lead?.city || lead?.name) {
        items.push({
          key: 'venue-location',
          label: 'Lead Location',
          value: pickString(lead.neighborhood, lead.city, lead.name),
          icon: cityIcon,
          tone: 'indigo'
        })
      }
      break
    }

    case 'catering_agent': {
      const caterers = safeArray<any>(data.recommended_caterers)
      items.push({
        key: 'caterer-count',
        label: 'Catering Options',
        value: caterers.length ? `${caterers.length} chefs` : undefined,
        icon: chefIcon,
        tone: 'emerald',
        hint: caterers.length ? undefined : 'List dietary needs to unlock tailored menus.'
      })
      const menuPairings = safeArray<string>(data.menu_pairings)
      if (menuPairings[0]) {
        items.push({
          key: 'menu-highlight',
          label: 'Menu Highlight',
          value: menuPairings[0],
          icon: paletteIcon,
          tone: 'amber'
        })
      }
      break
    }

    case 'vendor_agent': {
      const categories = Object.keys(data.vendors_by_category || {})
      items.push({
        key: 'vendor-coverage',
        label: 'Categories',
        value: categories.length ? `${categories.length} covered` : undefined,
        icon: vendorIcon,
        tone: 'slate',
        hint: categories.length ? undefined : 'Add vendor categories to grow your roster.'
      })
      const totalVendors = categories.reduce(
        (acc, category) => acc + safeArray<any>(data.vendors_by_category?.[category]).length,
        0
      )
      if (totalVendors) {
        items.push({
          key: 'vendor-total',
          label: 'Vendor Count',
          value: `${totalVendors} in play`,
          icon: checklistIcon,
          tone: 'indigo'
        })
      }
      break
    }

    case 'planner_agent': {
      const agenda = safeArray<any>(data.final_plan?.agenda || data.agenda)
      const checklist = safeArray<any>(data.final_plan?.checklist || data.checklist)
      items.push({
        key: 'planner-agenda',
        label: 'Agenda Beats',
        value: agenda.length ? `${agenda.length} lined up` : undefined,
        icon: clockIcon,
        tone: 'blue'
      })
      items.push({
        key: 'planner-checklist',
        label: 'Checklist',
        value: checklist.length ? `${checklist.length} tasks` : undefined,
        icon: checklistIcon,
        tone: 'emerald',
        hint: checklist.length ? undefined : 'Add follow-ups to keep your plan on track.'
      })
      break
    }

    default:
      return []
  }

  return items
}

interface AgentAIBlockProps {
  agentKey: string
  agentName: string
  emoji: string
  status: 'idle' | 'running' | 'completed' | 'error'
  data?: any
  onInteraction?: (action: string, value?: any) => void
  onPositionChange?: (x: number, y: number) => void
  onAgentAction?: (action: 'pause' | 'restart' | 'delete') => void
  onPlayClick?: (agentKey: string) => void
  isActive?: boolean
  className?: string
  borderColor?: string
  initialX?: number
  initialY?: number
  variant?: 'floating' | 'focus' | 'secondary'
}

const AgentAIBlock: React.FC<AgentAIBlockProps> = ({
  agentKey,
  agentName,
  emoji,
  status,
  data,
  onInteraction,
  onPositionChange,
  onAgentAction,
  onPlayClick,
  isActive = false,
  className = '',
  borderColor,
  initialX = 0,
  initialY = 0,
  variant = 'floating'
}) => {
  const isFocus = variant === 'focus'
  const isSecondary = variant === 'secondary'
  const [isHovered, setIsHovered] = useState(false)
  const [localData, setLocalData] = useState(data)
  const [isDragging, setIsDragging] = useState(false)
  const [position, setPosition] = useState({ x: initialX, y: initialY })
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 })
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [zoomedImage, setZoomedImage] = useState<{ src: StaticImageData; alt: string } | null>(null)
  const [portalTarget, setPortalTarget] = useState<HTMLElement | null>(null)
  const isFloating = variant === 'floating'

  // Generate random vibrant border colors
  const getRandomBorderColor = () => {
    const colors = [
      'from-purple-400 to-pink-400',
      'from-blue-400 to-cyan-400', 
      'from-green-400 to-emerald-400',
      'from-orange-400 to-red-400',
      'from-indigo-400 to-purple-400',
      'from-pink-400 to-rose-400',
      'from-teal-400 to-green-400',
      'from-yellow-400 to-orange-400'
    ]
    return colors[Math.floor(Math.random() * colors.length)]
  }

  const borderGradient = borderColor || getRandomBorderColor()
  const isVisualAgent = agentKey === 'cake_agent' || agentKey === 'theme_agent'
  const imageHeightClass = isVisualAgent
    ? (isFocus ? 'h-64' : isSecondary ? 'h-40' : 'h-48')
    : (isFocus ? 'h-40' : isSecondary ? 'h-28' : 'h-36')
  const emojiSizeClass = isFocus ? 'text-6xl' : isSecondary ? 'text-4xl' : 'text-5xl'
  const cardSizeClass = isFocus
    ? 'w-full max-w-4xl min-h-[28rem]'
    : isSecondary
      ? 'w-[21rem] min-h-[22rem]'
      : 'w-[22rem] h-[24rem]'
  const highlightPadding = isFocus ? 'px-8 pt-6' : isSecondary ? 'px-5 pt-4' : 'px-5 pt-4'
  const standardImageWrapper = isFocus ? 'px-8 pt-8' : isSecondary ? 'px-5 pt-5' : 'px-5 pt-5'
  const visualImageWrapper = isFocus ? 'px-6 pt-6' : isSecondary ? 'px-4 pt-4' : 'px-4 pt-4'
  const imageWrapperClass = `relative ${isVisualAgent ? visualImageWrapper : standardImageWrapper}`
  const dataSectionClass = isFocus
    ? 'flex-1 px-8 pb-8 pt-6 flex flex-col justify-end gap-8'
    : isSecondary
      ? 'flex-1 p-5 flex flex-col justify-between'
      : 'flex-1 p-6 flex flex-col justify-between'

  useEffect(() => {
    if (!data) {
      setLocalData(undefined)
      return
    }

    const normalized =
      (typeof data === 'object' && data !== null && 'result' in data && data.result)
        ? (data as any).result
        : (typeof data === 'object' && data !== null && 'data' in data && (data as any).data)
          ? (data as any).data
          : data

    setLocalData(normalized)
  }, [data])

  const inputClassifierDetails = useMemo(() => {
    if (agentKey !== 'input_classifier' || !localData) return null
    return buildInputClassifierDetails(localData, onInteraction)
  }, [agentKey, localData, onInteraction])

  const dataHighlights = useMemo(() => {
    if (agentKey === 'input_classifier') {
      return inputClassifierDetails?.items ?? []
    }
    return localData ? buildGenericHighlights(agentKey, localData, onInteraction) : []
  }, [agentKey, localData, onInteraction, inputClassifierDetails])

  // Drag and drop handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    if (!isFloating) return
    if (e.target instanceof HTMLElement && (e.target.closest('.agent-menu-button') || e.target.closest('.agent-dropdown-menu'))) {
      return // Don't drag if clicking on menu or dropdown
    }
    
    setIsDragging(true)
    const rect = e.currentTarget.getBoundingClientRect()
    setDragOffset({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    })
    e.preventDefault()
  }

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging) return
    
    const newX = e.clientX - dragOffset.x
    const newY = e.clientY - dragOffset.y
    
    setPosition({ x: newX, y: newY })
    onPositionChange?.(newX, newY)
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  useEffect(() => {
    if (isFloating && isDragging) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      return () => {
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isFloating, isDragging, dragOffset])

  // Click outside to close menu
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (isMenuOpen && event.target instanceof HTMLElement) {
        if (!event.target.closest('.agent-menu-button') && !event.target.closest('.agent-dropdown-menu')) {
          setIsMenuOpen(false)
        }
      }
    }

    if (isMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isMenuOpen])

  useEffect(() => {
    if (!zoomedImage) return

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setZoomedImage(null)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    const originalOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = originalOverflow
    }
  }, [zoomedImage])

  useEffect(() => {
    if (typeof document !== 'undefined') {
      setPortalTarget(document.body)
    }
  }, [])

  const getStatusColor = () => {
    switch (status) {
      case 'running': return 'from-blue-500 to-cyan-500'
      case 'completed': return 'from-green-500 to-emerald-500'
      case 'error': return 'from-red-500 to-pink-500'
      default: return 'from-gray-400 to-gray-500'
    }
  }

  const getStatusGlow = () => {
    switch (status) {
      case 'running': return 'shadow-blue-500/30'
      case 'completed': return 'shadow-green-500/30'
      case 'error': return 'shadow-red-500/30'
      default: return 'shadow-gray-500/20'
    }
  }


  const renderStatusIndicator = () => (
    <motion.div 
      className={`w-5 h-5 rounded-full bg-gradient-to-r ${getStatusColor()} shadow-lg`}
      animate={status === 'running' ? { 
        scale: [1, 1.3, 1],
        opacity: [0.8, 1, 0.8]
      } : {}}
      transition={{ 
        duration: 1.5,
        repeat: status === 'running' ? Infinity : 0
      }}
    />
  )

  const renderAgentImage = () => {
    if (isVisualAgent) {
      const imageSrc = agentKey === 'cake_agent' ? defaultCakeImage : defaultThemeImage
      const altText = agentKey === 'cake_agent' ? 'Signature cake inspiration' : 'Default theme inspiration'
      return (
        <button
          type="button"
          onMouseDown={(e) => e.stopPropagation()}
          onClick={(e) => {
            e.stopPropagation()
            setZoomedImage({ src: imageSrc, alt: altText })
          }}
          className={`group relative z-10 w-full ${imageHeightClass} rounded-3xl overflow-hidden shadow-2xl cursor-zoom-in focus:outline-none focus:ring-4 focus:ring-blue-400/30`}
          aria-label="Zoom preview"
          title="Zoom preview"
        >
          <Image
            src={imageSrc}
            alt={altText}
            fill
            sizes={isFocus ? '(min-width: 1024px) 480px, 360px' : '(min-width: 1024px) 320px, 260px'}
            className="object-contain transition-transform duration-700 ease-out group-hover:scale-105"
            priority={isFocus}
          />
          <div className="absolute bottom-3 right-3 rounded-full bg-black/55 text-white text-xs font-medium px-3 py-1.5 flex items-center gap-1 shadow-lg backdrop-blur-sm">
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="opacity-90"
            >
              <rect x="3" y="3" width="7" height="7" rx="1" />
              <rect x="14" y="3" width="7" height="7" rx="1" />
              <rect x="14" y="14" width="7" height="7" rx="1" />
              <rect x="3" y="14" width="7" height="7" rx="1" />
            </svg>
            <span>Zoom</span>
          </div>
        </button>
      )
    }

    return (
      <div className={`relative w-full ${imageHeightClass} bg-gradient-to-br from-white/90 to-gray-100/90 rounded-2xl overflow-hidden`}>
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.div
            className={`${emojiSizeClass} filter drop-shadow-lg`}
            animate={status === 'running' ? { 
              scale: [1, 1.2, 1],
              rotate: [0, 10, -10, 0],
              filter: ['drop-shadow(0 0 0px rgba(59, 130, 246, 0))', 'drop-shadow(0 0 20px rgba(59, 130, 246, 0.8))', 'drop-shadow(0 0 0px rgba(59, 130, 246, 0))']
            } : {}}
            transition={{ 
              duration: 2.5,
              repeat: status === 'running' ? Infinity : 0,
              ease: "easeInOut"
            }}
            style={{
              filter: status === 'completed' ? 'drop-shadow(0 0 15px rgba(34, 197, 94, 0.6))' : 
                     status === 'error' ? 'drop-shadow(0 0 15px rgba(239, 68, 68, 0.6))' :
                     'drop-shadow(0 0 5px rgba(0, 0, 0, 0.1))'
            }}
          >
            {emoji}
          </motion.div>
        </div>
        
        {/* Animated pattern overlay */}
        <motion.div 
          className="absolute inset-0 opacity-20"
          animate={{
            background: [
              'linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.3) 50%, transparent 70%)',
              'linear-gradient(225deg, transparent 30%, rgba(255,255,255,0.3) 50%, transparent 70%)',
              'linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.3) 50%, transparent 70%)'
            ]
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />

        {/* Glow effect for running agents */}
        {status === 'running' && (
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-blue-400/20 to-purple-400/20 rounded-2xl"
            animate={{
              opacity: [0.3, 0.7, 0.3]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
        )}
      </div>
    )
  }

  // Helper function to safely render values
  const safeRender = (value: any): string => {
    if (value === null || value === undefined) return '';
    if (typeof value === 'string' || typeof value === 'number') return String(value);
    if (typeof value === 'object') {
      // If it's an object, try to extract a meaningful string value
      if (value.name) return String(value.name);
      if (value.title) return String(value.title);
      if (value.estimated) return String(value.estimated);
      if (value.min && value.max) return `${value.min}-${value.max}`;
      return JSON.stringify(value);
    }
    return String(value);
  };

  const renderDynamicData = () => {
    if (!localData) return null

    const summaryWrapper = isFocus ? 'space-y-5 text-center' : 'space-y-3'
    const badgeClass = isFocus ? 'text-xs tracking-[0.35em] uppercase text-gray-400' : 'text-xs text-gray-500 uppercase tracking-wide'
    const statRow = isFocus ? 'flex flex-col items-center gap-1' : 'flex items-center justify-between'
    const labelClass = isFocus ? 'text-sm text-gray-500' : 'text-sm text-gray-600'

    switch (agentKey) {
      case 'input_classifier': {
        const highlights = inputClassifierDetails?.highlights.slice(0, isFocus ? 4 : 3) ?? []
        const nextMove = inputClassifierDetails?.nextMove
        const confidence = inputClassifierDetails?.confidence

        return (
          <div className={isFocus ? 'space-y-5' : 'space-y-4'}>
            <div className={badgeClass}>Input Insights</div>
            {highlights.length > 0 ? (
              <div className="rounded-3xl border border-indigo-50 bg-white/85 p-4 shadow-inner shadow-indigo-100/40">
                <div className="space-y-2">
                  {highlights.map((highlight, index) => (
                    <div key={`highlight-${index}`} className="flex items-start gap-2 text-sm text-gray-700">
                      <span className="mt-0.5 text-indigo-400">✦</span>
                      <span>{highlight}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="rounded-3xl border border-dashed border-indigo-100 p-4 text-sm text-gray-500">
                Drop a link or prompt to unlock highlighted party cues.
              </div>
            )}

            {nextMove && (
              <div className="rounded-3xl bg-gradient-to-r from-indigo-50 via-blue-50 to-purple-50 p-4 text-sm text-indigo-700 shadow-sm">
                <div className="flex items-center gap-2 text-sm font-semibold text-indigo-600">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path d="m9 18 6-6-6-6" />
                  </svg>
                  <span>Next Move</span>
                </div>
                <p className="mt-1 leading-relaxed text-indigo-700">{nextMove}</p>
              </div>
            )}

            {typeof confidence === 'number' && (
              <div className="text-xs text-gray-400 text-center tracking-[0.2em] uppercase">
                {confidence}% confidence in extraction
              </div>
            )}
          </div>
        )
      }
      case 'budget_agent':
        let budgetValue = 1000; // Default value
        if (localData.total_budget) {
          if (typeof localData.total_budget === 'object') {
            // Handle object with min/max properties
            budgetValue = localData.total_budget.estimated || localData.total_budget.min || localData.total_budget.max || 1000;
          } else if (typeof localData.total_budget === 'number') {
            budgetValue = localData.total_budget;
          } else if (typeof localData.total_budget === 'string') {
            budgetValue = parseInt(localData.total_budget) || 1000;
          }
        }
        
        return (
          <div className={summaryWrapper}>
            <div className={badgeClass}>Budget Controls</div>
            <div className={statRow}>
              <span className={labelClass}>Current Budget</span>
              <span className={isFocus ? 'text-3xl font-bold text-green-600' : 'text-sm font-bold text-green-600'}>
                ${budgetValue}
              </span>
            </div>
            <div className={isFocus ? 'relative max-w-md mx-auto w-full' : 'relative'}>
              <input
                type="range"
                min="500"
                max="5000"
                value={budgetValue}
                onChange={(e) => onInteraction?.('budget_change', parseInt(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                style={{
                  background: `linear-gradient(to right, #10b981 0%, #10b981 ${(budgetValue - 500) / 45}%, #e5e7eb ${(budgetValue - 500) / 45}%, #e5e7eb 100%)`
                }}
              />
            </div>
            {isFocus && (
              <div className="text-xs text-gray-400">Drag the slider to fine-tune the party budget estimates.</div>
            )}
          </div>
        )

      case 'cake_agent':
        return (
          <div className={summaryWrapper}>
            <div className={badgeClass}>Sweet Selections</div>
            <div className={statRow}>
              <span className={labelClass}>Bakeries Suggested</span>
              <span className={isFocus ? 'text-3xl font-semibold text-purple-500' : 'text-sm font-semibold text-purple-600'}>
                {localData.recommended_bakeries?.length || 0}
              </span>
            </div>
            {isFocus && (
              <div className="text-sm text-gray-500">
                We’ve gathered top cake artists that match your theme and budget.
              </div>
            )}
          </div>
        )

      case 'decor_agent':
        return (
          <div className={summaryWrapper}>
            <div className={badgeClass}>Hero Décor Plan</div>
            <div className={statRow}>
              <span className={labelClass}>Focal Elements</span>
              <span className={isFocus ? 'text-3xl font-semibold text-indigo-500' : 'text-sm font-semibold text-indigo-500'}>
                {localData.focal_elements?.length || 0}
              </span>
            </div>
            {localData.focal_elements && (
              <div className={isFocus ? 'space-y-2 text-sm text-gray-600' : 'text-sm text-gray-500'}>
                {localData.focal_elements.slice(0, isFocus ? 3 : 2).map((item: string) => (
                  <div key={item} className="flex items-start gap-2 justify-center">
                    <span className="mt-1 text-indigo-400">✦</span>
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            )}
            {isFocus && localData.diy_tips && (
              <div className="text-xs text-gray-400">
                DIY boost: {localData.diy_tips[0]}
              </div>
            )}
          </div>
        )

      case 'balloon_agent':
        return (
          <div className={summaryWrapper}>
            <div className={badgeClass}>Balloon Stylists</div>
            <div className={statRow}>
              <span className={labelClass}>Recommended Artists</span>
              <span className={isFocus ? 'text-3xl font-semibold text-rose-500' : 'text-sm font-semibold text-rose-500'}>
                {localData.recommended_artists?.length || 0}
              </span>
            </div>
            {localData.recommended_artists && (
              <div className={isFocus ? 'space-y-2 text-sm text-gray-600' : 'text-sm text-gray-500'}>
                {localData.recommended_artists.slice(0, isFocus ? 2 : 1).map((artist: any) => (
                  <div key={artist.name} className="flex flex-col items-center">
                    <span className="font-medium text-gray-700">{artist.name}</span>
                    <span className="text-xs text-gray-500">{artist.specialty}</span>
                  </div>
                ))}
              </div>
            )}
            {isFocus && localData.quick_win && (
              <div className="text-xs text-gray-400">
                Quick win: {localData.quick_win}
              </div>
            )}
          </div>
        )

      case 'venue_agent':
        return (
          <div className={summaryWrapper}>
            <div className={badgeClass}>Venues</div>
            <div className={statRow}>
              <span className={labelClass}>Matching Venues</span>
              <span className={isFocus ? 'text-3xl font-semibold text-blue-600' : 'text-sm font-semibold text-blue-600'}>
                {localData.recommended_venues?.length || 0}
              </span>
            </div>
            {isFocus && (
              <div className="text-sm text-gray-500">
                Filtered to suit capacity, style, and location preferences.
              </div>
            )}
          </div>
        )

      case 'theme_agent':
        let themeValue = 'Detecting...';
        if (localData.primary_theme) {
          if (typeof localData.primary_theme === 'string') {
            themeValue = localData.primary_theme;
          } else if (typeof localData.primary_theme === 'object') {
            themeValue = localData.primary_theme.name || localData.primary_theme.title || 'Detecting...';
          }
        }
        return (
          <div className={summaryWrapper}>
            <div className={badgeClass}>Primary Theme</div>
            <div className={statRow}>
              <span className={isFocus ? 'text-3xl font-semibold text-indigo-600' : 'text-sm font-medium text-gray-600'}>
                {safeRender(themeValue)}
              </span>
            </div>
            {isFocus && (
              <div className="flex justify-center gap-2 text-xs text-gray-400">
                <span>Palette synced ·</span>
                <span>Decor plan aligned</span>
              </div>
            )}
          </div>
        )

      case 'vendor_agent':
        return (
          <div className={summaryWrapper}>
            <div className={badgeClass}>Vendor Coverage</div>
            <div className={statRow}>
              <span className={labelClass}>Categories Covered</span>
              <span className={isFocus ? 'text-3xl font-semibold text-emerald-500' : 'text-sm font-semibold text-emerald-500'}>
                {Object.keys(localData.vendors_by_category || {}).length}
              </span>
            </div>
            {isFocus && (
              <div className="text-sm text-gray-500">
                Includes entertainment, décor, food, and specialty services ready for quotes.
              </div>
            )}
          </div>
        )

      case 'catering_agent':
        return (
          <div className={summaryWrapper}>
            <div className={badgeClass}>Catering Options</div>
            <div className={statRow}>
              <span className={labelClass}>Curated Caterers</span>
              <span className={isFocus ? 'text-3xl font-semibold text-rose-500' : 'text-sm font-semibold text-rose-500'}>
                {localData.recommended_caterers?.length || 0}
              </span>
            </div>
            {isFocus && (
              <div className="text-sm text-gray-500">
                Menu pairings balance dietary preferences, service style, and budget targets.
              </div>
            )}
          </div>
        )

      default:
        return (
          <div className={summaryWrapper}>
            <div className={badgeClass}>Status</div>
            <div className={isFocus ? 'text-2xl font-semibold text-gray-700' : 'text-sm font-medium text-gray-600'}>
              {status === 'running' ? 'Processing...' : 
               status === 'completed' ? 'Complete' :
               status === 'error' ? 'Needs Attention' : 'Ready'}
            </div>
            {isFocus && (
              <div className="text-sm text-gray-500">
                {agentName} is standing by for your inputs or regenerating fresh results.
              </div>
            )}
          </div>
        )
    }
  }

  const zoomOverlay = portalTarget
    ? createPortal(
        <AnimatePresence>
          {zoomedImage && (
            <motion.div
              className="fixed inset-0 z-[200] flex items-center justify-center bg-black/70 backdrop-blur-sm p-6"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setZoomedImage(null)}
            >
            <motion.div
              className="relative w-full max-w-5xl"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              transition={{ type: 'spring', stiffness: 160, damping: 22 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="relative w-full max-w-5xl h-[80vh] rounded-[32px] overflow-hidden shadow-[0_40px_120px_rgba(0,0,0,0.45)] bg-gradient-to-b from-black via-black to-black">
                <Image
                  src={zoomedImage.src}
                  alt={zoomedImage.alt}
                  fill
                  sizes="100vw"
                  className="object-contain"
                  priority
                />
              </div>
              <button
                type="button"
                className="absolute top-4 right-4 w-10 h-10 rounded-full bg-black/60 text-white hover:bg-black/80 transition flex items-center justify-center shadow-lg focus:outline-none focus:ring-2 focus:ring-white/60"
                aria-label="Close zoomed image"
                onClick={() => setZoomedImage(null)}
              >
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>,
        portalTarget
      )
    : null

  return (
    <>
      {zoomOverlay}
      <motion.div
        className={`group relative bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl overflow-visible ${cardSizeClass} ${className} ${isFloating ? (isDragging ? 'cursor-grabbing' : 'cursor-move') : 'cursor-default'} ${isActive ? 'ring-4 ring-blue-400/50' : ''}`}
        style={{
          border: `3px solid transparent`,
          background: `linear-gradient(white, white) padding-box, linear-gradient(135deg, ${borderGradient}) border-box`,
          ...(isFloating ? { transform: `translate(${position.x}px, ${position.y}px)` } : {}),
          zIndex: isFloating ? (isDragging ? 1000 : (isActive ? 20 : 5)) : undefined,
          opacity: variant === 'focus' ? 1 : (isActive ? 1 : 0.75)
        }}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        onMouseDown={handleMouseDown}
        whileHover={isFloating ? { 
          scale: isDragging ? 1 : (isActive ? 1.1 : 1.05),
          y: isDragging ? 0 : (isActive ? -12 : -6),
          rotateY: isDragging ? 0 : (isActive ? 8 : 3),
          boxShadow: isActive 
            ? `0 25px 50px ${getStatusGlow()}, 0 0 40px rgba(59, 130, 246, 0.4), 0 0 80px rgba(147, 51, 234, 0.2)`
            : `0 25px 50px ${getStatusGlow()}, 0 0 30px rgba(59, 130, 246, 0.3), 0 0 60px rgba(147, 51, 234, 0.15)`
        } : (
          variant === 'focus'
            ? { scale: isActive ? 1.01 : 1, boxShadow: isActive ? `0 25px 50px ${getStatusGlow()}` : undefined }
            : { scale: 1.02 }
        )}
        initial={isFloating ? { opacity: 0, y: 30, scale: 0.8, rotateX: -15 } : { opacity: 0, y: 20, scale: 0.95 }}
        animate={isFloating ? { 
          opacity: isActive ? 1 : 0.6, 
          y: 0, 
          scale: isDragging ? 1.05 : (isActive ? 1.05 : 1), 
          rotateX: 0,
          rotateZ: isDragging ? 2 : 0
        } : { 
          opacity: 1,
          y: 0,
          scale: isActive ? 1.01 : 1,
          rotateX: 0,
          rotateZ: 0
        }}
        transition={{ 
          duration: 0.8,
          ease: [0.25, 0.46, 0.45, 0.94],
          type: "spring",
          stiffness: 100
        }}
      >

      {/* Animated background gradient */}
          <motion.div 
            className={`absolute inset-0 bg-gradient-to-br ${borderGradient} opacity-10 pointer-events-none`}
            animate={isActive ? { opacity: 0.4 } : (isHovered ? { opacity: 0.25 } : { opacity: 0.05 })}
            transition={{ duration: 0.3 }}
          />

          {/* Vibrant hover gradient overlay */}
          <AnimatePresence>
            {isHovered && (
              <motion.div
                className="absolute inset-0 bg-gradient-to-br from-blue-400/30 via-purple-400/20 to-pink-400/30 rounded-3xl pointer-events-none"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
              />
            )}
          </AnimatePresence>

          {/* Radiance effect on hover */}
          <AnimatePresence>
            {isHovered && (
              <motion.div
                className="absolute inset-0 rounded-3xl pointer-events-none"
                style={{
                  background: `radial-gradient(circle at center, 
                    rgba(59, 130, 246, 0.15) 0%, 
                    rgba(147, 51, 234, 0.1) 30%, 
                    rgba(236, 72, 153, 0.08) 60%, 
                    transparent 100%)`
                }}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ duration: 0.4, ease: "easeOut" }}
              />
            )}
          </AnimatePresence>

      {/* Active Agent Blue Overlay */}
      {isActive && (
        <motion.div
          className="absolute inset-0 bg-gradient-to-br from-blue-400/20 to-cyan-400/20 rounded-3xl pointer-events-none"
          initial={{ opacity: 0 }}
          animate={{ 
            opacity: [0.2, 0.4, 0.2],
            scale: [1, 1.02, 1]
          }}
          transition={{ 
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      )}
      
      {dataHighlights.length > 0 && (
        <div className={`relative z-30 ${highlightPadding}`}>
          <AgentDataItems items={dataHighlights} compact={!isFocus} />
        </div>
      )}

      {/* Agent Image Section (40%) */}
      <div className={imageWrapperClass}>
        {renderAgentImage()}
        <div className="absolute -top-2 -right-2 flex items-center justify-center pointer-events-none">
          {renderStatusIndicator()}
        </div>
      </div>

      {/* Data Section (60%) */}
      <div className={dataSectionClass}>
        <div className={isFocus ? 'flex-1 flex items-end justify-center w-full' : 'flex-1'}>
          <div className={isFocus ? 'w-full max-w-2xl mx-auto' : ''}>
            {renderDynamicData()}
          </div>
        </div>
        
        {/* Agent name with menu */}
        <div className={`relative ${isFocus ? 'pt-2' : ''}`}>
          <motion.div 
            className={`${isFocus ? 'text-lg' : 'text-sm'} font-semibold text-gray-700 text-center truncate pr-8 pl-8`}
            animate={isHovered ? { scale: 1.05 } : { scale: 1 }}
            transition={{ duration: 0.2 }}
          >
            {agentName}
          </motion.div>
          
          {/* Edit Agent Button - Bottom Left Corner */}
          <motion.button
            className="absolute left-[-4px] bottom-[-4px] w-9 h-9 bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-500 hover:from-blue-600 hover:via-indigo-600 hover:to-purple-600 rounded-full flex items-center justify-center text-white shadow-xl backdrop-blur-sm border border-white/60 cursor-pointer z-20 focus:outline-none focus:ring-2 focus:ring-blue-300"
            onClick={(e) => {
              e.stopPropagation()
              onPlayClick?.(agentKey)
            }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            title="Edit Agent"
            animate={isActive ? { 
              scale: [1, 1.1, 1],
              rotate: [0, 5, -5, 0]
            } : {}}
            transition={{ 
              duration: 2,
              repeat: isActive ? Infinity : 0,
              ease: "easeInOut"
            }}
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
              <path d="M4 20h3.6l10.9-10.9a1 1 0 0 0 0-1.4L15.4 4.6a1 1 0 0 0-1.4 0L3.1 15.5V19a1 1 0 0 0 1 1zm11.9-12.9 1.4 1.4-1.6 1.6-1.4-1.4 1.6-1.6zM5.1 18l8.2-8.2 1.4 1.4L6.5 19H5.1V18z" />
            </svg>
          </motion.button>
          
          {/* 3-Dots Menu Button - Absolute positioned */}
          <motion.button
            className="agent-menu-button absolute bottom-0 right-0 w-6 h-6 bg-white/90 hover:bg-white rounded-full flex items-center justify-center text-gray-600 hover:text-gray-800 shadow-lg backdrop-blur-sm border border-gray-200/50 cursor-pointer z-10"
            onClick={(e) => {
              e.stopPropagation()
              setIsMenuOpen(!isMenuOpen)
            }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            title="Agent Options"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
              <circle cx="12" cy="5" r="2"/>
              <circle cx="12" cy="12" r="2"/>
              <circle cx="12" cy="19" r="2"/>
            </svg>
          </motion.button>
          
          {/* Dropdown Menu */}
          <AnimatePresence>
            {isMenuOpen && (
              <motion.div
                className="agent-dropdown-menu absolute bottom-8 right-0 bg-white/98 backdrop-blur-xl rounded-lg shadow-xl border border-gray-200/60 py-1 min-w-[100px] z-[9999]"
                initial={{ opacity: 0, scale: 0.95, y: 8 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95, y: 8 }}
                transition={{ duration: 0.15, ease: "easeOut" }}
                style={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.98)',
                  border: '1px solid rgba(229, 231, 235, 0.8)'
                }}
              >
                {/* Pause Option */}
                <motion.button
                  className="w-full px-3 py-1.5 text-left text-xs text-gray-600 hover:bg-yellow-50 hover:text-yellow-700 flex items-center gap-1.5 transition-colors duration-100"
                  onClick={(e) => {
                    e.stopPropagation()
                    onAgentAction?.('pause')
                    setIsMenuOpen(false)
                  }}
                  whileHover={{ x: 2 }}
                >
                  <span className="text-sm">⏸️</span>
                  <span>Pause</span>
                </motion.button>

                {/* Restart Option */}
                <motion.button
                  className="w-full px-3 py-1.5 text-left text-xs text-gray-600 hover:bg-blue-50 hover:text-blue-700 flex items-center gap-1.5 transition-colors duration-100"
                  onClick={(e) => {
                    e.stopPropagation()
                    onAgentAction?.('restart')
                    setIsMenuOpen(false)
                  }}
                  whileHover={{ x: 2 }}
                >
                  <span className="text-sm">🔄</span>
                  <span>Restart</span>
                </motion.button>

                {/* Divider */}
                <div className="h-px bg-gray-200/40 mx-2 my-0.5"></div>

                {/* Delete Option */}
                <motion.button
                  className="w-full px-3 py-1.5 text-left text-xs text-gray-600 hover:bg-red-50 hover:text-red-700 flex items-center gap-1.5 transition-colors duration-100"
                  onClick={(e) => {
                    e.stopPropagation()
                    onAgentAction?.('delete')
                    setIsMenuOpen(false)
                  }}
                  whileHover={{ x: 2 }}
                >
                  <span className="text-sm">🗑️</span>
                  <span>Delete</span>
                </motion.button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Enhanced hover glow effect */}
      <AnimatePresence>
        {isHovered && !isActive && (
          <motion.div
            className="absolute inset-0 rounded-3xl"
            style={{
              background: `linear-gradient(135deg, 
                rgba(59, 130, 246, 0.1) 0%, 
                rgba(147, 51, 234, 0.08) 50%, 
                rgba(236, 72, 153, 0.1) 100%)`,
              boxShadow: `0 0 30px rgba(59, 130, 246, 0.3), 
                          0 0 60px rgba(147, 51, 234, 0.2), 
                          0 0 90px rgba(236, 72, 153, 0.1)`
            }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          />
        )}
      </AnimatePresence>

      {/* Enhanced status pulse effect */}
      {status === 'running' && (
        <motion.div
          className="absolute inset-0 border-3 border-blue-400 rounded-3xl"
          animate={{ 
            scale: [1, 1.02, 1],
            opacity: [0.3, 0.7, 0.3],
            rotate: [0, 1, -1, 0]
          }}
          transition={{ 
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      )}

      {/* Floating particles effect */}
      {status === 'running' && (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {[...Array(6)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-blue-400 rounded-full"
              style={{
                left: `${20 + i * 15}%`,
                top: `${30 + i * 10}%`
              }}
              animate={{
                y: [-20, -40, -20],
                opacity: [0, 1, 0],
                scale: [0.5, 1, 0.5]
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                delay: i * 0.5,
                ease: "easeInOut"
              }}
            />
          ))}
        </div>
      )}

      {/* Drag indicator */}
      {isFloating && isDragging && (
        <motion.div
          className="absolute inset-0 border-2 border-dashed border-blue-400 rounded-3xl bg-blue-50/20"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        />
      )}
    </motion.div>
    </>
  )
}

export default AgentAIBlock
