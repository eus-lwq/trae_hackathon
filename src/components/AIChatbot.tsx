import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles } from 'lucide-react';
import { Attraction } from '../data/mockPlaces';

export interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

interface AIChatbotProps {
  attractions: Attraction[];
  onFilterUpdate: (filteredAttractions: Attraction[]) => void;
  conversationHistory: ChatMessage[];
  onNewMessage: (message: ChatMessage) => void;
}

const AIChatbot: React.FC<AIChatbotProps> = ({
  attractions,
  onFilterUpdate,
  conversationHistory,
  onNewMessage,
}) => {
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversationHistory]);

  const processAIQuery = (query: string): Attraction[] => {
    const lowerQuery = query.toLowerCase();
    
    // Simple keyword-based filtering (simulating AI understanding)
    const keywords = {
      'food': ['food', 'restaurant', 'eat', 'dining', 'cuisine', 'hot pot', 'noodles', 'meal'],
      'scenic': ['scenic', 'view', 'landscape', 'beautiful', 'sightseeing', 'nature', 'river', 'mountain'],
      'culture': ['culture', 'historic', 'traditional', 'heritage', 'museum', 'temple', 'ancient'],
      'photo': ['photo', 'picture', 'photography', 'instagram', 'selfie', 'photogenic'],
      'hidden': ['hidden', 'secret', 'local', 'off beaten path', 'unknown', 'quiet', 'peaceful'],
      'night': ['night', 'evening', 'dark', 'illuminated', 'lights', 'night view'],
      'free': ['free', 'no cost', 'budget', 'cheap', 'no charge'],
      'river': ['river', 'yangtze', 'jialing', 'water', 'riverside'],
      'shopping': ['shopping', 'market', 'buy', 'shop', 'store', 'commercial'],
      'traditional': ['traditional', 'old', 'historic', 'ancient', 'classic']
    };

    let filtered = attractions;

    // Check for category-specific keywords
    for (const [category, categoryKeywords] of Object.entries(keywords)) {
      if (categoryKeywords.some(keyword => lowerQuery.includes(keyword))) {
        if (['food', 'scenic', 'culture', 'photo', 'hidden'].includes(category)) {
          filtered = filtered.filter(attraction => 
            attraction.category.toLowerCase() === category
          );
        } else if (category === 'night') {
          filtered = filtered.filter(attraction => 
            attraction.openingHours?.includes('PM') || 
            attraction.openingHours === '24 hours'
          );
        } else if (category === 'free') {
          filtered = filtered.filter(attraction => 
            attraction.price?.toLowerCase().includes('free')
          );
        } else if (category === 'river') {
          filtered = filtered.filter(attraction => 
            attraction.description.toLowerCase().includes('river') ||
            attraction.name.toLowerCase().includes('river')
          );
        } else if (category === 'shopping') {
          filtered = filtered.filter(attraction => 
            attraction.category === 'Culture' && 
            (attraction.name.toLowerCase().includes('street') || 
             attraction.description.toLowerCase().includes('market') ||
             attraction.description.toLowerCase().includes('commercial'))
          );
        } else if (category === 'traditional') {
          filtered = filtered.filter(attraction => 
            attraction.description.toLowerCase().includes('traditional') ||
            attraction.description.toLowerCase().includes('ancient') ||
            attraction.name.toLowerCase().includes('ancient')
          );
        }
      }
    }

    // If no specific category found, do a general text search
    if (filtered.length === attractions.length) {
      filtered = attractions.filter(attraction => 
        attraction.name.toLowerCase().includes(lowerQuery) ||
        attraction.description.toLowerCase().includes(lowerQuery) ||
        attraction.category.toLowerCase().includes(lowerQuery)
      );
    }

    return filtered;
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    onNewMessage(userMessage);
    setInputValue('');
    setIsTyping(true);

    // Simulate AI processing time
    setTimeout(() => {
      const filteredAttractions = processAIQuery(inputValue);
      onFilterUpdate(filteredAttractions);

      const aiResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: `I found ${filteredAttractions.length} attraction${filteredAttractions.length !== 1 ? 's' : ''} that match your request. ${
          filteredAttractions.length > 0 
            ? `Here are some great options for "${inputValue}":`
            : 'Try rephrasing your request or exploring different categories.'
        }`,
        sender: 'ai',
        timestamp: new Date(),
      };

      onNewMessage(aiResponse);
      setIsTyping(false);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const exampleQueries = [
    "Show me food places",
    "Find scenic spots near the river", 
    "Where can I take good photos?",
    "What are some hidden gems?",
    "Show me cultural sites",
    "Free attractions"
  ];

  const sendExampleQuery = (query: string) => {
    setInputValue(query);
    setTimeout(() => {
      handleSendMessage();
    }, 100);
  };

  return (
    <div className="h-full flex flex-col bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center gap-2">
          <Bot className="w-6 h-6 text-blue-500" />
          <h2 className="text-lg font-semibold text-gray-800">AI Travel Assistant</h2>
          <Sparkles className="w-4 h-4 text-yellow-500" />
        </div>
        <p className="text-sm text-gray-600 mt-1">Ask me about attractions, food, or activities!</p>
      </div>

      {/* Example Queries */}
      {conversationHistory.length === 0 && (
        <div className="p-4 border-b border-gray-100">
          <p className="text-sm text-gray-600 mb-3">Try asking:</p>
          <div className="flex flex-wrap gap-2">
            {exampleQueries.map((query, index) => (
              <button
                key={index}
                onClick={() => sendExampleQuery(query)}
                className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1 rounded-full transition-colors duration-200"
              >
                {query}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {conversationHistory.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {message.sender === 'ai' && (
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-white" />
              </div>
            )}
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.sender === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              <p className="text-sm">{message.content}</p>
              <p className={`text-xs mt-1 ${
                message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
              }`}>
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
            {message.sender === 'user' && (
              <div className="w-8 h-8 bg-gray-500 rounded-full flex items-center justify-center flex-shrink-0">
                <User className="w-4 h-4 text-white" />
              </div>
            )}
          </div>
        ))}
        
        {isTyping && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about attractions, food, or activities..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isTyping}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors duration-200"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIChatbot;