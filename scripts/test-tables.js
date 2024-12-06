const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function test() {
  try {
    console.log('Testing Reservation table access...');
    const reservations = await prisma.reservation.findMany();
    console.log('Successfully queried reservations:', reservations);

    console.log('\nTesting Guest table access...');
    const guests = await prisma.guest.findMany();
    console.log('Successfully queried guests:', guests);
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await prisma.$disconnect();
  }
}

test();
