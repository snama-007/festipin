export type DemoAgentKey =
  | 'input_classifier'
  | 'theme_agent'
  | 'cake_agent'
  | 'decor_agent'
  | 'balloon_agent'
  | 'venue_agent'
  | 'catering_agent'
  | 'budget_agent'
  | 'vendor_agent'
  | 'planner_agent'

export interface DemoAgentResult {
  agent: DemoAgentKey
  result: Record<string, any>
  summary: string
}

export interface DemoTimelineStep {
  agent: DemoAgentKey
  status: 'running' | 'completed'
  delay: number
}

export type DemoScenarioKey = 'birthday' | 'baby_shower' | 'graduation' | 'milestone_escape'

interface DemoScenarioMetadata {
  city: string
  heroTagline: string
  summary: string
}

interface DemoScenario {
  metadata: DemoScenarioMetadata
  agentResults: Record<DemoAgentKey, DemoAgentResult>
  timeline: DemoTimelineStep[]
}

const birthdayAgents: Record<DemoAgentKey, DemoAgentResult> = {
  input_classifier: {
    agent: 'input_classifier',
    result: {
      source: 'https://instagram.com/p/sparkle-skyline-sweet12',
      highlights: [
        'User dropped an Instagram reel with neon skyline balloons, shimmer photo tunnel, and confetti cannons.',
        'Prompt mentions “sparkly 12th birthday for Zahra” with sleepover lounge and pizza parade.',
        'Notes call out 22 guests, three dietary sensitivities, and a surprise cake reveal.',
      ],
      recommended_next_step: 'Spin up a theme kit and align décor, catering, and venue to the sparkle skyline vibe.',
    },
    summary:
      'Parsed the Instagram reel plus text prompt to capture guest count, must-have visuals, and allergy markers.',
  },
  theme_agent: {
    agent: 'theme_agent',
    result: {
      primary_theme: 'Sparkle Skyline Sweet 12',
      alternative_themes: ['Neon Night Market', 'Glitter City Rooftop', 'Midnight Confetti Bash'],
      palette: ['#FF9BD6', '#FFD166', '#7C3AED', '#38BDF8', '#0F172A'],
      hero_descriptor:
        'A skyline-inspired tween birthday with shimmering tunnels, neon balloon constellations, and a glow lounge.',
    },
    summary: 'Locked a skyline party direction that blends shimmer, neon, and cozy lounge energy for 12-year-olds.',
  },
  cake_agent: {
    agent: 'cake_agent',
    result: {
      recommended_bakeries: [
        {
          name: 'Glow Layer Cake Studio',
          signature: 'Three-tier galaxy glaze cake with skyline sugar panels',
          estimate: '$230 - $310',
        },
        {
          name: 'Confetti Pop Dessert Lab',
          signature: 'Sparkle cupcakes with LED toppers and allergen-friendly minis',
          estimate: '$4.50 per guest',
        },
        {
          name: 'City Slice Patisserie',
          signature: 'Mini cheesecakes with edible disco clouds',
          estimate: '$90 per dozen',
        },
      ],
      flavor_profile: ['vanilla bean confetti', 'strawberry pop rocks', 'salted caramel'],
    },
    summary:
      'Assembled bakeries that deliver dramatic reveals, allergy-friendly minis, and skyline sugar artistry.',
  },
  decor_agent: {
    agent: 'decor_agent',
    result: {
      focal_elements: [
        'Sparkle tunnel entrance with pixel LED curtain and reflective floor panels',
        'Cityscape dessert wall with skyline silhouettes and hanging disco orbs',
        'Tween lounge pods with LED cubes, plush plaid blankets, and faux fireplace projections',
      ],
      diy_tips: [
        'Layer foil drapes over foam board silhouettes for an inexpensive skyline backdrop.',
        'Use portable LED strip lights under stage risers to create floating lounge vibes.',
      ],
    },
    summary:
      'Mapped décor hero moments around tunnel reveals, skyline silhouettes, and cozy tween lounge pods.',
  },
  balloon_agent: {
    agent: 'balloon_agent',
    result: {
      recommended_artists: [
        {
          name: 'Skylit Balloon Atelier',
          specialty: 'Neon balloon constellations and skyline garlands with LED twinkle lines',
          package: 'Entry tunnel + dessert wall cascade; $680 installed',
        },
        {
          name: 'Confetti Loft Collective',
          specialty: 'Ceiling-suspended orb clouds with shimmer tassels',
          package: 'Dance floor feature + selfie corner; $520 installed',
        },
      ],
      quick_win: 'Add dollar-store metallic letters to balloon weights for a skyline street-sign effect.',
    },
    summary:
      'Booked balloon stylists who excel at LED-activated garlands and shimmer-forward dance floor clusters.',
  },
  venue_agent: {
    agent: 'venue_agent',
    result: {
      recommended_venues: [
        {
          name: 'Skyline Studio Loft',
          location: 'Downtown Riverfront',
          capacity: '28 lounge / 40 standing',
          vibe: 'Loft with floor-to-ceiling windows, dance-ready lighting grid, and parents’ mezzanine lounge.',
        },
        {
          name: 'Glowspace Play Lounge',
          location: 'Eastside Arts District',
          capacity: '24 lounge / 50 standing',
          vibe: 'Kid-forward studio with built-in glow flooring, pizza bar, and cinema room.',
        },
      ],
      virtual_tour: 'https://demo.festimo.app/venues/skyline-studio-loft',
    },
    summary:
      'Shortlisted tween-friendly lofts with easy load-in, glow lighting, and parent oversight alcoves.',
  },
  catering_agent: {
    agent: 'catering_agent',
    result: {
      recommended_caterers: [
        {
          name: 'Slice Parade Pizza Co.',
          highlight: 'Glow-in-the-dark pizza boxes, gluten-free and dairy-free pies, synchronized reveal parade',
          logistics: '45-minute set-up, includes pizza captains and allergen labeling.',
        },
        {
          name: "Fizz & Freeze Mocktail Bar",
          highlight: 'Dry-ice mocktails with customizable glitter rims and glow stirrers',
          logistics: 'Self-contained bar cart, 2 mixologists, crush on 4-foot footprint.',
        },
      ],
      menu_pairings: [
        'Color-shift pasta bowls with veggie confetti',
        'Frozen yoghurt pops with berry sparkle dust',
      ],
    },
    summary:
      'Aligned foodie moments to tween energy with pizza parade, glam mocktails, and inclusive dietary coverage.',
  },
  budget_agent: {
    agent: 'budget_agent',
    result: {
      total_budget: {
        min: 3600,
        max: 4700,
        estimated: 4150,
      },
      allocation: [
        { category: 'Venue & Lighting', amount: 1400 },
        { category: 'Décor & Balloons', amount: 1000 },
        { category: 'Culinary & Mocktails', amount: 900 },
        { category: 'Cake & Desserts', amount: 350 },
        { category: 'Activities & Keepsakes', amount: 500 },
      ],
    },
    summary:
      'Balanced loft rental, shimmer décor, and catering with buffers for keepsake boxes and late-night add-ons.',
  },
  vendor_agent: {
    agent: 'vendor_agent',
    result: {
      vendors_by_category: {
        decor: ['Skylit Balloon Atelier', 'Confetti Loft Collective'],
        food: ['Slice Parade Pizza Co.', 'Fizz & Freeze Mocktail Bar'],
        entertainment: ['Neon DJ Nova', 'Glow Photo Booth Co.'],
      },
      contact_strategy:
        'Send a three-point nightly update covering load-in order, allergy updates, and sparkle skyline keywords.',
    },
    summary:
      'Stacked vendors across décor, catering, and entertainment with nightly coordination nudges.',
  },
  planner_agent: {
    agent: 'planner_agent',
    result: {
      final_plan: {
        title: 'Sparkle Skyline Sweet 12 – Birthday Blueprint',
        agenda: [
          { time: '4:30 PM', activity: 'Parent set-up window, lounge styling, balloon rig' },
          { time: '5:45 PM', activity: 'Birthday girl reveal + shimmer tunnel first look' },
          { time: '6:15 PM', activity: 'Pizza parade, mocktail toast, and confetti selfie session' },
          { time: '7:00 PM', activity: 'Games & glow lounge rotations with DJ Nova' },
          { time: '7:45 PM', activity: 'Cake reveal, wishes, and surprise confetti cannons' },
          { time: '8:15 PM', activity: 'Build-your-own sparkle snack favors & parent pick-up' },
        ],
        checklist: [
          'Confirm sparkle tunnel install timing with Skyline Studio Loft management',
          'Review allergy list with Slice Parade and dessert vendors 72 hours prior',
          'Stage confetti cannons and designate adult supervisor for countdown',
          'Prep shimmer favor boxes with glow bracelets, mini journals, and thank-you notes',
        ],
        budget: {
          min: 3600,
          max: 4700,
          estimated: 4150,
          allocation: [
            { category: 'Venue & Lighting', amount: 1400 },
            { category: 'Décor & Balloons', amount: 1000 },
            { category: 'Culinary & Mocktails', amount: 900 },
            { category: 'Cake & Desserts', amount: 350 },
            { category: 'Activities & Keepsakes', amount: 500 },
          ],
        },
        contact_sheet: [
          { name: 'Skyline Studio Loft', role: 'Venue', contact: 'events@skylineloft.com', city: 'Downtown Riverfront' },
          { name: 'Skylit Balloon Atelier', role: 'Balloon Installation', contact: 'hello@skylitatelier.com', city: 'Downtown Riverfront' },
          { name: 'Slice Parade Pizza Co.', role: 'Catering', contact: 'party@sliceparade.com', city: 'Downtown Riverfront' },
        ],
      },
    },
    summary:
      'Sequenced the sparkle skyline celebration from load-in to favors with allergy coverage and parent logistics.',
  },
}

