// dashboard/src/LoginPage.jsx
import React, { useState } from 'react';

export default function LoginPage({ onLogin }) {
  const [form, setForm]     = useState({ username: "", password: "" });
  const [error, setError]   = useState("");
  const [loading, setLoading] = useState(false);

  const ROLE_LABELS = {
    admin: "System Admin",
    ddm:   "DDM Officer",
    uno:   "UNO Officer",
    ngo:   "NGO Worker",
    viewer: "Viewer",
  };

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Login failed");
      localStorage.setItem("pag_token", data.token);
      onLogin(data.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-800 to-green-600 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">🌍</div>
          <h1 className="text-2xl font-bold text-gray-800">PAG System</h1>
          <p className="text-gray-500 text-sm mt-1">Predictive Anticipatory Governance</p>
          <p className="text-gray-400 text-xs mt-1">বাংলাদেশ দুর্যোগ পূর্বাভাস সিস্টেম</p>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-3 mb-4 text-sm">
            ⚠️ {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              ব্যবহারকারীর নাম
            </label>
            <input
              type="text"
              required
              value={form.username}
              onChange={e => setForm({ ...form, username: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="username"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              পাসওয়ার্ড
            </label>
            <input
              type="password"
              required
              value={form.password}
              onChange={e => setForm({ ...form, password: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="••••••••"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-green-700 hover:bg-green-800 text-white font-semibold py-2 rounded-lg transition disabled:opacity-60"
          >
            {loading ? "লগইন হচ্ছে..." : "লগইন করুন"}
          </button>
        </form>

        {/* Role info */}
        <div className="mt-6 border-t pt-4">
          <p className="text-xs text-gray-400 text-center mb-2">উপলব্ধ ভূমিকা</p>
          <div className="flex flex-wrap gap-1 justify-center">
            {Object.entries(ROLE_LABELS).map(([role, label]) => (
              <span key={role} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                {label}
              </span>
            ))}
          </div>
        </div>

        <p className="text-center text-xs text-gray-400 mt-4">
          © 2026 Nafiul Ahmad Rafi · MIT License
        </p>
      </div>
    </div>
  );
}
