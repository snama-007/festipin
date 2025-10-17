/**
 * Bakery Results Component
 *
 * Displays recommended bakeries from the cake agent
 */

import React from 'react';

interface Bakery {
  id: number;
  name: string;
  specialties: string[];
  price_range: {
    small: number;
    medium: number;
    large: number;
  };
  contact: string;
  rating: number;
  portfolio_images: string[];
  custom_designs: boolean;
  description: string;
  similarity_score?: number;
}

interface BakeryResultsProps {
  bakeries: Bakery[];
  theme?: string;
  decorations?: string[];
}

export function BakeryResults({ bakeries, theme, decorations }: BakeryResultsProps) {
  if (!bakeries || bakeries.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-2xl font-bold mb-4">🎂 Recommended Bakeries</h2>

      {theme && (
        <div className="mb-4 p-3 bg-pink-50 rounded-lg">
          <p className="text-sm text-gray-700 mb-2">
            <strong>Theme:</strong> {theme}
          </p>
          {decorations && decorations.length > 0 && (
            <div>
              <p className="text-sm font-semibold text-gray-700 mb-1">Suggested Decorations:</p>
              <div className="flex flex-wrap gap-1">
                {decorations.map((dec, index) => (
                  <span key={index} className="px-2 py-1 bg-pink-100 text-xs rounded">
                    {dec}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {bakeries.map((bakery) => (
          <div key={bakery.id} className="border rounded-lg overflow-hidden hover:shadow-lg transition-shadow">
            {/* Bakery Image Placeholder */}
            <div className="h-48 bg-gradient-to-br from-pink-400 to-yellow-500 flex items-center justify-center text-white text-6xl">
              🎂
            </div>

            <div className="p-4">
              {/* Header */}
              <div className="flex justify-between items-start mb-2">
                <h3 className="text-lg font-bold">{bakery.name}</h3>
                <div className="flex items-center gap-1">
                  <span className="text-yellow-500">⭐</span>
                  <span className="font-semibold">{bakery.rating.toFixed(1)}</span>
                </div>
              </div>

              {/* Custom Designs Badge */}
              {bakery.custom_designs && (
                <span className="inline-block px-2 py-1 bg-purple-100 text-purple-700 text-xs font-semibold rounded mb-2">
                  ✨ Custom Designs Available
                </span>
              )}

              {/* Description */}
              <p className="text-sm text-gray-700 mb-3">{bakery.description}</p>

              {/* Specialties */}
              <div className="mb-3">
                <p className="text-sm font-semibold mb-1">Specialties:</p>
                <div className="flex flex-wrap gap-1">
                  {bakery.specialties.map((specialty, index) => (
                    <span key={index} className="px-2 py-1 bg-yellow-100 text-xs rounded">
                      {specialty}
                    </span>
                  ))}
                </div>
              </div>

              {/* Price Range */}
              <div className="mb-3 p-2 bg-gray-50 rounded">
                <p className="text-sm font-semibold mb-1">Price Range:</p>
                <div className="text-xs space-y-1">
                  <div className="flex justify-between">
                    <span>Small:</span>
                    <span className="font-semibold">${bakery.price_range.small}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Medium:</span>
                    <span className="font-semibold">${bakery.price_range.medium}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Large:</span>
                    <span className="font-semibold">${bakery.price_range.large}</span>
                  </div>
                </div>
              </div>

              {/* Contact */}
              <p className="text-sm text-gray-600 mb-3">
                <strong>Contact:</strong> <span className="text-blue-600">{bakery.contact}</span>
              </p>

              {/* AI Match Score */}
              {bakery.similarity_score && (
                <div className="mb-3 p-2 bg-purple-50 rounded">
                  <p className="text-xs text-purple-700">
                    🤖 AI Match Score: {(bakery.similarity_score * 100).toFixed(0)}%
                  </p>
                </div>
              )}

              {/* Action Button */}
              <button className="w-full bg-pink-600 text-white py-2 rounded hover:bg-pink-700 transition-colors">
                Request Quote
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
