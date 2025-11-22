import React from 'react';
import { X, Star, Clock, MapPin, Globe, Phone } from 'lucide-react';
import { Attraction } from '../data/mockPlaces';

interface PlaceDetailPanelProps {
  attraction: Attraction | null;
  isOpen: boolean;
  onClose: () => void;
}

const PlaceDetailPanel: React.FC<PlaceDetailPanelProps> = ({
  attraction,
  isOpen,
  onClose,
}) => {
  if (!isOpen || !attraction) return null;

  const getCategoryColor = (category: string) => {
    const colors = {
      Scenic: 'bg-blue-100 text-blue-800',
      Culture: 'bg-purple-100 text-purple-800',
      Food: 'bg-red-100 text-red-800',
      Photo: 'bg-pink-100 text-pink-800',
      Hidden: 'bg-green-100 text-green-800',
    };
    return colors[category as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-3xl">{attraction.emoji}</span>
            <div>
              <h2 className="text-xl font-bold text-gray-800">{attraction.name}</h2>
              <span className={`inline-block text-sm px-2 py-1 rounded-full ${getCategoryColor(attraction.category)}`}>
                {attraction.category}
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors duration-200"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Description */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">Description</h3>
            <p className="text-gray-600 leading-relaxed">{attraction.description}</p>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Rating */}
            {attraction.rating && (
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <Star className="w-5 h-5 text-yellow-500 fill-current" />
                <div>
                  <p className="text-sm text-gray-600">Rating</p>
                  <p className="font-semibold text-gray-800">{attraction.rating} / 5.0</p>
                </div>
              </div>
            )}

            {/* Opening Hours */}
            {attraction.openingHours && (
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <Clock className="w-5 h-5 text-blue-500" />
                <div>
                  <p className="text-sm text-gray-600">Opening Hours</p>
                  <p className="font-semibold text-gray-800">{attraction.openingHours}</p>
                </div>
              </div>
            )}

            {/* Price */}
            {attraction.price && (
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="w-5 h-5 flex items-center justify-center">
                  <span className="text-green-600 font-bold">¥</span>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Price</p>
                  <p className="font-semibold text-gray-800">{attraction.price}</p>
                </div>
              </div>
            )}

            {/* Location */}
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <MapPin className="w-5 h-5 text-red-500" />
              <div>
                <p className="text-sm text-gray-600">Coordinates</p>
                <p className="font-semibold text-gray-800 text-sm">
                  {attraction.coordinates.lat.toFixed(4)}, {attraction.coordinates.lng.toFixed(4)}
                </p>
              </div>
            </div>
          </div>

          {/* Images Placeholder */}
          {attraction.images && attraction.images.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">Images</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {attraction.images.map((image, index) => (
                  <div key={index} className="aspect-square bg-gray-200 rounded-lg flex items-center justify-center">
                    <span className="text-gray-400 text-sm">Image {index + 1}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4 border-t border-gray-200">
            <button className="flex-1 bg-blue-500 text-white py-3 px-4 rounded-lg hover:bg-blue-600 transition-colors duration-200 font-medium">
              Add to Trip
            </button>
            <button className="flex-1 bg-gray-100 text-gray-700 py-3 px-4 rounded-lg hover:bg-gray-200 transition-colors duration-200 font-medium">
              Get Directions
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlaceDetailPanel;