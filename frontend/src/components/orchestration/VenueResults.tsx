/**
 * Venue Results Component
 *
 * Displays recommended venues from the venue agent
 */

import React from 'react';

interface Venue {
  id: number;
  name: string;
  type: string;
  address: string;
  capacity: number;
  amenities: string[];
  daily_price: number;
  hourly_price: number;
  contact: string;
  rating: number;
  images: string[];
  description: string;
  similarity_score?: number;
}

interface VenueResultsProps {
  venues: Venue[];
  searchCriteria?: {
    guest_count?: number;
    budget?: number;
    theme?: string;
  };
}

export function VenueResults({ venues, searchCriteria }: VenueResultsProps) {
  if (!venues || venues.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-2xl font-bold mb-4">📍 Recommended Venues</h2>

      {searchCriteria && (
        <div className="mb-4 p-3 bg-blue-50 rounded-lg text-sm">
          <p className="text-gray-700">
            <strong>Search Criteria:</strong>
            {searchCriteria.guest_count && ` ${searchCriteria.guest_count} guests`}
            {searchCriteria.theme && ` • ${searchCriteria.theme} theme`}
            {searchCriteria.budget && ` • Budget up to $${searchCriteria.budget}`}
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {venues.map((venue) => (
          <div key={venue.id} className="border rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
            {/* Venue Image Placeholder */}
            <div className="h-48 bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center text-white text-6xl">
              📍
            </div>

            <div className="p-4">
              {/* Header */}
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-lg font-bold">{venue.name}</h3>
                <div className="flex items-center gap-1">
                  <span className="text-yellow-500">⭐</span>
                  <span className="font-semibold">{venue.rating.toFixed(1)}</span>
                </div>
              </div>

              {/* Type */}
              <p className="text-sm text-gray-600 mb-2">{venue.type}</p>

              {/* Description */}
              <p className="text-sm text-gray-700 mb-3">{venue.description}</p>

              {/* Details */}
              <div className="space-y-2 mb-3">
                <div className="flex items-center text-sm">
                  <span className="font-semibold mr-2">Capacity:</span>
                  <span>{venue.capacity} guests</span>
                </div>

                <div className="flex items-center text-sm">
                  <span className="font-semibold mr-2">Price:</span>
                  <span>
                    {venue.daily_price > 0 ? `$${venue.daily_price}/day` : 'Free (permit required)'}
                  </span>
                </div>

                <div className="flex items-center text-sm">
                  <span className="font-semibold mr-2">Contact:</span>
                  <span className="text-blue-600">{venue.contact}</span>
                </div>
              </div>

              {/* Amenities */}
              <div className="mb-3">
                <p className="text-sm font-semibold mb-1">Amenities:</p>
                <div className="flex flex-wrap gap-1">
                  {venue.amenities.slice(0, 4).map((amenity, index) => (
                    <span key={index} className="px-2 py-1 bg-gray-100 text-xs rounded">
                      {amenity}
                    </span>
                  ))}
                  {venue.amenities.length > 4 && (
                    <span className="px-2 py-1 bg-gray-100 text-xs rounded">
                      +{venue.amenities.length - 4} more
                    </span>
                  )}
                </div>
              </div>

              {/* AI Match Score */}
              {venue.similarity_score && (
                <div className="mb-3 p-2 bg-purple-50 rounded">
                  <p className="text-xs text-purple-700">
                    🤖 AI Match Score: {(venue.similarity_score * 100).toFixed(0)}%
                  </p>
                </div>
              )}

              {/* Action Button */}
              <button className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition-colors">
                Contact Venue
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
