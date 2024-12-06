import express from 'express';
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { authenticateToken, requireSuperAdmin } from '../middleware/auth';

const router = express.Router();
const prisma = new PrismaClient();

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

// Reservation routes
router.get('/reservations', authenticateToken, async (req, res) => {
  try {
    const reservations = await prisma.reservation.findMany({
      where: {
        hostId: req.user.userId
      },
      include: {
        guest: true,
        orders: true
      }
    });
    res.json(reservations);
  } catch (error) {
    console.error('Error fetching reservations:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.post('/reservations', authenticateToken, async (req, res) => {
  try {
    const { startDate, endDate, guestId } = req.body;
    const pin = Math.floor(1000 + Math.random() * 9000).toString(); // Generate 4-digit PIN

    const reservation = await prisma.reservation.create({
      data: {
        startDate: new Date(startDate),
        endDate: new Date(endDate),
        pin,
        hostId: req.user.userId,
        guestId
      },
      include: {
        guest: true
      }
    });
    res.status(201).json(reservation);
  } catch (error) {
    console.error('Error creating reservation:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.get('/reservations/:id/orders', authenticateToken, async (req, res) => {
  try {
    const { id } = req.params;
    const orders = await prisma.order.findMany({
      where: {
        reservationId: id,
        reservation: {
          hostId: req.user.userId
        }
      },
      include: {
        items: {
          include: {
            item: true
          }
        }
      }
    });
    res.json(orders);
  } catch (error) {
    console.error('Error fetching reservation orders:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Guest routes
router.get('/guests', authenticateToken, async (req, res) => {
  try {
    const guests = await prisma.guest.findMany({
      where: {
        hostId: req.user.userId
      }
    });
    res.json(guests);
  } catch (error) {
    console.error('Error fetching guests:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.post('/guests', authenticateToken, async (req, res) => {
  try {
    const { name, email } = req.body;
    const guest = await prisma.guest.create({
      data: {
        name,
        email,
        hostId: req.user.userId
      }
    });
    res.status(201).json(guest);
  } catch (error) {
    console.error('Error creating guest:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Menu item routes
router.get('/menu/items', authenticateToken, async (req, res) => {
  try {
    const items = await prisma.menuItem.findMany({
      where: {
        hostId: req.user.userId
      }
    });
    res.json(items);
  } catch (error) {
    console.error('Error fetching menu items:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.post('/menu/items', authenticateToken, async (req, res) => {
  try {
    const { name, description, price } = req.body;
    const item = await prisma.menuItem.create({
      data: {
        name,
        description,
        price,
        hostId: req.user.userId,
        available: true
      }
    });
    res.status(201).json(item);
  } catch (error) {
    console.error('Error creating menu item:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.put('/menu/items/:id', authenticateToken, async (req, res) => {
  try {
    const { id } = req.params;
    const { name, description, price, available } = req.body;
    const item = await prisma.menuItem.update({
      where: {
        id,
        hostId: req.user.userId
      },
      data: {
        name,
        description,
        price,
        available
      }
    });
    res.json(item);
  } catch (error) {
    console.error('Error updating menu item:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.delete('/menu/items/:id', authenticateToken, async (req, res) => {
  try {
    const { id } = req.params;
    await prisma.menuItem.delete({
      where: {
        id,
        hostId: req.user.userId
      }
    });
    res.json({ message: 'Menu item deleted successfully' });
  } catch (error) {
    console.error('Error deleting menu item:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
