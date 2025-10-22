# 🎯 Hybrid Input System Documentation

**Version:** 2.0
**Date:** October 22, 2025
**Status:** ✅ Production Ready

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Input Types](#input-types)
4. [Smart Routing](#smart-routing)
5. [API Usage](#api-usage)
6. [Cost Optimization](#cost-optimization)
7. [Examples](#examples)
8. [Testing](#testing)

---

## 🌟 Overview

The Hybrid Input System intelligently processes **all types of party planning inputs**:

- **Text-only:** Simple prompts or complex narratives
- **Image-only:** Pinterest URLs, uploaded photos, inspiration images
- **Combined:** Text descriptions + visual inspiration

### Key Features

✅ **Smart Routing** - Automatically chooses optimal processing strategy
✅ **Cost Optimized** - Saves ~70% by avoiding LLM for simple inputs
✅ **Vision Integration** - Images analyzed and converted to structured data
✅ **Hallucination Prevention** - LLM outputs validated against source
✅ **Agent Context** - Vision insights enhance agent searches

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INPUT                               │
│  Text, Image URL, or Both                                   │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│           UnifiedInputProcessor                              │
│  - Detects input type                                       │
│  - Processes images with Vision AI (if applicable)          │
│  - Routes to Smart Router                                   │
└────────────────┬────────────────────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
    ▼                         ▼
┌──────────┐           ┌──────────────┐
│ Vision AI│           │ Smart Router │
│ (images) │           │ (text)       │
└────┬─────┘           └──────┬───────┘
     │                        │
     │  Text                  │
     │  Description     ┌─────┴──────┐
     └─────────────────►│  Complexity│
                        │  Assessment│
                        └─────┬──────┘
                              │
                  ┌───────────┴────────────┐
                  │                        │
                  ▼                        ▼
          ┌──────────────┐        ┌─────────────┐
          │ SIMPLE INPUT │        │COMPLEX INPUT│
          │              │        │             │
          │ Regex        │        │ LLM Planning│
          │ Extraction   │        │ (GPT-4)     │
          │              │        │             │
          │ Free, 100ms  │        │ $0.02, 3s   │
          └──────┬───────┘        └──────┬──────┘
                 │                       │
                 └───────────┬───────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Enriched Data   │
                    │ - Natural Lang  │
                    │ - Structured    │
                    │ - Agent Context │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ InputAnalyzer   │
                    │ - Classifies    │
                    │ - Routes agents │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Agents Execute  │
                    │ theme, venue,   │
                    │ cake, budget... │
                    └─────────────────┘
```

---

## 📥 Input Types

### 1. Text-Only Inputs

**Use Cases:**
- Simple prompts: `"Birthday party for 30 guests, superhero theme"`
- Complex narratives: `"My grandmother loves tea and gardening..."`
- Detailed plans: Full party descriptions

**Processing:**
- **Simple** → Regex extraction (fast, free)
- **Complex** → LLM planning (high quality, small cost)

---

### 2. Image-Only Inputs

**Use Cases:**
- Pinterest inspiration pins
- Uploaded party photos
- Decoration ideas

**Processing:**
1. Vision AI analyzes image
2. Extracts: theme, colors, objects, venue type, budget estimate
3. Converts to natural language description
4. Routes to Smart Router
5. Triggers appropriate agents with vision context

---

### 3. Combined Text + Image

**Use Cases:**
- "I want something like this for my daughter turning 5" + image
- "Budget $500, outdoor venue" + Pinterest inspiration
- Text requirements + visual style reference

**Processing:**
1. Vision AI analyzes image
2. Combines vision description with user text
3. LLM understands complete context
4. Generates comprehensive plan
5. Agents receive both text and visual insights

---

## 🧠 Smart Routing

### Complexity Assessment

The system assesses input complexity based on:

#### Simple Indicators (use regex):
✅ Explicit theme keyword
✅ Explicit event type
✅ Guest count stated
✅ Concise (< 30 words)
✅ Structured format (commas, line breaks)

#### Complex Indicators (use LLM):
🔴 Narrative style
🔴 Implicit requirements
🔴 Context-dependent understanding
🔴 Emotional/subjective language
🔴 Long descriptions (> 50 words)
🔴 Has image input

### Example Classifications

```python
# SIMPLE (→ Regex)
"Birthday party, 50 guests, unicorn theme, 95050"
"Wedding for 200 people, downtown venue"
"Superhero party for 5 year old, 30 kids"

# COMPLEX (→ LLM)
"My daughter loves rainbows and horses, turning 5"
"Something elegant for grandma who enjoys tea and gardening"
"Magical party for my son interested in space"
```

---

## 🔌 API Usage

### Endpoint

```
POST /api/v1/event-driven/party/{party_id}/input
```

### Request Schema

```typescript
interface AddInputRequest {
  content: string;              // Text content
  source_type: string;          // "text", "image", "url", "upload"
  tags?: string[];              // Optional tags
  metadata?: object;            // Optional metadata
  image_url?: string;           // NEW: Image URL for vision analysis
}
```

---

### Example 1: Text-Only (Simple)

```bash
curl -X POST http://localhost:9000/api/v1/event-driven/party/fp2025A12345/input \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Birthday party, 50 guests, jungle theme, outdoor venue",
    "source_type": "text"
  }'
```

**Response:**
```json
{
  "success": true,
  "input_id": "inp_abc123",
  "message": "Input added successfully. [regex]"
}
```

**Processing:** Regex (free, 100ms)

---

### Example 2: Image-Only

```bash
curl -X POST http://localhost:9000/api/v1/event-driven/party/fp2025A12345/input \
  -H "Content-Type: application/json" \
  -d '{
    "content": "pinterest_inspiration",
    "source_type": "image",
    "image_url": "https://pinterest.com/pin/123456789"
  }'
```

**Response:**
```json
{
  "success": true,
  "input_id": "inp_def456",
  "message": "Input added successfully with vision analysis (detected: unicorn theme). [vision_ai + llm]"
}
```

**Processing:** Vision AI + LLM ($0.02, 3-5s)

**Vision Analysis Detects:**
- Theme: "rainbow unicorn"
- Colors: pink, purple, white, gold
- Objects: unicorn balloons, rainbow cake, pastel decorations
- Venue: indoor medium capacity
- Age range: 5-10 years
- Budget estimate: $300-600

---

### Example 3: Combined Text + Image

```bash
curl -X POST http://localhost:9000/api/v1/event-driven/party/fp2025A12345/input \
  -H "Content-Type: application/json" \
  -d '{
    "content": "I want something like this for my daughter turning 5. Around 30 kids.",
    "source_type": "text",
    "image_url": "https://pinterest.com/pin/987654321",
    "tags": ["inspiration"]
  }'
```

**Response:**
```json
{
  "success": true,
  "input_id": "inp_ghi789",
  "message": "Input added successfully with vision analysis (detected: princess theme). [vision_ai + llm]"
}
```

**Processing:** Vision AI + LLM ($0.02, 3-5s)

**Combined Understanding:**
- From text: daughter, age 5, 30 kids
- From image: princess theme, pink/gold colors, indoor setup
- LLM synthesizes: Princess birthday for 5-year-old girl, 30 guests, pink & gold decor, indoor venue

---

## 💰 Cost Optimization

### Performance Metrics

| Input Type | Strategy | Cost | Latency | Quality |
|------------|----------|------|---------|---------|
| Simple text | Regex | $0 | 100-500ms | Good |
| Complex text | LLM | $0.01-0.02 | 2-5s | Excellent |
| Image only | Vision + LLM | $0.02-0.03 | 3-6s | Excellent |
| Text + Image | Vision + LLM | $0.02-0.03 | 3-6s | Best |

### Cost Savings

**Traditional Approach** (LLM for everything):
- 1000 requests × $0.02 = **$20.00**

**Hybrid Approach** (smart routing):
- 700 simple → regex = **$0.00**
- 300 complex → LLM = **$6.00**
- **Total: $6.00 (70% savings!)**

---

## 📚 Examples

### Use Case 1: Quick Party Planning

**User:** `"Superhero birthday for 30 kids, outdoor park, budget $500"`

**System:**
1. Complexity: SIMPLE (has theme, count, venue, budget)
2. Processor: Regex extraction
3. Time: 150ms
4. Cost: $0
5. Agents triggered: theme_agent, venue_agent, budget_agent

**Result:** Fast, free, accurate ✅

---

### Use Case 2: Pinterest Inspiration

**User:** Uploads Pinterest pin of elegant garden tea party

**System:**
1. Vision AI analyzes image
2. Detects: garden tea party theme, floral decorations, vintage style
3. Extracts: pastel colors, outdoor venue, ages 70-80 (senior-friendly)
4. Estimates: $400-800 budget
5. Converts to: "Garden tea party theme with floral decorations, vintage style, pastel colors, outdoor venue, suitable for seniors"
6. LLM plans: Complete structured plan with inferred requirements
7. Agents triggered with vision context

**Result:** Rich visual understanding → detailed plan ✅

---

### Use Case 3: Narrative Description

**User:** `"My grandmother is turning 80. She loves tea and has a beautiful garden. We want something elegant but not too formal. About 30 family members will attend."`

**System:**
1. Complexity: COMPLEX (narrative, implicit needs, context-dependent)
2. Processor: LLM Planning
3. LLM infers:
   - Event: 80th birthday milestone
   - Theme: garden tea party
   - Style: elegant casual
   - Venue: home garden or tea room
   - Guests: 30 adults/seniors
   - Menu: afternoon tea service
4. Time: 3.5s
5. Cost: $0.02
6. Agents triggered: theme_agent, venue_agent, catering_agent, budget_agent

**Result:** Deep understanding → perfect plan ✅

---

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest tests/test_hybrid_input_system.py -v

# LLM tests (requires API key)
pytest tests/test_hybrid_input_system.py -v --llm

# Specific test
pytest tests/test_hybrid_input_system.py::TestSmartInputRouter::test_simple_input_detected -v
```

### Test Coverage

✅ Simple input detection
✅ Complex input detection
✅ Image complexity assessment
✅ Regex extraction for simple inputs
✅ LLM extraction for complex inputs
✅ Vision-to-text conversion
✅ Combined text+image processing
✅ End-to-end agent triggering
✅ Cost optimization validation
✅ Hallucination prevention

---

## 🚀 Deployment Checklist

### Required Environment Variables

```bash
# OpenAI API (for LLM Planning)
export OPENAI_API_KEY="sk-..."

# Google Gemini API (for Vision AI)
export GEMINI_API_KEY="..."
export GEMINI_MODEL="gemini-1.5-flash"
```

### Optional Configuration

```python
# app/core/config.py

# Enable/disable LLM planning
ENABLE_LLM_PLANNING = True  # Set False to force regex only

# LLM timeout
LLM_TIMEOUT_SECONDS = 30

# Complexity threshold (0-100)
# Lower = more LLM usage, Higher = more regex usage
COMPLEXITY_THRESHOLD = 50
```

---

## 📊 Monitoring

### Key Metrics to Track

1. **Processor Distribution**
   - % using regex vs LLM
   - Target: 60-70% regex for cost optimization

2. **Latency**
   - P50, P95, P99 response times
   - Target: P95 < 5s

3. **Cost**
   - Daily LLM API spend
   - Cost per party created

4. **Quality**
   - Agent trigger accuracy
   - User satisfaction with extracted data

### Logging

All processing includes detailed logs:

```python
logger.info(
    "Input processed",
    processor_chain=["vision_ai", "llm"],
    confidence=92.5,
    has_vision=True,
    complexity_level="complex"
)
```

---

## 🔧 Troubleshooting

### Issue: All inputs using LLM (high cost)

**Cause:** Complexity threshold too low
**Fix:** Increase `COMPLEXITY_THRESHOLD` or review complexity assessment logic

### Issue: Poor extraction quality for complex inputs

**Cause:** LLM disabled or regex used for complex input
**Fix:** Ensure `OPENAI_API_KEY` set and `ENABLE_LLM_PLANNING=True`

### Issue: Vision analysis not triggering

**Cause:** Missing `image_url` or Vision AI disabled
**Fix:** Ensure `GEMINI_API_KEY` set and `image_url` provided

### Issue: Slow response times

**Cause:** LLM timeout or Vision API latency
**Fix:** Reduce `LLM_TIMEOUT_SECONDS` or implement caching

---

## 📄 License

Copyright © 2025 Festipin. All rights reserved.

---

## 🆘 Support

For questions or issues:
- GitHub Issues: [festipin/backend/issues](https://github.com/festipin/backend/issues)
- Email: support@festipin.com
- Docs: [docs.festipin.com](https://docs.festipin.com)

---

**Last Updated:** October 22, 2025
**Version:** 2.0
**Status:** ✅ Production Ready
