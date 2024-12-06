'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { reservations } from '@/lib/api';
import type { Order } from '@/types/api';

export default function ReservationOrdersPage() {
  const params = useParams();
  const [orders, setOrders] = useState<Order[]>([]);
  const [error, setError] = useState('');
  const [totalAmount, setTotalAmount] = useState(0);

  useEffect(() => {
    loadOrders();
  }, [params.id]);

  const loadOrders = async () => {
    try {
      const data = await reservations.getOrders(params.id as string);
      setOrders(data);
      const total = data.reduce((sum, order) => sum + order.total, 0);
      setTotalAmount(total);
    } catch (err) {
      setError('Failed to load orders');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Reservation Orders</h1>
          <div className="text-lg font-medium">
            Total: ${totalAmount.toFixed(2)}
          </div>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {orders.map((order) => (
              <li key={order.id} className="px-4 py-4 sm:px-6">
                <div className="mb-2">
                  <span className="text-sm text-gray-500">
                    {new Date(order.createdAt).toLocaleString()}
                  </span>
                </div>
                <ul className="space-y-2">
                  {order.items.map((item) => (
                    <li key={item.id} className="flex justify-between">
                      <span>{item.item.name} x {item.quantity}</span>
                      <span>${(item.item.price * item.quantity).toFixed(2)}</span>
                    </li>
                  ))}
                </ul>
                <div className="mt-2 text-right font-medium">
                  Order Total: ${order.total.toFixed(2)}
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
