# 🎉 Festimo Agent Orchestration - Detailed Execution Flow

## 🔄 Complete System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    FESTIMO PARTY PLANNING SYSTEM                               │
│                                        Agent Orchestration Flow                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: INPUT PROCESSING & DATA EXTRACTION                                                  │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  User Input ──┐                                                                                │
│               │                                                                                │
│  ┌─────────────▼─────────────┐                                                                 │
│  │   Input Sources           │                                                                 │
│  │  • Text: "Sarah's 5th     │                                                                 │
│  │    birthday party..."     │                                                                 │
│  │  • Image: Party photo     │                                                                 │
│  │  • URL: Pinterest link    │                                                                 │
│  └───────────────────────────┘                                                                 │
│               │                                                                                │
│               ▼                                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐   │
│  │                    LANGGRAPH DATA EXTRACTION WORKFLOW                                  │   │
│  │                                                                                         │   │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                   │   │
│  │  │ 1. validate_input│───►│ 2. extract_     │───►│ 3. extract_     │                   │   │
│  │  │                 │    │    basic_info    │    │    event_       │                   │   │
│  │  │ • Party content │    │                 │    │    details      │                   │   │
│  │  │   validation    │    │ • Event type    │    │                 │                   │   │
│  │  │ • Input format   │    │ • Age detection │    │ • Guest count   │                   │   │
│  │  │   check          │    │ • Theme recog.  │    │ • Budget range  │                   │   │
│  │  │ • Error handling │    │ • Honoree name │    │ • Food prefs    │                   │   │
│  │  └─────────────────┘    └─────────────────┘    │ • Activities   │                   │   │
│  │                                                 │ • Location     │                   │   │
│  │                                                 └─────────────────┘                   │   │
│  │                                                           │                             │   │
│  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                   │   │
│  │  │ 4. extract_      │◄───│ 5. calculate_   │◄───│ 6. generate_    │                   │   │
│  │  │    logistics     │    │    confidence   │    │    suggestions   │                   │   │
│  │  │                 │    │                 │    │                 │                   │   │
│  │  │ • Date parsing  │    │ • Field complete│    │ • Missing fields│                   │   │
│  │  │ • Time extract. │    │   scoring       │    │   identification│                   │   │
│  │  │ • RSVP deadlines│    │ • User input    │    │ • Contextual    │                   │   │
│  │  │                 │    │   requirement   │    │   prompts       │                   │   │
│  │  └─────────────────┘    └─────────────────┘    └─────────────────┘                   │   │
│  └─────────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                                 │
│  Extraction Result:                                                                             │
│  • eventType: "Birthday" ✓                                                                      │
│  • theme: "Unicorn" ✓                                                                          │
│  • age: 5 ✓                                                                                     │
│  • guestCount: {adults: 12, kids: 8} ✓                                                         │
│  • budget: {min: 5, max: 7} ✓                                                                  │
│  • date: ❌ MISSING                                                                             │
│  • location: ❌ MISSING                                                                         │
│  • foodPreference: ❌ MISSING                                                                   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│  PHASE 2: DYNAMIC FORM GENERATION & USER INPUT COLLECTION                                      │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  Missing Fields ──┐                                                                             │
│                   │                                                                             │
│  ┌────────────────▼────────────────┐                                                          │
│  │     Frontend Form Builder        │                                                          │
│  │                                  │                                                          │
│  │  ┌─────────────────────────────┐│                                                          │
│  │  │  Dynamic Input Fields       ││                                                          │
│  │  │                             ││                                                          │
│  │  │  📅 Date Picker             ││                                                          │
│  │  │  🏠 Location Selector       ││                                                          │
│  │  │  🍽️ Food Preference         ││                                                          │
│  │  │  💰 Budget Range            ││                                                          │
│  │  │  👥 Guest Count             ││                                                          │
│  │  └─────────────────────────────┘│                                                          │
│  │                                  │                                                          │
│  │  ┌─────────────────────────────┐│                                                          │
│  │  │  Field Configuration        ││                                                          │
│  │  │                             ││                                                          │
│  │  │  • Labels & Placeholders    ││                                                          │
│  │  │  • Validation Rules         ││                                                          │
│  │  │  • Input Types              ││                                                          │
│  │  │  • Options Lists            ││                                                          │
│  │  └─────────────────────────────┘│                                                          │
│  └──────────────────────────────────┘                                                          │
│                   │                                                                             │
│                   ▼                                                                             │
│  User Completes Form ──► Complete Event Data                                                   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│  PHASE 3: AGENT ORCHESTRATION & PARTY PLAN GENERATION                                           │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  Complete Event Data ──┐                                                                        │
│                        │                                                                        │
│  ┌─────────────────────▼─────────────────────┐                                                │
│  │     Simple Orchestrator                    │                                                │
│  │                                             │                                                │
│  │  ┌─────────────────────────────────────┐   │                                                │
│  │  │ 1. Create Event State               │   │                                                │
│  │  │    • Initialize workflow            │   │                                                │
│  │  │    • Store in memory                │   │                                                │
│  │  │    • Generate event ID              │   │                                                │
│  │  └─────────────────────────────────────┘   │                                                │
│  │                                             │                                                │
│  │  ┌─────────────────────────────────────┐   │                                                │
│  │  │ 2. Execute Agents Sequentially      │   │                                                │
│  │  │                                     │   │                                                │
│  │  │  🎨 Theme Agent ──┐                 │   │                                                │
│  │  │  ├─ Theme validation               │   │                                                │
│  │  │  ├─ Color palette selection         │   │                                                │
│  │  │  ├─ Style recommendations          │   │                                                │
│  │  │  └─ Mood assessment                │   │                                                │
│  │  │                                     │   │                                                │
│  │  │  🏢 Venue Agent ──┐                 │   │                                                │
│  │  │  ├─ Location analysis              │   │                                                │
│  │  │  ├─ Capacity matching              │   │                                                │
│  │  │  ├─ Amenity requirements           │   │                                                │
│  │  │  └─ Booking recommendations        │   │                                                │
│  │  │                                     │   │                                                │
│  │  │  🎂 Cake Agent ──┐                 │   │                                                │
│  │  │  ├─ Design selection               │   │                                                │
│  │  │  ├─ Flavor recommendations         │   │                                                │
│  │  │  ├─ Size calculation               │   │                                                │
│  │  │  └─ Dietary considerations         │   │                                                │
│  │  │                                     │   │                                                │
│  │  │  🎪 Decoration Agent ──┐           │   │                                                │
│  │  │  ├─ Theme implementation          │   │                                                │
│  │  │  ├─ Color coordination             │   │                                                │
│  │  │  ├─ Supplier recommendations       │   │                                                │
│  │  │  └─ Setup timeline                │   │                                                │
│  │  │                                     │   │                                                │
│  │  │  🎭 Entertainment Agent ──┐        │   │                                                │
│  │  │  ├─ Activity selection            │   │                                                │
│  │  │  ├─ Performer booking             │   │                                                │
│  │  │  ├─ Equipment needs               │   │                                                │
│  │  │  └─ Schedule planning            │   │                                                │
│  │  │                                     │   │                                                │
│  │  │  🍽️ Catering Agent ──┐            │   │                                                │
│  │  │  ├─ Menu planning                 │   │                                                │
│  │  │  ├─ Dietary accommodations        │   │                                                │
│  │  │  ├─ Quantity calculation          │   │                                                │
│  │  │  └─ Service coordination          │   │                                                │
│  │  │                                     │   │                                                │
│  │  │  ⏰ Timeline Agent ──┐             │   │                                                │
│  │  │  ├─ Event scheduling              │   │                                                │
│  │  │  ├─ Setup requirements            │   │                                                │
│  │  │  ├─ Vendor coordination           │   │                                                │
│  │  │  └─ Contingency planning          │   │                                                │
│  │  │                                     │   │                                                │
│  │  │  💰 Budget Agent ──┐               │   │                                                │
│  │  │  ├─ Cost optimization             │   │                                                │
│  │  │  ├─ Vendor comparison             │   │                                                │
│  │  │  ├─ Budget allocation             │   │                                                │
│  │  │  └─ Savings recommendations       │   │                                                │
│  │  └─────────────────────────────────────┘   │                                                │
│  │                                             │                                                │
│  │  ┌─────────────────────────────────────┐   │                                                │
│  │  │ 3. Aggregate Results               │   │                                                │
│  │  │    • Combine agent outputs         │   │                                                │
│  │  │    • Validate consistency          │   │                                                │
│  │  │    • Generate final plan           │   │                                                │
│  │  │    • Store in memory               │   │                                                │
│  │  └─────────────────────────────────────┘   │                                                │
│  └─────────────────────────────────────────────┘                                                │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│  PHASE 4: REAL-TIME UPDATES & FRONTEND INTEGRATION                                            │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  Backend Orchestrator ──┐                                                                      │
│                         │                                                                      │
│  ┌──────────────────────▼──────────────────────┐    ┌─────────────────────────────────────────┐ │
│  │     Memory Store Updates                     │    │     Frontend Build Mode UI              │ │
│  │                                              │    │                                         │ │
│  │  • Event state changes                      │───►│  ┌─────────────────────────────────────┐ │ │
│  │  • Agent result storage                     │    │  │  Left Panel: Agent Timeline         │ │ │
│  │  • Workflow status tracking                 │    │  │                                     │ │ │
│  │  • Error handling & recovery                │    │  │  📊 Real-time Progress              │ │ │
│  │  • WebSocket broadcasts                     │    │  │  📝 Agent Logs                      │ │ │
│  │                                              │    │  │  ⚡ Status Updates                 │ │ │
│  │  ┌─────────────────────────────────────────┐│    │  │  🎯 Completion Indicators           │ │ │
│  │  │  WebSocket Communication                ││    │  └─────────────────────────────────────┘ │ │
│  │  │                                         ││    │                                         │ │
│  │  │  • Agent status broadcasts              ││◄───┤  ┌─────────────────────────────────────┐ │ │
│  │  │  • Progress updates                     ││    │  │  Right Panel: Interactive Canvas   │ │ │
│  │  │  • Error notifications                  ││    │  │                                     │ │ │
│  │  │  • Final plan delivery                  ││    │  │  🎨 Drag & Drop Elements            │ │ │
│  │  │  • Component updates                    ││    │  │  🔗 Connection Lines                │ │ │
│  │  │                                         ││    │  │  📋 Action Items                    │ │ │
│  │  │  Status: "running" | "completed" | "error"│    │  │  🎪 Party Components               │ │ │
│  │  └─────────────────────────────────────────┘│    │  └─────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────┘    └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│  FINAL OUTPUT: COMPLETE PARTY PLAN                                                              │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  🎉 Generated Party Plan:                                                                       │
│                                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────────────────┐   │
│  │  📋 Party Plan Summary                                                                  │   │
│  │                                                                                         │   │
│  │  🎂 Theme: Unicorn Princess Party                                                       │   │
│  │  🏠 Venue: Community Center (Capacity: 20 guests)                                       │   │
│  │  🎂 Cake: 3-tier unicorn cake with rainbow layers                                      │   │
│  │  🎪 Decorations: Pink & purple balloons, unicorn banners, rainbow tablecloths          │   │
│  │  🎭 Entertainment: Face painting, balloon twisting, unicorn piñata                    │   │
│  │  🍽️ Catering: Kid-friendly finger foods, rainbow fruit platter                         │   │
│  │  ⏰ Timeline: Setup 2hrs, Party 3hrs, Cleanup 1hr                                      │   │
│  │  💰 Budget: $500-700 total                                                              │   │
│  │                                                                                         │   │
│  │  📊 Agent Results:                                                                      │   │
│  │  • Theme Agent: ✅ Completed (Confidence: 95%)                                          │   │
│  │  • Venue Agent: ✅ Completed (Confidence: 88%)                                          │   │
│  │  • Cake Agent: ✅ Completed (Confidence: 92%)                                          │   │
│  │  • Decoration Agent: ✅ Completed (Confidence: 90%)                                    │   │
│  │  • Entertainment Agent: ✅ Completed (Confidence: 87%)                                │   │
│  │  • Catering Agent: ✅ Completed (Confidence: 89%)                                      │   │
│  │  • Timeline Agent: ✅ Completed (Confidence: 93%)                                     │   │
│  │  • Budget Agent: ✅ Completed (Confidence: 91%)                                       │   │
│  └─────────────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 🔧 Technical Architecture Components

