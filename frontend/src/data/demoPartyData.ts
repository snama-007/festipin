// Demo data for Party Summary UI testing
export const demoPartyData = {
  party_id: "fp2025A12345",
  status: "completed",
  completion_percent: 95,
  budget: {
    total_min: 2450,
    total_max: 2500,
    breakdown: [
      { category: "venue", amount: 800, percentage: 32 },
      { category: "catering", amount: 600, percentage: 24 },
      { category: "cake", amount: 300, percentage: 12 },
      { category: "decorations", amount: 400, percentage: 16 },
      { category: "vendors", amount: 350, percentage: 14 },
      { category: "other", amount: 50, percentage: 2 }
    ]
  },
  agent_results: {
    theme_agent: {
      status: "completed",
      result: {
        primary_theme: "Jungle Safari",
        color_scheme: ["Forest Green", "Safari Brown", "Sunset Orange"],
        decorations: ["Animal balloons", "Jungle vines", "Safari hats", "Animal masks"],
        mood: "Adventurous and fun"
      }
    },
    venue_agent: {
      status: "completed",
      result: {
        recommended_venues: [
          {
            name: "Garden Pavilion",
            location: "Central Park Community Center",
            capacity: 50,
            price_range: "$800-1000",
            features: ["Outdoor space", "Kitchen access", "Parking", "Sound system"]
          }
        ]
      }
    },
    cake_agent: {
      status: "completed",
      result: {
        cake_suggestions: [
          {
            type: "3-Tier Jungle Cake",
            flavor: "Chocolate with vanilla filling",
            size: "Serves 50 guests",
            price_range: "$250-300",
            bakery: "Sweet Safari Bakery"
          }
        ]
      }
    },
    catering_agent: {
      status: "completed",
      result: {
        menu_suggestions: [
          {
            category: "Main Course",
            items: ["Grilled chicken skewers", "Mini burgers", "Veggie wraps"],
            dietary_options: ["Vegetarian", "Gluten-free"]
          },
          {
            category: "Sides",
            items: ["Jungle fruit salad", "Animal crackers", "Trail mix"],
            dietary_options: ["Nut-free options"]
          }
        ]
      }
    },
    vendor_agent: {
      status: "completed",
      result: {
        vendor_suggestions: [
          {
            type: "Balloon Artist",
            name: "Sarah's Balloons",
            services: ["Animal balloons", "Balloon arch", "Party games"],
            price_range: "$200-250",
            contact_info: "sarah@balloons.com"
          },
          {
            type: "Face Painter",
            name: "Jungle Faces",
            services: ["Animal face painting", "Temporary tattoos"],
            price_range: "$150-200",
            contact_info: "jungle@faces.com"
          }
        ]
      }
    }
  },
  recommendations: [
    "Consider adding a photo booth with jungle props for memorable moments",
    "Book vendors at least 2 weeks in advance for best availability",
    "Prepare backup indoor activities in case of weather",
    "Create a themed playlist with jungle and animal sounds"
  ],
  next_steps: [
    "Contact Garden Pavilion to confirm booking",
    "Order cake from Sweet Safari Bakery",
    "Schedule vendor consultations",
    "Create detailed timeline for party day"
  ],
  created_at: "2025-01-22T10:30:00Z",
  updated_at: "2025-01-22T11:45:00Z"
}
