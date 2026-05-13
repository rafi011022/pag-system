// dashboard/src/LowBandwidthView.jsx
import React from 'react';
import SVGMap from './SVGMap';

const ALERTS = [
  { region: "সিলেট", risk: "উচ্চ", type: "বন্যা", score: 90 },
  { region: "কুড়িগ্রাম", risk: "উচ্চ", type: "বন্যা", score: 85 },
  { region: "চট্টগ্রাম", risk: "মধ্যম", type: "ঘূর্ণিঝড়", score: 70 },
  { region: "ঢাকা", risk: "মধ্যম", type: "বন্যা", score: 50 },
  { region: "বরিশাল", risk: "মধ্যম", type: "ঘূর্ণিঝড়", score: 60 },
  { region: "খুলনা", risk: "নিম্ন", type: "খরা", score: 40 },
];

function riskBadge(risk) {
  if (risk === "উচ্চ") return "bg-red-100 text-red-700";
  if (risk === "মধ্যম") return "bg-yellow-100 text-yellow-700";
  return "bg-green-100 text-green-700";
}

export default function LowBandwidthView() {
  return (
    <div className="p-4 space-y-4">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <p className="text-blue-800 text-sm font-semibold">📶 লো-ব্যান্ডউইথ মোড সক্রিয় (~50KB)</p>
        <p className="text-blue-600 text-xs mt-1">২জি নেটওয়ার্কের জন্য অপ্টিমাইজড ভিউ</p>
      </div>
      <SVGMap />
      <div className="bg-white rounded-lg shadow">
        <div className="p-3 border-b border-gray-200">
          <h2 className="font-bold text-gray-800">⚠️ সক্রিয় সতর্কতা</h2>
        </div>
        {ALERTS.map((a, i) => (
          <div key={i} className="p-3 border-b border-gray-100 flex justify-between items-center">
            <div>
              <span className="font-semibold text-gray-800">{a.region}</span>
              <span className="text-gray-500 text-sm ml-2">({a.type})</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-20 bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${a.score >= 80 ? 'bg-red-500' : a.score >= 50 ? 'bg-yellow-500' : 'bg-green-500'}`}
                  style={{ width: `${a.score}%` }}
                />
              </div>
              <span className={`text-xs px-2 py-1 rounded-full font-semibold ${riskBadge(a.risk)}`}>
                {a.risk}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
