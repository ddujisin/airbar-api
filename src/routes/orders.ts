import { Router, Request, Response } from 'express';
import { PrismaClient } from '@prisma/client';
import { authenticateToken } from '../middleware/auth';
import type { AuthenticatedRequest } from '../middleware/auth';

const router = Router();
const prisma = new PrismaClient();

router.post('/', authenticateToken, async (req: Request, res: Response) => {
  const { reservationId, items } = req.body;

  try {
    // Verify reservation exists and belongs to current date
    const reservation = await prisma.reservation.findFirst({
      where: {
        id: reservationId,
        startDate: { lte: new Date() },
        endDate: { gte: new Date() }
      }
    });

    if (!reservation) {
      return res.status(400).json({ error: 'Invalid or expired reservation' });
    }

    // Calculate total price and create order with items
    let totalPrice = 0;
    const orderItems = [];

    for (const item of items) {
      const menuItem = await prisma.menuItem.findUnique({
        where: { id: item.menuItemId }
      });

      if (!menuItem || !menuItem.available) {
        return res.status(400).json({ error: `Menu item ${item.menuItemId} not available` });
      }

      totalPrice += menuItem.price * item.quantity;
      orderItems.push({
        menuItemId: item.menuItemId,
        quantity: item.quantity,
        price: menuItem.price
      });
    }

    const order = await prisma.order.create({
      data: {
        reservationId,
        totalPrice,
        status: 'pending',
        items: {
          create: orderItems
        }
      },
      include: {
        items: {
          include: {
            menuItem: true
          }
        },
        reservation: {
          include: {
            guest: true
          }
        }
      }
    });

    res.status(201).json(order);
  } catch (error) {
    console.error('Order creation error:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

router.get('/', authenticateToken, async (req: Request, res: Response) => {
  const isAdmin = (req as AuthenticatedRequest).user.role === 'ADMIN';
  const userId = (req as AuthenticatedRequest).user.userId;

  try {
    const orders = await prisma.order.findMany({
      where: isAdmin ? {
        reservation: {
          hostId: userId
        }
      } : {
        reservation: {
          guest: {
            hostId: userId
          }
        }
      },
      include: {
        items: {
          include: {
            menuItem: true
          }
        },
        reservation: {
          include: {
            guest: true
          }
        }
      }
    });
    res.json(orders);
  } catch (error) {
    console.error('Order fetch error:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

export default router;
