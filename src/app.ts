import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import authRoutes from './routes/auth';
import menuRoutes from './routes/menu';
import orderRoutes from './routes/orders';
import adminRoutes from './routes/admin';
import { authenticateToken } from './middleware/auth';

dotenv.config();

const app = express();

app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true
}));
app.use(express.json());

// Public routes
app.use('/auth', authRoutes);
app.use('/admin/register', adminRoutes); // Public host registration

// Protected routes
app.use('/admin', authenticateToken, adminRoutes); // Other admin routes require auth
app.use('/menu', authenticateToken, menuRoutes);
app.use('/orders', authenticateToken, orderRoutes);

export default app;