### Backend Services:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│  BACKEND ARCHITECTURE                                                                           │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │   FastAPI       │  │   LangGraph     │  │   Simple        │  │   Memory        │             │
│  │   Gateway       │  │   Data          │  │   Orchestrator  │  │   Store         │             │
│  │                 │  │   Extraction    │  │                 │  │                 │             │
│  │ • Route handling│  │                 │  │ • Agent         │  │ • Local JSON    │             │
│  │ • Validation    │  │ • 6-step        │  │   execution     │  │   files         │             │
│  │ • Error handling│  │   workflow      │  │ • State         │  │ • Event states  │             │
│  │ • WebSocket     │  │ • State         │  │   management   │  │ • Agent results │             │
│  │   support       │  │   management    │  │ • Error         │  │ • Firebase      │             │
│  │                 │  │ • Pattern       │  │   handling      │  │   migration     │             │
│  │                 │  │   matching      │  │ • Progress      │  │   ready         │             │
│  │                 │  │ • Confidence    │  │   tracking      │  │                 │             │
│  │                 │  │   scoring       │  │                 │  │                 │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │   Agent          │  │   Agent         │  │   Agent         │  │   Agent         │             │
│  │   Registry       │  │   Services      │  │   Error         │  │   Monitoring    │             │
│  │                 │  │                 │  │   Handler       │  │                 │             │
│  │ • Theme Agent   │  │ • Theme         │  │                 │  │ • Performance   │             │
│  │ • Venue Agent   │  │   selection     │  │ • Circuit       │  │   metrics       │             │
│  │ • Cake Agent    │  │ • Venue         │  │   breaker       │  │ • Error         │             │
│  │ • Decoration    │  │   matching      │  │ • Retry logic   │  │   tracking      │             │
│  │   Agent         │  │ • Cake design   │  │ • Fallback      │  │ • Logging       │             │
│  │ • Entertainment │  │ • Decoration    │  │   mechanisms    │  │ • Alerting      │             │
│  │   Agent         │  │   planning      │  │ • Error         │  │                 │             │
│  │ • Catering      │  │ • Entertainment │  │   recovery      │  │                 │             │
│  │   Agent         │  │   booking       │  │                 │  │                 │             │
│  │ • Timeline      │  │ • Catering      │  │                 │  │                 │             │
│  │   Agent         │  │   arrangements  │  │                 │  │                 │             │
│  │ • Budget Agent  │  │ • Timeline      │  │                 │  │                 │             │
│  │                 │  │   creation      │  │                 │  │                 │             │
│  │                 │  │ • Budget        │  │                 │  │                 │             │
│  │                 │  │   optimization  │  │                 │  │                 │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Frontend Components:
```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│  FRONTEND ARCHITECTURE                                                                           │
├─────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │   Search        │  │   Dynamic       │  │   Build Mode     │  │   Interactive   │             │
│  │   Interface     │  │   Forms         │  │   UI             │  │   Canvas        │             │
│  │                 │  │                 │  │                 │  │                 │             │
│  │ • Multi-modal   │  │                 │  │ • Agent         │  │                 │             │
│  │   input         │  │ • Auto-generated│  │   timeline      │  │ • Drag & drop   │             │
│  │ • Text prompts  │  │   fields        │  │ • Real-time     │  │   components    │             │
│  │ • Image upload  │  │ • Field         │  │   updates       │  │ • Connection    │             │
│  │ • URL input     │  │   validation    │  │ • Progress      │  │   lines         │             │
│  │ • Voice input   │  │ • Contextual    │  │   indicators    │  │ • Visual        │             │
│  │                 │  │   prompts       │  │ • Error         │  │   workflow      │             │
│  │                 │  │ • User-friendly │  │   handling      │  │ • Component     │             │
│  │                 │  │   interface     │  │ • Status        │  │   management    │             │
│  │                 │  │                 │  │   tracking      │  │ • Real-time     │             │
│  │                 │  │                 │  │                 │  │   updates       │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │   State         │  │   API           │  │   WebSocket     │  │   Animation     │             │
│  │   Management    │  │   Integration   │  │   Client        │  │   System        │             │
│  │                 │  │                 │  │                 │  │                 │             │
│  │ • React hooks   │  │                 │  │ • Real-time     │  │                 │             │
│  │ • Context API   │  │ • HTTP client   │  │   communication│  │ • Framer Motion │             │
│  │ • Local storage │  │ • Error         │  │ • Status        │  │ • Smooth        │             │
│  │ • Session       │  │   handling      │  │   updates       │  │   transitions   │             │
│  │   management    │  │ • Request       │  │ • Progress      │  │ • Liquid glass  │             │
│  │ • Form state    │  │   retry logic   │  │   tracking      │  │   effects       │             │
│  │                 │  │ • Response      │  │ • Error         │  │ • Glowing       │             │
│  │                 │  │   parsing       │  │   notifications │  │   edges         │             │
│  │                 │  │                 │  │ • Reconnection  │  │ • Particle      │             │
│  │                 │  │                 │  │   handling      │  │   animations    │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

This comprehensive architecture provides a robust, scalable, and user-friendly party planning system with intelligent agent orchestration! 🎉
