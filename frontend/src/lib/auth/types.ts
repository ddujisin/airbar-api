export type UserRole = 'GUEST' | 'ADMIN' | 'SUPER_ADMIN';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  isSuperAdmin?: boolean;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    email: string;
    password: string;
    name: string;
    phone: string;
    address: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
  impersonateHost?: (hostId: string) => Promise<void>;
}
