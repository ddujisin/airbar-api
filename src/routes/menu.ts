import { Router } from 'express';
import { PrismaClient, MenuItem } from '@prisma/client';
import { authorizeRole, authenticateToken } from '../middleware/auth';
import { Request, Response } from 'express';

interface CreateMenuItemBody {
  name: string;
  description: string;
  price: number;
}

interface UpdateMenuItemBody extends CreateMenuItemBody {
  available?: boolean;
}

const router = Router();
const prisma = new PrismaClient();

// Public routes
router.get('/', async (_req: Request, res: Response) => {
  try {
    const menuItems = await prisma.menuItem.findMany({
      where: { available: true }
    });
    res.json(menuItems);
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

router.get('/:id', async (req: Request, res: Response) => {
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
router.post('/', authenticateToken, authorizeRole(['admin']), async (req: Request, res: Response) => {
  const { name, description, price } = req.body;
  const hostId = req.user?.userId;

  if (!hostId) {
    return res.status(401).json({ error: 'User ID not found in token' });
  }

  try {
    const menuItem = await prisma.menuItem.create({
      data: {
        name,
        description,
        price: Number(price),
        hostId
      }
    });
    res.status(201).json(menuItem);
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

router.put('/:id', authenticateToken, authorizeRole(['admin']), async (req: Request, res: Response) => {
  const { id } = req.params;
  const { name, description, price, available } = req.body;
  const hostId = req.user?.userId;

  if (!hostId) {
    return res.status(401).json({ error: 'User ID not found in token' });
  }

  try {
    const menuItem = await prisma.menuItem.update({
      where: {
        id,
        hostId // Ensure users can only update their own items
      },
      data: {
        name,
        description,
        price: Number(price),
        ...(available !== undefined && { available })
      }
    });
    res.json(menuItem);
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

router.delete('/:id', authenticateToken, authorizeRole(['admin']), async (req: Request, res: Response) => {
  const { id } = req.params;
  const hostId = req.user?.userId;

  if (!hostId) {
    return res.status(401).json({ error: 'User ID not found in token' });
  }

  try {
    await prisma.menuItem.delete({
      where: {
        id,
        hostId // Ensure users can only delete their own items
      }
    });
    res.json({ message: 'Menu item deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

export default router;
