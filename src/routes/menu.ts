import { Router } from 'express';
import { PrismaClient } from '@prisma/client';
import { authorizeRole } from '../middleware/auth';

const router = Router();
const prisma = new PrismaClient();

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

router.post('/', authorizeRole(['admin']), async (req, res) => {
  const { name, description, price } = req.body;

  try {
    const menuItem = await prisma.menuItem.create({
      data: {
        name,
        description,
        price
      }
    });
    res.status(201).json(menuItem);
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

router.put('/:id', authorizeRole(['admin']), async (req, res) => {
  const { id } = req.params;
  const { name, description, price, available } = req.body;

  try {
    const menuItem = await prisma.menuItem.update({
      where: { id },
      data: {
        name,
        description,
        price,
        available
      }
    });
    res.json(menuItem);
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

router.delete('/:id', authorizeRole(['admin']), async (req, res) => {
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
