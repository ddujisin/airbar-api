import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import authRoutes from './routes/auth';
import menuRoutes from './routes/menu';
import orderRoutes from './routes/orders';
import { authenticateToken } from './middleware/auth';

dotenv.config();

const app = express();

app.use(cors());
app.use(express.json());

// Public routes
app.use('/auth', authRoutes);

// Protected routes
app.use('/menu', authenticateToken, menuRoutes);
app.use('/orders', authenticateToken, orderRoutes);

export default app;
