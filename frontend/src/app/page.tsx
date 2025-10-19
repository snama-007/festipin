'use client'

import Link from 'next/link'
import Image from 'next/image'
import { motion } from 'framer-motion'

import FestimoLogo from './assets/festimologo.png'
import HeroBackgroundImage from './assets/blue-pink-gradient-smoke-dark-room.jpg'

const TRUST_LOGOS = ['Domino’s Events', 'Chromatic Clouds', 'Aurora Loft', 'Neon Collective', 'SkyShield Ops']

const CORE_PILLARS = [
  {
    title: 'Launch-ready agent orchestration',
    blurb:
      'From household milestones to global launches, Festimo agents interpret inspiration, map budgets, and deliver production-ready plans in under a minute.'
  },
  {
    title: 'Vendor onboarding without churn',
    blurb:
      'Smart briefs, compliance collection, and readiness tracking keep stylists, caterers, and venues aligned—no spreadsheets or endless threads.'
  },
  {
    title: 'Privacy-first collaboration',
    blurb:
      'Unify chat, files, and approvals with role-based visibility. SOC2-ready auditing protects every conversation from living-room surprise parties to enterprise launches.'
  }
]

const USE_CASES = [
  {
    title: 'Household celebrations',
    description:
      'Birthday bashes, baby showers, backyard grad nights. Festimo choreographs décor, catering, and keepsakes without losing the magic.',
    image:
      'https://img.freepik.com/free-photo/boho-style-picnic-table-with-floral-arrangement_53876-138181.jpg?t=st=1732110000~exp=1732113600~hmac=5b37ddaa7931027dcd0e96a1b031458900d7e42dd010dc17ff48b72d70ac8f0a&w=1800'
  },
  {
    title: 'Immersive brand activations',
    description:
      'Projection-mapped story worlds, pop-up retail, touring roadshows. Festimo Neon pods plug in when you need enterprise firepower.',
    image:
      'https://img.freepik.com/free-photo/futuristic-stage-with-glowing-lights_23-2150904087.jpg?t=st=1732110000~exp=1732113600~hmac=d7d5fdd3f0f8d0ba26ff7d7a1c8d0b6bb56c9a5f1c03d9c332ab6c108747fa09&w=1800'
  },
  {
    title: 'Corporate hospitality & launches',
    description:
      'Executive summits, new-product reveals, tech conferences. Orchestrate guest journeys, vendor pods, and security with one OS.',
    image:
      'https://img.freepik.com/free-photo/nightclub-with-purple-neon-lights_155003-11439.jpg?t=st=1732110000~exp=1732113600~hmac=68c65a06f6ad1fc9d6d3015f3fa7cf0b079f8c91332cd85ac0a8c0f761ef58cd&w=1800'
  }
]

const FLOW_STEPS = [
  {
    step: '01',
    title: 'Drop inspiration',
    blurb: 'Share a Pinterest link, typed prompt, or vendor notes. Festimo agents parse the context instantly.'
  },
  {
    step: '02',
    title: 'Agents assemble',
    blurb: 'Theme, décor, vendor, budget, and planner agents collaborate live to draft a holistic celebration plan.'
  },
  {
    step: '03',
    title: 'Vendors onboard',
    blurb:
      'Invite stylists, caterers, venues, and Neon producers. Each partner gets task-specific briefs with privacy controls.'
  },
  {
    step: '04',
    title: 'Guests & ops in sync',
    blurb:
      'Integrated RSVPs, live comms, and readiness dashboards keep household hosts and corporate producers perfectly aligned.'
  }
]

const METRICS = [
  { label: 'Household parties launched', value: '12K+' },
  { label: 'Global activations powered', value: '2.1K' },
  { label: 'Vendors onboarded', value: '18K+' },
  { label: 'Average plan delivery', value: '58 sec' }
]

const BENEFITS = [
  {
    label: 'Integrated RSVP & invitations',
    blurb: 'Send branded invites, capture preferences, and feed every update straight into agent workflows.'
  },
  {
    label: 'On-demand Neon B2B services',
    blurb: 'Need an enterprise pop-up or touring activation? Neon pods deliver the build while you keep the OS.'
  },
  {
    label: 'Household party perfection',
    blurb:
      'Birthday bashes, baby showers, backyard grad nights—Festimo coordinates décor, catering, and keepsakes without missing a beat.'
  },
  {
    label: 'Unified data privacy',
    blurb: 'SOC2-ready auditing, granular access controls, and secure vendor portals keep sensitive plans protected.'
  },
  {
    label: 'Real-time health pulses',
    blurb: 'Know who’s blocked, what’s over budget, and which moment needs extra love—right from the control room.'
  }
]