const babyShowerAgents: Record<DemoAgentKey, DemoAgentResult> = {
  input_classifier: {
    agent: 'input_classifier',
    result: {
      source: 'Prompt: “Modern boho baby shower with brunch and pampas in Napa”',
      highlights: [
        'Typed prompt requested a bilingual welcome, build-your-own bouquet bar, and a cozy storytelling nook.',
        'Pinterest board shows neutrals, woven textures, peach florals, and a mama-to-be throne.',
        'Guest list of 32 with 6 kids, plus desires for virtual stream for grandma abroad.',
      ],
      recommended_next_step: 'Shape the modern boho mood and coordinate brunch vendors, décor, and keepsake stations.',
    },
    summary:
      'Ingested the text prompt and Pinterest references to flag décor style, food preferences, and guest flow needs.',
  },
  theme_agent: {
    agent: 'theme_agent',
    result: {
      primary_theme: 'Golden Hour Boho Shower',
      alternative_themes: ['Peach Meadow Brunch', 'Sun-Soaked Pampas Lounge', 'Blush Vineyard Retreat'],
      palette: ['#FCD5CE', '#F8EDEB', '#F1D1B5', '#CDB4DB', '#85603F'],
      hero_descriptor:
        'A Napa-inspired brunch shower with pampas lounges, peach and clay tones, and heartfelt storytelling corners.',
    },
    summary:
      'Translated the boho request into a warm golden-hour palette with tactile textures and welcome rituals.',
  },
  cake_agent: {
    agent: 'cake_agent',
    result: {
      recommended_bakeries: [],
      flavor_profile: [],
      note: 'Dessert table handled by Brunch & Bloom; no standalone cake agent execution required.',
    },
    summary:
      'Skipped dedicated cake sourcing — brunch caterer bundles mini pavlovas and sweets in their package.',
  },
  decor_agent: {
    agent: 'decor_agent',
    result: {
      focal_elements: [
        'Layered pampas throne with rattan loveseat, canopy drape, and floral installation',
        'Storytelling lounge with floor cushions, ambient string lights, and memory jar station',
        'Bouquet bar with vintage bud vases, dried florals, and bilingual signage',
      ],
      diy_tips: [
        'Rent a rattan loveseat and add faux pampas to reduce fresh floral costs.',
        'Repurpose wine crates as risers for brunch buffet height and warmth.',
      ],
    },
    summary:
      'Designed tactile lounges, bouquet stations, and signage moments tuned to the Napa boho aesthetic.',
  },
  balloon_agent: {
    agent: 'balloon_agent',
    result: {
      recommended_artists: [
        {
          name: 'Aerie & Aire Installations',
          specialty: 'Neutral balloon cascades with dried floral accents',
          package: 'Backdrop garland + sweetheart vignette; $540 installed',
        },
        {
          name: 'Peachy Keen Parties',
          specialty: 'Soft ombré arches and bubble trails for entry experience',
          package: 'Entry arch + weaving along buffet; $480 installed',
        },
      ],
      quick_win: 'Clip small dried blooms into balloon knots for an instant boho upgrade.',
    },
    summary:
      'Locked in balloon stylists proficient in neutral palettes, organic shapes, and pampas-safe installs.',
  },
  venue_agent: {
    agent: 'venue_agent',
    result: {
      recommended_venues: [
        {
          name: 'Sunvale Courtyard',
          location: 'Downtown Napa',
          capacity: '40 seated / 60 lounge',
          vibe: 'Outdoor courtyard with pergola, string lights, and indoor salon for backup weather plan.',
        },
        {
          name: 'Harvest Hall Loft',
          location: 'Napa Riverfront',
          capacity: '35 seated / 55 standing',
          vibe: 'Light-filled loft with rustic beams, adjacent tasting room, and livestream-ready Wi-Fi.',
        },
      ],
      virtual_tour: 'https://demo.festimo.app/venues/sunvale-courtyard',
    },
    summary:
      'Recommended venues that pair golden-hour light, indoor rain backup, and streaming-ready infrastructure.',
  },
  catering_agent: {
    agent: 'catering_agent',
    result: {
      recommended_caterers: [
        {
          name: 'Brunch & Bloom Catering',
          highlight: 'Grazing brunch with mini frittatas, citrus salads, and vegan parfait bar',
          logistics: 'Arrives with chefs, ceramic serveware, and bilingual hosts.',
        },
        {
          name: 'Harvest Sparkle Mocktails',
          highlight: 'Zero-proof spritz station with rosemary smoke bubbles and custom name tags',
          logistics: 'Two mixologists, heirloom glassware, and travel within Napa Valley.',
        },
      ],
      menu_pairings: [
        'Lavender honey chicken & waffle bites',
        'Seasonal stone fruit tartlets with oat streusel',
      ],
    },
    summary:
      'Blended brunch comfort foods with photogenic spritz moments and inclusive vegan/gluten-free options.',
  },
  budget_agent: {
    agent: 'budget_agent',
    result: {
      total_budget: {
        min: 4200,
        max: 5600,
        estimated: 4900,
      },
      allocation: [
        { category: 'Venue & Rentals', amount: 1600 },
        { category: 'Catering & Mocktails', amount: 1500 },
        { category: 'Florals & Décor', amount: 900 },
        { category: 'Entertainment & Keepsakes', amount: 500 },
        { category: 'Contingency & Streaming', amount: 400 },
      ],
    },
    summary:
      'Budgeted for brunch hospitality, pampas décor, and a livestream line item with cushion for rain backup.',
  },
  vendor_agent: {
    agent: 'vendor_agent',
    result: {
      vendors_by_category: {
        decor: ['Aerie & Aire Installations', 'Peachy Keen Parties'],
        catering: ['Brunch & Bloom Catering', 'Harvest Sparkle Mocktails'],
        experiences: ['Stories & Strings Harpist', 'Napa Keepsake Studio'],
      },
      contact_strategy:
        'Share a Trello board with bilingual scripts, livestream timeline, and backup weather checklist.',
    },
    summary:
      'Coordinated décor, catering, and storytelling partners with shared bilingual touchpoints and Trello hub.',
  },
  planner_agent: {
    agent: 'planner_agent',
    result: {
      final_plan: {
        title: 'Golden Hour Boho Shower – Brunch Edition',
        agenda: [
          { time: '9:00 AM', activity: 'Vendors arrive, bouquet bar + throne install' },
          { time: '10:30 AM', activity: 'Guests welcomed with spritzes, harp prelude, and sign-in polaroids' },
          { time: '11:00 AM', activity: 'Brunch buffet opens with interactive parfait station' },
          { time: '11:40 AM', activity: 'Storytelling circle with memory jar prompts and live stream' },
          { time: '12:15 PM', activity: 'Game-free keepsake activity: build-a-bouquet + wish tags' },
          { time: '1:00 PM', activity: 'Dessert reveal, thank-you toast, guest departures' },
        ],
        checklist: [
          'Confirm livestream tech run and microphone check 24 hours prior',
          'Distribute bilingual welcome signage and menu cards to vendors',
          'Stage kids’ corner with quiet toys and mini snack packs',
          'Prep keepsake gift bags with custom candles and tea sachets',
        ],
        budget: {
          min: 4200,
          max: 5600,
          estimated: 4900,
          allocation: [
            { category: 'Venue & Rentals', amount: 1600 },
            { category: 'Catering & Mocktails', amount: 1500 },
            { category: 'Florals & Décor', amount: 900 },
            { category: 'Entertainment & Keepsakes', amount: 500 },
            { category: 'Contingency & Streaming', amount: 400 },
          ],
        },
        contact_sheet: [
          { name: 'Sunvale Courtyard', role: 'Venue', contact: 'hello@sunvalecourtyard.com', city: 'Napa, CA' },
          { name: 'Brunch & Bloom Catering', role: 'Catering', contact: 'events@brunchandbloom.com', city: 'Napa, CA' },
          { name: 'Aerie & Aire Installations', role: 'Décor & Balloons', contact: 'studio@aerieaire.com', city: 'Napa, CA' },
        ],
      },
    },
    summary:
      'Sequenced the boho baby shower with brunch flow, livestream support, and tactile keepsakes.',
  },
}

