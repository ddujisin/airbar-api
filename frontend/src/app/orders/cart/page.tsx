'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { orders } from '@/lib/api';
import type { MenuItem, Order } from '@/types/api';

interface CartItem extends MenuItem {
  quantity: number;
}

export default function CartPage() {
  const router = useRouter();
  const [cart, setCart] = useState<CartItem[]>([]);
  const [error, setError] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  useEffect(() => {
    const cartData = sessionStorage.getItem('cart');
    if (cartData) {
      setCart(JSON.parse(cartData));
    }
  }, []);

  const updateQuantity = (itemId: string, quantity: number) => {
    const updatedCart = cart.map(item =>
      item.id === itemId ? { ...item, quantity } : item
    ).filter(item => item.quantity > 0);

    setCart(updatedCart);
    sessionStorage.setItem('cart', JSON.stringify(updatedCart));
  };

  const getTotal = () => {
    return cart.reduce((total, item) => total + item.price * item.quantity, 0);
  };

  const handleCheckout = async () => {
    try {
      setIsSubmitting(true);
      const reservationData = sessionStorage.getItem('reservation');
      if (!reservationData) {
        throw new Error('No reservation found');
      }

      const reservation = JSON.parse(reservationData);
      await orders.createOrder({
        reservationId: reservation.id,
        items: cart.map(item => ({
          itemId: item.id,
          quantity: item.quantity,
        })),
      });

      // Clear cart and show success
      sessionStorage.removeItem('cart');
      router.push('/orders/success');
    } catch (err) {
      setError('Failed to create order');
    } finally {
      setIsSubmitting(false);
    }
  };

  const scanMore = () => {
    router.push('/orders/scan');
  };

  if (cart.length === 0) {
    return (
      <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
        <div className="relative py-3 sm:max-w-xl sm:mx-auto">
          <div className="relative px-4 py-10 bg-white mx-8 md:mx-0 shadow rounded-3xl sm:p-10">
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-4">Your cart is empty</h2>
              <button
                onClick={scanMore}
                className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Scan Items
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-2xl font-bold mb-8">Your Cart</h1>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-8">
            <ul className="divide-y divide-gray-200">
              {cart.map((item) => (
                <li key={item.id} className="px-4 py-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">
                        {item.name}
                      </h3>
                      <p className="text-sm text-gray-500">${item.price.toFixed(2)} each</p>
                    </div>
                    <div className="flex items-center space-x-4">
                      <button
                        onClick={() => updateQuantity(item.id, item.quantity - 1)}
                        className="text-gray-500 hover:text-gray-700"
                      >
                        -
                      </button>
                      <span>{item.quantity}</span>
                      <button
                        onClick={() => updateQuantity(item.id, item.quantity + 1)}
                        className="text-gray-500 hover:text-gray-700"
                      >
                        +
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-white shadow sm:rounded-lg mb-8">
            <div className="px-4 py-5 sm:p-6">
              <div className="text-lg font-medium text-gray-900 mb-4">
                Total: ${getTotal().toFixed(2)}
              </div>
              <div className="flex space-x-4">
                <button
                  onClick={handleCheckout}
                  disabled={isSubmitting}
                  className="flex-1 bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
                >
                  {isSubmitting ? 'Processing...' : 'Checkout'}
                </button>
                <button
                  onClick={scanMore}
                  disabled={isSubmitting}
                  className="flex-1 bg-gray-100 text-gray-700 px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
                >
                  Scan More
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
