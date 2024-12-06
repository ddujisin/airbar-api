'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { menu } from '@/lib/api';
import QRCode from 'qrcode';
import type { MenuItem } from '@/types/api';

export default function ItemsManagement() {
  const router = useRouter();
  const [items, setItems] = useState<MenuItem[]>([]);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
  });
  const [selectedItem, setSelectedItem] = useState<MenuItem | null>(null);

  useEffect(() => {
    loadItems();
  }, []);

  const loadItems = async () => {
    try {
      const data = await menu.getItems();
      setItems(data);
    } catch (err) {
      setError('Failed to load items');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (selectedItem) {
        await menu.updateItem(selectedItem.id, {
          ...formData,
          price: parseFloat(formData.price),
          available: true,
        });
      } else {
        await menu.createItem({
          ...formData,
          price: parseFloat(formData.price),
        });
      }
      setShowForm(false);
      setSelectedItem(null);
      setFormData({ name: '', description: '', price: '' });
      loadItems();
    } catch (err) {
      setError('Failed to save item');
    }
  };

  const handleEdit = (item: MenuItem) => {
    setSelectedItem(item);
    setFormData({
      name: item.name,
      description: item.description,
      price: item.price.toString(),
    });
    setShowForm(true);
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this item?')) return;
    try {
      await menu.deleteItem(id);
      loadItems();
    } catch (err) {
      setError('Failed to delete item');
    }
  };

  const generateQRCode = async (item: MenuItem) => {
    try {
      const orderUrl = `${window.location.origin}/orders/${item.id}`;
      const qrDataUrl = await QRCode.toDataURL(orderUrl);

      // Create a temporary link element to trigger download
      const link = document.createElement('a');
      link.download = `qr-${item.name.toLowerCase().replace(/\s+/g, '-')}.png`;
      link.href = qrDataUrl;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      setError('Failed to generate QR code');
    }
  };

  const printQRLabel = async (item: MenuItem) => {
    try {
      const orderUrl = `${window.location.origin}/orders/${item.id}`;
      const qrDataUrl = await QRCode.toDataURL(orderUrl);

      // Create a new window for printing
      const printWindow = window.open('', '_blank');
      if (!printWindow) {
        throw new Error('Failed to open print window');
      }

      // Generate HTML content for the label
      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
          <head>
            <title>QR Label - ${item.name}</title>
            <style>
              body { font-family: Arial, sans-serif; margin: 20px; }
              .label { width: 300px; padding: 20px; border: 1px solid #ccc; }
              .item-name { font-size: 18px; font-weight: bold; margin-bottom: 10px; }
              .item-price { font-size: 16px; margin-bottom: 15px; }
              .qr-code { text-align: center; }
              .qr-code img { max-width: 200px; }
              @media print {
                body { margin: 0; }
                .label { border: none; }
              }
            </style>
          </head>
          <body>
            <div class="label">
              <div class="item-name">${item.name}</div>
              <div class="item-price">$${item.price.toFixed(2)}</div>
              <div class="qr-code">
                <img src="${qrDataUrl}" alt="QR Code" />
              </div>
            </div>
          </body>
        </html>
      `);

      // Trigger print dialog
      printWindow.document.close();
      printWindow.focus();
      printWindow.print();
      printWindow.close();
    } catch (err) {
      setError('Failed to print QR label');
    }
  };


  return (
    <div className="min-h-screen bg-gray-100 py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Items Management</h1>
          <button
            onClick={() => {
              setSelectedItem(null);
              setFormData({ name: '', description: '', price: '' });
              setShowForm(true);
            }}
            className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium"
          >
            Add New Item
          </button>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {showForm && (
          <div className="bg-white shadow sm:rounded-lg mb-6">
            <div className="px-4 py-5 sm:p-6">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Name
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Description
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Price
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={formData.price}
                    onChange={(e) => setFormData(prev => ({ ...prev, price: e.target.value }))}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  />
                </div>

                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setShowForm(false)}
                    className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    {selectedItem ? 'Update' : 'Create'} Item
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {items.map((item) => (
              <li key={item.id} className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">{item.name}</h3>
                    <p className="text-sm text-gray-500">{item.description}</p>
                    <p className="text-sm font-medium text-gray-900">${item.price.toFixed(2)}</p>
                  </div>
                  <div className="flex space-x-3">
                    <button
                      onClick={() => generateQRCode(item)}
                      className="text-indigo-600 hover:text-indigo-900"
                    >
                      Download QR
                    </button>
                    <button
                      onClick={() => printQRLabel(item)}
                      className="text-indigo-600 hover:text-indigo-900"
                    >
                      Print Label
                    </button>
                    <button
                      onClick={() => handleEdit(item)}
                      className="text-indigo-600 hover:text-indigo-900"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(item.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
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