const graduationAgents: Record<DemoAgentKey, DemoAgentResult> = {
  input_classifier: {
    agent: 'input_classifier',
    result: {
      source: 'https://instagram.com/reel/grad-yard-festival',
      highlights: [
        'Instagram reel showed backyard string lights, mini stage, taco truck, and fireworks sparkle sticks.',
        'Prompt requested “Kai’s graduation festival – combine marching band vibes with taco night” for 60 guests.',
        'Checklist mentions college reveal moment, scholarship donors, and parking coordination.',
      ],
      recommended_next_step: 'Design an outdoor celebration plan with timeline, vendor lineup, and budget guardrails.',
    },
    summary:
      'Captured the backyard reel, typed notes, and parking concerns to guide stage, food, and reveal moments.',
  },
  theme_agent: {
    agent: 'theme_agent',
    result: {
      primary_theme: 'Backyard Grad Festival',
      alternative_themes: ['Sunset Stadium Night', 'Grad Street Fair', 'Cheers to Campus Bash'],
      palette: ['#1D4ED8', '#FACC15', '#F3F4F6', '#0F172A', '#DC2626'],
      hero_descriptor:
        'A block-party graduation night with marching band pops, taco trucks, scholarship shout-outs, and sparkle send-off.',
    },
    summary:
      'Framed a festive graduation story balancing school colors, family comfort, and donors’ VIP needs.',
  },
  cake_agent: {
    agent: 'cake_agent',
    result: {
      recommended_bakeries: [
        {
          name: 'Honor Roll Cakes',
          signature: 'Three-tier grad cap cake with edible transcript ribbons',
          estimate: '$260 - $340',
        },
        {
          name: 'Taco & Treat Labs',
          signature: 'Churro cake pops with school-color drizzle',
          estimate: '$3.80 per guest',
        },
        {
          name: 'Stadium Scoop Creamery',
          signature: 'DIY sundae bar with mascot sprinkles and vegan options',
          estimate: '$6 per guest',
        },
      ],
      flavor_profile: ['chocolate tres leches', 'vanilla bean', 'dulce de leche'],
    },
    summary:
      'Activated dessert partners for celebratory visuals, churro flavors, and allergy-friendly sundae bar.',
  },
  decor_agent: {
    agent: 'decor_agent',
    result: {
      focal_elements: [
        'Stage backdrop with LED school logo, string-light canopy, and grad photo collage',
        'VIP donor lounge with bistro tables, heater towers, and branded welcome signage',
        'Memory lane path with timeline milestones and QR code for thank-you notes',
      ],
      diy_tips: [
        'Use foam board and vinyl stickers for quick school logo signage.',
        'Borrow marching band flags to repurpose as entrance markers.',
      ],
    },
    summary:
      'Crafted stage, VIP lounge, and storytelling path to honor grads, donors, and family photo ops.',
  },
  balloon_agent: {
    agent: 'balloon_agent',
    result: {
      recommended_artists: [
        {
          name: 'Grad Gather Installers',
          specialty: 'School-color balloon tunnels with marquee numbers',
          package: 'Entry tunnel + stage accent; $610 installed',
        },
        {
          name: 'Spark Sticks Studio',
          specialty: 'Fire-safe sparkle stick send-off with handheld LED props',
          package: 'Sparkle send-off + photobooth glowing backdrop; $520 installed',
        },
      ],
      quick_win: 'Bundle battery-powered marquee letters for parking direction markers.',
    },
    summary:
      'Brought in balloon and send-off specialists to deliver school-color visuals and safe sparkle moments.',
  },
  venue_agent: {
    agent: 'venue_agent',
    result: {
      recommended_venues: [
        {
          name: 'Riverside Backyard Estate',
          location: 'Northbrook Suburbs',
          capacity: '80 standing / 60 seated',
          vibe: 'Expansive lawn with stage-ready deck, firepit, and onsite parking loop.',
        },
        {
          name: 'Community Arts Amphitheater',
          location: 'Northbrook Town Center',
          capacity: '120 standing / 90 seated',
          vibe: 'Outdoor amphitheater with built-in stage, green rooms, and vendor parking.',
        },
      ],
      virtual_tour: 'https://demo.festimo.app/venues/riverside-backyard-estate',
    },
    summary:
      'Scoped venues with stage capabilities, donor lounge potential, and multi-vehicle load-in access.',
  },
  catering_agent: {
    agent: 'catering_agent',
    result: {
      recommended_caterers: [
        {
          name: 'El Camino Taco Truck',
          highlight: 'Street taco trio with vegan and gluten-free stations',
          logistics: 'Two-truck service, power from generator, setup in 45 minutes.',
        },
        {
          name: 'Bandstand Beverage Co.',
          highlight: 'Lemonade + aguas frescas bar with color-change cups',
          logistics: 'Self-contained bar station, add-on hot cocoa for late-night chill.',
        },
      ],
      menu_pairings: [
        'Street corn cups with cotija crumble and spice bar',
        'Mini slider station for younger siblings and elders',
      ],
    },
    summary:
      'Balanced taco truck flair with inclusive beverage service and comfort-food backups.',
  },
  budget_agent: {
    agent: 'budget_agent',
    result: {
      total_budget: {
        min: 5200,
        max: 6900,
        estimated: 6050,
      },
      allocation: [
        { category: 'Venue & Rentals', amount: 1800 },
        { category: 'Food Trucks & Beverage', amount: 1700 },
        { category: 'Stage, AV & Lighting', amount: 1200 },
        { category: 'Décor & Balloons', amount: 800 },
        { category: 'Celebration Extras', amount: 550 },
      ],
    },
    summary:
      'Budget tracks rentals, food trucks, AV upgrades, and sparkle send-off with donor lounge buffer.',
  },
  vendor_agent: {
    agent: 'vendor_agent',
    result: {
      vendors_by_category: {
        production: ['Grad Gather Installers', 'Spark Sticks Studio'],
        food: ['El Camino Taco Truck', 'Bandstand Beverage Co.'],
        entertainment: ['DJ Campus Beats', 'Marching Line Drum Crew'],
      },
      contact_strategy:
        'Issue a shared Google Sheet with parking schedule, donor shout-out cues, and weather contingency plan.',
    },
    summary:
      'Coordinated production, food, and entertainment teams with shared logistics sheet and parking map.',
  },
  planner_agent: {
    agent: 'planner_agent',
    result: {
      final_plan: {
        title: 'Backyard Grad Festival – Kai’s Celebration',
        agenda: [
          { time: '3:00 PM', activity: 'Set-up window, stage rigging, AV checks' },
          { time: '5:30 PM', activity: 'Donor/VIP pre-reception in lounge' },
          { time: '6:00 PM', activity: 'Guests arrive, lawn games open, taco truck serving' },
          { time: '7:00 PM', activity: 'Scholarship thank-you + college reveal on stage' },
          { time: '7:45 PM', activity: 'Sparkle stick send-off and marching drum interlude' },
          { time: '8:15 PM', activity: 'Dessert bar opens, photo moments, relaxed departures' },
        ],
        checklist: [
          'Confirm permits for fireworks substitutes and amplified sound with township',
          'Assign parking volunteers and donor escorts with reflective vests',
          'Print bilingual signage for taco truck stations and allergen highlights',
          'Set up rain backup plan: tenting quotes + indoor garage lounge',
        ],
        budget: {
          min: 5200,
          max: 6900,
          estimated: 6050,
          allocation: [
            { category: 'Venue & Rentals', amount: 1800 },
            { category: 'Food Trucks & Beverage', amount: 1700 },
            { category: 'Stage, AV & Lighting', amount: 1200 },
            { category: 'Décor & Balloons', amount: 800 },
            { category: 'Celebration Extras', amount: 550 },
          ],
        },
        contact_sheet: [
          { name: 'Riverside Backyard Estate', role: 'Venue', contact: 'events@riversideestate.com', city: 'Northbrook, IL' },
          { name: 'El Camino Taco Truck', role: 'Catering', contact: 'bookings@elcaminotruck.com', city: 'Northbrook, IL' },
          { name: 'Grad Gather Installers', role: 'Décor & Balloon', contact: 'hello@gradgather.com', city: 'Northbrook, IL' },
        ],
      },
    },
    summary:
      'Orchestrated the grad festival from permits to sparkler send-off with donor lounge and college reveal cues.',
  },
}

