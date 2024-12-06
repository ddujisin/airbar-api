'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { auth } from '@/lib/api';
import { AuthContextType, AuthState, User } from './types';
import jwtDecode from 'jwt-decode';

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>(initialState);
  const router = useRouter();

  useEffect(() => {
    const initAuth = async () => {
      try {
        const token = localStorage.getItem('token');
        if (token) {
          const decoded = jwtDecode<User>(token);
          const { user } = await auth.verify();
          setState({
            user,
            isAuthenticated: true,
            isLoading: false,
          });
        } else {
          setState({ ...initialState, isLoading: false });
        }
      } catch (error) {
        localStorage.removeItem('token');
        setState({ ...initialState, isLoading: false });
      }
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const { token, user } = await auth.login(email, password);
      localStorage.setItem('token', token);
      setState({
        user,
        isAuthenticated: true,
        isLoading: false,
      });
      router.push(user.role === 'ADMIN' ? '/admin/dashboard' : '/');
    } catch (error) {
      throw error;
    }
  };

  const register = async (data: {
    email: string;
    password: string;
    name: string;
    phone: string;
    address: string;
  }) => {
    try {
      await auth.register(data);
      router.push('/login');
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    try {
      await auth.logout();
      localStorage.removeItem('token');
      setState({ ...initialState, isLoading: false });
      router.push('/login');
    } catch (error) {
      throw error;
    }
  };

  const impersonateHost = async (hostId: string) => {
    if (!state.user?.isSuperAdmin) return;
    try {
      const { token, user } = await auth.impersonateHost(hostId);
      localStorage.setItem('token', token);
      setState({
        user,
        isAuthenticated: true,
        isLoading: false,
      });
      router.push('/admin/dashboard');
    } catch (error) {
      throw error;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        register,
        logout,
        ...(state.user?.isSuperAdmin && { impersonateHost }),
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
