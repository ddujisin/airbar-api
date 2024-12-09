import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';

const prisma = new PrismaClient();

async function createTestReservation() {
  try {
    // First, find or create a test admin user
    let testAdmin = await prisma.user.findFirst({
      where: { email: 'test@example.com' }
    });

    if (!testAdmin) {
      console.log('Creating test admin user...');
      const hashedPassword = await bcrypt.hash('test123', 10);
      testAdmin = await prisma.user.create({
        data: {
          email: 'test@example.com',
          password: hashedPassword,
          name: 'Test Admin',
          role: 'ADMIN',
          phone: '123-456-7890',
          address: '123 Test St'
        }
      });
    }

    // Create a test guest
    let testGuest = await prisma.guest.findFirst({
      where: { email: 'guest@example.com' }
    });

    if (!testGuest) {
      console.log('Creating test guest...');
      testGuest = await prisma.guest.create({
        data: {
          name: 'Test Guest',
          email: 'guest@example.com',
          hostId: testAdmin.id
        }
      });
    }

    // Create a test reservation with PIN 9473
    const reservation = await prisma.reservation.create({
      data: {
        pin: '9473',
        hostId: testAdmin.id,
        guestId: testGuest.id,
        startDate: new Date(),
        endDate: new Date(Date.now() + 24 * 60 * 60 * 1000) // 24 hours from now
      }
    });

    console.log('Test reservation created:', reservation);
  } catch (error) {
    console.error('Error creating test reservation:', error);
  } finally {
    await prisma.$disconnect();
  }
}

createTestReservation();