const milestoneEscapeAgents: Record<DemoAgentKey, DemoAgentResult> = {
  input_classifier: {
    agent: 'input_classifier',
    result: {
      source: 'https://instagram.com/p/40th-baja-escape',
      highlights: [
        'Instagram post shows beachfront dinners, rooftop sunrise yoga, and a private catamaran.',
        'Prompt: “Celebrating Tasha turning 40 – 12 women, Cabo vibes, luxe but relaxed, need spa + nightlife.”',
        'Notes flag flight stagger plans, wellness mornings, and surprise guest speaker.',
      ],
      recommended_next_step: 'Craft a three-day Baja itinerary covering villas, transport, culinary, and celebration moments.',
    },
    summary:
      'Captured the Instagram inspiration and typed prompt to map wellness mornings, nightlife, and travel orchestration.',
  },
  theme_agent: {
    agent: 'theme_agent',
    result: {
      primary_theme: 'Sunset Muse Cabo Escape',
      alternative_themes: ['Desert Glow Retreat', 'Moonstone Beach Club', 'Paloma Nights Getaway'],
      palette: ['#EFB8C8', '#FEEBC8', '#F8FAFC', '#38BDF8', '#0F172A'],
      hero_descriptor:
        'A luxe-yet-playful 40th birthday escape with sunrise rituals, private catamaran, and candlelit beach supper.',
    },
    summary:
      'Balanced wellness mornings and nightlife glitz into a cohesive muse-filled Cabo celebration.',
  },
  cake_agent: {
    agent: 'cake_agent',
    result: {
      recommended_bakeries: [
        {
          name: 'Playa Dulce Atelier',
          signature: 'Champagne guava cake with edible shells and gold leaf',
          estimate: '$320 - $380',
        },
        {
          name: 'Azul Tasting Kitchen',
          signature: 'Late-night churro + mezcal dipping bar',
          estimate: '$9 per guest',
        },
        {
          name: 'Sea Breeze Gelato Cart',
          signature: 'Craft gelato pushcart with boozy paleta add-ons',
          estimate: '$480 flat fee',
        },
      ],
      flavor_profile: ['champagne guava', 'coconut lime', 'dark chocolate mezcal'],
    },
    summary:
      'Lined up dessert partners for luxe cake cutting, rooftop churro station, and refreshing gelato moments.',
  },
  decor_agent: {
    agent: 'decor_agent',
    result: {
      focal_elements: [
        'Sunset beach supper table with driftwood candelabras and personalized place cards',
        'Rooftop champagne lounge with low seating, projection art, and custom scent diffuser',
        'Wellness deck styling: woven mats, iced eucalyptus towels, and tonal parasols',
      ],
      diy_tips: [
        'Pack lightweight silk runners and napkin rings to elevate resort tables quickly.',
        'Use local markets for ceramic votives and palm fans as favors.',
      ],
    },
    summary:
      'Curated décor for wellness mornings, rooftop lounges, and beachfront dinners using packable accents.',
  },
  balloon_agent: {
    agent: 'balloon_agent',
    result: {
      recommended_artists: [
        {
          name: 'Luna Baja Installations',
          specialty: 'Sea breeze-proof balloon cabanas with woven fringe',
          package: 'Beach lounge feature + rooftop accent; $820 installed',
        },
        {
          name: 'Glow Marina Collective',
          specialty: 'LED balloon floats for catamaran sail',
          package: 'Catamaran rail décor + deck photo corner; $560 installed',
        },
      ],
      quick_win: 'Travel with satin ribbon sets to tie around venue lanterns for cohesive palette.',
    },
    summary:
      'Booked coastal teams adept at wind-proof installs and LED accents for yacht sail moments.',
  },
  venue_agent: {
    agent: 'venue_agent',
    result: {
      recommended_venues: [
        {
          name: 'Casa Miramar Villas',
          location: 'San José del Cabo',
          capacity: '12 lodging / 40 event',
          vibe: 'Three connected villas with infinity pool, private chef kitchen, and concierge.',
        },
        {
          name: 'Mar Azul Beach Club',
          location: 'Cabo Corridor',
          capacity: '60 seated / 80 lounge',
          vibe: 'Private beach deck with fire bowls, sound system, and dedicated spa cabanas.',
        },
      ],
      virtual_tour: 'https://demo.festimo.app/venues/casa-miramar-villas',
    },
    summary:
      'Matched villas and beach club spaces offering privacy, spa tie-ins, and event-friendly policies.',
  },
  catering_agent: {
    agent: 'catering_agent',
    result: {
      recommended_caterers: [],
      menu_pairings: [],
      note: 'Villa concierge pre-booked private chef and mixology teams — dedicated catering agent not dispatched.',
    },
    summary:
      'No separate catering search required; concierge locked chefs and bar program before the agent workflow began.',
  },
  budget_agent: {
    agent: 'budget_agent',
    result: {
      total_budget: {
        min: 13400,
        max: 16800,
        estimated: 15200,
      },
      allocation: [
        { category: 'Villas & Venues', amount: 6200 },
        { category: 'Culinary & Mixology', amount: 4200 },
        { category: 'Experiences & Excursions', amount: 2500 },
        { category: 'Décor & Styling', amount: 1500 },
        { category: 'Travel Cushion & Tips', amount: 800 },
      ],
    },
    summary:
      'Budget layers villa rental, private chefs, catamaran charter, and contingency for travel buffers.',
  },
  vendor_agent: {
    agent: 'vendor_agent',
    result: {
      vendors_by_category: {
        hospitality: ['Casa Miramar Concierge', 'Chef Valeria Collective'],
        experiences: ['Glow Marina Collective', 'Baja Sound Bath Guides'],
        nightlife: ['Paloma Nights Mixology', 'DJ Solara'],
      },
      contact_strategy:
        'Daily WhatsApp digest covering flight arrivals, spa schedules, and nightlife dress codes with shared Google Drive.',
    },
    summary:
      'Rallied concierge, chef, wellness, and nightlife partners around a shared daily digest.',
  },
  planner_agent: {
    agent: 'planner_agent',
    result: {
      final_plan: {
        title: 'Sunset Muse Cabo Escape – Tasha’s 40th',
        agenda: [
          { time: 'Day 1 — 2:00 PM', activity: 'Arrivals, welcome paletas, villa check-in' },
          { time: 'Day 1 — 6:30 PM', activity: 'Rooftop champagne lounge + guest storyteller surprise' },
          { time: 'Day 2 — 8:00 AM', activity: 'Sunrise yoga and wellness breakfast bar' },
          { time: 'Day 2 — 1:00 PM', activity: 'Private catamaran sail with LED sunset toast' },
          { time: 'Day 2 — 8:00 PM', activity: 'Beach supper with live acoustic set and cake reveal' },
          { time: 'Day 3 — 10:00 AM', activity: 'Spa cabana rotation + farewell brunch' },
        ],
        checklist: [
          'Finalize airport transfers and flight stagger spreadsheet for concierge',
          'Confirm yacht manifest with passport scans 72 hours prior',
          'Arrange spa menu selections and treatment schedule per guest',
          'Pack emergency décor kit: runners, candles, signage, gifting notes',
        ],
        budget: {
          min: 13400,
          max: 16800,
          estimated: 15200,
          allocation: [
            { category: 'Villas & Venues', amount: 6200 },
            { category: 'Culinary & Mixology', amount: 4200 },
            { category: 'Experiences & Excursions', amount: 2500 },
            { category: 'Décor & Styling', amount: 1500 },
            { category: 'Travel Cushion & Tips', amount: 800 },
          ],
        },
        contact_sheet: [
          { name: 'Casa Miramar Concierge', role: 'Villa Operations', contact: 'host@casamiramar.mx', city: 'San José del Cabo' },
          { name: 'Chef Valeria Collective', role: 'Culinary Team', contact: 'hola@chefvaleria.mx', city: 'Cabo, Mexico' },
          { name: 'Glow Marina Collective', role: 'Excursions', contact: 'sail@glowmarina.mx', city: 'Cabo, Mexico' },
        ],
      },
    },
    summary:
      'Threaded the 40th celebration across villas, yacht, and spa with daily communications and surprise moments.',
  },
}

