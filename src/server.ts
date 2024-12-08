import app from './app';
import { WebSocketServer } from 'ws';
import { createServer } from 'http';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

console.log('[Server Debug] Environment variables loaded:', {
  BACKEND_PORT: process.env.BACKEND_PORT,
  JWT_SECRET: process.env.JWT_SECRET ? 'Set' : 'Not set',
  DATABASE_URL: process.env.DATABASE_URL ? 'Set' : 'Not set'
});

const port = process.env.PORT || 3001;
const server = createServer(app);
const wss = new WebSocketServer({ server });

wss.on('connection', (ws) => {
  console.log('Client connected');

  ws.on('message', (message) => {
    console.log('Received:', message);
  });

  ws.on('close', () => {
    console.log('Client disconnected');
  });
});

server.listen(port, () => {
  console.log(`[Server Debug] Server running on port ${port}`);
  console.log('[Server Debug] Server configuration:', {
    port,
    nodeEnv: process.env.NODE_ENV
  });
});
