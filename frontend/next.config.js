/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    outputFileTracingRoot: __dirname,
  },
  // Disable strict mode to avoid hydration issues
  reactStrictMode: false,
  // Ensure proper client-side rendering
  swcMinify: true,
}

module.exports = nextConfig
