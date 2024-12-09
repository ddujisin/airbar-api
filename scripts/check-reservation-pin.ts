import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function checkReservationPin() {
  try {
    const pin = '9473';
    console.log('Checking for reservation with PIN:', pin);

    const reservation = await prisma.reservation.findFirst({
      where: { pin },
      include: {
        host: true
      }
    });

    if (reservation) {
      console.log('Reservation found:', reservation);
    } else {
      console.log('Reservation not found');

      // List all reservations to see what's available
      const allReservations = await prisma.reservation.findMany({
        include: {
          host: true
        }
      });
      console.log('\nAll reservations in database:');
      console.log(JSON.stringify(allReservations, null, 2));
    }
  } catch (error) {
    console.error('Error checking reservation:', error);
  } finally {
    await prisma.$disconnect();
  }
}

checkReservationPin();
