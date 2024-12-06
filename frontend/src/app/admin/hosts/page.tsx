'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth/authContext';
import { auth } from '@/lib/api';
import type { User } from '@/types/api';

export default function HostsPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [hosts, setHosts] = useState<User[]>([]);
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    if (!user?.isSuperAdmin) {
      router.push('/admin/dashboard');
      return;
    }
    loadHosts();
  }, [user]);

  const loadHosts = async () => {
    try {
      const response = await fetch('/api/admin/hosts');
      const data = await response.json();
      if (data.error) {
        throw new Error(data.error);
      }
      setHosts(data.data);
    } catch (err) {
      setError('Failed to load hosts');
    } finally {
      setLoading(false);
    }
  };

  const handleImpersonate = async (hostId: string) => {
    try {
      const { data } = await auth.impersonate(hostId);
      // Update auth context with new token and user
      window.location.href = '/admin/dashboard';
    } catch (err) {
      setError('Failed to impersonate host');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl mx-auto">
            <p>Loading...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-2xl font-bold mb-8">Manage Hosts</h1>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <div className="bg-white shadow overflow-hidden sm:rounded-lg">
            <ul className="divide-y divide-gray-200">
              {hosts.map((host) => (
                <li key={host.id} className="px-4 py-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">
                        {host.name}
                      </h3>
                      <p className="text-sm text-gray-500">{host.email}</p>
                    </div>
                    <button
                      onClick={() => handleImpersonate(host.id)}
                      className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium"
                    >
                      Impersonate
                    </button>
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