const CTA_BACKGROUND =
  'url("https://img.freepik.com/free-photo/glitter-golden-confetti-with-copy-space_23-2150448833.jpg")'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[#05020F] text-white">
      <div
        className="absolute inset-0 -z-10 bg-cover bg-center opacity-40"
        style={{ backgroundImage: `url(${HeroBackgroundImage.src})` }}
      />
      <motion.div
        aria-hidden="true"
        className="pointer-events-none absolute -top-40 left-1/2 h-[38rem] w-[38rem] -translate-x-1/2 rounded-full bg-[radial-gradient(circle,_rgba(104,62,255,0.55),_transparent_60%)] blur-3xl"
        animate={{ opacity: [0.5, 0.8, 0.5], scale: [1, 1.08, 1] }}
        transition={{ duration: 18, repeat: Infinity, repeatType: 'mirror', ease: 'easeInOut' }}
      />
      <motion.div
        aria-hidden="true"
        className="pointer-events-none absolute bottom-[-12rem] right-[-8rem] h-[30rem] w-[30rem] rounded-full bg-[radial-gradient(circle,_rgba(0,204,255,0.35),_transparent_70%)] blur-3xl"
        animate={{ opacity: [0.4, 0.65, 0.4], scale: [1, 1.12, 1] }}
        transition={{ duration: 20, repeat: Infinity, repeatType: 'mirror', ease: 'easeInOut' }}
      />

      <div className="relative mx-auto flex w-full max-w-6xl flex-col gap-24 px-6 pb-28 pt-16 lg:gap-28 lg:px-12">
        {/* Hero */}
        <header className="grid gap-12 lg:grid-cols-[1.05fr,0.95fr] lg:items-center">
          <div className="space-y-8 text-center lg:text-left">
            <motion.div
              initial={{ opacity: 0, y: -12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
              className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/5 px-4 py-1 text-xs font-semibold uppercase tracking-[0.35em] text-white/70 backdrop-blur-md"
            >
              Festimo Platform
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-gradient-to-r from-pink-400 to-purple-500" />
            </motion.div>
            <motion.h1
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
              className="text-balance text-[3.4rem] font-semibold leading-[1.05] text-white sm:text-[4.4rem]"
            >
              The celebration OS.
              <span className="block text-[2.2rem] font-medium text-white/70 sm:text-[2.5rem]">
                Party planning, from living-room legends to global launches, synced in one timeline.
              </span>
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
              className="mx-auto max-w-2xl text-pretty text-base text-white/70 lg:mx-0"
            >
              Let agents choreograph the work while you focus on experience design. Household hosts, corporate producers, and
              Neon B2B pods stay in flow with Festimo.
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
              className="flex flex-col gap-3 sm:flex-row sm:justify-start sm:gap-4"
            >
              <Link
                href="/demo"
                className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 px-8 py-3 text-sm font-semibold text-white shadow-[0_20px_60px_rgba(168,85,247,0.35)] transition-transform duration-300 hover:-translate-y-0.5"
              >
                Launch live demo
              </Link>
              <Link
                href="/neon"
                className="inline-flex items-center justify-center rounded-full border border-white/30 bg-white/10 px-8 py-3 text-sm font-semibold text-white/85 transition-colors duration-300 hover:border-white/60 hover:text-white"
              >
                Talk to Neon B2B
              </Link>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.35, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
              className="grid grid-cols-2 gap-3 rounded-3xl border border-white/10 bg-white/5 p-4 text-left text-xs text-white/70 backdrop-blur-lg sm:grid-cols-4"
            >
              {METRICS.map(metric => (
                <div key={metric.label} className="rounded-2xl bg-white/5 px-4 py-3">
                  <p className="text-lg font-semibold text-white">{metric.value}</p>
                  <p>{metric.label}</p>
                </div>
              ))}
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0, scale: 0.94 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2, duration: 0.6, ease: [0.18, 1, 0.3, 1] }}
            className="relative mx-auto flex w-full max-w-md flex-col gap-5 rounded-[3rem] border border-white/15 bg-white/5 p-6 text-sm text-white/75 backdrop-blur-xl"
          >
            <div className="relative flex items-center justify-center rounded-[2.5rem] border border-white/20 bg-white/85 px-6 py-4 shadow-[0_22px_60px_rgba(168,85,247,0.25)]">
              <Image
                src={FestimoLogo}
                alt="Festimo logo"
                priority
                className="h-16 w-16 rounded-2xl border border-white/60 bg-white p-3"
              />
              <div className="ml-4 text-left text-sm text-[#1f1037]">
                <p className="text-xs font-semibold uppercase tracking-[0.3em] text-[#6f4ed4]">Mission</p>
                <p className="text-base font-semibold">Celebrate brilliantly, skip the chaos.</p>
              </div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-xs uppercase tracking-[0.3em] text-white/50">Real-time activity</p>
              <ul className="mt-3 space-y-3">
                <li className="flex items-start justify-between">
                  <span>Household birthday · décor finalized</span>
                  <span className="text-white/50">2m ago</span>
                </li>
                <li className="flex items-start justify-between">
                  <span>Neon pop-up · vendor onboarding complete</span>
                  <span className="text-white/50">9m ago</span>
                </li>
                <li className="flex items-start justify-between">
                  <span>Corporate summit · guest RSVP sync</span>
                  <span className="text-white/50">14m ago</span>
                </li>
              </ul>
            </div>
          </motion.div>
        </header>

        {/* Trust logos */}
        <section className="space-y-10">
          <p className="text-center text-xs font-semibold uppercase tracking-[0.35em] text-white/50">
            Trusted by celebration operators across the globe
          </p>
          <div className="flex flex-wrap items-center justify-center gap-x-8 gap-y-4 text-sm font-semibold text-white/60">
            {TRUST_LOGOS.map(name => (
              <span key={name} className="uppercase tracking-[0.25em]">
                {name}
              </span>
            ))}
          </div>
        </section>

        {/* Pillars */}
        <section className="grid gap-6 lg:grid-cols-3">
          {CORE_PILLARS.map(pillar => (
            <motion.article
              key={pillar.title}
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-80px' }}
              transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
              className="relative overflow-hidden rounded-3xl border border-white/10 bg-white/5 p-6 text-sm text-white/75 backdrop-blur-lg"
            >
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-white">{pillar.title}</h3>
                <p className="leading-relaxed">{pillar.blurb}</p>
              </div>
            </motion.article>
          ))}
        </section>

        {/* Use cases */}
        <section className="grid gap-6 lg:grid-cols-3">
          {USE_CASES.map(card => (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-80px' }}
              transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
              className="group relative overflow-hidden rounded-3xl border border-white/15 shadow-[0_32px_90px_rgba(10,10,25,0.55)]"
            >
              <div
                className="h-[220px] w-full bg-cover bg-center transition-transform duration-500 group-hover:scale-105"
                style={{ backgroundImage: `url(${card.image})` }}
              />
              <div className="space-y-2 bg-[#101231]/80 px-6 py-5 backdrop-blur-xl">
                <h3 className="text-lg font-semibold">{card.title}</h3>
                <p className="text-sm text-white/70">{card.description}</p>
              </div>
            </motion.div>
          ))}
          <p className="text-xs text-center text-white/40 lg:col-span-3">
            Visual mood references courtesy of Freepik creators.
          </p>
        </section>

        {/* How it works */}
        <section className="grid gap-8 lg:grid-cols-[0.9fr,1.1fr] lg:items-center">
          <div className="space-y-5 text-center lg:text-left">
            <h2 className="text-2xl font-semibold text-white sm:text-3xl">How Festimo coordinates the party</h2>
            <p className="text-sm text-white/70 sm:text-base">
              Agents orchestrate the work, vendors execute with clarity, and guests enjoy seamless experiences. Household or
              enterprise—same rhythm, same control room.
            </p>
            <div className="grid gap-3">
              {FLOW_STEPS.slice(0, 2).map(item => (
                <div
                  key={item.step}
                  className="rounded-2xl border border-white/10 bg-white/5 px-4 py-4 text-left text-sm text-white/75 backdrop-blur-md transition-all duration-300 hover:border-white/40"
                >
                  <p className="text-xs font-semibold uppercase tracking-[0.3em] text-white/55">{item.step}</p>
                  <p className="mt-2 text-base font-semibold text-white">{item.title}</p>
                  <p className="mt-1 text-xs leading-relaxed text-white/60">{item.blurb}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            {FLOW_STEPS.slice(2).map(item => (
              <motion.div
                key={item.step}
                initial={{ opacity: 0, x: 40 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, margin: '-120px' }}
                transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
                className="rounded-3xl border border-white/10 bg-white/5 px-5 py-5 text-left text-sm text-white/75 backdrop-blur-lg"
              >
                <p className="text-xs font-semibold uppercase tracking-[0.3em] text-white/55">{item.step}</p>
                <p className="mt-2 text-base font-semibold text-white">{item.title}</p>
                <p className="mt-1 text-xs leading-relaxed text-white/60">{item.blurb}</p>
              </motion.div>
            ))}
          </div>
        </section>

        {/* Benefits */}
        <section className="grid gap-3 text-sm text-white/75 sm:grid-cols-2">
          {FLOW_STEPS &&
            FLOW_STEPS.length > 0 &&
            BENEFITS.map(item => (
              <div
                key={item.label}
                className="rounded-2xl border border-white/10 bg-white/5 px-4 py-4 backdrop-blur-lg transition-all duration-300 hover:border-white/40"
              >
                <p className="text-base font-semibold text-white">{item.label}</p>
                <p className="mt-1 text-xs leading-relaxed text-white/60">{item.blurb}</p>
              </div>
            ))}
        </section>

        {/* CTA */}
        <section
          className="relative overflow-hidden rounded-[2.75rem] border border-white/15 px-8 py-10 text-center shadow-[0_35px_120px_rgba(168,85,247,0.38)]"
          style={{
            backgroundImage: `linear-gradient(120deg, rgba(168,85,247,0.88), rgba(236,72,153,0.78)), ${CTA_BACKGROUND}`,
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        >
          <motion.div
            className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(255,255,255,0.15),_transparent_55%)]"
            animate={{ opacity: [0.4, 0.6, 0.4] }}
            transition={{ duration: 12, repeat: Infinity, repeatType: 'mirror' }}
          />
          <div className="relative space-y-5">
            <p className="text-xs font-semibold uppercase tracking-[0.35em] text-white/70">Get started</p>
            <h2 className="text-3xl font-semibold text-white sm:text-4xl">
              Ready to orchestrate celebrations at the speed of inspiration?
            </h2>
            <p className="mx-auto max-w-2xl text-sm text-white/80">
              Launch the live demo, invite your vendors, and let Festimo’s agents carry the workload. Neon B2B is on-call when
              you need the big guns.
            </p>
            <div className="flex flex-col items-center justify-center gap-3 sm:flex-row sm:gap-4">
              <Link
                href="/demo"
                className="inline-flex items-center justify-center rounded-full bg-white px-8 py-3 text-sm font-semibold text-purple-600 shadow-[0_18px_55px_rgba(255,255,255,0.45)] transition-transform duration-300 hover:-translate-y-0.5"
              >
                Run live demo
              </Link>
              <Link
                href="/build"
                className="inline-flex items-center justify-center rounded-full border border-white/40 bg-white/10 px-8 py-3 text-sm font-semibold text-white/85 transition-colors duration-300 hover:border-white/70 hover:text-white"
              >
                Explore workspace
              </Link>
            </div>
          </div>
        </section>

        <footer className="flex flex-col items-center gap-4 pb-10 text-xs text-white/40 sm:flex-row sm:justify-between">
          <span>© {new Date().getFullYear()} Festimo · The celebration operating system.</span>
          <div className="flex items-center gap-5">
            <Link href="/dev" className="transition-colors hover:text-white/70">
              Developer mode
            </Link>
            <Link href="/motif" className="transition-colors hover:text-white/70">
              Motif creative kit
            </Link>
            <Link href="/neon" className="transition-colors hover:text-white/70">
              Neon services
            </Link>
          </div>
        </footer>
      </div>
    </div>
  )
}
