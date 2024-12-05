import { Router } from 'express';
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { AuthRequest, LoginResponse, VerifyResponse } from '../types/auth';

const router = Router();
const prisma = new PrismaClient();

router.post('/register', async (req, res) => {
  const { email, password, name, phone, address, role } = req.body;
  console.log('[Auth Debug] Registration request received:', {
    email,
    name,
    phone,
    address,
    role
  });

  try {
    const existingUser = await prisma.user.findUnique({
      where: { email }
    });

    if (existingUser) {
      console.log('[Auth Debug] Email already registered:', email);
      return res.status(400).json({ error: 'Email already registered' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    console.log('[Auth Debug] Creating new user with role:', role);

    const user = await prisma.user.create({
      data: {
        email,
        password: hashedPassword,
        name,
        phone,
        address,
        role: role || 'ADMIN'
      }
    });

    console.log('[Auth Debug] User created successfully:', user.id);
    res.status(201).json({ message: 'User registered successfully' });
  } catch (error) {
    console.error('[Auth Debug] Registration error:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

router.post('/login', async (req: AuthRequest, res) => {
  const { email, password } = req.body;
  console.log('[Auth Debug] Login attempt:', { email, timestamp: new Date().toISOString() });

  try {
    const user = await prisma.user.findUnique({ where: { email } });
    if (!user) {
      console.log('[Auth Debug] User not found:', email);
      return res.status(401).json({ success: false, message: 'Invalid credentials' });
    }

    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      console.log('[Auth Debug] Invalid password for user:', email);
      return res.status(401).json({ success: false, message: 'Invalid credentials' });
    }

    const accessToken = jwt.sign(
      { userId: user.id, role: user.role, isSuperAdmin: user.isSuperAdmin },
      process.env.JWT_SECRET!,
      { expiresIn: '24h' }
    );

    // Create session record in database
    const expiresAt = new Date();
    expiresAt.setHours(expiresAt.getHours() + 24);

    await prisma.session.create({
      data: {
        userId: user.id,
        accessToken,
        expiresAt,
      },
    });

    // Set HTTP-only cookie with token and session info
    res.cookie('accessToken', accessToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      maxAge: 24 * 60 * 60 * 1000,
      sameSite: 'lax',
      path: '/'
    });

    console.log('[Auth Debug] Login successful:', {
      userId: user.id,
      role: user.role,
      isSuperAdmin: user.isSuperAdmin,
      timestamp: new Date().toISOString()
    });

    const response: LoginResponse = {
      success: true,
      role: user.role,
      isSuperAdmin: user.isSuperAdmin,
      valid: true,
      message: 'Login successful'
    };

    return res.json(response);
  } catch (error) {
    console.error('[Auth Debug] Login error:', error);
    return res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

router.post('/logout', async (req, res) => {
  const authHeader = req.headers['authorization'];
  const accessToken = authHeader && authHeader.split(' ')[1];

  if (accessToken) {
    try {
      await prisma.session.delete({
        where: { accessToken: accessToken }
      });
    } catch (error) {
      // Session might already be expired/deleted
    }
  }

  res.clearCookie('accessToken', { path: '/' });
  res.json({ message: 'Logged out successfully' });
});

router.get('/verify', async (req, res) => {
  console.log('[Auth Debug] Verify endpoint hit');

  const token = req.cookies.accessToken;

  if (!token) {
    console.log('[Auth Debug] No token cookie found');
    return res.status(401).json({ valid: false, error: 'No token provided' } as VerifyResponse);
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as {
      userId: string;
      role: string;
      isSuperAdmin: boolean
    };

    const session = await prisma.session.findFirst({
      where: {
        accessToken: token,
        expiresAt: { gt: new Date() }
      }
    });

    if (!session) {
      console.log('[Auth Debug] Session not found or expired');
      res.clearCookie('accessToken', { path: '/' });
      return res.status(401).json({ valid: false, error: 'Session expired' } as VerifyResponse);
    }

    console.log('[Auth Debug] Token verified successfully');
    const response: VerifyResponse = {
      valid: true,
      role: decoded.role,
      isSuperAdmin: decoded.isSuperAdmin
    };
    res.json(response);
  } catch (error) {
    console.error('[Auth Debug] Token verification error:', error);
    res.clearCookie('accessToken', { path: '/' });
    res.status(401).json({ valid: false, error: 'Invalid token' } as VerifyResponse);
  }
});

export default router;
