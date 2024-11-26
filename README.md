# AirBar API - Express.js/Node.js backend for the AirBar application.

## Technology Stack

- Express.js with Node.js
- TypeScript for type safety
- PostgreSQL with Prisma ORM
- JWT for authentication
- WebSocket for real-time notifications

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment:
- Copy `.env.example` to `.env`
- Update the database URL and JWT secret

3. Initialize database:
```bash
npm run prisma:generate
npm run prisma:migrate
```

4. Start development server:
```bash
npm run dev
```

## API Endpoints

### Authentication
- POST `/auth/register` - Register new user
- POST `/auth/login` - User login
- POST `/auth/logout` - User logout

### Menu Management
- GET `/menu` - List available menu items
- POST `/menu` - Add menu item (admin only)
- PUT `/menu/:id` - Update menu item (admin only)
- DELETE `/menu/:id` - Delete menu item (admin only)

### Orders
- POST `/orders` - Create new order
- GET `/orders` - List orders (filtered by user role)

## Development

- Build: `npm run build`
- Test: `npm test`
- Generate Prisma client: `npm run prisma:generate`
- Run migrations: `npm run prisma:migrate`

## WebSocket Events

The server implements WebSocket connections for real-time updates:
- Order status changes
- New order notifications
- Menu item updates
