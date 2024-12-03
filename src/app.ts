import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import authRoutes from './routes/auth';
import menuRoutes from './routes/menu';
import orderRoutes from './routes/orders';
import adminRoutes from './routes/admin';
import registrationRoutes from './routes/registration';
import { authenticateToken } from './middleware/auth';

dotenv.config();

const app = express();

app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true
}));
app.use(express.json());

// Public routes
app.use('/api/auth', authRoutes);
app.use('/api/admin/register', registrationRoutes);

// Protected routes
app.use('/api/admin', authenticateToken, adminRoutes); // Other admin routes require auth
app.use('/api/menu', authenticateToken, menuRoutes);
app.use('/api/orders', authenticateToken, orderRoutes);

export default app;
