import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Public routes that don't require authentication
  const publicPaths = ['/login', '/admin/register', '/orders'];
  if (publicPaths.some(path => request.nextUrl.pathname.startsWith(path))) {
    return NextResponse.next();
  }

  // API routes are handled by the backend
  if (request.nextUrl.pathname.startsWith('/api')) {
    return NextResponse.next();
  }

  // Check for token on protected routes
  const token = request.headers.get('authorization')?.replace('Bearer ', '');
  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
