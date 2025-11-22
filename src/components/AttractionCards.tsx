import React from 'react';
import { Attraction } from '../data/mockPlaces';
import { Plus, Star, Clock, MapPin } from 'lucide-react';

interface AttractionCardsProps {
  attractions: Attraction[];
  selectedAttractions: string[];
  onAddToTrip: (id: string) => void;
  onViewDetails: (id: string) => void;
}

const AttractionCards: React.FC<AttractionCardsProps> = ({
  attractions,
  selectedAttractions,
  onAddToTrip,
  onViewDetails,
}) => {
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

  if (attractions.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500">
        <p className="text-lg">No attractions found</p>
        <p className="text-sm mt-2">Try adjusting your filters or search criteria</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
      {attractions.map((attraction) => {
        const isSelected = selectedAttractions.includes(attraction.id);
        
        return (
          <div
            key={attraction.id}
            className={`
              bg-white rounded-lg shadow-md hover:shadow-lg transition-all duration-200 
              overflow-hidden transform hover:scale-105 cursor-pointer
              ${isSelected ? 'ring-2 ring-green-500' : ''}
            `}
            onClick={() => onViewDetails(attraction.id)}
          >
            {/* Card Header */}
            <div className="p-4 pb-2">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{attraction.emoji}</span>
                  <div>
                    <h3 className="font-semibold text-gray-800 text-lg">{attraction.name}</h3>
                    <span className={`inline-block text-xs px-2 py-1 rounded-full ${getCategoryColor(attraction.category)}`}>
                      {attraction.category}
                    </span>
                  </div>
                </div>
              </div>
              
              {/* Description */}
              <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                {attraction.description}
              </p>
              
              {/* Rating and Price */}
              <div className="flex items-center justify-between mb-3">
                {attraction.rating && (
                  <div className="flex items-center gap-1">
                    <Star className="w-4 h-4 text-yellow-500 fill-current" />
                    <span className="text-sm font-medium text-gray-700">{attraction.rating}</span>
                  </div>
                )}
                {attraction.price && (
                  <span className="text-sm font-medium text-green-600">{attraction.price}</span>
                )}
              </div>
              
              {/* Opening Hours */}
              {attraction.openingHours && (
                <div className="flex items-center gap-2 text-xs text-gray-500 mb-3">
                  <Clock className="w-3 h-3" />
                  <span>{attraction.openingHours}</span>
                </div>
              )}
            </div>
            
            {/* Add to Trip Button */}
            <div className="px-4 pb-4">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onAddToTrip(attraction.id);
                }}
                className={`
                  w-full py-2 px-4 rounded-lg font-medium transition-all duration-200
                  flex items-center justify-center gap-2
                  ${
                    isSelected
                      ? 'bg-green-500 text-white hover:bg-green-600'
                      : 'bg-blue-500 text-white hover:bg-blue-600'
                  }
                `}
              >
                <Plus className="w-4 h-4" />
                {isSelected ? 'Added to Trip' : 'Add to Trip'}
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default AttractionCards;