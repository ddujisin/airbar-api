export interface User {
  id: string;
  email: string;
  name: string;
  phone: string;
  address: string;
  role: 'GUEST' | 'ADMIN' | 'SUPER_ADMIN';
  isSuperAdmin?: boolean;
}

export interface MenuItem {
  id: string;
  name: string;
  description: string;
  price: number;
  available: boolean;
  hostId: string;
}

export interface Guest {
  id: string;
  name: string;
  email: string;
  hostId: string;
}

export interface Reservation {
  id: string;
  startDate: string;
  endDate: string;
  pin: string;
  guestId: string;
  guest: Guest;
  hostId: string;
  orders: Order[];
}

export interface Order {
  id: string;
  createdAt: string;
  reservationId: string;
  items: OrderItem[];
  total: number;
}

export interface OrderItem {
  id: string;
  orderId: string;
  menuItemId: string;
  quantity: number;
  price: number;
  menuItem: MenuItem;
}

export interface CartItem {
  itemId: string;
  name: string;
  price: number;
  quantity: number;
}

export interface ApiError {
  message: string;
  status: number;
}

export interface LoginResponse {
  token: string;
  user: User;
}

export interface VerifyResponse {
  user: User;
}
