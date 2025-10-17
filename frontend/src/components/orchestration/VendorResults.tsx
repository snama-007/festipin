/**
 * Vendor Results Component
 *
 * Displays recommended vendors by category from the vendor agent
 */

import React from 'react';

interface Vendor {
  id: number;
  name: string;
  category: string;
  services: string[];
  contact: string;
  rating: number;
  avg_price: number;
  review_count: number;
  description: string;
  portfolio_images: string[];
  similarity_score?: number;
}

interface VendorResultsProps {
  vendorsByCategory: Record<string, Vendor[]>;
  searchCriteria?: {
    theme?: string;
    budget?: { min: number; max: number };
  };
}

const CATEGORY_EMOJIS: Record<string, string> = {
  decorations: '🎈',
  entertainment: '🎭',
  photography: '📸',
  rentals: '🎪',
  planning: '📋',
};

const CATEGORY_COLORS: Record<string, string> = {
  decorations: 'from-pink-400 to-red-500',
  entertainment: 'from-purple-400 to-indigo-500',
  photography: 'from-blue-400 to-cyan-500',
  rentals: 'from-green-400 to-teal-500',
  planning: 'from-yellow-400 to-orange-500',
};

export function VendorResults({ vendorsByCategory, searchCriteria }: VendorResultsProps) {
  if (!vendorsByCategory || Object.keys(vendorsByCategory).length === 0) {
    return null;
  }

  const totalVendors = Object.values(vendorsByCategory).reduce(
    (sum, vendors) => sum + vendors.length,
    0
  );

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-2xl font-bold mb-4">🏪 Recommended Vendors</h2>

      {searchCriteria && (
        <div className="mb-4 p-3 bg-purple-50 rounded-lg text-sm">
          <p className="text-gray-700">
            <strong>Search Criteria:</strong>
            {searchCriteria.theme && ` ${searchCriteria.theme} theme`}
            {searchCriteria.budget && (
              ` • Budget: $${searchCriteria.budget.min}-$${searchCriteria.budget.max}`
            )}
          </p>
          <p className="text-gray-600 mt-1">Found {totalVendors} vendors across {Object.keys(vendorsByCategory).length} categories</p>
        </div>
      )}

      <div className="space-y-8">
        {Object.entries(vendorsByCategory).map(([category, vendors]) => {
          if (vendors.length === 0) return null;

          const emoji = CATEGORY_EMOJIS[category] || '🏪';
          const gradientColor = CATEGORY_COLORS[category] || 'from-gray-400 to-gray-500';

          return (
            <div key={category}>
              {/* Category Header */}
              <div className="flex items-center gap-3 mb-4">
                <span className="text-3xl">{emoji}</span>
                <h3 className="text-xl font-bold capitalize">{category}</h3>
                <span className="text-gray-500">({vendors.length})</span>
              </div>

              {/* Vendor Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {vendors.map((vendor) => (
                  <div
                    key={vendor.id}
                    className="border rounded-lg overflow-hidden hover:shadow-lg transition-shadow"
                  >
                    {/* Vendor Image Placeholder */}
                    <div className={`h-40 bg-gradient-to-br ${gradientColor} flex items-center justify-center text-white text-5xl`}>
                      {emoji}
                    </div>

                    <div className="p-4">
                      {/* Header */}
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="text-lg font-bold">{vendor.name}</h4>
                        <div className="flex items-center gap-1">
                          <span className="text-yellow-500">⭐</span>
                          <span className="font-semibold text-sm">{vendor.rating.toFixed(1)}</span>
                        </div>
                      </div>

                      {/* Review Count */}
                      <p className="text-xs text-gray-500 mb-2">
                        {vendor.review_count} reviews
                      </p>

                      {/* Description */}
                      <p className="text-sm text-gray-700 mb-3">{vendor.description}</p>

                      {/* Services */}
                      <div className="mb-3">
                        <p className="text-xs font-semibold text-gray-600 mb-1">Services:</p>
                        <div className="flex flex-wrap gap-1">
                          {vendor.services.slice(0, 3).map((service, index) => (
                            <span
                              key={index}
                              className="px-2 py-1 bg-gray-100 text-xs rounded"
                            >
                              {service}
                            </span>
                          ))}
                          {vendor.services.length > 3 && (
                            <span className="px-2 py-1 bg-gray-100 text-xs rounded">
                              +{vendor.services.length - 3} more
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Pricing */}
                      <div className="mb-3 p-2 bg-gray-50 rounded">
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-gray-600">Average Price:</span>
                          <span className="text-sm font-bold">${vendor.avg_price}</span>
                        </div>
                      </div>

                      {/* Contact */}
                      <p className="text-xs text-gray-600 mb-3">
                        <strong>Contact:</strong>{' '}
                        <span className="text-blue-600">{vendor.contact}</span>
                      </p>

                      {/* AI Match Score */}
                      {vendor.similarity_score && (
                        <div className="mb-3 p-2 bg-purple-50 rounded">
                          <p className="text-xs text-purple-700">
                            🤖 AI Match Score: {(vendor.similarity_score * 100).toFixed(0)}%
                          </p>
                        </div>
                      )}

                      {/* Action Button */}
                      <button className="w-full bg-purple-600 text-white py-2 rounded hover:bg-purple-700 transition-colors text-sm">
                        Contact Vendor
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
