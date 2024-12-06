'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth/authContext';
import { admin } from '@/lib/api';
import Link from 'next/link';

interface Reservation {
  id: string;
  startDate: string;
  endDate: string;
  pin: string;
  guest: {
    id: string;
    name: string;
    email: string;
  };
}

export default function AdminDashboard() {
  const { user } = useAuth();
  const [reservations, setReservations] = useState<Reservation[]>([]);
  const [showPin, setShowPin] = useState<{ [key: string]: boolean }>({});
  const [error, setError] = useState('');

  useEffect(() => {
    loadReservations();
  }, []);

  const loadReservations = async () => {
    try {
      const data = await admin.getReservations();
      setReservations(data);
    } catch (err) {
      setError('Failed to load reservations');
    }
  };

  const togglePinVisibility = (reservationId: string) => {
    setShowPin(prev => ({
      ...prev,
      [reservationId]: !prev[reservationId]
    }));
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-xl font-bold">AirBar Admin</h1>
              </div>
            </div>
            <div className="flex items-center">
              <span className="text-gray-700 px-3">{user?.name}</span>
              <Link
                href="/admin/items"
                className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Manage Items
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Reservations</h2>
            <Link
              href="/admin/reservations/new"
              className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              New Reservation
            </Link>
          </div>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {reservations.map((reservation) => (
                <li key={reservation.id} className="px-6 py-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        Guest: {reservation.guest.name}
                      </p>
                      <p className="text-sm text-gray-500">
                        {reservation.guest.email}
                      </p>
                      <p className="text-sm text-gray-500">
                        {new Date(reservation.startDate).toLocaleDateString()} - {new Date(reservation.endDate).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex items-center space-x-4">
                      <button
                        onClick={() => togglePinVisibility(reservation.id)}
                        className="text-indigo-600 hover:text-indigo-900"
                      >
                        {showPin[reservation.id] ? 'Hide PIN' : 'Show PIN'}
                      </button>
                      {showPin[reservation.id] && (
                        <span className="text-lg font-mono bg-gray-100 px-3 py-1 rounded">
                          {reservation.pin}
                        </span>
                      )}
                      <Link
                        href={`/admin/reservations/${reservation.id}/orders`}
                        className="text-indigo-600 hover:text-indigo-900"
                      >
                        View Orders
                      </Link>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
