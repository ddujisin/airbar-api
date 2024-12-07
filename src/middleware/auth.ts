import { Request, Response, NextFunction, RequestHandler } from 'express';
import jwt from 'jsonwebtoken';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export interface TokenPayload {
  userId: string;
  role: string;
  isSuperAdmin: boolean;
  impersonatedBy?: string;
}

export interface AuthenticatedRequest extends Request {
  user: TokenPayload;
}

export function isAuthenticatedRequest(req: Request): req is AuthenticatedRequest {
  return 'user' in req && req.user !== undefined;
}

declare global {
  namespace Express {
    interface Request {
      user?: TokenPayload;
    }
  }
}

export const authenticateToken: RequestHandler = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const authHeader = req.headers['authorization'];
  const accessToken = authHeader && authHeader.split(' ')[1];

  if (!accessToken) {
    return res.status(401).json({ error: 'Authentication required' });
  }

  try {
    const decoded = jwt.verify(accessToken, process.env.JWT_SECRET!) as TokenPayload;
    const session = await prisma.session.findUnique({
      where: { accessToken },
      include: { user: true }
    });

    if (!session || new Date() > session.expiresAt) {
      return res.status(401).json({ error: 'Session expired' });
    }

    req.user = decoded;
    next();
  } catch (error) {
    return res.status(403).json({ error: 'Invalid token' });
  }
};

// Type assertion middleware
export const assertAuthenticated: RequestHandler = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  if (!isAuthenticatedRequest(req)) {
    return res.status(401).json({ error: 'Authentication required' });
  }
  next();
};

export const requireSuperAdmin: RequestHandler = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  if (!isAuthenticatedRequest(req) || !req.user.isSuperAdmin) {
    return res.status(403).json({ error: 'Super admin access required' });
  }
  next();
};

export const authorizeRole = (roles: string[]): RequestHandler => {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!isAuthenticatedRequest(req) || !roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    next();
  };
};
