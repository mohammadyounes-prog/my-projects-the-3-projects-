import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  console.log('Middleware executing for:', request.nextUrl.pathname);
  const response = NextResponse.next();
  response.headers.set('Cross-Origin-Opener-Policy', 'unsafe-none');
  return response;
}
