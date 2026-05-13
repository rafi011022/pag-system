// dashboard/src/FullMapView.jsx
import React, { useEffect, useRef } from 'react';

const RISK_DATA = [
  { region: "সিলেট", lat: 24.89, lon: 91.88, risk: 0.9, type: "বন্যা" },
  { region: "কুড়িগ্রাম", lat: 25.81, lon: 89.63, risk: 0.85, type: "বন্যা" },
  { region: "চট্টগ্রাম", lat: 22.34, lon: 91.81, risk: 0.7, type: "ঘূর্ণিঝড়" },
  { region: "ঢাকা", lat: 23.81, lon: 90.41, risk: 0.5, type: "বন্যা" },
  { region: "বরিশাল", lat: 22.70, lon: 90.36, risk: 0.6, type: "ঘূর্ণিঝড়" },
  { region: "খুলনা", lat: 22.84, lon: 89.54, risk: 0.4, type: "খরা" },
];

function riskColor(risk) {
  if (risk >= 0.8) return "red";
  if (risk >= 0.5) return "orange";
  return "green";
}

export default function FullMapView() {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);

  useEffect(() => {
    if (mapInstance.current || !window.L) return;
    const L = window.L;
    const map = L.map(mapRef.current).setView([23.68, 90.35], 7);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    RISK_DATA.forEach(d => {
      const circle = L.circle([d.lat, d.lon], {
        color: riskColor(d.risk),
        fillColor: riskColor(d.risk),
        fillOpacity: 0.6,
        radius: d.risk * 50000
      }).addTo(map);
      circle.bindPopup(`
        <b>${d.region}</b><br/>
        দুর্যোগ: ${d.type}<br/>
        ঝুঁকি স্কোর: ${Math.round(d.risk * 100)}%
      `);
    });
    mapInstance.current = map;
  }, []);

  return (
    <div className="p-4">
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-3 border-b border-gray-200">
          <h2 className="font-bold text-gray-800">🗺️ ইন্টারেক্টিভ ঝুঁকি মানচিত্র (Leaflet)</h2>
        </div>
        <div ref={mapRef} style={{ height: '450px', width: '100%' }} />
      </div>
    </div>
  );
}
