'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { reservations, guests } from '@/lib/api';
import type { Reservation, Guest } from '@/types/api';

export default function ReservationsPage() {
  const router = useRouter();
  const [reservationList, setReservationList] = useState<Reservation[]>([]);
  const [guestList, setGuestList] = useState<Guest[]>([]);
  const [error, setError] = useState('');
  const [showPinCode, setShowPinCode] = useState<string | null>(null);

  useEffect(() => {
    loadReservations();
    loadGuests();
  }, []);

  const loadReservations = async () => {
    try {
      const data = await reservations.getAll();
      setReservationList(data);
    } catch (err) {
      setError('Failed to load reservations');
    }
  };

  const loadGuests = async () => {
    try {
      const data = await guests.getAll();
      setGuestList(data);
    } catch (err) {
      setError('Failed to load guests');
    }
  };

  const togglePinCode = (reservationId: string) => {
    setShowPinCode(showPinCode === reservationId ? null : reservationId);
  };

  return (
    <div className="min-h-screen bg-gray-100 py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Reservations</h1>
          <button
            onClick={() => router.push('/admin/reservations/new')}
            className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium"
          >
            New Reservation
          </button>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {reservationList.map((reservation) => (
              <li key={reservation.id} className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">
                      {reservation.guest.name}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {new Date(reservation.startDate).toLocaleDateString()} - {new Date(reservation.endDate).toLocaleDateString()}
                    </p>
                    {showPinCode === reservation.id && (
                      <p className="text-sm font-medium text-gray-900 mt-2">
                        PIN Code: {reservation.pin}
                      </p>
                    )}
                  </div>
                  <div className="flex space-x-3">
                    <button
                      onClick={() => togglePinCode(reservation.id)}
                      className="text-indigo-600 hover:text-indigo-900"
                    >
                      {showPinCode === reservation.id ? 'Hide PIN' : 'Show PIN'}
                    </button>
                    <button
                      onClick={() => router.push(`/admin/reservations/${reservation.id}/orders`)}
                      className="text-indigo-600 hover:text-indigo-900"
                    >
                      View Orders
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
