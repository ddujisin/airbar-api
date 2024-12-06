'use client';

import React, { useState, useEffect } from 'react';
import { guests } from '@/lib/api';
import type { Guest } from '@/types/api';

export default function GuestsPage() {
  const [guestList, setGuestList] = useState<Guest[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newGuest, setNewGuest] = useState({ name: '', email: '' });
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    fetchGuests();
  }, []);

  const fetchGuests = async () => {
    try {
      const data = await guests.getAll();
      setGuestList(data);
    } catch (err) {
      setError('Failed to load guests');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await guests.create(newGuest);
      setNewGuest({ name: '', email: '' });
      setShowForm(false);
      await fetchGuests();
    } catch (err) {
      setError('Failed to create guest');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Guests</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          {showForm ? 'Cancel' : 'Add Guest'}
        </button>
      </div>

      {error && (
        <div className="text-red-500 mb-4">{error}</div>
      )}

      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 border rounded-lg">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Name</label>
              <input
                type="text"
                value={newGuest.name}
                onChange={(e) => setNewGuest({ ...newGuest, name: e.target.value })}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Email</label>
              <input
                type="email"
                value={newGuest.email}
                onChange={(e) => setNewGuest({ ...newGuest, email: e.target.value })}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                required
              />
            </div>
            <button
              type="submit"
              className="w-full bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700"
            >
              Create Guest
            </button>
          </div>
        </form>
      )}

      <div className="grid gap-4">
        {guestList.map((guest) => (
          <div key={guest.id} className="border p-4 rounded-lg">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-xl font-semibold">{guest.name}</h2>
                <p className="text-gray-600">{guest.email}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
