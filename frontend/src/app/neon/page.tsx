'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'

export default function NeonB2BPage() {
  const [hoveredFeature, setHoveredFeature] = useState<number | null>(null)
  const [selectedIndustry, setSelectedIndustry] = useState<string>('real-estate')
  const [showExitPopup, setShowExitPopup] = useState(false)
  const [calculatorInputs, setCalculatorInputs] = useState({
    currentEvents: 2,
    dealValue: 8000,
    referralsPerEvent: 1
  })

  const features = [
    {
      icon: '🧠',
      title: 'Planning Agent',
      headline: 'Strategic Event Planning in Minutes',
      description: 'Tell us your goal, budget, and client profile. Our AI generates a complete event plan with timelines, vendor recommendations, and ROI projections—based on what\'s actually working in your industry right now.',
      benefit: 'Saves 8-10 hours of research and planning per event'
    },
    {
      icon: '🎨',
      title: 'Brand Agent',
      headline: 'Every Touchpoint, Perfectly On-Brand',
      description: 'Upload your logo and brand colors once. Neon creates white-labeled invitations, email campaigns, event signage, and social graphics that look like they came from a $5,000 designer.',
      benefit: 'Professional brand presence without hiring a design team'
    },
    {
      icon: '💬',
      title: 'Concierge Agent',
      headline: '24/7 Guest Communication',
      description: 'Your clients text questions about parking, dietary restrictions, or directions—our AI concierge responds instantly, professionally, and helpfully. You never miss a beat.',
      benefit: 'Eliminates 20+ back-and-forth emails per event'
    },
    {
      icon: '🧩',
      title: 'Memory Agent',
      headline: 'Turn Events into CRM Gold',
      description: 'After each event, Neon automatically creates detailed recaps: who attended, who brought referrals, conversation highlights, and follow-up actions. Syncs directly to your CRM.',
      benefit: 'Never lose track of a warm lead or referral opportunity'
    },
    {
      icon: '📄',
      title: 'Contract Agent',
      headline: 'Vendor Agreements, Zero Legal Headaches',
      description: 'We generate compliant contracts, handle e-signatures, and ensure insurance requirements are met. Built-in protections for cancellations, weather issues, and vendor no-shows.',
      benefit: 'Legal peace of mind and professional vendor relationships'
    }
  ]

  const pricing = [
    {
      name: 'DIY Planner',
      price: '$79',
      period: '/month',
      features: [
        'AI Planning Agent + Brand Agent',
        'Up to 3 events per year',
        'Self-service event templates',
        'White-labeled invites & RSVP pages',
        'Basic CRM integration (Zapier)',
        'Email support',
        'Access to vendor marketplace'
      ],
      popular: false,
      cta: 'Start with DIY Planner'
    },
    {
      name: 'Assisted',
      price: '$149',
      period: '/month',
      badge: 'MOST POPULAR',
      features: [
        'Up to 6 events per year',
        'Concierge Agent (chat support)',
        'Memory Agent (post-event recaps)',
        'Advanced CRM integrations',
        'Vendor coordination assistance',
        'Post-event analytics & ROI tracking',
        'Social media content generation',
        'Average user ROI: $47,000/year'
      ],
      popular: true,
      cta: 'Start Free 14-Day Trial'
    },
    {
      name: 'White Glove',
      price: '$299',
      period: '/month',
      features: [
        'Unlimited events',
        'Dedicated event coordinator',
        'Contract Agent (vendor agreements)',
        'White-label branding (remove Neon logo)',
        'Custom vendor negotiation',
        'Team collaboration (unlimited users)',
        'Priority phone support',
        'Event-day on-site support',
        'Quarterly strategy sessions'
      ],
      popular: false,
      cta: 'Schedule Strategy Call'
    }
  ]

  const testimonials = [
    {
      name: 'Sarah Chen',
      title: 'Luxury Real Estate Agent',
      location: 'Austin, TX',
      image: '👩🏻‍💼',
      quote: 'I used to stress over client appreciation events and wonder if they were worth it. Neon planned my "Welcome Home Wine Tasting" in 45 minutes, and I closed 3 deals from referrals at that event—$42,000 in commission. Now I host one every quarter.',
      metrics: ['3 Referrals', '$42K Revenue', '1 Event']
    },
    {
      name: 'James Park, CFP®',
      title: 'Financial Advisor',
      location: 'Charlotte, NC',
      image: '👨🏻‍💼',
      quote: 'FINRA compliance made me nervous about client events. Neon handles all the rules automatically—keeps dinners under $100/person, documents everything as "educational." I\'ve hosted 6 events this year with zero compliance issues and added $2.4M in AUM from referrals.',
      metrics: ['$2.4M New AUM', '6 Events', '100% Compliant']
    },
    {
      name: 'Dr. Maria Rodriguez',
      title: 'Veterinary Practice Owner',
      location: 'Nashville, TN',
      image: '👩🏽‍⚕️',
      quote: 'Our "Puppy Social" events used to be chaotic. Neon turned them into branded experiences that clients rave about. We went from 2 events/year to 8, and our new client acquisition cost dropped 40% because of word-of-mouth.',
      metrics: ['8 Events/Year', '40% Lower CAC', '300+ Attendees']
    }
  ]

  const industries = {
    'real-estate': {
      title: 'Real Estate Agents',
      templates: [
        { name: 'Welcome Home Party', price: '$349-799' },
        { name: 'Broker Open House VIP Preview', price: '$199-499' },
        { name: 'Client Appreciation BBQ', price: '$599-1,299' },
        { name: 'Neighborhood Block Party', price: '$799-1,999' }
      ],
      compliance: [
        'RESPA-compliant (no gifts over $100)',
        'Automatically tracks attendee relationships',
        'Vendor pricing transparency'
      ],
      integrations: ['LionDesk', 'Follow Up Boss', 'kvCORE', 'Top Producer'],
      stat: 'Top 1% of agents host 4+ client events per year. Neon makes it effortless.'
    },
    'financial': {
      title: 'Financial Advisors',
      templates: [
        { name: 'Client Appreciation Dinner', price: '$799-1,999' },
        { name: 'Market Update Seminar', price: '$299-699' },
        { name: 'Estate Planning Workshop', price: '$499-1,299' },
        { name: 'Quarterly Economic Briefing', price: '$399-899' }
      ],
      compliance: [
        'FINRA entertainment limits (auto-calculates)',
        'Documents as "education" not "entertainment"',
        'Approval-ready event descriptions'
      ],
      integrations: ['Wealthbox', 'Redtail', 'Salesforce Financial', 'Orion'],
      stat: 'Advisors using Neon see 32% higher client retention vs industry average.'
    },
    'veterinary': {
      title: 'Veterinary Practices',
      templates: [
        { name: 'Puppy Socialization Hour', price: '$249-599' },
        { name: 'Senior Pet Wellness Day', price: '$399-899' },
        { name: 'Client Appreciation Clinic Tour', price: '$349-749' },
        { name: 'Adopt-a-Thon Partnership', price: '$599-1,499' }
      ],
      compliance: [
        'Vaccination records integration',
        'Pet-specific invitations (by species/age)',
        'Vendor network (pet-safe caterers, trainers)'
      ],
      integrations: ['AVImark', 'Impromed', 'eVetPractice', 'Cornerstone'],
      stat: 'Practices hosting quarterly events see 3x higher annual visit frequency.'
    },
    'wellness': {
      title: 'Wellness & MedSpas',
      templates: [
        { name: 'Glow Up Launch Party', price: '$799-2,499' },
        { name: 'VIP Treatment Preview', price: '$599-1,499' },
        { name: 'Wellness Workshop', price: '$399-999' },
        { name: 'Client Appreciation Spa Day', price: '$1,299-3,999' }
      ],
      compliance: [
        'Treatment package integration',
        'Before/after photo galleries (HIPAA-compliant)',
        'Influencer coordination tools'
      ],
      integrations: ['Zenoti', 'Mindbody', 'Booker', 'Vagaro'],
      stat: 'MedSpas using events see 45% higher treatment package conversion.'
    }
  }

  // Calculate ROI
  const currentRevenue = calculatorInputs.currentEvents * calculatorInputs.referralsPerEvent * calculatorInputs.dealValue
  const neonRevenue = 5 * 3 * calculatorInputs.dealValue
  const revenueIncrease = neonRevenue - currentRevenue
  const neonInvestment = 1788 // Assisted plan annual
  const roi = Math.round((revenueIncrease / neonInvestment) * 100)

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0f0c29] via-[#302b63] to-[#24243e] text-white overflow-x-hidden">
      {/* Navigation */}
      <motion.nav
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6 }}
        className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl bg-black/30 border-b border-purple-500/30"
      >
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <motion.a
            href="/"
            className="text-2xl font-bold bg-gradient-to-r from-pink-500 to-purple-600 bg-clip-text text-transparent"
            whileHover={{ scale: 1.05 }}
          >
            Festimo Neon
          </motion.a>
          
          <div className="flex items-center gap-4">
            <motion.a
              href="#pricing"
              className="text-gray-300 hover:text-white transition-colors"
              whileHover={{ scale: 1.05 }}
            >
              Pricing
            </motion.a>
            <motion.button
              className="px-6 py-2.5 rounded-full bg-gradient-to-r from-pink-500 to-purple-600 font-semibold"
              whileHover={{ scale: 1.05, boxShadow: '0 0 30px rgba(236, 72, 153, 0.6)' }}
              whileTap={{ scale: 0.95 }}
            >
              Start Free Trial
            </motion.button>
          </div>
        </div>
      </motion.nav>

      {/* Animated background */}
      <div className="fixed inset-0 opacity-20 pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={`bg-${i}`}
            className="absolute rounded-full"
            style={{
              width: Math.random() * 300 + 50,
              height: Math.random() * 300 + 50,
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              background: `radial-gradient(circle, ${
                i % 2 === 0 ? 'rgba(167, 139, 250, 0.3)' : 'rgba(236, 72, 153, 0.3)'
              }, transparent)`,
              filter: 'blur(40px)'
            }}
            animate={{
              x: [0, Math.random() * 100 - 50],
              y: [0, Math.random() * 100 - 50],
              scale: [1, 1.2, 1]
            }}
            transition={{
              duration: Math.random() * 10 + 10,
              repeat: Infinity,
              ease: 'easeInOut'
            }}
          />
        ))}
      </div>

      <div className="relative z-10 pt-32 px-6">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="max-w-6xl mx-auto text-center mb-20"
        >
          <motion.div
            className="inline-block mb-6"
            animate={{
              textShadow: [
                '0 0 20px rgba(167, 139, 250, 0.8)',
                '0 0 40px rgba(236, 72, 153, 0.8)',
                '0 0 20px rgba(167, 139, 250, 0.8)'
              ]
            }}
            transition={{ duration: 3, repeat: Infinity }}
          >
            <h1 className="text-6xl md:text-7xl font-bold bg-gradient-to-r from-purple-400 via-pink-500 to-purple-600 bg-clip-text text-transparent mb-4">
              Your Clients Remember
            </h1>
            <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-pink-400 via-purple-500 to-pink-600 bg-clip-text text-transparent">
              Experiences, Not Emails
            </h1>
          </motion.div>
          
          <p className="text-xl md:text-2xl text-gray-300 mb-6 max-w-4xl mx-auto">
            Top-performing professionals close 3-5 referrals per event. Neon plans, executes, and tracks client appreciation events that turn moments into revenue—while you focus on what you do best.
          </p>
          
          <p className="text-lg text-gray-400 max-w-3xl mx-auto mb-12">
            Trusted by 500+ real estate agents, financial advisors, and wellness professionals across 15 cities
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <motion.button
              className="px-8 py-4 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 font-bold text-lg"
              style={{
                boxShadow: '0 0 30px rgba(167, 139, 250, 0.5)'
              }}
              whileHover={{ 
                scale: 1.05,
                boxShadow: '0 0 50px rgba(167, 139, 250, 0.8)'
              }}
              whileTap={{ scale: 0.95 }}
            >
              Plan Your First Event (Free Strategy Session)
            </motion.button>
            
            <motion.button
              className="px-8 py-4 rounded-full border-2 border-purple-500 font-bold text-lg backdrop-blur-sm"
              whileHover={{ 
                scale: 1.05,
                backgroundColor: 'rgba(167, 139, 250, 0.1)'
              }}
              whileTap={{ scale: 0.95 }}
            >
              See How It Works (2-min video)
            </motion.button>
          </div>
        </motion.div>

        {/* Problem Section */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="max-w-7xl mx-auto mb-20"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-center mb-4">
            You Know Events Build Loyalty.
          </h2>
          <p className="text-2xl text-gray-400 text-center mb-16">
            But Planning Them Drains You.
          </p>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                title: 'Time Vacuum',
                problem: 'You spend 12-15 hours per event coordinating vendors, designing invites, and managing RSVPs—time you could spend closing deals.',
                icon: '⏰'
              },
              {
                title: 'Inconsistent Results',
                problem: 'Some events generate 5 referrals. Others? Zero. You\'re not sure what\'s working or why.',
                icon: '📊'
              },
              {
                title: 'Generic = Forgettable',
                problem: 'Generic invites and cookie-cutter venues don\'t reflect your premium brand. Your clients deserve better.',
                icon: '😴'
              },
              {
                title: 'No ROI Tracking',
                problem: 'You invest $2,000 in an event but can\'t prove it brought back $20,000 in business. Your events feel like expenses, not investments.',
                icon: '💸'
              }
            ].map((item, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * idx }}
                className="p-6 rounded-2xl backdrop-blur-xl bg-white/5 border border-red-500/30"
              >
                <div className="text-5xl mb-4">{item.icon}</div>
                <h3 className="text-xl font-bold mb-3 text-red-400">{item.title}</h3>
                <p className="text-gray-400 text-sm">{item.problem}</p>
              </motion.div>
            ))}
          </div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="text-2xl text-center mt-12 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent font-bold"
          >
            What if you could host 4x more events, in 1/10th the time, with measurable ROI?
          </motion.p>
        </motion.div>

        {/* 5 AI Agents Section */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="max-w-7xl mx-auto mb-20"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-center mb-4">
            5 AI Agents Working for
          </h2>
          <h2 className="text-4xl md:text-5xl font-bold text-center mb-16 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            Your Business Growth
          </h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * idx }}
                onHoverStart={() => setHoveredFeature(idx)}
                onHoverEnd={() => setHoveredFeature(null)}
                className="relative p-8 rounded-3xl backdrop-blur-xl bg-white/5 border border-purple-500/30 overflow-hidden"
                style={{
                  boxShadow: hoveredFeature === idx 
                    ? '0 0 40px rgba(167, 139, 250, 0.4)' 
                    : 'none'
                }}
              >
                <motion.div
                  className="absolute inset-0 bg-gradient-to-br from-purple-500/20 to-pink-500/20"
                  animate={{
                    opacity: hoveredFeature === idx ? 1 : 0
                  }}
                  transition={{ duration: 0.3 }}
                />

                <div className="relative z-10">
                  <div className="text-6xl mb-4">{feature.icon}</div>
                  <h3 className="text-2xl font-bold mb-3">{feature.headline}</h3>
                  <p className="text-gray-400 mb-4 text-sm">{feature.description}</p>
                  <div className="pt-4 border-t border-purple-500/30">
                    <p className="text-purple-400 font-semibold text-sm">✓ {feature.benefit}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* ROI Calculator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="max-w-4xl mx-auto mb-20"
        >
          <div className="p-12 rounded-3xl backdrop-blur-xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-400"
            style={{
              boxShadow: '0 0 60px rgba(167, 139, 250, 0.3)'
            }}
          >
            <h2 className="text-4xl font-bold text-center mb-4">
              Calculate Your Neon ROI
            </h2>
            <p className="text-gray-300 text-center mb-8">in 60 Seconds</p>

            <div className="space-y-6 mb-8">
              <div>
                <label className="block text-sm mb-2">How many events do you host per year currently?</label>
                <input
                  type="range"
                  min="0"
                  max="6"
                  value={calculatorInputs.currentEvents}
                  onChange={(e) => setCalculatorInputs({...calculatorInputs, currentEvents: parseInt(e.target.value)})}
                  className="w-full"
                />
                <div className="text-right text-purple-400 font-bold">{calculatorInputs.currentEvents} events</div>
              </div>

              <div>
                <label className="block text-sm mb-2">What's your average commission/deal value?</label>
                <input
                  type="number"
                  value={calculatorInputs.dealValue}
                  onChange={(e) => setCalculatorInputs({...calculatorInputs, dealValue: parseInt(e.target.value)})}
                  className="w-full px-4 py-3 rounded-xl bg-white/10 border border-purple-500/30 text-white"
                  placeholder="$8,000"
                />
              </div>

              <div>
                <label className="block text-sm mb-2">How many referrals do you typically get per event?</label>
                <input
                  type="range"
                  min="0"
                  max="5"
                  value={calculatorInputs.referralsPerEvent}
                  onChange={(e) => setCalculatorInputs({...calculatorInputs, referralsPerEvent: parseInt(e.target.value)})}
                  className="w-full"
                />
                <div className="text-right text-purple-400 font-bold">{calculatorInputs.referralsPerEvent} referrals</div>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className="p-6 rounded-2xl bg-white/5 border border-purple-500/30">
                <div className="text-sm text-gray-400 mb-2">Current Annual Revenue from Events</div>
                <div className="text-3xl font-bold text-white">
                  ${currentRevenue.toLocaleString()}
                </div>
              </div>

              <div className="p-6 rounded-2xl bg-gradient-to-br from-purple-500/30 to-pink-500/30 border border-purple-400">
                <div className="text-sm text-gray-200 mb-2">With Neon (5 events/year, 3 referrals/event avg)</div>
                <div className="text-3xl font-bold text-white">
                  ${neonRevenue.toLocaleString()}
                </div>
              </div>
            </div>

            <div className="text-center space-y-2 mb-8">
              <div className="text-lg text-gray-300">
                <span className="text-green-400 font-bold">Revenue Increase:</span> +${revenueIncrease.toLocaleString()}/year
              </div>
              <div className="text-lg text-gray-300">
                <span className="text-purple-400 font-bold">Neon Investment:</span> ${neonInvestment.toLocaleString()}/year
              </div>
              <div className="text-3xl font-bold bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent">
                Net ROI: {roi}%
              </div>
            </div>

            <motion.button
              className="w-full py-4 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 font-bold text-lg"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              Start Generating Measurable ROI →
            </motion.button>
          </div>
        </motion.div>

        {/* Testimonials */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7 }}
          className="max-w-7xl mx-auto mb-20"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-center mb-16">
            Join 500+ Professionals Building Businesses Through Experiences
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * idx }}
                whileHover={{ y: -10 }}
                className="p-8 rounded-3xl backdrop-blur-xl bg-white/5 border border-purple-500/30"
              >
                <div className="text-6xl mb-4">{testimonial.image}</div>
                <h3 className="text-xl font-bold mb-1">{testimonial.name}</h3>
                <p className="text-sm text-purple-400 mb-2">{testimonial.title}</p>
                <p className="text-xs text-gray-500 mb-4">{testimonial.location}</p>
                <p className="text-gray-300 mb-6 italic">"{testimonial.quote}"</p>
                <div className="flex flex-wrap gap-2">
                  {testimonial.metrics.map((metric, i) => (
                    <span key={i} className="px-3 py-1 rounded-full bg-purple-500/20 text-xs text-purple-300 border border-purple-500/30">
                      {metric}
                    </span>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Industry Specific */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="max-w-7xl mx-auto mb-20"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-center mb-4">
            Built for How YOU Actually Work
          </h2>
          <p className="text-gray-400 text-center mb-12">
            Industry-specific templates, compliance, and integrations
          </p>

          {/* Tab Navigation */}
          <div className="flex flex-wrap justify-center gap-4 mb-12">
            {Object.entries(industries).map(([key, industry]) => (
              <motion.button
                key={key}
                onClick={() => setSelectedIndustry(key)}
                className={`px-6 py-3 rounded-full font-semibold transition-all ${
                  selectedIndustry === key
                    ? 'bg-gradient-to-r from-purple-500 to-pink-500'
                    : 'bg-white/10 hover:bg-white/20'
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {industry.title}
              </motion.button>
            ))}
          </div>

          {/* Industry Content */}
          <AnimatePresence mode="wait">
            <motion.div
              key={selectedIndustry}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className="p-12 rounded-3xl backdrop-blur-xl bg-white/5 border border-purple-500/30"
            >
              <h3 className="text-3xl font-bold mb-8">{industries[selectedIndustry as keyof typeof industries].title}</h3>

              <div className="grid md:grid-cols-2 gap-8 mb-8">
                <div>
                  <h4 className="text-xl font-semibold mb-4 text-purple-400">Event Templates</h4>
                  <div className="space-y-3">
                    {industries[selectedIndustry as keyof typeof industries].templates.map((template, idx) => (
                      <div key={idx} className="flex justify-between items-center p-4 rounded-xl bg-white/5 border border-purple-500/20">
                        <span>{template.name}</span>
                        <span className="text-purple-400 font-semibold">{template.price}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-xl font-semibold mb-4 text-pink-400">Built-In Compliance</h4>
                  <div className="space-y-3">
                    {industries[selectedIndustry as keyof typeof industries].compliance.map((item, idx) => (
                      <div key={idx} className="flex items-start gap-3 p-4 rounded-xl bg-white/5 border border-pink-500/20">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="text-green-400 flex-shrink-0 mt-0.5">
                          <polyline points="20 6 9 17 4 12"/>
                        </svg>
                        <span className="text-sm">{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="mb-6">
                <h4 className="text-xl font-semibold mb-4 text-cyan-400">CRM Integrations</h4>
                <div className="flex flex-wrap gap-3">
                  {industries[selectedIndustry as keyof typeof industries].integrations.map((integration, idx) => (
                    <span key={idx} className="px-4 py-2 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                      {integration}
                    </span>
                  ))}
                </div>
              </div>

              <div className="p-6 rounded-2xl bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-400">
                <p className="text-lg">
                  <span className="font-bold text-purple-400">📊 Stat:</span> {industries[selectedIndustry as keyof typeof industries].stat}
                </p>
              </div>
            </motion.div>
          </AnimatePresence>
        </motion.div>

        {/* Pricing Section */}
        <motion.div
          id="pricing"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.9 }}
          className="max-w-7xl mx-auto mb-20"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-center mb-4">
            Plans That Grow With Your Business
          </h2>
          <p className="text-gray-400 text-center mb-4">
            No hidden fees. No vendor markups. Cancel anytime.
          </p>
          <p className="text-sm text-gray-500 text-center mb-12">
            Pay for the platform, get transparent vendor pricing
          </p>

          <div className="grid md:grid-cols-3 gap-8">
            {pricing.map((plan, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * idx }}
                whileHover={{ y: -10 }}
                className={`relative p-8 rounded-3xl backdrop-blur-xl border overflow-hidden ${
                  plan.popular
                    ? 'bg-gradient-to-br from-purple-500/20 to-pink-500/20 border-purple-400'
                    : 'bg-white/5 border-purple-500/30'
                }`}
                style={{
                  boxShadow: plan.popular 
                    ? '0 0 50px rgba(167, 139, 250, 0.4)' 
                    : 'none'
                }}
              >
                {plan.badge && (
                  <div className="absolute top-4 right-4 px-3 py-1 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 text-xs font-bold">
                    {plan.badge}
                  </div>
                )}

                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                <div className="mb-6">
                  <span className="text-5xl font-bold">{plan.price}</span>
                  <span className="text-gray-400">{plan.period}</span>
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      <svg 
                        width="20" 
                        height="20" 
                        viewBox="0 0 24 24" 
                        fill="none" 
                        stroke="currentColor" 
                        strokeWidth="2.5"
                        className="text-purple-400 flex-shrink-0 mt-0.5"
                      >
                        <polyline points="20 6 9 17 4 12"/>
                      </svg>
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                <motion.button
                  className={`w-full py-3 rounded-full font-bold ${
                    plan.popular
                      ? 'bg-gradient-to-r from-purple-500 to-pink-500'
                      : 'border-2 border-purple-500'
                  }`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {plan.cta}
                </motion.button>
              </motion.div>
            ))}
          </div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.2 }}
            className="text-center text-sm text-gray-400 mt-8"
          >
            💰 Average event execution cost: $800-2,500 (transparent vendor pricing)
          </motion.p>
        </motion.div>

        {/* Final CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="max-w-4xl mx-auto text-center mb-20 p-12 rounded-3xl backdrop-blur-xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 border border-purple-400"
          style={{
            boxShadow: '0 0 60px rgba(167, 139, 250, 0.3)'
          }}
        >
          <h2 className="text-4xl font-bold mb-4">
            Ready to Transform Your Business?
          </h2>
          <p className="text-gray-300 text-lg mb-6">
            Join thousands of event professionals who trust Festimo Neon
          </p>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
            {[
              { value: '$47,000', label: 'Average revenue increase/year' },
              { value: '10-15', label: 'Hours saved per event' },
              { value: '3-5', label: 'Referrals per event' },
              { value: '4.8/5', label: 'User rating (247 reviews)' }
            ].map((stat, idx) => (
              <div key={idx} className="text-center">
                <div className="text-3xl font-bold text-purple-400 mb-1">{stat.value}</div>
                <div className="text-xs text-gray-400">{stat.label}</div>
              </div>
            ))}
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-6">
            <motion.button
              className="px-8 py-4 rounded-full bg-white text-purple-600 font-bold text-lg"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Plan Your First Event Free →
            </motion.button>
            <motion.button
              className="px-8 py-4 rounded-full border-2 border-white font-bold text-lg"
              whileHover={{ scale: 1.05, backgroundColor: 'rgba(255, 255, 255, 0.1)' }}
              whileTap={{ scale: 0.95 }}
            >
              Schedule 15-Minute Demo Call →
            </motion.button>
          </div>

          <p className="text-sm text-gray-400">
            ✅ 14-day free trial • No credit card required • Cancel anytime
          </p>
          <p className="text-xs text-gray-500 mt-2">
            100% money-back guarantee if your first event doesn't exceed expectations
          </p>
        </motion.div>
      </div>

      {/* Footer */}
      <div className="border-t border-purple-500/30 py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <h4 className="font-bold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white">About Neon</a></li>
                <li><a href="#" className="hover:text-white">How It Works</a></li>
                <li><a href="#" className="hover:text-white">Case Studies</a></li>
                <li><a href="#" className="hover:text-white">Careers</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4">Resources</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white">Help Center</a></li>
                <li><a href="#" className="hover:text-white">Video Tutorials</a></li>
                <li><a href="#" className="hover:text-white">ROI Calculator</a></li>
                <li><a href="#" className="hover:text-white">Industry Guides</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white">Terms of Service</a></li>
                <li><a href="#" className="hover:text-white">Refund Policy</a></li>
                <li><a href="#" className="hover:text-white">Compliance</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4">Contact</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>hello@neon.parx.ai</li>
                <li>1-888-NEON-AI</li>
                <li>Chat: Available 24/7</li>
                <li>Office: Austin, TX</li>
              </ul>
            </div>
          </div>
          <div className="text-center text-sm text-gray-500 pt-8 border-t border-purple-500/30">
            <p>© 2025 Festimo Neon. All rights reserved.</p>
            <p className="mt-2">Rated 4.8/5 stars by 247 professionals</p>
          </div>
        </div>
      </div>
    </div>
  )
}
