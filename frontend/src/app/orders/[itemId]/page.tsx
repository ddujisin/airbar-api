'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { menu } from '@/lib/api';
import { addToCart, getReservation, setReservation } from '@/lib/cart';
import PinValidation from '@/components/PinValidation';
import type { MenuItem, Reservation } from '@/types/api';

export default function OrderPage({ params }: { params: { itemId: string } }) {
  const router = useRouter();
  const [item, setItem] = useState<MenuItem | null>(null);
  const [quantity, setQuantity] = useState<number>(1);
  const [error, setError] = useState<string | null>(null);
  const [reservation, setReservationState] = useState<Reservation | null>(null);
  const [step, setStep] = useState<'pin' | 'quantity'>('pin');

  useEffect(() => {
    const loadItem = async () => {
      try {
        const menuItem = await menu.getItem(params.itemId);
        setItem(menuItem);
      } catch (err) {
        setError('Failed to load item');
      }
    };

    loadItem();
  }, [params.itemId]);

  const handlePinValidated = (validatedReservation: Reservation) => {
    setReservationState(validatedReservation);
    setReservation(validatedReservation.id, validatedReservation.pin);
    setStep('quantity');
  };

  const handleAddToCart = () => {
    if (!item || !reservation) return;

    addToCart({
      itemId: item.id,
      name: item.name,
      price: item.price,
      quantity,
    });

    router.push('/orders/cart');
  };

  if (!item) {
    return (
      <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
        <div className="relative py-3 sm:max-w-xl sm:mx-auto">
          <div className="relative px-4 py-10 bg-white mx-8 md:mx-0 shadow rounded-3xl sm:p-10">
            {error || 'Loading...'}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
      <div className="relative py-3 sm:max-w-xl sm:mx-auto">
        <div className="relative px-4 py-10 bg-white mx-8 md:mx-0 shadow rounded-3xl sm:p-10">
          <div className="max-w-md mx-auto">
            <div className="divide-y divide-gray-200">
              <div className="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7">
                <h2 className="text-2xl font-bold mb-8">{item.name}</h2>
                <p className="text-gray-600">{item.description}</p>
                <p className="text-xl font-bold">${item.price.toFixed(2)}</p>

                {error && (
                  <div className="text-red-500 text-sm mb-4">{error}</div>
                )}

                {step === 'pin' && (
                  <PinValidation
                    onValidated={handlePinValidated}
                    onError={setError}
                  />
                )}

                {step === 'quantity' && (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        Quantity
                      </label>
                      <input
                        type="number"
                        min="1"
                        value={quantity}
                        onChange={(e) => setQuantity(parseInt(e.target.value))}
                        className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      />
                    </div>
                    <button
                      onClick={handleAddToCart}
                      className="w-full bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700"
                    >
                      Add to Cart
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
