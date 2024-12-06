import { Router, Response } from 'express';
import { PrismaClient } from '@prisma/client';
import { AuthenticatedRequestHandler } from '../middleware/auth';

const router = Router();
const prisma = new PrismaClient();

const createOrder: AuthenticatedRequestHandler = async (req, res) => {
  const { menuItemId, quantity, reservationId } = req.body;

  try {
    const menuItem = await prisma.menuItem.findUnique({
      where: { id: menuItemId }
    });

    if (!menuItem || !menuItem.available) {
      return res.status(400).json({ error: 'Menu item not available' });
    }

    const order = await prisma.order.create({
      data: {
        reservationId,
        totalPrice: menuItem.price * quantity,
        OrderItem: {
          create: {
            id: `${Date.now()}-${menuItemId}`,
            menuItemId,
            quantity,
            price: menuItem.price
          }
        }
      },
      include: {
        OrderItem: {
          include: {
            MenuItem: true
          }
        },
        Reservation: {
          include: {
            Guest: true
          }
        }
      }
    });

    res.status(201).json(order);
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
};

const getOrders: AuthenticatedRequestHandler = async (req, res) => {
  const userId = req.user.userId;
  const isAdmin = req.user.role === 'ADMIN';

  try {
    const orders = await prisma.order.findMany({
      where: isAdmin ? {} : { Reservation: { hostId: userId } },
      include: {
        OrderItem: {
          include: {
            MenuItem: true
          }
        },
        Reservation: {
          include: {
            Guest: true
          }
        }
      }
    });
    res.json(orders);
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
};

router.post('/', createOrder);
router.get('/', getOrders);

export default router;
