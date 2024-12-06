'use client';

import React from 'react';
import Link from 'next/link';

export default function OrderSuccessPage() {
  return (
    <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
      <div className="relative py-3 sm:max-w-xl sm:mx-auto">
        <div className="relative px-4 py-10 bg-white mx-8 md:mx-0 shadow rounded-3xl sm:p-10">
          <div className="max-w-md mx-auto text-center">
            <h2 className="text-2xl font-bold text-green-600 mb-4">Order Successful!</h2>
            <p className="text-gray-600 mb-8">
              Your order has been placed successfully. The items will be added to your room bill.
            </p>
            <Link
              href="/orders/scan"
              className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Order More Items
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
