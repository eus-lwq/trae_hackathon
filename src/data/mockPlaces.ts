export interface Attraction {
  id: string;
  name: string;
  emoji: string;
  category: 'Scenic' | 'Culture' | 'Food' | 'Photo' | 'Hidden';
  description: string;
  coordinates: {
    lat: number;
    lng: number;
  };
  images?: string[];
  rating?: number;
  openingHours?: string;
  price?: string;
}

export const mockPlaces: Attraction[] = [
  {
    id: '1',
    name: '洪崖洞',
    emoji: '🏮',
    category: 'Scenic',
    description: 'Traditional stilted buildings with stunning night views over the Jialing River',
    coordinates: { lat: 29.5583, lng: 106.5839 },
    rating: 4.5,
    openingHours: '9:00 AM - 10:00 PM',
    price: 'Free'
  },
  {
    id: '2',
    name: '解放碑',
    emoji: '🏢',
    category: 'Culture',
    description: 'Historic monument and bustling commercial center of Chongqing',
    coordinates: { lat: 29.5587, lng: 106.5748 },
    rating: 4.3,
    openingHours: '24 hours',
    price: 'Free'
  },
  {
    id: '3',
    name: '磁器口古镇',
    emoji: '🏮',
    category: 'Culture',
    description: 'Ancient town with traditional architecture and local crafts',
    coordinates: { lat: 29.5434, lng: 106.4572 },
    rating: 4.4,
    openingHours: '8:00 AM - 6:00 PM',
    price: 'Free'
  },
  {
    id: '4',
    name: '重庆火锅一条街',
    emoji: '🍲',
    category: 'Food',
    description: 'Famous hot pot district with authentic Chongqing spicy hot pot',
    coordinates: { lat: 29.5634, lng: 106.5487 },
    rating: 4.7,
    openingHours: '11:00 AM - 2:00 AM',
    price: '¥80-150 per person'
  },
  {
    id: '5',
    name: '长江索道',
    emoji: '🚠',
    category: 'Scenic',
    description: 'Scenic cable car ride across the Yangtze River with city views',
    coordinates: { lat: 29.5487, lng: 106.5891 },
    rating: 4.2,
    openingHours: '7:30 AM - 9:30 PM',
    price: '¥20 one way'
  },
  {
    id: '6',
    name: '南山一棵树',
    emoji: '🌳',
    category: 'Photo',
    description: 'Panoramic viewpoint offering the best night views of Chongqing',
    coordinates: { lat: 29.5167, lng: 106.6067 },
    rating: 4.6,
    openingHours: '6:00 AM - 11:00 PM',
    price: '¥30'
  },
  {
    id: '7',
    name: '小天鹅火锅',
    emoji: '🦢',
    category: 'Food',
    description: 'Iconic Chongqing hot pot restaurant with traditional recipes',
    coordinates: { lat: 29.5512, lng: 106.5698 },
    rating: 4.4,
    openingHours: '10:00 AM - 10:00 PM',
    price: '¥60-120 per person'
  },
  {
    id: '8',
    name: '鹅岭二厂',
    emoji: '🏭',
    category: 'Photo',
    description: 'Creative industrial park with art installations and city views',
    coordinates: { lat: 29.5445, lng: 106.5212 },
    rating: 4.3,
    openingHours: '10:00 AM - 8:00 PM',
    price: 'Free'
  },
  {
    id: '9',
    name: '朝天门',
    emoji: '⛵',
    category: 'Scenic',
    description: 'Historic port where the Yangtze and Jialing rivers meet',
    coordinates: { lat: 29.5634, lng: 106.5891 },
    rating: 4.1,
    openingHours: '24 hours',
    price: 'Free'
  },
  {
    id: '10',
    name: '十八梯',
    emoji: '🪜',
    category: 'Hidden',
    description: 'Traditional hillside neighborhood with steep stairways and old Chongqing charm',
    coordinates: { lat: 29.5512, lng: 106.5745 },
    rating: 4.0,
    openingHours: '24 hours',
    price: 'Free'
  },
  {
    id: '11',
    name: '重庆小面街',
    emoji: '🍜',
    category: 'Food',
    description: 'Street dedicated to Chongqing\'s famous spicy noodles',
    coordinates: { lat: 29.5489, lng: 106.5623 },
    rating: 4.5,
    openingHours: '6:00 AM - 10:00 PM',
    price: '¥10-25 per bowl'
  },
  {
    id: '12',
    name: '白公馆',
    emoji: '🏛️',
    category: 'Culture',
    description: 'Historic site and former residence with cultural significance',
    coordinates: { lat: 29.5345, lng: 106.5234 },
    rating: 4.2,
    openingHours: '9:00 AM - 5:00 PM',
    price: '¥20'
  },
  {
    id: '13',
    name: '渣滓洞',
    emoji: '⛓️',
    category: 'Hidden',
    description: 'Historical prison site with important revolutionary history',
    coordinates: { lat: 29.5323, lng: 106.5212 },
    rating: 4.1,
    openingHours: '9:00 AM - 5:00 PM',
    price: '¥15'
  },
  {
    id: '14',
    name: '李子坝轻轨站',
    emoji: '🚇',
    category: 'Photo',
    description: 'Famous monorail station where the train passes through a building',
    coordinates: { lat: 29.5412, lng: 106.5234 },
    rating: 4.3,
    openingHours: '6:00 AM - 11:00 PM',
    price: '¥2-10 per ride'
  },
  {
    id: '15',
    name: '山城步道',
    emoji: '🚶',
    category: 'Hidden',
    description: 'Scenic walking path along the mountain with city views',
    coordinates: { lat: 29.5456, lng: 106.5345 },
    rating: 4.0,
    openingHours: '24 hours',
    price: 'Free'
  }
];