# 🎉 Festimo Agent Orchestration Architecture & Execution Flow

## 🏗️ System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              FESTIMO PARTY PLANNING SYSTEM                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│  FRONTEND (Next.js/React)          │  BACKEND (FastAPI/Python)                 │
│  ┌─────────────────────────────┐   │  ┌─────────────────────────────────────┐   │
│  │     Search Interface        │   │  │        API Gateway                 │   │
│  │  • URL/Prompt Input         │◄──┼──┤  • FastAPI Routes                  │   │
│  │  • Image Upload             │   │  │  • Request Validation              │   │
│  │  • Dynamic Forms            │   │  │  • Response Formatting              │   │
│  └─────────────────────────────┘   │  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────┐   │  ┌─────────────────────────────────────┐   │
│  │     Build Mode UI           │   │  │     Agent Orchestration             │   │
│  │  • Agent Timeline           │◄──┼──┤  • LangGraph Workflow               │   │
│  │  • Interactive Canvas       │   │  │  • State Management                 │   │
│  │  • Real-time Updates       │   │  │  • Error Handling                   │   │
│  └─────────────────────────────┘   │  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🔄 Agent Orchestration Execution Flow

### Phase 1: Input Validation & Data Extraction
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           INPUT PROCESSING PIPELINE                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  User Input ──┐                                                                 │
│               │                                                                 │
│  ┌─────────────▼─────────────┐    ┌─────────────────────────────────────────┐   │
│  │   Input Sources           │    │     LangGraph Data Extraction           │   │
│  │  • Text Prompt            │───►│     Agent Workflow                      │   │
│  │  • Image Upload           │    │                                         │   │
│  │  • Pinterest URL          │    │  ┌─────────────────────────────────────┐ │   │
│  └───────────────────────────┘    │  │ 1. validate_input                  │ │   │
│                                   │  │    • Check party-related content    │ │   │
│                                   │  │    • Validate input format          │ │   │
│                                   │  └─────────────────────────────────────┘ │   │
│                                   │  ┌─────────────────────────────────────┐ │   │
│                                   │  │ 2. extract_basic_info               │ │   │
│                                   │  │    • Event type (birthday, etc.)   │ │   │
│                                   │  │    • Age detection                 │ │   │
│                                   │  │    • Theme recognition             │ │   │
│                                   │  │    • Honoree name                  │ │   │
│                                   │  └─────────────────────────────────────┘ │   │
│                                   │  ┌─────────────────────────────────────┐ │   │
│                                   │  │ 3. extract_event_details            │ │   │
│                                   │  │    • Guest count estimation        │ │   │
│                                   │  │    • Budget range detection        │ │   │
│                                   │  │    • Food preferences               │ │   │
│                                   │  │    • Activities list               │ │   │
│                                   │  │    • Location type                 │ │   │
│                                   │  └─────────────────────────────────────┘ │   │
│                                   │  ┌─────────────────────────────────────┐ │   │
│                                   │  │ 4. extract_logistics                │ │   │
│                                   │  │    • Date parsing (multiple formats)│ │   │
│                                   │  │    • Time extraction               │ │   │
│                                   │  │    • RSVP deadlines               │ │   │
│                                   │  └─────────────────────────────────────┘ │   │
│                                   │  ┌─────────────────────────────────────┐ │   │
│                                   │  │ 5. calculate_confidence             │ │   │
│                                   │  │    • Field completeness scoring    │ │   │
│                                   │  │    • User input requirement check  │ │   │
│                                   │  └─────────────────────────────────────┘ │   │
│                                   │  ┌─────────────────────────────────────┐ │   │
│                                   │  │ 6. generate_suggestions             │ │   │
│                                   │  │    • Missing field identification  │ │   │
│                                   │  │    • Contextual prompts            │ │   │
│                                   │  └─────────────────────────────────────┘ │   │
│                                   └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Phase 2: Dynamic Form Generation & User Input Collection
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        DYNAMIC FORM GENERATION                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Extraction Result ──┐                                                         │
│                      │                                                         │
│  ┌───────────────────▼───────────────────┐    ┌─────────────────────────────┐ │
│  │     Missing Fields Analysis            │    │     Frontend Form Builder    │ │
│  │                                       │    │                             │ │
│  │  • eventType: "Birthday" ✓           │───►│  ┌─────────────────────────┐ │ │
│  │  • theme: "Unicorn" ✓                │    │  │  Dynamic Input Fields   │ │ │
│  │  • age: 5 ✓                          │    │  │                         │ │ │
│  │  • guestCount: {adults: 12, kids: 8} ✓│    │  │  • Date Picker          │ │ │
│  │  • budget: {min: 5, max: 7} ✓        │    │  │  • Location Selector    │ │ │
│  │  • date: ❌ MISSING                   │    │  │  • Food Preference      │ │ │
│  │  • location: ❌ MISSING               │    │  │  • Budget Range         │ │ │
│  │  • foodPreference: ❌ MISSING         │    │  │  • Guest Count          │ │ │
│  └───────────────────────────────────────┘    │  └─────────────────────────┘ │ │
│                                               │                             │ │
│                                               │  ┌─────────────────────────┐ │ │
│                                               │  │  Field Configuration    │ │ │
│                                               │  │                         │ │ │
│                                               │  │  • Labels & Placeholders│ │ │
│                                               │  │  • Validation Rules     │ │ │
│                                               │  │  • Input Types          │ │ │
│                                               │  │  • Options Lists        │ │ │
│                                               │  └─────────────────────────┘ │ │
│                                               └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Phase 3: Agent Orchestration & Party Plan Generation
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        AGENT ORCHESTRATION WORKFLOW                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Complete Event Data ──┐                                                       │
│                        │                                                       │
│  ┌─────────────────────▼─────────────────────┐    ┌─────────────────────────┐ │
│  │     Simple Orchestrator                    │    │     Agent Registry      │ │
│  │                                             │    │                         │ │
│  │  ┌─────────────────────────────────────┐   │    │  • Theme Agent          │ │
│  │  │ 1. Create Event State               │   │    │  • Venue Agent          │ │
│  │  │    • Initialize workflow            │   │    │  • Cake Agent           │ │
│  │  │    • Store in memory                │   │    │  • Decoration Agent     │ │
│  │  └─────────────────────────────────────┘   │    │  • Entertainment Agent  │ │
│  │                                             │    │  • Catering Agent       │ │
│  │  ┌─────────────────────────────────────┐   │    │  • Timeline Agent       │ │
│  │  │ 2. Execute Agents Sequentially      │   │    │  • Budget Agent         │ │
│  │  │    • Theme selection & validation   │   │    └─────────────────────────┘ │
│  │  │    • Venue recommendations          │   │                               │
│  │  │    • Cake design & flavors         │   │                               │
│  │  │    • Decoration planning           │   │                               │
│  │  │    • Entertainment booking         │   │                               │
│  │  │    • Catering arrangements          │   │                               │
│  │  │    • Timeline creation             │   │                               │
│  │  │    • Budget optimization           │   │                               │
│  │  └─────────────────────────────────────┘   │                               │
│  │                                             │                               │
│  │  ┌─────────────────────────────────────┐   │                               │
│  │  │ 3. Aggregate Results               │   │                               │
│  │  │    • Combine agent outputs         │   │                               │
│  │  │    • Validate consistency          │   │                               │
│  │  │    • Generate final plan           │   │                               │
│  │  └─────────────────────────────────────┘   │                               │
│  └─────────────────────────────────────────────┘                               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Phase 4: Real-time Updates & Frontend Integration
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        REAL-TIME COMMUNICATION                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Backend Orchestrator ──┐                                                      │
│                         │                                                      │
│  ┌──────────────────────▼──────────────────────┐    ┌─────────────────────────┐ │
│  │     Memory Store Updates                     │    │     Frontend Updates     │ │
│  │                                              │    │                         │ │
│  │  • Event state changes                      │───►│  • Agent status updates  │ │
│  │  • Agent result storage                     │    │  • Progress indicators   │ │
│  │  • Workflow status tracking                 │    │  • Real-time logs        │ │
│  │  • Error handling & recovery                │    │  • Interactive canvas   │ │
│  └──────────────────────────────────────────────┘    │  • Component updates    │ │
│                                                      └─────────────────────────┘ │
│                                                                                 │
│  ┌──────────────────────────────────────────────┐    ┌─────────────────────────┐ │
│  │     WebSocket Communication                  │    │     Build Mode UI       │ │
│  │                                              │    │                         │ │
│  │  • Agent status broadcasts                  │◄───┤  • Left Panel: Timeline  │ │
│  │  • Progress updates                         │    │  • Right Panel: Canvas   │ │
│  │  • Error notifications                      │    │  • Drag & drop elements  │ │
│  │  • Final plan delivery                      │    │  • Connection lines      │ │
│  └──────────────────────────────────────────────┘    │  • Real-time feedback   │ │
│                                                      └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🎯 Agent Execution Sequence

### Sequential Agent Flow:
```
1. 📝 Data Extraction Agent (LangGraph)
   ├── Input validation
   ├── Basic info extraction
   ├── Event details extraction
   ├── Logistics extraction
   ├── Confidence calculation
   └── Suggestion generation

2. 🎨 Theme Agent
   ├── Theme validation
   ├── Color palette selection
   ├── Style recommendations
   └── Mood assessment

3. 🏢 Venue Agent
   ├── Location analysis
   ├── Capacity matching
   ├── Amenity requirements
   └── Booking recommendations

4. 🎂 Cake Agent
   ├── Design selection
   ├── Flavor recommendations
   ├── Size calculation
   └── Dietary considerations

5. 🎪 Decoration Agent
   ├── Theme implementation
   ├── Color coordination
   ├── Supplier recommendations
   └── Setup timeline

6. 🎭 Entertainment Agent
   ├── Activity selection
   ├── Performer booking
   ├── Equipment needs
   └── Schedule planning

7. 🍽️ Catering Agent
   ├── Menu planning
   ├── Dietary accommodations
   ├── Quantity calculation
   └── Service coordination

8. ⏰ Timeline Agent
   ├── Event scheduling
   ├── Setup requirements
   ├── Vendor coordination
   └── Contingency planning

9. 💰 Budget Agent
   ├── Cost optimization
   ├── Vendor comparison
   ├── Budget allocation
   └── Savings recommendations
```

## 🔧 Technical Components

### Backend Services:
- **LangGraph Data Extraction**: 6-step workflow for intelligent data parsing
- **Simple Orchestrator**: Sequential agent execution with state management
- **Memory Store**: Local JSON file-based persistence (Firebase migration ready)
- **API Gateway**: FastAPI routes with validation and error handling
- **WebSocket Support**: Real-time communication for live updates

### Frontend Components:
- **Search Interface**: Multi-modal input (text, image, URL)
- **Dynamic Forms**: Auto-generated based on missing fields
- **Build Mode**: Interactive canvas with drag & drop functionality
- **Agent Timeline**: Real-time progress tracking
- **Connection System**: Visual workflow representation

### Data Flow:
```
User Input → Validation → Extraction → Form Generation → Agent Orchestration → Plan Generation → Real-time Updates → Interactive Canvas
```

This architecture provides a robust, scalable, and user-friendly party planning system with intelligent agent orchestration! 🎉
