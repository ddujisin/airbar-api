'use client';

import React, { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Html5QrcodeScanner } from 'html5-qrcode';

export default function ScanPage() {
  const router = useRouter();
  const [error, setError] = useState<string>('');
  const scannerRef = useRef<Html5QrcodeScanner | null>(null);

  useEffect(() => {
    scannerRef.current = new Html5QrcodeScanner(
      'qr-reader',
      { fps: 10, qrbox: 250 },
      false
    );

    scannerRef.current.render(onScanSuccess, onScanError);

    return () => {
      if (scannerRef.current) {
        scannerRef.current.clear();
      }
    };
  }, []);

  const onScanSuccess = (decodedText: string) => {
    try {
      const url = new URL(decodedText);
      const pathParts = url.pathname.split('/');
      const itemId = pathParts[pathParts.length - 1];

      router.push(`/orders/${itemId}`);
    } catch (err) {
      setError('Invalid QR code');
    }
  };

  const onScanError = (err: string) => {
  };

  return (
    <div className="min-h-screen bg-gray-100 py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-2xl font-bold mb-8">Scan Item QR Code</h1>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <div className="bg-white shadow sm:rounded-lg p-6">
            <div id="qr-reader" className="w-full"></div>
          </div>
        </div>
      </div>
    </div>
  );
}
