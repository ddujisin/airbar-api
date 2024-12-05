import { Router } from 'express';
import { PrismaClient } from '@prisma/client';
import { authenticateToken } from '../middleware/auth';

const router = Router();
const prisma = new PrismaClient();

router.post('/', authenticateToken, async (req, res) => {
  const { itemId, quantity, reservationId } = req.body;
  const hostId = req.user!.userId;

  try {
    const item = await prisma.item.findFirst({
      where: {
        id: itemId,
        hostId // Ensure the item belongs to the host
      }
    });

    if (!item) {
      return res.status(400).json({ error: 'Item not available' });
    }

    const order = await prisma.order.create({
      data: {
        quantity,
        totalPrice: item.price * quantity,
        hostId,
        itemId,
        reservationId
      },
      include: {
        item: true,
        reservation: {
          include: {
            guest: true
          }
        }
      }
    });

    res.status(201).json(order);
  } catch (error) {
    console.error('[Orders Error]:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

router.get('/', authenticateToken, async (req, res) => {
  const hostId = req.user!.userId;

  try {
    const orders = await prisma.order.findMany({
      where: { hostId },
      include: {
        item: true,
        reservation: {
          include: {
            guest: true
          }
        }
      }
    });
    res.json(orders);
  } catch (error) {
    console.error('[Orders Error]:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

export default router;
