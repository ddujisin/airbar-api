import axios from 'axios';
import type { MenuItem, User, Reservation, Guest, Order } from '@/types/api';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth endpoints
export const auth = {
  login: async (email: string, password: string): Promise<{ token: string; user: User }> => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },
  register: async (userData: {
    email: string;
    password: string;
    name: string;
    phone: string;
    address: string;
  }): Promise<{ token: string; user: User }> => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
  verify: async (): Promise<{ user: User }> => {
    const response = await api.get('/auth/verify');
    return response.data;
  },
  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
    localStorage.removeItem('token');
  },
};

// Admin endpoints
export const hosts = {
  getAll: async (): Promise<User[]> => {
    const response = await api.get('/admin/hosts');
    return response.data;
  },
  impersonate: async (hostId: string): Promise<{ token: string; user: User }> => {
    const response = await api.post(`/admin/hosts/${hostId}/impersonate`);
    localStorage.setItem('token', response.data.token);
    return response.data;
  },
};

export const reservations = {
  getAll: async (): Promise<Reservation[]> => {
    const response = await api.get('/admin/reservations');
    return response.data;
  },
  create: async (data: {
    startDate: string;
    endDate: string;
    guestId: string;
  }): Promise<Reservation> => {
    const response = await api.post('/admin/reservations', data);
    return response.data;
  },
  getByPin: async (pin: string): Promise<Reservation> => {
    const response = await api.get(`/reservations/pin/${pin}`);
    return response.data;
  },
  getOrders: async (id: string): Promise<Order[]> => {
    const response = await api.get(`/admin/reservations/${id}/orders`);
    return response.data;
  },
};

export const guests = {
  getAll: async (): Promise<Guest[]> => {
    const response = await api.get('/admin/guests');
    return response.data;
  },
  create: async (data: { name: string; email: string }): Promise<Guest> => {
    const response = await api.post('/admin/guests', data);
    return response.data;
  },
};

// Menu endpoints
export const menu = {
  getItems: async (): Promise<MenuItem[]> => {
    const response = await api.get('/menu/items');
    return response.data;
  },
  getItem: async (id: string): Promise<MenuItem> => {
    const response = await api.get(`/menu/items/${id}`);
    return response.data;
  },
  createItem: async (data: {
    name: string;
    description: string;
    price: number;
  }): Promise<MenuItem> => {
    const response = await api.post('/menu/items', data);
    return response.data;
  },
  updateItem: async (
    id: string,
    data: { name: string; description: string; price: number; available: boolean }
  ): Promise<MenuItem> => {
    const response = await api.put(`/menu/items/${id}`, data);
    return response.data;
  },
  deleteItem: async (id: string): Promise<void> => {
    await api.delete(`/menu/items/${id}`);
  },
};

// Order endpoints
export const orders = {
  create: async (data: {
    reservationId: string;
    items: { itemId: string; quantity: number }[];
  }): Promise<Order> => {
    const response = await api.post('/orders', data);
    return response.data;
  },
  getAll: async (): Promise<Order[]> => {
    const response = await api.get('/orders');
    return response.data;
  },
};

export default api;
