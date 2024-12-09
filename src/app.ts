import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { PrismaClient } from '@prisma/client';
import authRoutes from './routes/auth';
import menuRoutes from './routes/menu';
import orderRoutes from './routes/orders';
import adminRoutes from './routes/admin';
import registrationRoutes from './routes/registration';
import { authenticateToken } from './middleware/auth';
import { Router } from 'express';

// Load environment variables
dotenv.config();

console.log('[App Debug] Environment configuration:', {
  FRONTEND_URL: process.env.FRONTEND_URL,
  JWT_SECRET: process.env.JWT_SECRET ? 'Set' : 'Not set',
  DATABASE_URL: process.env.DATABASE_URL ? 'Set' : 'Not set',
  BACKEND_PORT: process.env.BACKEND_PORT
});

const app = express();
const prisma = new PrismaClient();

// Configure CORS
const corsOptions = {
  origin: ['http://localhost:3000', 'http://localhost:3001', 'http://localhost:3002'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
};

console.log('[App Debug] CORS configuration:', corsOptions);

app.use(cors(corsOptions));
app.use(express.json());

// Debug middleware for all requests
app.use((req, res, next) => {
  console.log('[App Debug] Incoming request:', {
    method: req.method,
    path: req.path,
    headers: req.headers,
    body: req.body
  });
  next();
});

// Split menu routes into public and protected
const publicMenuRouter = Router();
publicMenuRouter.get('/items/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const menuItem = await prisma.menuItem.findUnique({
      where: {
        id,
        available: true
      }
    });
    if (!menuItem) {
      return res.status(404).json({ error: 'Menu item not found' });
    }
    res.json(menuItem);
  } catch (error) {
    console.error('Error fetching menu item:', error);
    res.status(500).json({ error: 'Server error' });
  }
});

// Public routes
app.use('/api/auth', authRoutes);
app.use('/api/admin/register', registrationRoutes);
app.use('/api/public/menu', publicMenuRouter);

// Protected routes
app.use('/api/admin', authenticateToken, adminRoutes);
app.use('/api/menu', authenticateToken, menuRoutes);
app.use('/api/orders', authenticateToken, orderRoutes);

export default app;
