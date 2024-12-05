import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import cookieParser from 'cookie-parser';
import authRoutes from './routes/auth';
import itemRoutes from './routes/items';
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
  origin: process.env.FRONTEND_URL || 'http://localhost:3002',
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: [
    'Content-Type',
    'Authorization',
    'Cookie',
    'X-Requested-With',
    'Accept'
  ],
  exposedHeaders: ['Set-Cookie'],
  maxAge: 86400 // 24 hours
};

console.log('[App Debug] CORS configuration:', corsOptions);

app.use(cors(corsOptions));
app.use(express.json());
app.use(cookieParser());  // Add cookie-parser middleware

// Debug middleware for all requests
app.use((req, res, next) => {
  console.log('[App Debug] Incoming request:', {
    method: req.method,
    path: req.path,
    headers: {
      ...req.headers,
      authorization: req.headers.authorization ? 'Bearer [redacted]' : undefined
    },
    body: req.method === 'POST' ? req.body : undefined,
    query: req.query,
    timestamp: new Date().toISOString()
  });
  next();
});

// Public routes
app.use('/api/auth', authRoutes);
app.use('/api/admin/register', registrationRoutes);

// Protected routes
app.use('/api/admin', authenticateToken, adminRoutes);
app.use('/api/items', authenticateToken, itemRoutes);
app.use('/api/orders', authenticateToken, orderRoutes);

export default app;
