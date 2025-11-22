import React, { useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import InteractiveMap from '../components/InteractiveMap';
import CategorySelector from '../components/CategorySelector';
import AttractionCards from '../components/AttractionCards';
import AIChatbot from '../components/AIChatbot';
import PlaceDetailPanel from '../components/PlaceDetailPanel';
import { useTripStore } from '../store/tripStore';
import { mockPlaces } from '../data/mockPlaces';

const Planner: React.FC = () => {
  const navigate = useNavigate();
  const {
    selectedAttractions,
    filteredAttractions,
    selectedCategory,
    conversationHistory,
    selectedAttraction,
    isDetailPanelOpen,
    addToTrip,
    setFilteredAttractions,
    setSelectedCategory,
    addMessage,
    openDetailPanel,
    closeDetailPanel,
  } = useTripStore();

  // Initialize with all attractions
  useEffect(() => {
    setFilteredAttractions(mockPlaces);
  }, [setFilteredAttractions]);

  // Filter attractions based on selected category
  const displayAttractions = useMemo(() => {
    if (selectedCategory === 'All') {
      return filteredAttractions.length > 0 ? filteredAttractions : mockPlaces;
    }
    const baseAttractions = filteredAttractions.length > 0 ? filteredAttractions : mockPlaces;
    return baseAttractions.filter(attraction => attraction.category === selectedCategory);
  }, [selectedCategory, filteredAttractions]);

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category);
  };

  const handleAddToTrip = (attractionId: string) => {
    addToTrip(attractionId);
  };

  const handleAttractionClick = (attractionId: string) => {
    const attraction = mockPlaces.find(p => p.id === attractionId);
    if (attraction) {
      openDetailPanel(attraction);
    }
  };

  const handleViewDetails = (attractionId: string) => {
    const attraction = mockPlaces.find(p => p.id === attractionId);
    if (attraction) {
      openDetailPanel(attraction);
    }
  };

  const handleAIChatFilter = (attractions: any[]) => {
    setFilteredAttractions(attractions);
  };

  const handleNewMessage = (message: any) => {
    addMessage(message);
  };

  return (
    <div className="h-screen bg-gray-50 flex">
      {/* Left Side - Map and Attractions */}
      <div className="flex-1 flex flex-col">
        {/* Top Half - Map */}
        <div className="h-1/2 p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="text-lg font-semibold">Planner</div>
            <button
              onClick={() => navigate('/summary')}
              className="px-3 py-1.5 rounded-full bg-teal-600 text-white hover:bg-teal-700"
            >
              View Trip Summary
            </button>
          </div>
          <InteractiveMap
            attractions={displayAttractions}
            selectedAttractions={selectedAttractions}
            onAttractionClick={handleAttractionClick}
          />
        </div>

        {/* Bottom Half - Category Selector and Cards */}
        <div className="h-1/2 flex flex-col overflow-hidden">
          {/* Category Selector */}
          <div className="p-4 pb-2">
            <CategorySelector
              attractions={mockPlaces}
              selectedCategory={selectedCategory}
              onCategoryChange={handleCategoryChange}
            />
          </div>

          {/* Attraction Cards - Scrollable */}
          <div className="flex-1 overflow-y-auto">
            <AttractionCards
              attractions={displayAttractions}
              selectedAttractions={selectedAttractions}
              onAddToTrip={handleAddToTrip}
              onViewDetails={handleViewDetails}
            />
          </div>
        </div>
      </div>

      {/* Right Side - AI Chatbot */}
      <div className="w-96 p-4">
        <AIChatbot
          attractions={mockPlaces}
          onFilterUpdate={handleAIChatFilter}
          conversationHistory={conversationHistory}
          onNewMessage={handleNewMessage}
        />
      </div>

      {/* Place Detail Panel Overlay */}
      <PlaceDetailPanel
        attraction={selectedAttraction}
        isOpen={isDetailPanelOpen}
        onClose={closeDetailPanel}
      />
    </div>
  );
};

export default Planner;
