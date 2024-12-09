import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function checkMenuItem() {
  try {
    const itemId = '0c855e5c-d1cb-469f-8ec1-62f205dad9f7';
    console.log('Checking for menu item with ID:', itemId);

    const menuItem = await prisma.menuItem.findUnique({
      where: {
        id: itemId
      }
    });

    if (menuItem) {
      console.log('Menu item found:', menuItem);
    } else {
      console.log('Menu item not found');

      // List all menu items to see what's available
      const allItems = await prisma.menuItem.findMany();
      console.log('\nAll menu items in database:');
      console.log(JSON.stringify(allItems, null, 2));
    }
  } catch (error) {
    console.error('Error checking menu item:', error);
  } finally {
    await prisma.$disconnect();
  }
}

checkMenuItem();
