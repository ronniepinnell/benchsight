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
  
  // Experimental features
  experimental: {
    // Enable server actions if needed
    serverActions: true,
  },
}

module.exports = nextConfig
