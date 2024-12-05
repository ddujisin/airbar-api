import { Router } from 'express';
import { PrismaClient } from '@prisma/client';
import { authenticateToken } from '../middleware/auth';

const router = Router();
const prisma = new PrismaClient();

router.get('/', authenticateToken, async (req, res) => {
  try {
    const items = await prisma.Item.findMany({
      where: { hostId: req.user!.userId }
    });
    res.json(items);
  } catch (error) {
    console.error('[Items Error]:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

router.post('/', authenticateToken, async (req, res) => {
  const { name, description, price } = req.body;
  const hostId = req.user!.userId;

  try {
    const item = await prisma.Item.create({
      data: {
        name,
        description,
        price,
        hostId
      }
    });
    res.status(201).json(item);
  } catch (error) {
    console.error('[Items Error]:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

router.put('/:id', authenticateToken, async (req, res) => {
  const { id } = req.params;
  const { name, description, price } = req.body;
  const hostId = req.user!.userId;

  try {
    const item = await prisma.Item.update({
      where: {
        id,
        hostId // Ensure the item belongs to the host
      },
      data: {
        name,
        description,
        price
      }
    });
    res.json(item);
  } catch (error) {
    console.error('[Items Error]:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

router.delete('/:id', authenticateToken, async (req, res) => {
  const { id } = req.params;
  const hostId = req.user!.userId;

  try {
    await prisma.Item.delete({
      where: {
        id,
        hostId // Ensure the item belongs to the host
      }
    });
    res.json({ message: 'Item deleted successfully' });
  } catch (error) {
    console.error('[Items Error]:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

export default router;
