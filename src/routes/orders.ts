import { Router } from 'express';
import { PrismaClient } from '@prisma/client';

const router = Router();
const prisma = new PrismaClient();

router.post('/', async (req, res) => {
  const { menuItemId, quantity } = req.body;
  const userId = req.user!.userId;

  try {
    const menuItem = await prisma.menuItem.findUnique({
      where: { id: menuItemId }
    });

    if (!menuItem || !menuItem.available) {
      return res.status(400).json({ error: 'Menu item not available' });
    }

    const order = await prisma.order.create({
      data: {
        userId,
        menuItemId,
        quantity,
        totalPrice: menuItem.price * quantity
      },
      include: {
        menuItem: true,
        user: true
      }
    });

    res.status(201).json(order);
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

router.get('/', async (req, res) => {
  const userId = req.user!.userId;
  const isAdmin = req.user?.role === 'admin';

  try {
    const orders = await prisma.order.findMany({
      where: isAdmin ? {} : { userId },
      include: {
        menuItem: true,
        user: {
          select: {
            id: true,
            email: true
          }
        }
      }
    });
    res.json(orders);
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

export default router;
