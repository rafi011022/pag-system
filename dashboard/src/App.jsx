// dashboard/src/App.jsx
import React, { useState, useEffect } from 'react';
import LoginPage from './LoginPage';
import FullMapView from './FullMapView';
import LowBandwidthView from './LowBandwidthView';

const STATS = [
  { label: "সক্রিয় সতর্কতা",  value: "৬",      icon: "⚠️",  color: "bg-red-50 text-red-700" },
  { label: "উচ্চ ঝুঁকি এলাকা", value: "২",      icon: "🔴",  color: "bg-orange-50 text-orange-700" },
  { label: "পর্যবেক্ষণ কেন্দ্র", value: "৪৮",    icon: "📡",  color: "bg-blue-50 text-blue-700" },
  { label: "SMS পাঠানো",        value: "১২,৩৪৫", icon: "📱",  color: "bg-green-50 text-green-700" },
];

const ROLE_BADGE = {
  admin:  "bg-red-100 text-red-700",
  ddm:    "bg-blue-100 text-blue-700",
  uno:    "bg-purple-100 text-purple-700",
  ngo:    "bg-yellow-100 text-yellow-700",
  viewer: "bg-gray-100 text-gray-700",
};

export default function App() {
  const [user, setUser]               = useState(null);
  const [lowBandwidth, setLowBandwidth] = useState(false);
  const [lastUpdate, setLastUpdate]   = useState(new Date().toLocaleTimeString('bn-BD'));

  // Restore session from localStorage
  useEffect(() => {
    const token = localStorage.getItem("pag_token");
    const saved = localStorage.getItem("pag_user");
    if (token && saved) setUser(JSON.parse(saved));
  }, []);

  useEffect(() => {
    if (!user) return;
    const id = setInterval(() => setLastUpdate(new Date().toLocaleTimeString('bn-BD')), 30000);
    return () => clearInterval(id);
  }, [user]);

  function handleLogin(userData) {
    setUser(userData);
    localStorage.setItem("pag_user", JSON.stringify(userData));
  }

  function handleLogout() {
    localStorage.removeItem("pag_token");
    localStorage.removeItem("pag_user");
    setUser(null);
  }

  if (!user) return <LoginPage onLogin={handleLogin} />;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-green-700 text-white shadow-lg">
        <div className="max-w-6xl mx-auto px-4 py-3 flex justify-between items-center">
          <div>
            <h1 className="text-xl font-bold">🌍 PAG System — বাংলাদেশ</h1>
            <p className="text-green-200 text-xs">Predictive Anticipatory Governance</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-green-200 text-xs hidden md:block">আপডেট: {lastUpdate}</span>
            <span className={`text-xs px-2 py-1 rounded-full font-semibold ${ROLE_BADGE[user.role] || ROLE_BADGE.viewer}`}>
              {user.role.toUpperCase()}
            </span>
            <span className="text-sm text-green-100">{user.full_name || user.username}</span>
            <button
              onClick={() => setLowBandwidth(!lowBandwidth)}
              className={`px-3 py-1 rounded-full text-xs font-semibold transition ${
                lowBandwidth ? 'bg-yellow-400 text-yellow-900' : 'bg-white text-green-800'
              }`}
            >
              {lowBandwidth ? '📶 লো-ব্যান্ড' : '🌐 ফুল'}
            </button>
            <button
              onClick={handleLogout}
              className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded-full text-xs font-semibold transition"
            >
              লগআউট
            </button>
          </div>
        </div>
      </header>

      {/* Stats */}
      <div className="max-w-6xl mx-auto px-4 py-4 grid grid-cols-2 md:grid-cols-4 gap-3">
        {STATS.map((s, i) => (
          <div key={i} className={`rounded-lg p-3 ${s.color} flex items-center gap-2 shadow-sm`}>
            <span className="text-2xl">{s.icon}</span>
            <div>
              <p className="text-xs opacity-70">{s.label}</p>
              <p className="text-lg font-bold">{s.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Main view */}
      <div className="max-w-6xl mx-auto px-4 pb-8">
        {lowBandwidth ? <LowBandwidthView /> : <FullMapView />}
      </div>

      <footer className="bg-gray-800 text-gray-400 text-center py-3 text-xs">
        PAG System v2.0 · © 2026 Nafiul Ahmad Rafi · MIT License
      </footer>
    </div>
  );
}
