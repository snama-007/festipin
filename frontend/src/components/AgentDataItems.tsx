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
    <div className={`w-full overflow-x-auto no-scrollbar ${className}`}>
      <div className="flex gap-3 min-w-full">
        {items.map((item, index) => {
          const tone = toneStyles[item.tone ?? 'indigo']

          return (
            <motion.div
              key={item.key}
              className={`group relative flex min-w-[11rem] flex-1 items-start gap-3 rounded-2xl border border-white/60 bg-white/90 p-3 shadow-sm shadow-indigo-100/30 backdrop-blur-xl transition hover:-translate-y-1 hover:shadow-xl ${compact ? 'min-w-[9.5rem] p-2.5' : ''}`}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05, duration: 0.25 }}
            >
              <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${tone.bg} opacity-0 transition group-hover:opacity-100`} />
              <div className="relative z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white/70 text-lg shadow-sm shadow-black/5">
                {item.icon}
              </div>
              <div className="relative z-10 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-semibold uppercase tracking-[0.28em] text-gray-400">
                    {item.label}
                  </span>
                  {item.onAction && item.actionLabel && (
                    <button
                      type="button"
                      onClick={item.onAction}
                      className={`ml-auto inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium transition ${tone.badge}`}
                    >
                      {item.actionLabel}
                    </button>
                  )}
                </div>
                <div className={`truncate text-sm font-semibold ${tone.text}`}>
                  {item.value || 'Add detail'}
                </div>
                {item.hint && (
                  <div className="mt-1 text-xs text-gray-500 leading-snug">
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
