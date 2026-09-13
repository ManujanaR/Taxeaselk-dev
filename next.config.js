/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    // Browser calls /api/* same-origin; Next proxies to FastAPI so the
    // httpOnly session cookie needs no CORS/credentials handling.
    return [{ source: "/api/:path*", destination: `${process.env.API_URL || "http://localhost:8000"}/api/:path*` }];
  },
};

module.exports = nextConfig;
