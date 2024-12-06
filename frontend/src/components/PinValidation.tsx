'use client';

import { useState } from 'react';
import { reservations } from '@/lib/api';
import { setReservation } from '@/lib/cart';
import type { Reservation } from '@/types/api';

interface PinValidationProps {
  onValidated: (reservation: Reservation) => void;
  onError?: (error: string) => void;
}

export default function PinValidation({ onValidated, onError }: PinValidationProps) {
  const [pin, setPin] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const reservation = await reservations.getByPin(pin);
      setReservation(reservation.id, pin);
      onValidated(reservation);
    } catch (err) {
      onError?.('Invalid PIN code. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="pin" className="block text-sm font-medium text-gray-700">
          Enter your 4-digit PIN code
        </label>
        <input
          type="text"
          id="pin"
          value={pin}
          onChange={(e) => setPin(e.target.value)}
          maxLength={4}
          pattern="\d{4}"
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
          required
        />
      </div>
      <button
        type="submit"
        disabled={loading || pin.length !== 4}
        className="w-full rounded-md bg-blue-500 px-4 py-2 text-white hover:bg-blue-600 disabled:opacity-50"
      >
        {loading ? 'Validating...' : 'Validate PIN'}
      </button>
    </form>
  );
}
