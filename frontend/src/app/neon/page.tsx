'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'

export default function NeonB2BPage() {
  const [hoveredFeature, setHoveredFeature] = useState<number | null>(null)
  const [selectedIndustry, setSelectedIndustry] = useState<string>('real-estate')
  const [calculatorInputs, setCalculatorInputs] = useState({
    currentEvents: 2,
    dealValue: 8000,
    referralsPerEvent: 1
  })

  const features = [
    {
      icon: '🧠',
      title: 'Planning Agent',
      description: 'AI generates complete event plans with timelines and vendor recommendations based on industry best practices.',
      benefit: 'Saves 8-10 hours per event'
    },
    {
      icon: '🎨',
      title: 'Brand Agent',
      description: 'White-labeled invitations, campaigns, and graphics that match your brand identity perfectly.',
      benefit: 'Professional presence, no designer needed'
    },
    {
      icon: '💬',
      title: 'Concierge Agent',
      description: '24/7 AI concierge handles guest communications instantly and professionally.',
      benefit: 'Eliminates 20+ emails per event'
    },
    {
      icon: '🧩',
      title: 'Memory Agent',
      description: 'Automated post-event recaps with attendee insights and CRM integration.',
      benefit: 'Never miss a warm lead'
    },
    {
      icon: '📄',
      title: 'Contract Agent',
      description: 'Generate compliant vendor contracts with built-in protections and e-signatures.',
      benefit: 'Legal peace of mind'
    }
  ]

  const pricing = [
    {
      name: 'DIY Planner',
      price: '$79',
      period: '/month',
      features: [
        'AI Planning + Brand Agent',
        'Up to 3 events/year',
        'Event templates',
        'White-labeled invites',
        'Basic CRM integration',
        'Email support'
      ],
      popular: false,
      cta: 'Start DIY Plan'
    },
    {
      name: 'Assisted',
      price: '$149',
      period: '/month',
      badge: 'POPULAR',
      features: [
        'Up to 6 events/year',
        'Concierge Agent',
        'Memory Agent',
        'Advanced CRM integrations',
        'Vendor coordination',
        'ROI tracking',
        'Avg ROI: $47K/year'
      ],
      popular: true,
      cta: 'Start 14-Day Trial'
    },
    {
      name: 'White Glove',
      price: '$299',
      period: '/month',
      features: [
        'Unlimited events',
        'Dedicated coordinator',
        'Contract Agent',
        'White-label branding',
        'Custom vendor negotiation',
        'Team collaboration',
        'On-site support'
      ],
      popular: false,
      cta: 'Schedule Call'
    }
  ]

  const testimonials = [
    {
      name: 'Sarah Chen',
      title: 'Luxury Real Estate Agent',
      location: 'Austin, TX',
      quote: 'Neon planned my Welcome Home Wine Tasting in 45 minutes. I closed 3 deals from referrals—$42K in commission.',
      metrics: ['3 Referrals', '$42K Revenue', '1 Event']
    },
    {
      name: 'James Park, CFP®',
      title: 'Financial Advisor',
      location: 'Charlotte, NC',
      quote: 'FINRA compliance made me nervous. Neon handles all rules automatically. I\'ve hosted 6 events with zero issues and $2.4M in new AUM.',
      metrics: ['$2.4M AUM', '6 Events', '100% Compliant']
    },
    {
      name: 'Dr. Maria Rodriguez',
      title: 'Veterinary Practice Owner',
      location: 'Nashville, TN',
      quote: 'Our Puppy Socials went from chaotic to branded experiences. We scaled to 8 events/year and cut CAC by 40%.',
      metrics: ['8 Events/Year', '40% Lower CAC', '300+ Attendees']
    }
  ]

  const industries = {
    'real-estate': {
      title: 'Real Estate Agents',
      templates: [
        { name: 'Welcome Home Party', price: '$349-799' },
        { name: 'Broker VIP Preview', price: '$199-499' },
        { name: 'Client Appreciation BBQ', price: '$599-1,299' }
      ],
      compliance: [
        'RESPA-compliant (no gifts over $100)',
        'Attendee relationship tracking',
        'Transparent vendor pricing'
      ],
      integrations: ['LionDesk', 'Follow Up Boss', 'kvCORE', 'Top Producer'],
      stat: 'Top 1% of agents host 4+ events/year. Neon makes it effortless.'
    },
    'financial': {
      title: 'Financial Advisors',
      templates: [
        { name: 'Client Appreciation Dinner', price: '$799-1,999' },
        { name: 'Market Update Seminar', price: '$299-699' },
        { name: 'Estate Planning Workshop', price: '$499-1,299' }
      ],
      compliance: [
        'FINRA entertainment limits (auto-calculates)',
        'Documents as "education" not "entertainment"',
        'Approval-ready descriptions'
      ],
      integrations: ['Wealthbox', 'Redtail', 'Salesforce', 'Orion'],
      stat: 'Advisors using Neon see 32% higher client retention.'
    },
    'veterinary': {
      title: 'Veterinary Practices',
      templates: [
        { name: 'Puppy Socialization', price: '$249-599' },
        { name: 'Senior Pet Wellness', price: '$399-899' },
        { name: 'Adopt-a-Thon', price: '$599-1,499' }
      ],
      compliance: [
        'Vaccination records integration',
        'Pet-specific invitations',
        'Pet-safe vendor network'
      ],
      integrations: ['AVImark', 'Impromed', 'eVetPractice'],
      stat: 'Quarterly events drive 3x higher annual visit frequency.'
    }
  }

  // Calculate ROI
  const currentRevenue = calculatorInputs.currentEvents * calculatorInputs.referralsPerEvent * calculatorInputs.dealValue
  const neonRevenue = 5 * 3 * calculatorInputs.dealValue
  const revenueIncrease = neonRevenue - currentRevenue
  const neonInvestment = 1788
  const roi = Math.round((revenueIncrease / neonInvestment) * 100)

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#f5f1e8] via-[#faf8f3] to-[#f0ebe0]">
      {/* Subtle Pattern Overlay */}
      <div className="fixed inset-0 opacity-[0.03] pointer-events-none" style={{
        backgroundImage: `radial-gradient(circle at 2px 2px, #6b46c1 1px, transparent 0)`,
        backgroundSize: '40px 40px'
      }} />

      {/* Navigation */}
      <motion.nav
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="fixed top-0 left-0 right-0 z-50 bg-[#faf8f3]/80 backdrop-blur-xl border-b border-[#6b46c1]/10"
      >
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <a href="/" className="text-xl font-bold text-[#6b46c1]">
            Festimo Neon
          </a>
          
          <div className="flex items-center gap-6">
            <a href="#pricing" className="text-gray-700 hover:text-[#6b46c1] transition-colors text-sm font-medium">
              Pricing
            </a>
            <motion.button
              className="px-5 py-2 rounded-full bg-[#6b46c1] text-white text-sm font-medium"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Start Free Trial
            </motion.button>
          </div>
        </div>
      </motion.nav>

      <div className="relative pt-24 pb-16 px-6">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-5xl mx-auto text-center mb-20"
        >
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Your Clients Remember<br/>
            <span className="text-[#6b46c1]">Experiences, Not Emails</span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-4 max-w-3xl mx-auto">
            Top professionals close 3-5 referrals per event. Neon plans, executes, and tracks client appreciation events that turn moments into revenue.
          </p>
          
          <p className="text-sm text-gray-500 mb-8">
            Trusted by 500+ professionals across 15 cities
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <motion.button
              className="px-8 py-4 rounded-full bg-[#6b46c1] text-white font-medium"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Plan Your First Event
            </motion.button>
            
            <motion.button
              className="px-8 py-4 rounded-full border-2 border-[#6b46c1] text-[#6b46c1] font-medium"
              whileHover={{ scale: 1.05, backgroundColor: 'rgba(107, 70, 193, 0.05)' }}
              whileTap={{ scale: 0.95 }}
            >
              See How It Works
            </motion.button>
          </div>
        </motion.div>

        {/* Problem Section */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="max-w-6xl mx-auto mb-20"
        >
          <h2 className="text-3xl font-bold text-center mb-3 text-gray-900">
            You Know Events Build Loyalty.
          </h2>
          <p className="text-xl text-gray-600 text-center mb-12">
            But Planning Them Drains You.
          </p>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { title: 'Time Vacuum', problem: '12-15 hours per event coordinating vendors and managing RSVPs.' },
              { title: 'Inconsistent Results', problem: 'Some events generate 5 referrals. Others? Zero.' },
              { title: 'Generic = Forgettable', problem: 'Cookie-cutter venues don\'t reflect your premium brand.' },
              { title: 'No ROI Tracking', problem: 'Can\'t prove events generate actual business value.' }
            ].map((item, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * idx }}
                className="p-6 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200/50"
              >
                <h3 className="text-lg font-bold mb-2 text-[#6b46c1]">{item.title}</h3>
                <p className="text-sm text-gray-600">{item.problem}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Features Section */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="max-w-6xl mx-auto mb-20"
        >
          <h2 className="text-3xl font-bold text-center mb-3 text-gray-900">
            5 AI Agents Working for Your Business
          </h2>
          <p className="text-gray-600 text-center mb-12">
            Automated intelligence that drives results
          </p>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * idx }}
                onHoverStart={() => setHoveredFeature(idx)}
                onHoverEnd={() => setHoveredFeature(null)}
                className="p-6 rounded-2xl bg-white/60 backdrop-blur-sm border border-gray-200/50 transition-all"
                style={{
                  boxShadow: hoveredFeature === idx 
                    ? '0 10px 40px rgba(107, 70, 193, 0.15)' 
                    : 'none'
                }}
              >
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-lg font-bold mb-2 text-gray-900">{feature.title}</h3>
                <p className="text-sm text-gray-600 mb-3">{feature.description}</p>
                <p className="text-xs text-[#6b46c1] font-medium">✓ {feature.benefit}</p>
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
          <div className="p-10 rounded-3xl bg-white/70 backdrop-blur-sm border border-[#6b46c1]/20">
            <h2 className="text-3xl font-bold text-center mb-3 text-gray-900">
              Calculate Your ROI in 60 Seconds
            </h2>
            <p className="text-gray-600 text-center mb-8">
              See your potential revenue increase
            </p>

            <div className="space-y-6 mb-8">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Events hosted per year currently
                </label>
                <input
                  type="range"
                  min="0"
                  max="6"
                  value={calculatorInputs.currentEvents}
                  onChange={(e) => setCalculatorInputs({...calculatorInputs, currentEvents: parseInt(e.target.value)})}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[#6b46c1]"
                />
                <div className="text-right text-[#6b46c1] font-bold mt-1">{calculatorInputs.currentEvents} events</div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Average commission/deal value
                </label>
                <input
                  type="number"
                  value={calculatorInputs.dealValue}
                  onChange={(e) => setCalculatorInputs({...calculatorInputs, dealValue: parseInt(e.target.value)})}
                  className="w-full px-4 py-3 rounded-xl bg-white border border-gray-300 text-gray-900 focus:border-[#6b46c1] focus:ring-2 focus:ring-[#6b46c1]/20 outline-none"
                  placeholder="$8,000"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Referrals per event typically
                </label>
                <input
                  type="range"
                  min="0"
                  max="5"
                  value={calculatorInputs.referralsPerEvent}
                  onChange={(e) => setCalculatorInputs({...calculatorInputs, referralsPerEvent: parseInt(e.target.value)})}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-[#6b46c1]"
                />
                <div className="text-right text-[#6b46c1] font-bold mt-1">{calculatorInputs.referralsPerEvent} referrals</div>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <div className="p-5 rounded-2xl bg-gray-100">
                <div className="text-sm text-gray-600 mb-2">Current Annual Revenue</div>
                <div className="text-2xl font-bold text-gray-900">
                  ${currentRevenue.toLocaleString()}
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-[#6b46c1]/10 border border-[#6b46c1]/20">
                <div className="text-sm text-gray-700 mb-2">With Neon (5 events, 3 referrals avg)</div>
                <div className="text-2xl font-bold text-[#6b46c1]">
                  ${neonRevenue.toLocaleString()}
                </div>
              </div>
            </div>

            <div className="text-center space-y-2 mb-6">
              <div className="text-lg text-gray-700">
                Revenue Increase: <span className="font-bold text-green-600">+${revenueIncrease.toLocaleString()}/year</span>
              </div>
              <div className="text-lg text-gray-700">
                Neon Investment: <span className="font-bold">${neonInvestment.toLocaleString()}/year</span>
              </div>
              <div className="text-3xl font-bold text-[#6b46c1]">
                ROI: {roi}%
              </div>
            </div>

            <motion.button
              className="w-full py-4 rounded-full bg-[#6b46c1] text-white font-medium"
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
          transition={{ delay: 0.8 }}
          className="max-w-6xl mx-auto mb-20"
        >
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
            Join 500+ Professionals Building Businesses Through Experiences
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * idx }}
                whileHover={{ y: -5 }}
                className="p-6 rounded-2xl bg-white/70 backdrop-blur-sm border border-gray-200/50"
              >
                <h3 className="text-lg font-bold mb-1 text-gray-900">{testimonial.name}</h3>
                <p className="text-sm text-[#6b46c1] mb-1">{testimonial.title}</p>
                <p className="text-xs text-gray-500 mb-4">{testimonial.location}</p>
                <p className="text-sm text-gray-700 mb-4 italic">"{testimonial.quote}"</p>
                <div className="flex flex-wrap gap-2">
                  {testimonial.metrics.map((metric, i) => (
                    <span key={i} className="px-3 py-1 rounded-full bg-[#6b46c1]/10 text-xs text-[#6b46c1] font-medium">
                      {metric}
                    </span>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Industry Tabs */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1 }}
          className="max-w-6xl mx-auto mb-20"
        >
          <h2 className="text-3xl font-bold text-center mb-3 text-gray-900">
            Built for How You Work
          </h2>
          <p className="text-gray-600 text-center mb-8">
            Industry-specific templates, compliance, and integrations
          </p>

          <div className="flex flex-wrap justify-center gap-3 mb-8">
            {Object.entries(industries).map(([key, industry]) => (
              <motion.button
                key={key}
                onClick={() => setSelectedIndustry(key)}
                className={`px-5 py-2.5 rounded-full font-medium transition-all text-sm ${
                  selectedIndustry === key
                    ? 'bg-[#6b46c1] text-white'
                    : 'bg-white/60 text-gray-700 hover:bg-white/80'
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {industry.title}
              </motion.button>
            ))}
          </div>

          <AnimatePresence mode="wait">
            <motion.div
              key={selectedIndustry}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="p-8 rounded-3xl bg-white/70 backdrop-blur-sm border border-gray-200/50"
            >
              <h3 className="text-2xl font-bold mb-6 text-gray-900">{industries[selectedIndustry as keyof typeof industries].title}</h3>

              <div className="grid md:grid-cols-2 gap-8 mb-6">
                <div>
                  <h4 className="text-lg font-semibold mb-4 text-[#6b46c1]">Event Templates</h4>
                  <div className="space-y-3">
                    {industries[selectedIndustry as keyof typeof industries].templates.map((template, idx) => (
                      <div key={idx} className="flex justify-between items-center p-3 rounded-xl bg-gray-50">
                        <span className="text-sm text-gray-700">{template.name}</span>
                        <span className="text-sm text-[#6b46c1] font-semibold">{template.price}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-lg font-semibold mb-4 text-[#6b46c1]">Built-In Compliance</h4>
                  <div className="space-y-3">
                    {industries[selectedIndustry as keyof typeof industries].compliance.map((item, idx) => (
                      <div key={idx} className="flex items-start gap-2 p-3 rounded-xl bg-gray-50">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="text-green-600 flex-shrink-0 mt-0.5">
                          <polyline points="20 6 9 17 4 12"/>
                        </svg>
                        <span className="text-sm text-gray-700">{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="mb-6">
                <h4 className="text-lg font-semibold mb-3 text-[#6b46c1]">CRM Integrations</h4>
                <div className="flex flex-wrap gap-2">
                  {industries[selectedIndustry as keyof typeof industries].integrations.map((integration, idx) => (
                    <span key={idx} className="px-4 py-2 rounded-full bg-gray-100 text-sm text-gray-700 font-medium">
                      {integration}
                    </span>
                  ))}
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-[#6b46c1]/10 border border-[#6b46c1]/20">
                <p className="text-gray-700">
                  <span className="font-bold text-[#6b46c1]">📊 </span>
                  {industries[selectedIndustry as keyof typeof industries].stat}
                </p>
              </div>
            </motion.div>
          </AnimatePresence>
        </motion.div>

        {/* Pricing */}
        <motion.div
          id="pricing"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          className="max-w-6xl mx-auto mb-20"
        >
          <h2 className="text-3xl font-bold text-center mb-3 text-gray-900">
            Plans That Grow With Your Business
          </h2>
          <p className="text-gray-600 text-center mb-3">
            No hidden fees. No vendor markups. Cancel anytime.
          </p>
          <p className="text-sm text-gray-500 text-center mb-12">
            Transparent pricing + vendor marketplace access
          </p>

          <div className="grid md:grid-cols-3 gap-8">
            {pricing.map((plan, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * idx }}
                whileHover={{ y: -5 }}
                className={`relative p-8 rounded-3xl border ${
                  plan.popular
                    ? 'bg-[#6b46c1]/5 border-[#6b46c1]/30'
                    : 'bg-white/60 border-gray-200/50'
                }`}
              >
                {plan.badge && (
                  <div className="absolute top-4 right-4 px-3 py-1 rounded-full bg-[#6b46c1] text-white text-xs font-bold">
                    {plan.badge}
                  </div>
                )}

                <h3 className="text-2xl font-bold mb-2 text-gray-900">{plan.name}</h3>
                <div className="mb-6">
                  <span className="text-4xl font-bold text-gray-900">{plan.price}</span>
                  <span className="text-gray-600">{plan.period}</span>
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className="text-[#6b46c1] flex-shrink-0 mt-0.5">
                        <polyline points="20 6 9 17 4 12"/>
                      </svg>
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>

                <motion.button
                  className={`w-full py-3 rounded-full font-medium ${
                    plan.popular
                      ? 'bg-[#6b46c1] text-white'
                      : 'border-2 border-[#6b46c1] text-[#6b46c1]'
                  }`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {plan.cta}
                </motion.button>
              </motion.div>
            ))}
          </div>

          <p className="text-center text-sm text-gray-500 mt-8">
            💰 Average event cost: $800-2,500 (transparent vendor pricing)
          </p>
        </motion.div>

        {/* Final CTA */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.4 }}
          className="max-w-4xl mx-auto text-center mb-20 p-10 rounded-3xl bg-white/70 backdrop-blur-sm border border-[#6b46c1]/20"
        >
          <h2 className="text-3xl font-bold mb-4 text-gray-900">
            Ready to Transform Your Business?
          </h2>
          <p className="text-gray-600 text-lg mb-6">
            Join thousands who trust Festimo Neon
          </p>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
            {[
              { value: '$47K', label: 'Avg revenue increase' },
              { value: '10-15h', label: 'Hours saved per event' },
              { value: '3-5', label: 'Referrals per event' },
              { value: '4.8/5', label: 'User rating' }
            ].map((stat, idx) => (
              <div key={idx} className="text-center">
                <div className="text-2xl font-bold text-[#6b46c1] mb-1">{stat.value}</div>
                <div className="text-xs text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-6">
            <motion.button
              className="px-8 py-4 rounded-full bg-[#6b46c1] text-white font-medium"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Plan Your First Event Free
            </motion.button>
            <motion.button
              className="px-8 py-4 rounded-full border-2 border-[#6b46c1] text-[#6b46c1] font-medium"
              whileHover={{ scale: 1.05, backgroundColor: 'rgba(107, 70, 193, 0.05)' }}
              whileTap={{ scale: 0.95 }}
            >
              Schedule 15-Min Demo
            </motion.button>
          </div>

          <p className="text-sm text-gray-600">
            ✓ 14-day trial • No credit card • Cancel anytime
          </p>
        </motion.div>
      </div>

      {/* Footer */}
      <div className="border-t border-gray-300/50 py-12 bg-white/40">
        <div className="max-w-6xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <h4 className="font-bold mb-3 text-gray-900">Company</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="#" className="hover:text-[#6b46c1]">About Neon</a></li>
                <li><a href="#" className="hover:text-[#6b46c1]">How It Works</a></li>
                <li><a href="#" className="hover:text-[#6b46c1]">Careers</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-3 text-gray-900">Resources</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="#" className="hover:text-[#6b46c1]">Help Center</a></li>
                <li><a href="#" className="hover:text-[#6b46c1]">Tutorials</a></li>
                <li><a href="#" className="hover:text-[#6b46c1]">ROI Calculator</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-3 text-gray-900">Legal</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="#" className="hover:text-[#6b46c1]">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-[#6b46c1]">Terms of Service</a></li>
                <li><a href="#" className="hover:text-[#6b46c1]">Refund Policy</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-3 text-gray-900">Contact</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li>hello@neon.parx.ai</li>
                <li>1-888-NEON-AI</li>
                <li>Chat: Available 24/7</li>
              </ul>
            </div>
          </div>
          <div className="text-center text-sm text-gray-500 pt-8 border-t border-gray-300/50">
            <p>© 2025 Festimo Neon. All rights reserved.</p>
            <p className="mt-2">Rated 4.8/5 stars by 247 professionals</p>
          </div>
        </div>
      </div>
    </div>
  )
}
