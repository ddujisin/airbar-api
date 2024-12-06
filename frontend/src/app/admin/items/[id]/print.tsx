'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { menu } from '@/lib/api';
import { generateQRLabel } from '@/lib/qr';
import type { MenuItem } from '@/types/api';

export default function PrintQRLabel() {
  const { id } = useParams();
  const [item, setItem] = useState<MenuItem | null>(null);
  const [qrLabel, setQrLabel] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadItem = async () => {
      try {
        const menuItem = await menu.getItem(id as string);
        setItem(menuItem);
        const label = await generateQRLabel({
          id: menuItem.id,
          name: menuItem.name,
          price: menuItem.price,
        });
        setQrLabel(label);
      } catch (err) {
        setError('Failed to load item details');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      loadItem();
    }
  }, [id]);

  const handlePrint = () => {
    const printWindow = window.open('', '_blank');
    if (printWindow) {
      printWindow.document.write(`
        <html>
          <head>
            <title>Print QR Label - ${item?.name}</title>
          </head>
          <body>
            ${qrLabel}
            <script>
              window.onload = () => {
                window.print();
                window.onafterprint = () => window.close();
              };
            </script>
          </body>
        </html>
      `);
      printWindow.document.close();
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="text-red-500">{error}</div>;
  if (!item) return <div>Item not found</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Print QR Label</h1>
      <div className="mb-4">
        <h2 className="text-xl">{item.name}</h2>
        <p className="text-gray-600">Price: ${item.price.toFixed(2)}</p>
      </div>
      <div className="mb-4" dangerouslySetInnerHTML={{ __html: qrLabel }} />
      <button
        onClick={handlePrint}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        Print Label
      </button>
    </div>
  );
}
