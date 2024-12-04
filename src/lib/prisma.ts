import { PrismaClient } from '@prisma/client';

console.log('[Prisma Debug] Initializing Prisma client');
console.log('[Prisma Debug] Database URL:', process.env.DATABASE_URL ? 'Set' : 'Not set');

const prisma = new PrismaClient({
  log: ['query', 'info', 'warn', 'error'],
});

// Test database connection
prisma.$connect()
  .then(() => {
    console.log('[Prisma Debug] Successfully connected to database');
  })
  .catch((error) => {
    console.error('[Prisma Debug] Failed to connect to database:', error);
    process.exit(1);
  });

process.on('beforeExit', async () => {
  await prisma.$disconnect();
});

export default prisma;
