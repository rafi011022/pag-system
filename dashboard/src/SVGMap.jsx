// dashboard/src/SVGMap.jsx
import React from 'react';

const REGIONS = [
  { name: "সিলেট", x: 310, y: 120, risk: 0.9, type: "বন্যা" },
  { name: "ঢাকা", x: 230, y: 200, risk: 0.5, type: "বন্যা" },
  { name: "চট্টগ্রাম", x: 320, y: 270, risk: 0.7, type: "ঘূর্ণিঝড়" },
  { name: "কুড়িগ্রাম", x: 160, y: 100, risk: 0.85, type: "বন্যা" },
  { name: "বরিশাল", x: 200, y: 300, risk: 0.6, type: "ঘূর্ণিঝড়" },
  { name: "খুলনা", x: 140, y: 290, risk: 0.4, type: "খরা" },
];

function riskColor(risk) {
  if (risk >= 0.8) return "#ef4444";
  if (risk >= 0.5) return "#f59e0b";
  return "#22c55e";
}

export default function SVGMap() {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-lg font-bold mb-2 text-gray-800">বাংলাদেশ ঝুঁকি মানচিত্র (SVG)</h2>
      <svg viewBox="0 0 450 420" width="100%" style={{ border: "1px solid #e5e7eb", borderRadius: 8 }}>
        <rect width="450" height="420" fill="#dbeafe" />
        <text x="225" y="30" textAnchor="middle" fontSize="16" fill="#1e40af" fontWeight="bold">
          বাংলাদেশ দুর্যোগ ঝুঁকি মানচিত্র
        </text>
        {REGIONS.map((r) => (
          <g key={r.name}>
            <circle cx={r.x} cy={r.y} r={20} fill={riskColor(r.risk)} opacity={0.8} />
            <text x={r.x} y={r.y + 5} textAnchor="middle" fontSize="9" fill="white" fontWeight="bold">
              {Math.round(r.risk * 100)}%
            </text>
            <text x={r.x} y={r.y + 35} textAnchor="middle" fontSize="10" fill="#1f2937">
              {r.name}
            </text>
            <text x={r.x} y={r.y + 47} textAnchor="middle" fontSize="9" fill="#6b7280">
              {r.type}
            </text>
          </g>
        ))}
        <g>
          <rect x="10" y="370" width="15" height="15" fill="#ef4444" rx="3" />
          <text x="30" y="382" fontSize="10" fill="#374151">উচ্চ ঝুঁকি (≥80%)</text>
          <rect x="120" y="370" width="15" height="15" fill="#f59e0b" rx="3" />
          <text x="140" y="382" fontSize="10" fill="#374151">মধ্যম ঝুঁকি (50-79%)</text>
          <rect x="260" y="370" width="15" height="15" fill="#22c55e" rx="3" />
          <text x="280" y="382" fontSize="10" fill="#374151">নিম্ন ঝুঁকি (&lt;50%)</text>
        </g>
      </svg>
    </div>
  );
}
