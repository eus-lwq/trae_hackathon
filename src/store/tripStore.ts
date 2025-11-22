import { create } from 'zustand';
import { Attraction } from '../data/mockPlaces';
import { ChatMessage } from '../components/AIChatbot';

interface TripState {
  selectedAttractions: string[];
  filteredAttractions: Attraction[];
  selectedCategory: string;
  conversationHistory: ChatMessage[];
  selectedAttraction: Attraction | null;
  isDetailPanelOpen: boolean;
}

interface TripActions {
  addToTrip: (attractionId: string) => void;
  removeFromTrip: (attractionId: string) => void;
  setFilteredAttractions: (attractions: Attraction[]) => void;
  setSelectedCategory: (category: string) => void;
  addMessage: (message: ChatMessage) => void;
  openDetailPanel: (attraction: Attraction) => void;
  closeDetailPanel: () => void;
}

export const useTripStore = create<TripState & TripActions>((set, get) => ({
  // Initial state
  selectedAttractions: [],
  filteredAttractions: [],
  selectedCategory: 'All',
  conversationHistory: [],
  selectedAttraction: null,
  isDetailPanelOpen: false,

  // Actions
  addToTrip: (attractionId) => {
    const { selectedAttractions } = get();
    if (!selectedAttractions.includes(attractionId)) {
      set({ selectedAttractions: [...selectedAttractions, attractionId] });
    }
  },

  removeFromTrip: (attractionId) => {
    const { selectedAttractions } = get();
    set({ 
      selectedAttractions: selectedAttractions.filter(id => id !== attractionId) 
    });
  },

  setFilteredAttractions: (attractions) => {
    set({ filteredAttractions: attractions });
  },

  setSelectedCategory: (category) => {
    set({ selectedCategory: category });
  },

  addMessage: (message) => {
    const { conversationHistory } = get();
    set({ conversationHistory: [...conversationHistory, message] });
  },

  openDetailPanel: (attraction) => {
    set({ 
      selectedAttraction: attraction, 
      isDetailPanelOpen: true 
    });
  },

  closeDetailPanel: () => {
    set({ 
      selectedAttraction: null, 
      isDetailPanelOpen: false 
    });
  },
}));