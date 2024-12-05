const { PrismaClient } = require('@prisma/client');
const bcrypt = require('bcrypt');

async function setupDatabase() {
    const prisma = new PrismaClient();
    try {
        console.log('Connecting to database...');
        await prisma.$connect();

        console.log('Creating admin user...');
        const hashedPassword = await bcrypt.hash('Admin123!', 10);
        const user = await prisma.user.upsert({
            where: { email: 'admin@test.com' },
            update: {
                password: hashedPassword,
                role: 'ADMIN',
                isSuperAdmin: true
            },
            create: {
                email: 'admin@test.com',
                password: hashedPassword,
                name: 'Admin User',
                role: 'ADMIN',
                isSuperAdmin: true
            }
        });
        console.log('Admin user created/updated successfully:', {
            id: user.id,
            email: user.email,
            role: user.role,
            isSuperAdmin: user.isSuperAdmin
        });
    } catch (error) {
        console.error('Database setup error:', error);
        process.exit(1);
    } finally {
        await prisma.$disconnect();
    }
}

setupDatabase().catch(console.error);
