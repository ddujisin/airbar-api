```typescript
// Types derived from Prisma schema
export type UserRole = 'SUPER_ADMIN' | 'ADMIN' | 'GUEST';

export interface User {
  id: string;
  email: string;
  password?: string; // Optional in responses
  role: UserRole;
  isSuperAdmin: boolean;
  name?: string;
  phone?: string;
  address?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Session {
  id: string;
  userId: string;
  accessToken: string;
  expiresAt: Date;
  createdAt: Date;
  user?: User; // Optional for responses that don't need full user data
}

export interface Item {
  id: string;
  name: string;
  description?: string;
  price: number;
  qrCode: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Guest {
  id: string;
  name: string;
  email: string;
  createdAt: Date;
  updatedAt: Date;
  reservations?: Reservation[];
}

export interface Reservation {
  id: string;
  startDate: Date;
  endDate: Date;
  pinCode: string;
  guestId: string;
  guest?: Guest;
  orders?: Order[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Order {
  id: string;
  quantity: number;
  totalPrice: number;
  itemId: string;
  reservationId: string;
  item?: Item;
  reservation?: Reservation;
  createdAt: Date;
  updatedAt: Date;
}

// Response types for consistent API responses
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface AuthResponse extends ApiResponse<{
  user: User;
  accessToken: string;
}> {}

export interface SessionResponse extends ApiResponse<{
  session: Session;
}> {}
```
