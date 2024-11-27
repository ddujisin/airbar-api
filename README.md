# AirBar API

## Overview
Express.js/Node.js backend for the AirBar application, providing REST APIs and WebSocket functionality for real-time bar order management.

## Technology Stack
- Express.js with Node.js
- TypeScript for type safety
- PostgreSQL with Prisma ORM
- JWT for authentication
- WebSocket for real-time notifications

## Environment Variables
Create a `.env` file with the following:
```bash
# Database
DATABASE_URL="postgresql://user:password@localhost:5432/airbar"

# Authentication
JWT_SECRET="your-jwt-secret"
JWT_EXPIRY="3600"  # Token expiry in seconds

# Server
PORT=3000
NODE_ENV="development"
CORS_ORIGIN="http://localhost:3000"  # Frontend URL

# WebSocket
WS_PATH="/ws"
```

## Project Structure
```
src/
├── routes/          # API route handlers
├── middleware/      # Express middleware
├── services/        # Business logic
├── models/          # Prisma models
├── utils/           # Utility functions
├── websocket/       # WebSocket handlers
└── types/          # TypeScript definitions
```

## Setup and Installation

### Prerequisites
- Node.js 18+
- PostgreSQL 13+
- npm or yarn

### Development Setup
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

## API Documentation

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

### Notifications
- GET `/notifications` - Get user notifications
- POST `/notifications/preferences` - Update notification preferences
- WS `/ws` - WebSocket connection for real-time updates

## Database Management
```bash
# Generate Prisma client
npm run prisma:generate

# Create migration
npm run prisma:migrate:dev

# Apply migrations
npm run prisma:migrate:deploy

# Reset database
npm run prisma:reset
```

## Testing
```bash
# Run all tests
npm test

# Run specific test suite
npm test -- orders.test.ts

# Run tests with coverage
npm run test:coverage
```

## WebSocket Integration
The server implements WebSocket connections for real-time updates:
- Order status changes
- New order notifications
- Menu item updates

## Security
- JWT-based authentication
- Role-based access control (RBAC)
- Request rate limiting
- CORS configuration
- Input validation and sanitization

## Error Handling
- Standardized error responses
- Error codes and messages
- Validation error formatting
- Custom error classes

## Deployment

### Production Setup
1. Build the application:
```bash
npm run build
```

2. Set production environment variables:
```bash
NODE_ENV=production
CORS_ORIGIN=https://your-frontend-domain.com
```

3. Run database migrations:
```bash
npm run prisma:migrate:deploy
```

4. Start the server:
```bash
npm start
```

### Docker Deployment
```bash
# Build image
docker build -t airbar-api .

# Run container
docker run -p 3000:3000 --env-file .env airbar-api
```

## Performance Optimization
- Connection pooling
- Query optimization
- Response caching
- Rate limiting

## Monitoring
- Error logging
- Performance metrics
- Request/response logging
- WebSocket connection monitoring

## Contributing
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License
MIT License - see LICENSE file for details
