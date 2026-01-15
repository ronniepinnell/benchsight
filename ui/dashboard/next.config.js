/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    // Allow external images from noradhockey.com and Supabase storage
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'www.noradhockey.com',
        pathname: '/wp-content/uploads/**',
      },
      {
        protocol: 'http',
        hostname: 'www.noradhockey.com',
        pathname: '/wp-content/uploads/**',
      },
      {
        // WordPress CDN (Jetpack Photon)
        protocol: 'https',
        hostname: 'i0.wp.com',
        pathname: '/www.noradhockey.com/**',
      },
      {
        protocol: 'https',
        hostname: 'i1.wp.com',
        pathname: '/www.noradhockey.com/**',
      },
      {
        protocol: 'https',
        hostname: 'i2.wp.com',
        pathname: '/www.noradhockey.com/**',
      },
      {
        protocol: 'https',
        hostname: '*.supabase.co',
        pathname: '/storage/v1/object/**',
      },
      {
        protocol: 'http',
        hostname: 'localhost',
      },
      {
        protocol: 'http',
        hostname: '127.0.0.1',
      },
    ],
    // Allow unoptimized images for better compatibility
    unoptimized: false,
    // Disable strict domain checking for development
    dangerouslyAllowSVG: true,
    contentDispositionType: 'attachment',
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },
  // During migration, allow production builds even if TypeScript has errors.
  // This does NOT affect runtime behaviour, only build-time checking.
  typescript: {
    ignoreBuildErrors: true,
  },

  // Server Actions are enabled by default in Next.js 14+
  // Routes are now under /norad folder structure, so no basePath needed
  
  // Turbopack configuration (Turbopack is default in Next.js 16)
  turbopack: {
    // Set root to current directory to fix multiple lockfile warning
    root: __dirname,
  },
  
  reactStrictMode: false,
}

module.exports = nextConfig
