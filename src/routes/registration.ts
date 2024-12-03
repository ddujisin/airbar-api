import express from 'express';
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';

const router = express.Router();
const prisma = new PrismaClient();

// Host registration
router.post('/', async (req, res) => {
  try {
    console.log('Received registration request:', {
      email: req.body.email,
      name: req.body.name,
      phone: req.body.phone,
      address: req.body.address,
      role: req.body.role
    });

    const { email, password, name, phone, address } = req.body;

    if (!email || !password) {
      console.error('Missing required fields');
      return res.status(400).json({ error: 'Email and password are required' });
    }

    console.log('Checking for existing user with email:', email);
    const existingUser = await prisma.user.findUnique({
      where: { email }
    });

    if (existingUser) {
      console.log('User already exists with email:', email);
      return res.status(400).json({ error: 'Email already registered' });
    }

    console.log('Hashing password...');
    const hashedPassword = await bcrypt.hash(password, 10);

    console.log('Creating new user...');
    const user = await prisma.user.create({
      data: {
        email,
        password: hashedPassword,
        role: 'ADMIN',
        name,
        phone,
        address
      }
    });

    console.log('User created successfully:', { userId: user.id, email: user.email });
    res.status(201).json({ message: 'Host registered successfully', userId: user.id });
  } catch (error) {
    console.error('Error registering host:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
