'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { admin } from '@/lib/api';

interface Guest {
  id: string;
  name: string;
  email: string;
}

export default function NewReservation() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    startDate: '',
    endDate: '',
    guestId: '',
  });
  const [guests, setGuests] = useState<Guest[]>([]);
  const [error, setError] = useState('');
  const [showNewGuest, setShowNewGuest] = useState(false);
  const [newGuest, setNewGuest] = useState({
    name: '',
    email: '',
  });

  useEffect(() => {
    loadGuests();
  }, []);

  const loadGuests = async () => {
    try {
      const data = await admin.getGuests();
      setGuests(data);
    } catch (err) {
      setError('Failed to load guests');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await admin.createReservation(formData);
      router.push('/admin/dashboard');
    } catch (err) {
      setError('Failed to create reservation');
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleNewGuestSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const guest = await admin.createGuest(newGuest);
      setGuests(prev => [...prev, guest]);
      setShowNewGuest(false);
      setNewGuest({ name: '', email: '' });
      setFormData(prev => ({ ...prev, guestId: guest.id }));
    } catch (err) {
      setError('Failed to create guest');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
      <div className="relative py-3 sm:max-w-xl sm:mx-auto">
        <div className="relative px-4 py-10 bg-white mx-8 md:mx-0 shadow rounded-3xl sm:p-10">
          <div className="max-w-md mx-auto">
            <div className="divide-y divide-gray-200">
              <div className="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7">
                <h2 className="text-2xl font-bold mb-8">New Reservation</h2>

                {error && (
                  <div className="text-red-500 text-sm mb-4">{error}</div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Start Date
                    </label>
                    <input
                      type="date"
                      name="startDate"
                      required
                      value={formData.startDate}
                      onChange={handleChange}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      End Date
                    </label>
                    <input
                      type="date"
                      name="endDate"
                      required
                      value={formData.endDate}
                      onChange={handleChange}
                      className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    />
                  </div>

                  {!showNewGuest ? (
                    <>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Guest
                        </label>
                        <select
                          name="guestId"
                          required
                          value={formData.guestId}
                          onChange={handleChange}
                          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        >
                          <option value="">Select a guest</option>
                          {guests.map(guest => (
                            <option key={guest.id} value={guest.id}>
                              {guest.name} ({guest.email})
                            </option>
                          ))}
                        </select>
                      </div>

                      <button
                        type="button"
                        onClick={() => setShowNewGuest(true)}
                        className="text-indigo-600 hover:text-indigo-900 text-sm"
                      >
                        Add New Guest
                      </button>
                    </>
                  ) : (
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Guest Name
                        </label>
                        <input
                          type="text"
                          value={newGuest.name}
                          onChange={e => setNewGuest(prev => ({ ...prev, name: e.target.value }))}
                          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          Guest Email
                        </label>
                        <input
                          type="email"
                          value={newGuest.email}
                          onChange={e => setNewGuest(prev => ({ ...prev, email: e.target.value }))}
                          className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        />
                      </div>

                      <div className="flex space-x-4">
                        <button
                          type="button"
                          onClick={handleNewGuestSubmit}
                          className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium"
                        >
                          Add Guest
                        </button>
                        <button
                          type="button"
                          onClick={() => setShowNewGuest(false)}
                          className="text-gray-600 hover:text-gray-900 text-sm"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}

                  <div className="pt-5">
                    <div className="flex justify-end">
                      <button
                        type="submit"
                        className="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                      >
                        Create Reservation
                      </button>
                    </div>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