const timelinePatterns = [
  { running: 600, completed: 800 },
  { running: 600, completed: 900 },
  { running: 500, completed: 900 },
  { running: 400, completed: 700 },
  { running: 500, completed: 850 }
]

const buildTimeline = (agents: DemoAgentKey[]): DemoTimelineStep[] =>
  agents.flatMap((agent, index) => {
    const pattern = timelinePatterns[index % timelinePatterns.length]
    return [
      { agent, status: 'running', delay: pattern.running },
      { agent, status: 'completed', delay: pattern.completed }
    ]
  })

const birthdayTimeline = buildTimeline([
  'input_classifier',
  'theme_agent',
  'cake_agent',
  'decor_agent',
  'balloon_agent',
  'venue_agent',
  'catering_agent',
  'budget_agent',
  'vendor_agent',
  'planner_agent'
])

const babyShowerTimeline = buildTimeline([
  'input_classifier',
  'theme_agent',
  'decor_agent',
  'balloon_agent',
  'venue_agent',
  'catering_agent',
  'budget_agent',
  'vendor_agent',
  'planner_agent'
])

const graduationTimeline = buildTimeline([
  'input_classifier',
  'theme_agent',
  'decor_agent',
  'balloon_agent',
  'venue_agent',
  'catering_agent',
  'cake_agent',
  'budget_agent',
  'vendor_agent',
  'planner_agent'
])

