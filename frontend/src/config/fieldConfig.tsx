import React from 'react'

export interface FieldConfig {
  label: string
  placeholder: string
  component: React.ComponentType<any>
  options?: string[]
  validation?: (value: any) => boolean
}

// Location field component with venue database integration
const LocationField: React.FC<{
  label: string
  placeholder: string
  value: any
  onChange: (value: any) => void
  options?: string[]
  suggestions?: string[]
}> = ({ label, placeholder, value, onChange, suggestions }) => {
  const venueTypes = [
    'Home',
    'Park', 
    'Restaurant',
    'Banquet Hall',
    'Hotel',
    'Community Center'
  ]

  const handleVenueTypeChange = (venueType: string) => {
    if (venueType === 'Home') {
      onChange({
        type: venueType,
        name: 'Home',
        address: '',
        needs_user_input: true,
        venue_data: null
      })
    } else {
      // For external venues, we'll let the backend fetch from database
      onChange({
        type: venueType,
        name: 'TBD',
        address: 'TBD',
        needs_user_input: false,
        venue_data: null
      })
    }
  }

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">
        {label}
      </label>
      
      {/* Venue Type Selection */}
      <div className="grid grid-cols-2 gap-2">
        {venueTypes.map((type) => (
          <button
            key={type}
            type="button"
            onClick={() => handleVenueTypeChange(type)}
            className={`p-3 rounded-lg border-2 text-sm font-medium transition-all ${
              value?.type === type
                ? 'border-pink-500 bg-pink-50 text-pink-700'
                : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
            }`}
          >
            {type}
          </button>
        ))}
      </div>

      {/* Address Input (only for Home venues) */}
      {value?.type === 'Home' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            City & Zip Code *
          </label>
          <input
            type="text"
            value={value?.address || ''}
            onChange={(e) => onChange({
              ...value,
              address: e.target.value
            })}
            placeholder="Enter your city and zip code (e.g., San Francisco, CA 94102)"
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
            required
          />
          <p className="text-xs text-gray-500 mt-1">Required for venue planning and vendor coordination</p>
        </div>
      )}

      {/* Venue Information Display (for external venues) */}
      {value?.venue_data && (
        <div className="bg-blue-50 p-4 rounded-lg">
          <h4 className="font-medium text-blue-900 mb-2">Selected Venue</h4>
          <div className="text-sm text-blue-800 space-y-1">
            <p><strong>Name:</strong> {value.name}</p>
            <p><strong>Address:</strong> {value.address}</p>
            <p><strong>Capacity:</strong> {value.venue_data.capacity} guests</p>
            <p><strong>Rating:</strong> ⭐ {value.venue_data.rating}/5</p>
            <p><strong>Pricing:</strong> ${value.venue_data.pricing.daily}/day</p>
            <p><strong>Contact:</strong> {value.venue_data.contact_info.phone}</p>
          </div>
        </div>
      )}

      {/* Suggestions */}
      {suggestions && suggestions.length > 0 && (
        <div className="text-sm text-gray-600">
          <p className="font-medium mb-1">Suggestions:</p>
          <ul className="list-disc list-inside space-y-1">
            {suggestions.map((suggestion, index) => (
              <li key={index}>{suggestion}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

// Other field components
const TextField: React.FC<{
  label: string
  placeholder: string
  value: any
  onChange: (value: any) => void
  options?: string[]
  suggestions?: string[]
}> = ({ label, placeholder, value, onChange, suggestions }) => (
  <div className="space-y-2">
    <label className="block text-sm font-medium text-gray-700">
      {label}
    </label>
    <input
      type="text"
      value={value || ''}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
    />
    {suggestions && suggestions.length > 0 && (
      <div className="text-sm text-gray-600">
        <p className="font-medium mb-1">Suggestions:</p>
        <ul className="list-disc list-inside space-y-1">
          {suggestions.map((suggestion, index) => (
            <li key={index}>{suggestion}</li>
          ))}
        </ul>
      </div>
    )}
  </div>
)

const NumberField: React.FC<{
  label: string
  placeholder: string
  value: any
  onChange: (value: any) => void
  options?: string[]
  suggestions?: string[]
}> = ({ label, placeholder, value, onChange, suggestions }) => (
  <div className="space-y-2">
    <label className="block text-sm font-medium text-gray-700">
      {label}
    </label>
    <input
      type="number"
      value={value || ''}
      onChange={(e) => onChange(parseInt(e.target.value) || 0)}
      placeholder={placeholder}
      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
    />
    {suggestions && suggestions.length > 0 && (
      <div className="text-sm text-gray-600">
        <p className="font-medium mb-1">Suggestions:</p>
        <ul className="list-disc list-inside space-y-1">
          {suggestions.map((suggestion, index) => (
            <li key={index}>{suggestion}</li>
          ))}
        </ul>
      </div>
    )}
  </div>
)

const SelectField: React.FC<{
  label: string
  placeholder: string
  value: any
  onChange: (value: any) => void
  options?: string[]
  suggestions?: string[]
}> = ({ label, placeholder, value, onChange, options = [], suggestions }) => (
  <div className="space-y-2">
    <label className="block text-sm font-medium text-gray-700">
      {label}
    </label>
    <select
      value={value || ''}
      onChange={(e) => onChange(e.target.value)}
      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
    >
      <option value="">{placeholder}</option>
      {options.map((option) => (
        <option key={option} value={option}>
          {option}
        </option>
      ))}
    </select>
    {suggestions && suggestions.length > 0 && (
      <div className="text-sm text-gray-600">
        <p className="font-medium mb-1">Suggestions:</p>
        <ul className="list-disc list-inside space-y-1">
          {suggestions.map((suggestion, index) => (
            <li key={index}>{suggestion}</li>
          ))}
        </ul>
      </div>
    )}
  </div>
)

const DateField: React.FC<{
  label: string
  placeholder: string
  value: any
  onChange: (value: any) => void
  options?: string[]
  suggestions?: string[]
}> = ({ label, placeholder, value, onChange, suggestions }) => (
  <div className="space-y-2">
    <label className="block text-sm font-medium text-gray-700">
      {label}
    </label>
    <input
      type="date"
      value={value || ''}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
    />
    {suggestions && suggestions.length > 0 && (
      <div className="text-sm text-gray-600">
        <p className="font-medium mb-1">Suggestions:</p>
        <ul className="list-disc list-inside space-y-1">
          {suggestions.map((suggestion, index) => (
            <li key={index}>{suggestion}</li>
          ))}
        </ul>
      </div>
    )}
  </div>
)

const BudgetField: React.FC<{
  label: string
  placeholder: string
  value: any
  onChange: (value: any) => void
  options?: string[]
  suggestions?: string[]
}> = ({ label, placeholder, value, onChange, suggestions }) => (
  <div className="space-y-2">
    <label className="block text-sm font-medium text-gray-700">
      {label}
    </label>
    <div className="grid grid-cols-2 gap-3">
      <div>
        <label className="block text-xs text-gray-600 mb-1">Minimum Budget</label>
        <input
          type="number"
          value={value?.min || ''}
          onChange={(e) => onChange({
            ...value,
            min: parseInt(e.target.value) || 0
          })}
          placeholder="Min amount"
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
        />
      </div>
      <div>
        <label className="block text-xs text-gray-600 mb-1">Maximum Budget</label>
        <input
          type="number"
          value={value?.max || ''}
          onChange={(e) => onChange({
            ...value,
            max: parseInt(e.target.value) || 0
          })}
          placeholder="Max amount"
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
        />
      </div>
    </div>
    {suggestions && suggestions.length > 0 && (
      <div className="text-sm text-gray-600">
        <p className="font-medium mb-1">Suggestions:</p>
        <ul className="list-disc list-inside space-y-1">
          {suggestions.map((suggestion, index) => (
            <li key={index}>{suggestion}</li>
          ))}
        </ul>
      </div>
    )}
  </div>
)

const GuestCountField: React.FC<{
  label: string
  placeholder: string
  value: any
  onChange: (value: any) => void
  options?: string[]
  suggestions?: string[]
}> = ({ label, placeholder, value, onChange, suggestions }) => (
  <div className="space-y-2">
    <label className="block text-sm font-medium text-gray-700">
      {label}
    </label>
    <div className="grid grid-cols-2 gap-3">
      <div>
        <label className="block text-xs text-gray-600 mb-1">Adults</label>
        <input
          type="number"
          value={value?.adults || ''}
          onChange={(e) => onChange({
            ...value,
            adults: parseInt(e.target.value) || 0
          })}
          placeholder="Number of adults"
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
        />
      </div>
      <div>
        <label className="block text-xs text-gray-600 mb-1">Kids</label>
        <input
          type="number"
          value={value?.kids || ''}
          onChange={(e) => onChange({
            ...value,
            kids: parseInt(e.target.value) || 0
          })}
          placeholder="Number of kids"
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
        />
      </div>
    </div>
    {suggestions && suggestions.length > 0 && (
      <div className="text-sm text-gray-600">
        <p className="font-medium mb-1">Suggestions:</p>
        <ul className="list-disc list-inside space-y-1">
          {suggestions.map((suggestion, index) => (
            <li key={index}>{suggestion}</li>
          ))}
        </ul>
      </div>
    )}
  </div>
)

export const FIELD_CONFIG: Record<string, FieldConfig> = {
  eventType: {
    label: "Event Type",
    placeholder: "Select event type",
    component: SelectField,
    options: [
      "Birthday",
      "Wedding", 
      "Anniversary",
      "Baby Shower",
      "Graduation",
      "Retirement",
      "Holiday Party",
      "Christmas",
      "Halloween",
      "New Year",
      "Easter",
      "Thanksgiving",
      "Valentine",
      "Mothers Day",
      "Fathers Day",
      "Engagement",
      "Bachelor",
      "Bachelorette",
      "Housewarming"
    ]
  },
  theme: {
    label: "Party Theme",
    placeholder: "Select theme",
    component: SelectField,
    options: [
      "Princess",
      "Superhero", 
      "Unicorn",
      "Dinosaur",
      "Space",
      "Pirate",
      "Fairy",
      "Mermaid",
      "Jungle",
      "Safari",
      "Underwater",
      "Circus",
      "Carnival",
      "Vintage",
      "Rustic",
      "Modern",
      "Minimalist",
      "Bohemian",
      "Tropical",
      "Beach",
      "Pool",
      "Garden",
      "Tea Party",
      "Masquerade",
      "Hollywood",
      "Disney",
      "Frozen",
      "Moana",
      "Cars",
      "Toy Story",
      "Blippi"
    ]
  },
  date: {
    label: "Event Date",
    placeholder: "Select date",
    component: DateField
  },
  location: {
    label: "Venue Location",
    placeholder: "Select venue type",
    component: LocationField
  },
  location_address: {
    label: "Home Address",
    placeholder: "Enter your home address",
    component: TextField
  },
  guestCount: {
    label: "Guest Count",
    placeholder: "Enter guest count",
    component: GuestCountField
  },
  budget: {
    label: "Budget Range",
    placeholder: "Enter budget range",
    component: BudgetField
  },
  foodPreference: {
    label: "Food Preference",
    placeholder: "Select food preference",
    component: SelectField,
    options: ["Vegetarian", "Non-Vegetarian", "Mixed", "Vegan", "Gluten-Free"]
  },
  honoreeName: {
    label: "Honoree Name",
    placeholder: "Enter honoree name",
    component: TextField
  },
  age: {
    label: "Age",
    placeholder: "Enter age",
    component: NumberField
  },
  hostName: {
    label: "Host Name",
    placeholder: "Enter host name",
    component: TextField
  },
  title: {
    label: "Event Title",
    placeholder: "Enter event title",
    component: TextField
  },
  activities: {
    label: "Activities",
    placeholder: "Select activities",
    component: SelectField,
    options: [
      "Balloon Twisting",
      "Magic Show",
      "Face Painting",
      "Pinata",
      "Bouncy Castle",
      "Photo Booth",
      "Dancing",
      "Karaoke",
      "Treasure Hunt",
      "Scavenger Hunt",
      "Crafts",
      "Storytelling",
      "Music",
      "DJ",
      "Live Band",
      "Entertainment",
      "Performers",
      "Dance Floor"
    ]
  }
}
