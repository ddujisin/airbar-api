'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { orders } from '@/lib/api';
import { getCart, getReservation, clearCart, getCartTotal } from '@/lib/cart';
import type { CartItem } from '@/types/api';

export default function CheckoutPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const cart = getCart();
  const { reservationId } = getReservation();
  const total = getCartTotal();

  const handleCheckout = async () => {
    if (!reservationId || cart.items.length === 0) {
      setError('Invalid cart or reservation');
      return;
    }

    setLoading(true);
    try {
      await orders.create({
        reservationId,
        items: cart.items.map(item => ({
          itemId: item.itemId,
          quantity: item.quantity,
        })),
      });

      clearCart();
      router.push('/orders/success');
    } catch (err) {
      setError('Failed to create order');
    } finally {
      setLoading(false);
    }
  };

  if (cart.items.length === 0) {
    return (
      <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
        <div className="relative py-3 sm:max-w-xl sm:mx-auto">
          <div className="relative px-4 py-10 bg-white mx-8 md:mx-0 shadow rounded-3xl sm:p-10">
            <p>Your cart is empty</p>
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
            <h2 className="text-2xl font-bold mb-8">Checkout</h2>

            {error && (
              <div className="text-red-500 text-sm mb-4">{error}</div>
            )}

            <div className="space-y-4">
              <div className="border-t pt-4">
                <h3 className="text-lg font-medium">Order Summary</h3>
                {cart.items.map((item) => (
                  <div key={item.itemId} className="flex justify-between py-2">
                    <span>{item.name} x {item.quantity}</span>
                    <span>${(item.price * item.quantity).toFixed(2)}</span>
                  </div>
                ))}
                <div className="border-t pt-4 mt-4">
                  <div className="flex justify-between font-bold">
                    <span>Total</span>
                    <span>${total.toFixed(2)}</span>
                  </div>
                </div>
              </div>

              <button
                onClick={handleCheckout}
                disabled={loading}
                className="w-full bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
              >
                {loading ? 'Processing...' : 'Confirm Order'}
              </button>

              <button
                onClick={() => router.push('/orders/cart')}
                className="w-full bg-gray-200 text-gray-700 px-4 py-2 rounded-md text-sm font-medium hover:bg-gray-300"
              >
                Back to Cart
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
