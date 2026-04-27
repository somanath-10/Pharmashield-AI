import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token')?.value;
  const path = request.nextUrl.pathname;

  // Protect dashboard routes
  if (path.startsWith('/patient') || path.startsWith('/pharmacist') || path.startsWith('/doctor') || path.startsWith('/admin')) {
    if (!token) {
      return NextResponse.redirect(new URL('/login', request.url));
    }
    
    // In a full implementation, we'd verify the JWT payload here to check roles.
    // For MVP, we at least ensure a token exists. A robust approach would be to
    // decode the JWT without verification (since it's client-side) and check the 'role' claim.
    try {
      // Basic JWT decode (token is Header.Payload.Signature)
      const payloadBase64 = token.split('.')[1];
      if (payloadBase64) {
        const payload = JSON.parse(atob(payloadBase64));
        const role = payload.role; // e.g. "PATIENT"
        
        // Simple role guard
        if (path.startsWith('/patient') && role !== 'PATIENT') return NextResponse.redirect(new URL('/login', request.url));
        if (path.startsWith('/pharmacist') && role !== 'PHARMACIST') return NextResponse.redirect(new URL('/login', request.url));
        if (path.startsWith('/doctor') && role !== 'DOCTOR') return NextResponse.redirect(new URL('/login', request.url));
        if (path.startsWith('/admin') && role !== 'ADMIN') return NextResponse.redirect(new URL('/login', request.url));
      }
    } catch (e) {
      // Ignore parse errors, just fallback to default behavior
    }
  }

  // Redirect root to login if no active session
  if (path === '/') {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/', '/patient/:path*', '/pharmacist/:path*', '/doctor/:path*', '/admin/:path*'],
};
