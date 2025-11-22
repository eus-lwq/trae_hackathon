import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">Chongqing Trip Planner</h1>
        <p className="text-lg text-gray-600 mb-8">Discover amazing attractions with our AI-powered trip planner</p>
        <Link
          to="/planner"
          className="inline-block bg-blue-500 text-white px-8 py-3 rounded-lg hover:bg-blue-600 transition-colors duration-200 font-medium"
        >
          Start Planning Your Trip
        </Link>
      </div>
    </div>
  );
}