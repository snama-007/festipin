'use client'

import React, { useEffect, useMemo } from 'react'
import { motion } from 'framer-motion'
import { CommunicationHubProps, Message, WebSocketMessage } from '../types/communication'
import { useCommunication, useWebSocket } from '../hooks/useCommunication'
import { MessageComposer } from './MessageComposer'
import { testCommunicationData } from '../utils/testData'

type MoodTone = 'positive' | 'neutral' | 'attention'

interface MessageVisual {
  accent: string
  icon: string
  badge: string
  mood: MoodTone
  headline: string
}

interface TimelineEvent {
  id: string
  title: string
  subtitle: string
  actorLabel: string
  timestamp: string
  relativeTime: string
  accent: string
  icon: string
  badge: string
  mood: MoodTone
}

const MOOD_SHADOW: Record<MoodTone, string> = {
  positive: '0 18px 42px rgba(16, 185, 129, 0.28)',
  neutral: '0 18px 42px rgba(167, 139, 250, 0.26)',
  attention: '0 18px 42px rgba(248, 113, 113, 0.32)',
}

const MILESTONE_CAPTION: Record<MoodTone, string> = {
  positive: 'Milestone celebrated',
  neutral: 'Milestone progressing',
  attention: 'Follow up to unlock magic',
}

const MILESTONE_PROGRESS: Record<MoodTone, string> = {
  positive: '100%',
  neutral: '65%',
  attention: '35%',
}

const senderDefaults: Record<string, MessageVisual> = {
  user: {
    accent: 'from-sky-400 via-indigo-500 to-purple-500',
    icon: '💌',
    badge: 'From you',
    mood: 'neutral',
    headline: 'You painted a detail',
  },
  vendor: {
    accent: 'from-amber-400 via-orange-500 to-pink-500',
    icon: '🤝',
    badge: 'Vendor update',
    mood: 'neutral',
    headline: 'Your vendor responded',
  },
  festimo: {
    accent: 'from-fuchsia-400 via-pink-500 to-purple-500',
    icon: '🪄',
    badge: 'Festimo agent',
    mood: 'positive',
    headline: 'Your concierge added magic',
  },
  default: {
    accent: 'from-slate-300 to-slate-500',
    icon: '✨',
    badge: 'Update',
    mood: 'neutral',
    headline: 'A new detail arrived',
  },
}

function evaluateMessageVisual(message?: Message): MessageVisual {
  if (!message) {
    return {
      accent: 'from-slate-200 via-slate-300 to-slate-400',
      icon: '🌈',
      badge: 'Awaiting hello',
      mood: 'neutral',
      headline: 'Ready for the first sparkle',
    }
  }

  const base = senderDefaults[message.sender_type] ?? senderDefaults.default
  const content = message.content?.toLowerCase() ?? ''

  if (/(confirm|confirmed|locked|booked|secured|approved)/i.test(content)) {
    return {
      accent: 'from-emerald-400 via-green-500 to-teal-500',
      icon: '🎉',
      badge: 'Magic confirmed',
      mood: 'positive',
      headline: 'All set and shining',
    }
  }

  if (/(calendar|schedule|time|date)/i.test(content)) {
    return {
      accent: 'from-sky-400 via-cyan-500 to-indigo-500',
      icon: '🗓️',
      badge: 'Calendar locked',
      mood: 'positive',
      headline: 'Timing perfectly aligned',
    }
  }

  if (/(quote|price|invoice|deposit|budget)/i.test(content)) {
    return {
      accent: 'from-blue-400 via-indigo-500 to-purple-500',
      icon: '💎',
      badge: 'Pricing in motion',
      mood: 'neutral',
      headline: 'Reviewing the sparkle budget',
    }
  }

  if (/(adjust|update|change|tweak|refine)/i.test(content)) {
    return {
      accent: 'from-violet-400 via-purple-500 to-fuchsia-500',
      icon: '🎯',
      badge: 'Adjusting details',
      mood: 'neutral',
      headline: 'Fine-tuning the celebration',
    }
  }

  if (/(cancel|decline|issue|unavailable|problem)/i.test(content)) {
    return {
      accent: 'from-rose-400 via-red-500 to-orange-500',
      icon: '⚠️',
      badge: 'Needs love',
      mood: 'attention',
      headline: 'Let’s smooth this bump',
    }
  }

  return base
}

