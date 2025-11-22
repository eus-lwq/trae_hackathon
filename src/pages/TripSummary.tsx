import React, { useMemo } from 'react';
import { useTripStore } from '@/store/tripStore';
import { mockPlaces, Attraction } from '@/data/mockPlaces';
import InteractiveMap from '@/components/InteractiveMap';
import { cn } from '@/lib/utils';

type ItineraryStop = {
  time: string;
  attraction: Attraction;
};

type ItineraryDay = {
  title: string;
  intro: string;
  stops: ItineraryStop[];
};

const defaultTimes = ['10:00 AM', '2:00 PM', '6:00 PM'];

const buildItinerary = (selected: Attraction[]): ItineraryDay[] => {
  if (selected.length === 0) return [];
  const perDay = 3;
  const days: ItineraryDay[] = [];
  for (let i = 0; i < selected.length; i += perDay) {
    const slice = selected.slice(i, i + perDay);
    const dayIndex = days.length + 1;
    const title = dayIndex === 1 ? 'Arrival & Old Town Walk' : `City Highlights Day ${dayIndex}`;
    const intro = dayIndex === 1
      ? 'Start your journey exploring the historic old town. Visit charming cafes and get oriented with the city layout.'
      : 'Discover more of Chongqing\'s highlights with scenic views and local flavors.';
    days.push({
      title,
      intro,
      stops: slice.map((a, idx) => ({ time: defaultTimes[idx] ?? '4:00 PM', attraction: a })),
    });
  }
  return days;
};

const TripSummary: React.FC = () => {
  const { selectedAttractions } = useTripStore();

  const selected = useMemo(() => {
    return mockPlaces.filter(p => selectedAttractions.includes(p.id));
  }, [selectedAttractions]);

  const itinerary = useMemo(() => buildItinerary(selected), [selected]);

  const dayColors = ['#3b82f6', '#ef4444', '#10b981', '#8b5cf6', '#f59e0b', '#06b6d4'];
  const dayRoutes = useMemo(() => {
    return itinerary.map((d, i) => ({
      day: i + 1,
      color: dayColors[i % dayColors.length],
      stops: d.stops.map(s => s.attraction),
    }));
  }, [itinerary]);

  const exportPlan = () => {
    const payload = {
      createdAt: new Date().toISOString(),
      totalDays: itinerary.length,
      days: itinerary.map((d, di) => ({
        day: di + 1,
        title: d.title,
        intro: d.intro,
        stops: d.stops.map(s => ({ id: s.attraction.id, name: s.attraction.name, time: s.time }))
      })),
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'trip-plan.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-gradient-to-r from-teal-500 to-cyan-500 text-white p-6 rounded-b-xl shadow">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button onClick={() => history.back()} className="flex items-center gap-1 hover:opacity-90">
              <span className="text-xl">‹</span>
              <span>Back</span>
            </button>
            <div>
              <div className="text-2xl font-bold">Trip Summary</div>
              <div className="text-sm opacity-90">Your personalized travel plan</div>
            </div>
          </div>
          <button onClick={exportPlan} className="px-4 py-2 rounded-full bg-teal-600 hover:bg-teal-700 shadow">
            <span className="mr-2">⬇️</span> Export Plan
          </button>
        </div>
      </header>

      <div className="max-w-6xl mx-auto p-6">
        <div className="h-64 rounded-xl overflow-hidden bg-blue-50 border border-blue-100 shadow mb-2">
          <InteractiveMap
            attractions={selected.length ? selected : mockPlaces}
            selectedAttractions={selected.map(a => a.id)}
            onAttractionClick={() => {}}
            dayRoutes={dayRoutes}
          />
        </div>

        {dayRoutes.length > 0 && (
          <div className="mb-6 flex flex-wrap items-center gap-3 text-sm">
            {dayRoutes.map(dr => (
              <div key={dr.day} className="flex items-center gap-2">
                <span className="inline-block w-3 h-3 rounded-full" style={{ background: dr.color }}></span>
                <span className="text-gray-700">Day {dr.day}</span>
              </div>
            ))}
          </div>
        )}

        <h2 className="text-2xl font-bold mb-4">Daily Itinerary</h2>

        {itinerary.length === 0 && (
          <div className="rounded-lg bg-white shadow p-6 text-gray-600">No places selected yet. Go back to the planner and add attractions to your trip.</div>
        )}

        {itinerary.map((day, di) => (
          <section key={di} className="bg-white rounded-xl shadow mb-6">
            <div className="flex items-center justify-between p-4 border-b">
              <div className="flex items-center gap-3">
                <div className="w-7 h-7 rounded-full bg-blue-500 text-white flex items-center justify-center text-sm">{di + 1}</div>
                <div className="font-semibold">{day.title}</div>
              </div>
              <button className="text-gray-500 hover:text-gray-700">✎</button>
            </div>
            <div className="px-4 pb-4 text-gray-600">{day.intro}</div>
            <ul className="px-2 pb-4">
              {day.stops.map((s, si) => (
                <li key={si} className={cn('flex items-start gap-3 px-2 py-3 rounded-lg', 'hover:bg-gray-50')}> 
                  <div className="w-7 h-7 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center">📍</div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-gray-900">{s.attraction.name}</span>
                      <span className="text-xs uppercase text-gray-500">{s.time}</span>
                    </div>
                    <div className="text-sm text-gray-600">{s.attraction.description}</div>
                  </div>
                  <button className="text-gray-400 hover:text-gray-600">🗑️</button>
                </li>
              ))}
            </ul>
          </section>
        ))}
      </div>
    </div>
  );
};

export default TripSummary;
