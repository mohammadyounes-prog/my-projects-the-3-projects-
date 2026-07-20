/** @type {import('next').NextConfig} */
const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  async redirects() {
    return [
      {
        source: '/',
        destination: '/en',
        permanent: false,
      },
      {
        source: '/:path*',
        has: [
          {
            type: 'query',
            key: 'sso_token',
          },
        ],
        destination: '/en/:path*',
        permanent: false,
      },
    ]
  },
};

module.exports = nextConfig;
