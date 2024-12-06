import { Router } from 'express';
import { PrismaClient } from '@prisma/client';
import { authorizeRole, authenticateToken } from '../middleware/auth';

const router = Router();
const prisma = new PrismaClient();

// Public routes
router.get('/', async (req, res) => {
  try {
    const menuItems = await prisma.menuItem.findMany({
      where: { available: true }
    });
    res.json(menuItems);
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

router.get('/:id', async (req, res) => {
  const { id } = req.params;
  try {
    const menuItem = await prisma.menuItem.findUnique({
      where: { id }
    });
    if (!menuItem) {
      return res.status(404).json({ error: 'Menu item not found' });
    }
    res.json(menuItem);
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

// Protected routes (require authentication)
router.post('/', authenticateToken, authorizeRole(['admin']), async (req, res) => {
  const { name, description, price } = req.body;
  try {
    const menuItem = await prisma.menuItem.create({
      data: {
        name,
        description,
        price: Number(price),
        available: true
      }
    });
    res.status(201).json(menuItem);
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

router.put('/:id', authenticateToken, authorizeRole(['admin']), async (req, res) => {
  const { id } = req.params;
  const { name, description, price, available } = req.body;
  try {
    const menuItem = await prisma.menuItem.update({
      where: { id },
      data: {
        name,
        description,
        price: Number(price),
        available
      }
    });
    res.json(menuItem);
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

router.delete('/:id', authenticateToken, authorizeRole(['admin']), async (req, res) => {
  const { id } = req.params;
  try {
    await prisma.menuItem.delete({
      where: { id }
    });
    res.json({ message: 'Menu item deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

export default router;
