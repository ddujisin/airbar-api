import { Request, Response } from 'express';

export interface AuthRequest extends Request {
  body: {
    email: string;
    password: string;
    name?: string;
    phone?: string;
    address?: string;
    role?: string;
  };
}

export interface LoginResponse {
  success: boolean;
  role?: string;
  isSuperAdmin?: boolean;
  valid?: boolean;
  message?: string;
}

export interface VerifyResponse {
  valid: boolean;
  role?: string;
  isSuperAdmin?: boolean;
  error?: string;
}
