import express from 'express';
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { authenticateToken, requireSuperAdmin } from '../middleware/auth';

const router = express.Router();
const prisma = new PrismaClient();

// Dashboard stats endpoint
router.get('/dashboard/stats', authenticateToken, async (req, res) => {
  try {
    const userId = req.user!.userId;

    // Get counts for various entities
    const [reservationsCount, guestsCount, itemsCount, ordersCount] = await Promise.all([
      prisma.Reservation.count({ where: { hostId: userId } }),
      prisma.Guest.count({ where: { hostId: userId } }),
      prisma.Item.count({ where: { hostId: userId } }),
      prisma.Order.count({ where: { hostId: userId } })
    ]);

    res.json({
      success: true,
      stats: {
        reservations: reservationsCount,
        guests: guestsCount,
        items: itemsCount,
        orders: ordersCount
      }
    });
  } catch (error) {
    console.error('[Dashboard Stats Error]:', error);
    res.status(500).json({ success: false, error: 'Failed to fetch dashboard stats' });
  }
});

// Host registration route
router.post('/register', async (req, res) => {
  console.log('[Backend Debug] Starting host registration');
  console.log('[Backend Debug] Request body:', { ...req.body, password: '[REDACTED]' });

  try {
    const { email, password, name, phone, address } = req.body;

    // Check if email already exists
    console.log('[Backend Debug] Checking for existing email:', email);
    const existingUser = await prisma.user.findUnique({
      where: { email }
    });

    if (existingUser) {
      console.log('[Backend Debug] Email already registered:', email);
      return res.status(400).json({ error: 'Email already registered' });
    }

    // Hash password
    console.log('[Backend Debug] Hashing password');
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create new host user
    console.log('[Backend Debug] Creating new host user');
    const newUser = await prisma.user.create({
      data: {
        email,
        password: hashedPassword,
        role: 'ADMIN',
        name,
        phone,
        address,
        isSuperAdmin: false
      }
    });

    console.log('[Backend Debug] Host created successfully:', { id: newUser.id, email: newUser.email });
    res.status(201).json({ message: 'Host registered successfully' });
  } catch (error) {
    console.error('[Backend Debug] Error in host registration:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Super-admin routes
router.get('/hosts', authenticateToken, requireSuperAdmin, async (req, res) => {
  try {
    const hosts = await prisma.user.findMany({
      where: {
        role: 'ADMIN',
        isSuperAdmin: false
      },
      select: {
        id: true,
        email: true,
        createdAt: true,
        updatedAt: true
      }
    });
    res.json(hosts);
  } catch (error) {
    console.error('Error fetching hosts:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Impersonate host
router.post('/impersonate/:hostId', authenticateToken, requireSuperAdmin, async (req, res) => {
  try {
    const { hostId } = req.params;
    const superAdminId = req.user!.userId;

    const host = await prisma.user.findFirst({
      where: {
        id: hostId,
        role: 'ADMIN',
        isSuperAdmin: false
      }
    });

    if (!host) {
      return res.status(404).json({ error: 'Host not found' });
    }

    const accessToken = jwt.sign(
      {
        userId: host.id,
        role: host.role,
        isSuperAdmin: false,
        impersonatedBy: superAdminId
      },
      process.env.JWT_SECRET!,
      { expiresIn: '24h' }
    );

    const session = await prisma.session.create({
      data: {
        accessToken,
        userId: host.id,
        expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000)
      }
    });

    res.json({ accessToken });
  } catch (error) {
    console.error('Error impersonating host:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Delete host
router.delete('/hosts/:hostId', authenticateToken, requireSuperAdmin, async (req, res) => {
  try {
    const { hostId } = req.params;

    const host = await prisma.user.findFirst({
      where: {
        id: hostId,
        role: 'ADMIN',
        isSuperAdmin: false
      }
    });

    if (!host) {
      return res.status(404).json({ error: 'Host not found' });
    }

    await prisma.user.delete({
      where: { id: hostId }
    });

    res.json({ message: 'Host deleted successfully' });
  } catch (error) {
    console.error('Error deleting host:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