const milestoneEscapeTimeline = buildTimeline([
  'input_classifier',
  'theme_agent',
  'cake_agent',
  'decor_agent',
  'venue_agent',
  'balloon_agent',
  'budget_agent',
  'vendor_agent',
  'planner_agent'
])

export const demoScenarios: Record<DemoScenarioKey, DemoScenario> = {
  birthday: {
    metadata: {
      city: 'Downtown Riverfront',
      heroTagline: 'Instagram sparkle reel → tween birthday master plan',
      summary: 'Shows how a single reel becomes a full shimmer-forward birthday blueprint.',
    },
    agentResults: birthdayAgents,
    timeline: birthdayTimeline,
  },
  baby_shower: {
    metadata: {
      city: 'Napa Valley',
      heroTagline: 'Typed prompt → golden-hour baby shower brunch',
      summary: 'Walks through brunch hospitality, pampas décor, and bilingual keepsakes.',
    },
    agentResults: babyShowerAgents,
    timeline: babyShowerTimeline,
  },
  graduation: {
    metadata: {
      city: 'Northbrook Suburbs',
      heroTagline: 'Instagram backyard inspo → grad festival game plan',
      summary: 'Covers taco trucks, donor lounges, and sparkle send-offs in minutes.',
    },
    agentResults: graduationAgents,
    timeline: graduationTimeline,
  },
  milestone_escape: {
    metadata: {
      city: 'San José del Cabo',
      heroTagline: 'Reel + prompt → luxe 40th milestone escape',
      summary: 'Blends wellness mornings, catamaran nights, and concierge comms for 12 best friends.',
    },
    agentResults: milestoneEscapeAgents,
    timeline: milestoneEscapeTimeline,
  },
}

export const defaultScenarioKey: DemoScenarioKey = 'birthday'
