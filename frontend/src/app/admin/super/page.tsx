'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { hosts } from '@/lib/api';
import type { User } from '@/types/api';

export default function SuperAdminDashboard() {
  const [hostList, setHostList] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchHosts = async () => {
      try {
        const hosts = await hosts.getAll();
        setHostList(hosts);
      } catch (err) {
        setError('Failed to load hosts');
      } finally {
        setLoading(false);
      }
    };

    fetchHosts();
  }, []);

  const handleImpersonate = async (hostId: string) => {
    try {
      const { token, user } = await hosts.impersonate(hostId);
      localStorage.setItem('token', token);
      router.push('/admin/dashboard');
    } catch (err) {
      setError('Failed to impersonate host');
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Host Management</h1>
      <div className="grid gap-4">
        {hostList.map((host) => (
          <div key={host.id} className="border p-4 rounded-lg">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-xl">{host.name}</h2>
                <p className="text-gray-600">{host.email}</p>
                <p className="text-sm text-gray-500">
                  Phone: {host.phone} | Address: {host.address}
                </p>
              </div>
              <button
                onClick={() => handleImpersonate(host.id)}
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
              >
                Impersonate
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
