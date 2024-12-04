import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import authRoutes from './routes/auth';
import menuRoutes from './routes/menu';
import orderRoutes from './routes/orders';
import adminRoutes from './routes/admin';
import registrationRoutes from './routes/registration';
import { authenticateToken } from './middleware/auth';

// Load environment variables
dotenv.config();

console.log('[App Debug] Environment configuration:', {
  FRONTEND_URL: process.env.FRONTEND_URL,
  JWT_SECRET: process.env.JWT_SECRET ? 'Set' : 'Not set',
  DATABASE_URL: process.env.DATABASE_URL ? 'Set' : 'Not set',
  BACKEND_PORT: process.env.BACKEND_PORT
});

const app = express();

// Configure CORS
const corsOptions = {
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
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

// Public routes
app.use('/api/auth', authRoutes);
app.use('/api/admin/register', registrationRoutes);

// Protected routes
app.use('/api/admin', authenticateToken, adminRoutes);
app.use('/api/menu', authenticateToken, menuRoutes);
app.use('/api/orders', authenticateToken, orderRoutes);

export default app;
