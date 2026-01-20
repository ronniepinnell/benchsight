import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  try {
    // Check for required environment variables
    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
    const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

    // If environment variables are missing, skip auth checks but allow request
    if (!supabaseUrl || !supabaseAnonKey) {
      console.warn('Supabase environment variables not set, skipping auth checks')
      return NextResponse.next()
    }

    // Create response once and reuse it
    const response = NextResponse.next({
      request: {
        headers: request.headers,
      },
    })

    const supabase = createServerClient(
      supabaseUrl,
      supabaseAnonKey,
      {
        cookies: {
          get(name: string) {
            return request.cookies.get(name)?.value
          },
          set(name: string, value: string, options: CookieOptions) {
            // Only set cookies on the response, don't create new response objects
            response.cookies.set({
              name,
              value,
              ...options,
            })
          },
          remove(name: string, options: CookieOptions) {
            // Only remove cookies on the response, don't create new response objects
            response.cookies.set({
              name,
              value: '',
              ...options,
            })
          },
        },
      }
    )

    // Refresh session if expired
    let user = null
    try {
      const {
        data: { user: authUser },
      } = await supabase.auth.getUser()
      user = authUser
    } catch (error) {
      // If auth check fails, continue without user (might be network issue)
      console.warn('Auth check failed in middleware:', error)
    }

    // Protected routes
    const protectedRoutes = ['/norad/admin', '/norad/tracker']
    const isProtectedRoute = protectedRoutes.some((route) =>
      request.nextUrl.pathname.startsWith(route)
    )

    // If accessing protected route without auth, redirect to login
    if (isProtectedRoute && !user) {
      const redirectUrl = new URL('/login', request.url)
      redirectUrl.searchParams.set('redirect', request.nextUrl.pathname)
      return NextResponse.redirect(redirectUrl)
    }

    // If accessing login page while authenticated, redirect to dashboard
    if (request.nextUrl.pathname === '/login' && user) {
      return NextResponse.redirect(new URL('/norad/standings', request.url))
    }

    return response
  } catch (error) {
    // Log error but don't break the request
    console.error('Middleware error:', error)
    // Return a basic response to allow the request to continue
    return NextResponse.next()
  }
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
}
