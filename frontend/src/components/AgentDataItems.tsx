'use client'

import React, { ReactNode } from 'react'
import { motion } from 'framer-motion'

export type AgentDataTone = 'indigo' | 'emerald' | 'rose' | 'amber' | 'blue' | 'purple' | 'slate'

export interface AgentDataItem {
  key: string
  label: string
  value?: string
  icon?: ReactNode
  hint?: string
  actionLabel?: string
  onAction?: () => void
  tone?: AgentDataTone
}

interface AgentDataItemsProps {
  items: AgentDataItem[]
  className?: string
  compact?: boolean
}

const toneStyles: Record<AgentDataTone, { bg: string; text: string; badge: string }> = {
  indigo: {
    bg: 'from-indigo-500/12 via-indigo-400/8 to-indigo-500/10',
    text: 'text-indigo-600',
    badge: 'bg-indigo-500/10 text-indigo-500'
  },
  emerald: {
    bg: 'from-emerald-500/12 via-emerald-400/8 to-emerald-500/10',
    text: 'text-emerald-600',
    badge: 'bg-emerald-500/10 text-emerald-500'
  },
  rose: {
    bg: 'from-rose-500/12 via-rose-400/8 to-rose-500/10',
    text: 'text-rose-600',
    badge: 'bg-rose-500/10 text-rose-500'
  },
  amber: {
    bg: 'from-amber-500/12 via-amber-400/8 to-amber-500/10',
    text: 'text-amber-600',
    badge: 'bg-amber-500/10 text-amber-500'
  },
  blue: {
    bg: 'from-blue-500/12 via-blue-400/8 to-blue-500/10',
    text: 'text-blue-600',
    badge: 'bg-blue-500/10 text-blue-500'
  },
  purple: {
    bg: 'from-purple-500/12 via-purple-400/8 to-purple-500/10',
    text: 'text-purple-600',
    badge: 'bg-purple-500/10 text-purple-500'
  },
  slate: {
    bg: 'from-slate-500/12 via-slate-400/8 to-slate-500/10',
    text: 'text-slate-600',
    badge: 'bg-slate-500/10 text-slate-500'
  }
}

const AgentDataItems: React.FC<AgentDataItemsProps> = ({ items, className = '', compact = false }) => {
  if (!items.length) return null

  return (
    <div className={`w-full ${className}`}>
      <div className="flex flex-wrap gap-3">
        {items.map((item, index) => {
          const tone = toneStyles[item.tone ?? 'indigo']
          const basisClass = compact ? 'basis-[160px]' : 'basis-[200px]'

          return (
            <motion.div
              key={item.key}
              className={`group relative ${basisClass} grow rounded-2xl border border-white/60 bg-white/90 p-4 shadow-sm shadow-indigo-100/30 backdrop-blur-xl transition hover:-translate-y-1 hover:shadow-xl`}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05, duration: 0.25 }}
            >
              <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${tone.bg} opacity-0 transition group-hover:opacity-100`} />
              <div className="relative z-10 flex min-h-[112px] flex-col gap-2">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    {item.icon && (
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/80 text-base shadow-sm shadow-black/5">
                        {item.icon}
                      </div>
                    )}
                    <span className="text-[10px] font-semibold uppercase tracking-[0.32em] text-gray-400">
                      {item.label}
                    </span>
                  </div>
                  {item.onAction && item.actionLabel && (
                    <button
                      type="button"
                      onClick={item.onAction}
                      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium transition ${tone.badge}`}
                    >
                      {item.actionLabel}
                    </button>
                  )}
                </div>
                <div className={`text-sm font-semibold leading-5 ${tone.text}`}>
                  {item.value || 'Add detail'}
                </div>
                {item.hint && (
                  <div className="text-xs text-gray-500 leading-snug">
                    {item.hint}
                  </div>
                )}
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}

export default AgentDataItems
