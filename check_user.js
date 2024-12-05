const { PrismaClient } = require('@prisma/client');
const bcrypt = require('bcrypt');
const prisma = new PrismaClient();

async function main() {
  try {
    console.log('Checking for admin user...');
    const user = await prisma.user.findUnique({
      where: { email: 'admin@test.com' }
    });

    if (!user) {
      console.log('Admin user not found, creating...');
      const hashedPassword = await bcrypt.hash('Admin123!', 10);
      const newUser = await prisma.user.create({
        data: {
          email: 'admin@test.com',
          password: hashedPassword,
          name: 'Test Admin',
          role: 'ADMIN',
          phone: '123-456-7890',
          address: '123 Test St'
        }
      });
      console.log('Created admin user:', newUser);
    } else {
      console.log('Found existing admin user:', user);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect());
