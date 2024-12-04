import { Router } from 'express';
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';

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

router.post('/login', async (req, res) => {
  const { email, password } = req.body;

  try {
    const user = await prisma.user.findUnique({
      where: { email }
    });

    if (!user || !await bcrypt.compare(password, user.password)) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const accessToken = jwt.sign(
      { userId: user.id, role: user.role, isSuperAdmin: user.isSuperAdmin },
      process.env.JWT_SECRET!,
      { expiresIn: '24h' }
    );

    await prisma.session.create({
      data: {
        userId: user.id,
        accessToken: accessToken,
        expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000)
      }
    });

    res.json({ accessToken, role: user.role, isSuperAdmin: user.isSuperAdmin });
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
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

  res.json({ message: 'Logged out successfully' });
});

router.get('/verify', async (req, res) => {
  console.log('[Auth Debug] Verify endpoint hit');
  console.log('[Auth Debug] Headers:', req.headers);

  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    console.log('[Auth Debug] No token provided');
    return res.status(401).json({ valid: false, error: 'No token provided' });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as { userId: string; role: string; isSuperAdmin: boolean };

    // Check if session exists
    const session = await prisma.session.findUnique({
      where: { accessToken: token },
      include: { user: true }
    });

    if (!session || session.expiresAt < new Date()) {
      console.log('[Auth Debug] Session not found or expired');
      return res.status(401).json({ valid: false, error: 'Session expired' });
    }

    console.log('[Auth Debug] Token verified successfully');
    res.json({
      valid: true,
      userId: decoded.userId,
      role: decoded.role,
      isSuperAdmin: decoded.isSuperAdmin
    });
  } catch (error) {
    console.error('[Auth Debug] Token verification error:', error);
    res.status(401).json({ valid: false, error: 'Invalid token' });
  }
});

export default router;
