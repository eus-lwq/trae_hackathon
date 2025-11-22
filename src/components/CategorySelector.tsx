import React from 'react';
import { Attraction } from '../data/mockPlaces';

interface CategorySelectorProps {
  attractions: Attraction[];
  selectedCategory: string;
  onCategoryChange: (category: string) => void;
}

const CategorySelector: React.FC<CategorySelectorProps> = ({
  attractions,
  selectedCategory,
  onCategoryChange,
}) => {
  const categories = [
    { name: 'All', color: 'bg-gray-500' },
    { name: 'Scenic', color: 'bg-blue-500' },
    { name: 'Culture', color: 'bg-purple-500' },
    { name: 'Food', color: 'bg-red-500' },
    { name: 'Photo', color: 'bg-pink-500' },
    { name: 'Hidden', color: 'bg-green-500' },
  ];

  const getCategoryCount = (category: string) => {
    if (category === 'All') return attractions.length;
    return attractions.filter(attraction => attraction.category === category).length;
  };

  return (
    <div className="p-4 bg-white rounded-lg shadow-md">
      <h3 className="text-lg font-semibold text-gray-800 mb-3">Filter by Category</h3>
      <div className="flex flex-wrap gap-2">
        {categories.map((category) => {
          const count = getCategoryCount(category.name);
          const isSelected = selectedCategory === category.name;
          
          return (
            <button
              key={category.name}
              onClick={() => onCategoryChange(category.name)}
              className={`
                px-4 py-2 rounded-full text-sm font-medium transition-all duration-200
                flex items-center gap-2 hover:shadow-md transform hover:scale-105
                ${
                  isSelected
                    ? `${category.color} text-white shadow-lg`
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }
              `}
            >
              <span>{category.name}</span>
              <span className={`
                text-xs px-2 py-1 rounded-full
                ${
                  isSelected
                    ? 'bg-white bg-opacity-30 text-white'
                    : 'bg-gray-300 text-gray-600'
                }
              `}>
                {count}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default CategorySelector;