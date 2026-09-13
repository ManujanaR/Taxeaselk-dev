/** @type {import('next').NextConfig} */
const nextConfig = {
  // Always re-fetch server data on navigation (default keeps a 30s client cache of dynamic pages).
  experimental: { staleTimes: { dynamic: 0 } },
  async rewrites() {
    // Browser calls /api/* same-origin; Next proxies to FastAPI so the
    // httpOnly session cookie needs no CORS/credentials handling.
    return [{ source: "/api/:path*", destination: `${process.env.API_URL || "http://localhost:8000"}/api/:path*` }];
  },
};

module.exports = nextConfig;