function formatVendorLabel(vendorType?: string, businessName?: string) {
  if (businessName) return businessName
  if (!vendorType) return 'Wonderful vendor'
  return vendorType
    .split('_')
    .map(part => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

function formatRelativeTime(isoDate: string) {
  const now = Date.now()
  const then = new Date(isoDate).getTime()
  const diff = now - then
  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour
  const week = 7 * day

  if (diff < minute) return 'just now'
  if (diff < hour) return `${Math.round(diff / minute)}m ago`
  if (diff < day) return `${Math.round(diff / hour)}h ago`
  if (diff < week) return `${Math.round(diff / day)}d ago`
  return new Date(isoDate).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

function getActorLabel(sender?: Message['sender_type']) {
  if (sender === 'user') return 'You'
  if (sender === 'festimo') return 'Festimo Concierge'
  if (sender === 'vendor') return 'Vendor Partner'
  return 'Timeline'
}

function truncateContent(content?: string, length = 120) {
  if (!content) return 'Awaiting the next sparkle.'
  if (content.length <= length) return content
  return `${content.slice(0, length)}…`
}

export function CommunicationHub({ partyId, vendorRecommendations, onBack }: CommunicationHubProps) {
  const {
    conversations,
    selectedConversation,
    messages,
    vendors,
    isLoading,
    error,
    sendMessage,
    selectConversation,
    markAsRead,
    refetch,
  } = useCommunication(partyId)

  const { isConnected, sendTypingIndicator } = useWebSocket(partyId, handleWebSocketMessage)

  useEffect(() => {
    console.log('🔍 CommunicationHub mounted, testing data flow...')
    testCommunicationData()
  }, [])

  function handleWebSocketMessage(message: WebSocketMessage) {
    console.log('📥 Received WebSocket message:', message.type)
  }

  const handleSendMessage = async (conversationId: string, content: string) => {
    try {
      await sendMessage(conversationId, content)
    } catch (sendError) {
      console.error('Error sending message:', sendError)
    }
  }

  const handleSelectConversation = (conversationId: string) => {
    selectConversation(conversationId)
    markAsRead(conversationId)
  }

  const handleTyping = (isTyping: boolean) => {
    if (selectedConversation) {
      sendTypingIndicator(selectedConversation.conversation_id, isTyping)
    }
  }

  const refreshData = async () => {
    if (refetch) {
      await refetch()
    }
  }

  const vendorLookup = useMemo(() => {
    const map = new Map<string, string>()
    vendors.forEach(vendor => map.set(vendor.vendor_id, vendor.business_name))
    return map
  }, [vendors])

  const partyTimeline: TimelineEvent[] = useMemo(() => {
    return conversations
      .map(conversation => {
        const lastMessage = conversation.last_message
        const visuals = evaluateMessageVisual(lastMessage)
        const vendorLabel = formatVendorLabel(
          conversation.vendor_type,
          vendorLookup.get(conversation.vendor_id ?? '')
        )

        const timestamp = lastMessage?.timestamp ?? conversation.updated_at ?? conversation.created_at

        return {
          id: conversation.conversation_id,
          title: vendorLabel,
          subtitle: truncateContent(lastMessage?.content),
          actorLabel: getActorLabel(lastMessage?.sender_type),
          timestamp,
          relativeTime: formatRelativeTime(timestamp),
          accent: visuals.accent,
          icon: visuals.icon,
          badge: visuals.badge,
          mood: visuals.mood,
        }
      })
      .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
  }, [conversations, vendorLookup])

  const completionInsights = useMemo(() => {
    if (partyTimeline.length === 0) {
      return {
        completion: 0,
        headline: 'Let’s start sculpting the celebration timeline',
        subtext: 'Invite a vendor or send a message to spark the first milestone.',
        attentionCount: 0,
      }
    }

    let confirmed = 0
    let attention = 0
    partyTimeline.forEach(event => {
      if (event.mood === 'positive') confirmed += 1
      if (event.mood === 'attention') attention += 1
    })

    const neutral = partyTimeline.length - confirmed - attention
    const completionRaw =
      ((confirmed * 1 + neutral * 0.65) / partyTimeline.length) * 100
    const completion = Math.min(100, Math.round(completionRaw))

    const headline =
      attention > 0
        ? 'A couple of sparkles need your touch'
        : completion > 80
          ? 'Your celebration timeline is glowing'
          : 'The party energy is building'

    const subtext =
      attention > 0
        ? 'Tap the highlighted milestones to smooth out any bumps and keep the celebration on track.'
        : 'Milestones are aligning beautifully—keep the momentum by confirming the remaining details.'

    return {
      completion,
      headline,
      subtext,
      attentionCount: attention,
    }
  }, [partyTimeline])

  const detailedTimeline = useMemo(() => {
    if (!selectedConversation) return []
    return messages.map(message => {
      const visuals = evaluateMessageVisual(message)
      return {
        message,
        visuals,
        relativeTime: formatRelativeTime(message.timestamp),
        actorLabel: getActorLabel(message.sender_type),
      }
    })
  }, [messages, selectedConversation])

  const curatedRecommendations = useMemo(
    () => (vendorRecommendations ?? []).slice(0, 3),
    [vendorRecommendations]
  )

  if (isLoading) {
    return (
      <div
        className="min-h-screen flex items-center justify-center relative overflow-hidden"
        style={{
          background:
            'radial-gradient(circle at 15% 85%, rgba(244, 114, 182, 0.25), transparent 55%), radial-gradient(circle at 80% 20%, rgba(129, 140, 248, 0.25), transparent 50%), linear-gradient(135deg, rgba(255, 255, 255, 0.85), rgba(250, 245, 255, 0.85))',
        }}
      >
        {[...Array(18)].map((_, index) => (
          <motion.div
            key={index}
            className="absolute w-2 h-2 bg-gradient-to-r from-pink-400 to-purple-400 rounded-full opacity-70"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -35, 0],
              opacity: [0.2, 0.8, 0.2],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}

        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center relative z-10 px-6"
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2.8, repeat: Infinity, ease: 'linear' }}
            className="text-7xl mb-6"
          >
            💫
          </motion.div>
          <motion.h2
            className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-pink-600 via-purple-600 to-blue-600 bg-clip-text text-transparent mb-4"
            animate={{ backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'] }}
            transition={{ duration: 5, repeat: Infinity, ease: 'linear' }}
            style={{ backgroundSize: '200% 100%' }}
          >
            Curating your celebration timeline
          </motion.h2>
          <p className="text-xl text-purple-700/80 font-medium">
            Gathering vendor moments so you can watch the confirmations sparkle.
          </p>
        </motion.div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-rose-50 via-white to-purple-50 px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-md text-center space-y-4 bg-white/80 backdrop-blur-sm rounded-3xl p-10 shadow-2xl border border-rose-100"
        >
          <div className="text-5xl">🙈</div>
          <h2 className="text-2xl font-semibold text-rose-500">We hit a tiny snag</h2>
          <p className="text-gray-600">{error}</p>
          <motion.button
            onClick={refreshData}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.96 }}
            className="bg-gradient-to-r from-rose-500 to-purple-500 text-white px-6 py-3 rounded-xl font-semibold shadow-lg"
          >
            Try again with sparkle
          </motion.button>
        </motion.div>
      </div>
    )
  }

  return (
    <div
      className="min-h-screen relative overflow-hidden"
      style={{
        background:
          'radial-gradient(circle at 10% 80%, rgba(244, 114, 182, 0.22), transparent 55%), radial-gradient(circle at 85% 15%, rgba(129, 140, 248, 0.25), transparent 50%), linear-gradient(135deg, rgba(254, 249, 255, 0.96), rgba(244, 243, 255, 0.92))',
      }}
    >
      {[...Array(32)].map((_, index) => (
        <motion.div
          key={index}
          className="absolute w-2 h-2 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full opacity-60"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
          }}
          animate={{
            y: [0, -28, 0],
            opacity: [0.2, 0.7, 0.2],
          }}
          transition={{
            duration: 3.5 + Math.random() * 2,
            repeat: Infinity,
            delay: Math.random() * 3,
          }}
        />
      ))}

      <div className="relative z-10 max-w-7xl mx-auto px-4 md:px-6 lg:px-10 py-16 space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center space-y-6"
        >
          <div className="flex flex-col items-center gap-4">
            <span className="text-6xl md:text-7xl">🎉</span>
            <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-pink-600 via-purple-600 to-indigo-500 bg-clip-text text-transparent">
              Celebration Communication Hub
            </h1>
            <p className="text-lg md:text-xl text-slate-600 max-w-2xl">
              Watch every confirmation, adjustment, and joyful nod land on a living timeline
              designed to keep your party planning smooth and smile-worthy.
            </p>
          </div>

          <div className="flex flex-wrap justify-center gap-4">
            <motion.button
              onClick={onBack}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="inline-flex items-center gap-2 bg-gradient-to-r from-slate-600 to-slate-800 text-white px-6 py-3 rounded-2xl font-semibold shadow-lg"
            >
              ← Back to Party Overview
            </motion.button>
            <div className="inline-flex items-center gap-3 bg-white/70 backdrop-blur-md border border-white/60 rounded-2xl px-5 py-3 shadow-sm">
              <span
                className={`inline-flex h-3 w-3 rounded-full ${
                  isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
                }`}
              />
              <div className="text-left">
                <p className="text-sm font-semibold text-slate-700">
                  {isConnected ? 'Live sync with vendors' : 'Replaying recent updates'}
                </p>
                <p className="text-xs text-slate-500">
                  {isConnected
                    ? 'Real-time confirmations flowing in'
                    : 'We will reconnect automatically'}
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Party Timeline */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.8 }}
          className="bg-white/80 backdrop-blur-xl border border-white/60 rounded-3xl shadow-2xl overflow-hidden"
        >
          <div className="bg-gradient-to-r from-pink-100 via-purple-100 to-blue-100 px-5 py-4 border-b border-white/70">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
              <div className="text-left">
                <p className="text-xs uppercase tracking-[0.28em] text-pink-500 font-semibold">
                  Party Milestone Timeline
                </p>
                <h2 className="text-xl font-bold text-slate-800">
                  {completionInsights.headline}
                </h2>
                <p className="text-xs text-slate-600 mt-1 max-w-2xl leading-snug">
                  {completionInsights.subtext}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <div className="relative">
                  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-white to-purple-100 flex items-center justify-center shadow-inner">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-100 to-pink-100 flex items-center justify-center border border-white/60">
                      <span className="text-xl font-bold text-purple-600">
                        {completionInsights.completion}%
                      </span>
                    </div>
                  </div>
                  <div className="absolute inset-0 rounded-full animate-ping opacity-20 bg-gradient-to-br from-pink-400 to-purple-500" />
                </div>
                <div className="text-left">
                  <p className="text-xs font-semibold text-slate-700">Timeline Harmony</p>
                  <p className="text-[11px] text-slate-500">
                    {partyTimeline.length} active vendor {partyTimeline.length === 1 ? 'thread' : 'threads'}
                  </p>
                  {completionInsights.attentionCount > 0 && (
                    <p className="text-[11px] text-rose-500 font-semibold">
                      {completionInsights.attentionCount} milestone
                      {completionInsights.attentionCount > 1 ? 's need' : ' needs'} your attention
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="relative px-4 md:px-8 py-6">
            {partyTimeline.length === 0 ? (
              <div className="text-center text-slate-500">
                Your milestone panorama is ready—start a conversation to illuminate the first stop.
              </div>
            ) : (
              <div className="overflow-x-auto pb-2">
                <div className="relative min-w-max md:min-w-full py-6">
                  <div className="hidden md:block absolute top-12 left-10 right-10 h-[3px] bg-gradient-to-r from-pink-200 via-purple-200 to-blue-200 rounded-full" />
                  <div className="relative flex gap-4 md:gap-6 pl-2 pr-4 md:px-12">
                    {partyTimeline.map((event, index) => (
                      <motion.div
                        key={event.id}
                        initial={{ opacity: 0, y: 18 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="relative flex min-w-[220px] max-w-[250px] flex-col items-center"
                      >
                        <div className="relative z-10">
                          <div className="flex items-center justify-center w-12 h-12 rounded-full bg-white shadow-md border border-white/70">
                            <span className="text-xl">{event.icon}</span>
                          </div>
                          <div
                            className="absolute inset-0 rounded-full opacity-30"
                            style={{ boxShadow: MOOD_SHADOW[event.mood] }}
                          />
                        </div>
                        <div
                          className="relative mt-4 w-full bg-white/90 border border-white/70 rounded-2xl shadow transition-all duration-300 hover:-translate-y-1 hover:shadow-xl"
                          style={{ boxShadow: MOOD_SHADOW[event.mood] }}
                        >
                          <div className="absolute -top-1.5 left-1/2 h-1 w-12 -translate-x-1/2 rounded-full bg-gradient-to-r from-white/60 via-white to-white/60 opacity-80" />
                          <div className="flex items-center justify-between gap-2 px-4 pt-5 pb-2">
                            <span
                              className={`inline-flex items-center gap-1 text-[11px] font-semibold text-white px-2.5 py-0.5 rounded-full bg-gradient-to-r ${event.accent}`}
                            >
                              {event.badge}
                            </span>
                            <span className="text-[11px] font-semibold text-slate-500">
                              {event.relativeTime}
                            </span>
                          </div>
                          <div className="px-4 pb-4 space-y-2">
                            <h3 className="text-base font-semibold text-slate-800 leading-snug">
                              {event.title}
                            </h3>
                            <p
                              className="text-[13px] text-slate-600 leading-snug overflow-hidden"
                              style={{ display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical' }}
                            >
                              {event.subtitle}
                            </p>
                            <div className="flex items-center justify-between text-[11px] text-slate-400">
                              <span className="uppercase tracking-[0.18em]">
                                {event.actorLabel}
                              </span>
                              <span>
                                {new Date(event.timestamp).toLocaleString(undefined, {
                                  hour: 'numeric',
                                  minute: '2-digit',
                                  month: 'short',
                                  day: 'numeric',
                                })}
                              </span>
                            </div>
                          </div>
                          <div className="px-4 pb-4">
                            <div className="relative h-1.5 rounded-full bg-slate-100 overflow-hidden">
                              <div
                                className={`absolute inset-y-0 left-0 rounded-full bg-gradient-to-r ${event.accent}`}
                                style={{ width: MILESTONE_PROGRESS[event.mood] }}
                              />
                            </div>
                            <p className="mt-2 text-[11px] font-semibold text-slate-500">
                              {MILESTONE_CAPTION[event.mood]}
                            </p>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </motion.div>

        <div className="grid lg:grid-cols-3 gap-10">
          {/* Detailed Conversation Timeline */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.7 }}
            className="lg:col-span-2 space-y-4"
          >
            <div className="bg-white/85 backdrop-blur-xl border border-white/70 rounded-3xl shadow-2xl overflow-hidden">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 px-5 py-3 bg-gradient-to-r from-purple-100/70 via-pink-100/70 to-emerald-100/60 border-b border-white/70">
                <div>
                  <p className="text-xs uppercase tracking-[0.35em] text-purple-500 font-semibold">
                    Conversation Flow
                  </p>
                  <h3 className="text-lg font-bold text-slate-800">
                    {selectedConversation
                      ? formatVendorLabel(
                          selectedConversation.vendor_type,
                          vendorLookup.get(selectedConversation.vendor_id ?? '')
                        )
                      : 'Choose a vendor to view the journey'}
                  </h3>
                  <p className="text-sm text-slate-500 max-w-xl">
                    {selectedConversation
                      ? 'Follow each message as a milestone moment. Adjustments, confirmations, and happy dances appear in order.'
                      : 'Tap a vendor on the right to explore the enchanting back-and-forth.'}
                  </p>
                </div>
                {selectedConversation && (
                  <div className="flex items-center gap-2 bg-white/70 border border-purple-200 rounded-2xl px-3 py-1.5 text-xs font-semibold text-purple-600">
                    <span>✨</span>
                    <span>
                      {messages.length}{' '}
                      {messages.length === 1 ? 'message crafted' : 'messages crafted'}
                    </span>
                  </div>
                )}
              </div>

              {selectedConversation ? (
                <div className="max-h-[28rem] overflow-y-auto px-4 py-4 space-y-3">
                  <div className="relative">
                    <div className="absolute left-3 top-2 bottom-2 w-px bg-gradient-to-b from-purple-200 via-pink-200 to-emerald-200" />
                    <div className="space-y-3">
                      {detailedTimeline.map(({ message, visuals, relativeTime, actorLabel }) => (
                        <motion.div
                          key={message.message_id}
                          initial={{ opacity: 0, y: 12 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="relative pl-9"
                        >
                          <div className="absolute left-0 top-1 flex items-center justify-center w-7 h-7 rounded-full bg-white shadow-sm border border-white/70">
                            <span className="text-[11px]">{visuals.icon}</span>
                          </div>
                          <div
                            className="bg-white/90 border border-white/70 rounded-xl px-3 py-2.5 shadow"
                            style={{ boxShadow: MOOD_SHADOW[visuals.mood] }}
                          >
                            <div className="flex flex-wrap items-center justify-between gap-1.5 mb-1.5">
                              <div className="flex items-center gap-1.5">
                                <span
                                  className={`inline-flex items-center text-[10px] font-semibold text-white px-2 py-0.5 rounded-full bg-gradient-to-r ${visuals.accent}`}
                                >
                                  {visuals.badge}
                                </span>
                                <span className="text-[10px] uppercase tracking-[0.18em] text-slate-400">
                                  {actorLabel}
                                </span>
                              </div>
                              <span className="text-[10px] text-slate-400">{relativeTime}</span>
                            </div>
                            <p className="text-[13px] text-slate-700 leading-snug whitespace-pre-wrap">
                              {message.content}
                            </p>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="px-6 py-14 text-center text-slate-500">
                  <div className="text-5xl mb-4">🪄</div>
                  Select a conversation to watch the milestones unfold like a storybook.
                </div>
              )}

              {selectedConversation && (
                <div className="border-t border-white/70 px-4 py-3 bg-white/85">
                  <MessageComposer
                    onSendMessage={content =>
                      handleSendMessage(selectedConversation.conversation_id, content)
                    }
                    onTyping={handleTyping}
                    placeholder={`Celebrate with a note to ${formatVendorLabel(
                      selectedConversation.vendor_type,
                      vendorLookup.get(selectedConversation.vendor_id ?? '')
                    )}...`}
                  />
                </div>
              )}
            </div>
          </motion.div>

          {/* Sidebar */}
          <motion.aside
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35, duration: 0.7 }}
            className="space-y-6"
          >
            <div className="bg-white/85 backdrop-blur-xl border border-white/70 rounded-3xl shadow-2xl overflow-hidden">
              <div className="px-5 py-5 bg-gradient-to-r from-purple-100/60 to-blue-100/60 border-b border-white/70">
                <h3 className="text-lg font-bold text-slate-800">Active Vendor Streams</h3>
                <p className="text-xs text-slate-500">
                  Tap a stream to dive into its milestone journey.
                </p>
              </div>
              <div className="max-h-[24rem] overflow-y-auto p-5 space-y-4">
                {conversations.length === 0 ? (
                  <div className="text-sm text-slate-500 text-center py-6">
                    Start a conversation to light up this panel.
                  </div>
                ) : (
                  conversations.map(conversation => {
                    const lastMessage = conversation.last_message
                    const visuals = evaluateMessageVisual(lastMessage)
                    const isActive =
                      selectedConversation?.conversation_id === conversation.conversation_id
                    const unread =
                      conversation.unread_count?.['user_123'] ??
                      Object.values(conversation.unread_count || {}).reduce(
                        (total, value) => total + value,
                        0
                      )

                    return (
                      <motion.button
                        key={conversation.conversation_id}
                        onClick={() => handleSelectConversation(conversation.conversation_id)}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className={`w-full text-left bg-white/90 border border-white/70 rounded-2xl px-4 py-4 shadow-lg transition-all ${
                          isActive ? 'ring-2 ring-pink-300' : 'hover:-translate-y-1'
                        }`}
                        style={{ boxShadow: MOOD_SHADOW[visuals.mood] }}
                      >
                        <div className="flex items-center gap-3">
                          <div
                            className={`flex items-center justify-center w-11 h-11 rounded-2xl bg-gradient-to-r ${visuals.accent} text-xl`}
                          >
                            {visuals.icon}
                          </div>
                          <div className="flex-1">
                            <p className="text-sm font-semibold text-slate-800">
                              {formatVendorLabel(
                                conversation.vendor_type,
                                vendorLookup.get(conversation.vendor_id ?? '')
                              )}
                            </p>
                            <p className="text-xs text-slate-500 line-clamp-2">
                              {truncateContent(lastMessage?.content, 80)}
                            </p>
                          </div>
                          <div className="flex flex-col items-end gap-1">
                            <span className="text-xs font-semibold text-slate-500">
                              {lastMessage?.timestamp
                                ? formatRelativeTime(lastMessage.timestamp)
                                : 'New'}
                            </span>
                            {unread > 0 && (
                              <span className="inline-flex items-center justify-center text-xs font-semibold text-white bg-gradient-to-r from-pink-400 to-purple-400 rounded-full px-2 py-0.5">
                                {unread}
                              </span>
                            )}
                          </div>
                        </div>
                      </motion.button>
                    )
                  })
                )}
              </div>
            </div>

            <div className="bg-white/85 backdrop-blur-xl border border-white/70 rounded-3xl shadow-2xl overflow-hidden">
              <div className="px-5 py-5 bg-gradient-to-r from-emerald-100/60 to-teal-100/60 border-b border-white/70">
                <h3 className="text-lg font-bold text-slate-800">Next Magic to Book</h3>
                <p className="text-xs text-slate-500">
                  Recommendations to keep the momentum joyful.
                </p>
              </div>
              <div className="p-5 space-y-4">
                {curatedRecommendations.length === 0 ? (
                  <div className="text-sm text-slate-500">
                    Every key vendor is in motion. We’ll suggest more sparkle soon.
                  </div>
                ) : (
                  curatedRecommendations.map((recommendation, index) => (
                    <div
                      key={`${recommendation.type}-${index}`}
                      className="bg-white/90 border border-white/70 rounded-2xl px-4 py-4 shadow-inner"
                    >
                      <div className="flex items-center justify-between gap-3 mb-2">
                        <span className="text-sm font-semibold text-slate-800">
                          {formatVendorLabel(recommendation.type)}
                        </span>
                        {recommendation.book_by && (
                          <span className="text-xs font-semibold text-emerald-500">
                            Book by {recommendation.book_by}
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-slate-500 mb-2">
                        {recommendation.why_needed}
                      </p>
                      {recommendation.suggested_vendors && recommendation.suggested_vendors.length > 0 && (
                        <div className="flex flex-wrap gap-2">
                          {recommendation.suggested_vendors.map(vendor => (
                            <span
                              key={vendor}
                              className="inline-flex text-xs font-semibold text-emerald-600 bg-emerald-50 border border-emerald-100 rounded-full px-3 py-1"
                            >
                              {vendor}
                            </span>
                          ))}
                        </div>
                      )}
                      <div className="mt-3 text-xs text-slate-400">
                        Budget smile: ${recommendation.budget_range?.[0] ?? 0} - $
                        {recommendation.budget_range?.[1] ?? 0}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </motion.aside>
        </div>
      </div>
    </div>
  )
}
