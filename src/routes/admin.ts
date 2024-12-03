import express from 'express';
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { authenticateToken, requireSuperAdmin } from '../middleware/auth';

const router = express.Router();
const prisma = new PrismaClient();

// Host registration
router.post('/register', async (req, res) => {
  try {
    const { email, password } = req.body;

    const existingUser = await prisma.user.findUnique({
      where: { email }
    });

    if (existingUser) {
      return res.status(400).json({ error: 'Email already registered' });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    const user = await prisma.user.create({
      data: {
        email,
        password: hashedPassword,
        role: 'ADMIN'
      }
    });

    res.status(201).json({ message: 'Host registered successfully' });
  } catch (error) {
    console.error('Error registering host:', error);
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

    const token = jwt.sign(
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
        token,
        userId: host.id,
        expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000)
      }
    });

    res.json({ token });
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
