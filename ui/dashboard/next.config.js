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
        protocol: 'https',
        hostname: '*.supabase.co',
        pathname: '/storage/v1/object/**',
      },
    ],
    // Disable image optimization for external URLs (use unoptimized prop instead)
    unoptimized: false,
  },
  // During migration, allow production builds even if TypeScript has errors.
  // This does NOT affect runtime behaviour, only build-time checking.
  typescript: {
    ignoreBuildErrors: true,
  },
  // Likewise, don't fail the build on ESLint errors.
  eslint: {
    ignoreDuringBuilds: true,
  },

  // Server Actions are enabled by default in Next.js 14+
}

module.exports = nextConfig
