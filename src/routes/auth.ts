import { Router } from 'express';
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';
interface DecodedToken {
  userId: string;
  role: string;
  isSuperAdmin: boolean;
  impersonatedBy?: string;
}

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
  console.log('[Auth Debug] Login attempt for email:', email);

  try {
    const user = await prisma.user.findUnique({
      where: { email }
    });

    console.log('[Auth Debug] User found:', !!user);

    if (!user || !await bcrypt.compare(password, user.password)) {
      console.log('[Auth Debug] Invalid credentials');
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const accessToken = jwt.sign(
      { userId: user.id, role: user.role, isSuperAdmin: user.isSuperAdmin },
      process.env.JWT_SECRET!,
      { expiresIn: '24h' }
    );

    console.log('[Auth Debug] Token generated:', accessToken.substring(0, 10) + '...');

    await prisma.session.create({
      data: {
        userId: user.id,
        accessToken: accessToken,
        expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000)
      }
    });

    console.log('[Auth Debug] Session created successfully');
    res.json({ accessToken, role: user.role, isSuperAdmin: user.isSuperAdmin });
  } catch (error) {
    console.error('[Auth Debug] Login error:', error);
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
    const decoded = jwt.verify(token, JWT_SECRET) as DecodedToken;

    // Check if session exists
    const session = await prisma.session.findUnique({
      where: { accessToken: token },
      include: { user: true }
    });

    if (!session || session.expiresAt < new Date()) {
      console.log('[Auth Debug] Session not found or expired');
      return res.status(401).json({ valid: false, error: 'Session expired' });
    }

    const { user } = session;

    // Build a user object that the frontend expects
    const responseUser = {
      id: user.id,
      email: user.email,
      name: user.name || '',
      phone: user.phone || '',
      address: user.address || '',
      role: decoded.role,          // Use the role from the token
      isSuperAdmin: decoded.isSuperAdmin
    };

    console.log('[Auth Debug] Token verified successfully, returning user:', responseUser);
    res.json({
      valid: true,
      user: responseUser
    });

  } catch (error) {
    console.error('[Auth Debug] Token verification error:', error);
    return res.status(401).json({ valid: false, error: 'Invalid token' });
  }
});

//Route for pin-based guest login
router.get('/pin/:pin', async (req, res) => {
  const { pin } = req.params;
  console.log('[Auth Debug] PIN verification attempt:', pin);

  try {
    const now = new Date();
    const reservation = await prisma.reservation.findFirst({
      where: {
        pin,
        startDate: { lte: now },
        endDate: { gte: now }
      },
      include: { host: true }
    });

    if (!reservation) {
      console.log('[Auth Debug] No valid reservation found for pin:', pin);
      return res.status(401).json({ error: 'Invalid or expired PIN' });
    }

    // Create a guest token
    const accessToken = jwt.sign(
      {
        userId: reservation.hostId, // We'll use the host's userId since sessions must reference a user
        role: 'GUEST',
        isSuperAdmin: false,
        reservationId: reservation.id
      },
      process.env.JWT_SECRET!,
      { expiresIn: '24h' }
    );

    await prisma.session.create({
      data: {
        userId: reservation.hostId,
        accessToken: accessToken,
        expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000)
      }
    });

    console.log('[Auth Debug] Guest session created successfully for reservation:', reservation.id);
    res.json({
      accessToken,
      role: 'GUEST',
      reservationId: reservation.id,
      guestId: reservation.guestId,
      hostId: reservation.hostId,
      message: 'PIN validated successfully, guest session started'
    });
  } catch (error) {
    console.error('[Auth Debug] PIN verification error:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

export default router;
