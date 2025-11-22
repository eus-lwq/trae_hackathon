import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, Polyline } from 'react-leaflet';
import L from 'leaflet';
import { Attraction } from '../data/mockPlaces';
import 'leaflet/dist/leaflet.css';

// Fix for default markers
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

interface InteractiveMapProps {
  attractions: Attraction[];
  selectedAttractions: string[];
  onAttractionClick: (id: string) => void;
  dayRoutes?: { day: number; color: string; stops: Attraction[] }[];
}

const MapController: React.FC<{ center: [number, number]; zoom: number }> = ({ center, zoom }) => {
  const map = useMap();
  React.useEffect(() => {
    map.setView(center, zoom);
  }, [map, center, zoom]);
  return null;
};

const RouteController: React.FC<{ points: [number, number][] | null }> = ({ points }) => {
  const map = useMap();
  React.useEffect(() => {
    if (points && points.length) {
      const bounds = L.latLngBounds(points.map(p => L.latLng(p[0], p[1])));
      map.fitBounds(bounds, { padding: [40, 40] });
    }
  }, [map, points]);
  return null;
};

const InteractiveMap: React.FC<InteractiveMapProps> = ({ 
  attractions, 
  selectedAttractions, 
  onAttractionClick,
  dayRoutes
}) => {
  const chongqingCenter: [number, number] = [29.5583, 106.5839];
  const mapZoom = 12;

  const getDayInfoFor = (id: string): { color: string; day: number } | null => {
    if (!dayRoutes) return null;
    for (const d of dayRoutes) {
      if (d.stops.some(s => s.id === id)) return { color: d.color, day: d.day };
    }
    return null;
  };

  const createCustomIcon = (emoji: string, isSelected: boolean, id: string) => {
    const dayInfo = getDayInfoFor(id);
    const borderColor = dayInfo?.color ?? (isSelected ? '#16a34a' : '#3b82f6');
    const borderWidth = isSelected ? 4 : 2;
    return L.divIcon({
      html: `
        <div class="relative">
          <div class="rounded-full w-12 h-12 flex items-center justify-center shadow-lg hover:shadow-xl transition-all duration-200 cursor-pointer" style="background:#ffffff;border:${borderWidth}px solid ${borderColor}">
            <span class="text-2xl">${emoji}</span>
          </div>
          ${dayInfo ? `<div class="absolute -top-1 -right-1 w-6 h-6 rounded-full text-white text-xs flex items-center justify-center" style="background:${dayInfo.color}">${dayInfo.day}</div>` : ''}
          ${isSelected && !dayInfo ? '<div class="absolute inset-0 rounded-full border-2 border-green-400 animate-pulse"></div>' : ''}
        </div>
      `,
      className: 'custom-marker-icon',
      iconSize: [48, 48],
      iconAnchor: [24, 24],
      popupAnchor: [0, -24]
    });
  };

  return (
    <div className="h-full w-full rounded-lg overflow-hidden shadow-lg">
      <AnyMapContainer
        center={chongqingCenter}
        zoom={mapZoom}
        className="h-full w-full"
        style={{ height: '100%', width: '100%' }}
      >
        <MapController center={chongqingCenter} zoom={mapZoom} />
        <RouteController points={dayRoutes ? dayRoutes.flatMap(d => d.stops.map(s => [s.coordinates.lat, s.coordinates.lng] as [number, number])) : null} />
        <AnyTileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {dayRoutes?.map((d) => (
          <Polyline
            key={`route-${d.day}`}
            positions={d.stops.map(s => [s.coordinates.lat, s.coordinates.lng])}
            pathOptions={{ color: d.color, weight: 4, opacity: 0.85 }}
          />
        ))}
        {attractions.map((attraction) => (
          <AnyMarker
            key={attraction.id}
            position={[attraction.coordinates.lat, attraction.coordinates.lng]}
            icon={createCustomIcon(
              attraction.emoji, 
              selectedAttractions.includes(attraction.id),
              attraction.id
            )}
            eventHandlers={{
              click: () => onAttractionClick(attraction.id),
            }}
          >
            <Popup>
              <div className="p-2 min-w-[200px]">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">{attraction.emoji}</span>
                  <div>
                    <h3 className="font-semibold text-gray-800">{attraction.name}</h3>
                    <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                      {attraction.category}
                    </span>
                  </div>
                </div>
                <p className="text-sm text-gray-600 mb-2">{attraction.description}</p>
                {attraction.rating && (
                  <div className="flex items-center gap-1 mb-1">
                    <span className="text-yellow-500">★</span>
                    <span className="text-sm font-medium">{attraction.rating}</span>
                  </div>
                )}
                {attraction.price && (
                  <p className="text-sm text-green-600 font-medium">{attraction.price}</p>
                )}
              </div>
            </Popup>
          </AnyMarker>
        ))}
      </AnyMapContainer>
    </div>
  );
};

export default InteractiveMap;
const AnyMapContainer = MapContainer as unknown as React.FC<any>;
const AnyTileLayer = TileLayer as unknown as React.FC<any>;
const AnyMarker = Marker as unknown as React.FC<any>;
