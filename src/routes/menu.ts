import { Router, Request, Response } from 'express';
import { PrismaClient } from '@prisma/client';
import { authenticateToken } from '../middleware/auth';
import type { AuthenticatedRequest } from '../middleware/auth';

const router = Router();
const prisma = new PrismaClient();

router.get('/', authenticateToken, async (req: Request, res: Response) => {
  try {
    const menuItems = await prisma.menuItem.findMany({
      where: {
        AND: [
          { available: true },
          { hostId: (req as AuthenticatedRequest).user.userId }
        ]
      }
    });
    res.json(menuItems);
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

router.post('/', authenticateToken, async (req: Request, res: Response) => {
  const { name, description, price } = req.body;

  try {
    const menuItem = await prisma.menuItem.create({
      data: {
        name,
        description,
        price: parseFloat(price),
        hostId: (req as AuthenticatedRequest).user.userId,
        available: true
      }
    });
    res.status(201).json(menuItem);
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

router.put('/:id', authenticateToken, async (req: Request, res: Response) => {
  const { id } = req.params;
  const { name, description, price, available } = req.body;

  try {
    const menuItem = await prisma.menuItem.update({
      where: {
        id,
        hostId: (req as AuthenticatedRequest).user.userId
      },
      data: {
        name,
        description,
        price: parseFloat(price),
        available
      }
    });
    res.json(menuItem);
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

router.delete('/:id', authenticateToken, async (req: Request, res: Response) => {
  const { id } = req.params;

  try {
    await prisma.menuItem.delete({
      where: {
        id,
        hostId: (req as AuthenticatedRequest).user.userId
      }
    });
    res.json({ message: 'Menu item deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

export default router;
