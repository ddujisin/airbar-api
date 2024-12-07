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
  origin: ['http://localhost:3000', 'https://airbar-web-2684925f8263.herokuapp.com'],
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

// Protected routes at top-level
app.use('/api/admin', authenticateToken, adminRoutes);
app.use('/api/orders', authenticateToken, orderRoutes);

// For menu routes, do not apply `authenticateToken` here.
// Instead, let `menu.ts` determine which routes are protected and which are public.
app.use('/api/menu', menuRoutes);

export default app;