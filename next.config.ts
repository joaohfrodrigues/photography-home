import type { NextConfig } from 'next'
import path from 'path'

const nextConfig: NextConfig = {
  outputFileTracingRoot: path.join(__dirname),
  outputFileTracingIncludes: {
    '/**': ['./data/photos.db'],
  },
  // Tell webpack to require better-sqlite3 at runtime (native module, not bundled)
  webpack(config) {
    config.externals = [...(config.externals ?? []), { 'better-sqlite3': 'commonjs better-sqlite3' }]
    return config
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'images.unsplash.com',
      },
      {
        protocol: 'https',
        hostname: 'plus.unsplash.com',
      },
    ],
  },
}

export default nextConfig
