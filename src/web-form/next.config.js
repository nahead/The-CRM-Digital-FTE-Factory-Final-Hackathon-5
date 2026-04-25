/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    API_ENDPOINT: process.env.API_ENDPOINT || 'http://localhost:8000',
  },
}

module.exports = nextConfig
