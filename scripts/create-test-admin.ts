import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';

const prisma = new PrismaClient();

async function createTestAdmin() {
  try {
    const hashedPassword = await bcrypt.hash('test123', 10);
    const admin = await prisma.user.create({
      data: {
        email: 'test@example.com',
        password: hashedPassword,
        name: 'Test Admin',
        role: 'admin',
        phone: '123-456-7890',
        address: '123 Test St'
      }
    });
    console.log('Test admin created:', admin);
  } catch (error) {
    console.error('Error creating test admin:', error);
  } finally {
    await prisma.$disconnect();
  }
}

createTestAdmin();
