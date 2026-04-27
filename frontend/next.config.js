/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.INTERNAL_API_BASE_URL
          ? `${process.env.INTERNAL_API_BASE_URL}/api/:path*`
          : 'http://localhost:8000/api/:path*',
      },
      {
        source: '/auth/:path*',
        destination: process.env.INTERNAL_API_BASE_URL
          ? `${process.env.INTERNAL_API_BASE_URL}/auth/:path*`
          : 'http://localhost:8000/auth/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
