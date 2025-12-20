const { withSentryConfig } = require("@sentry/nextjs");

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost', 'librarymomsclub.ru', 'api.librarymomsclub.ru'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL + '/:path*',
      },
    ];
  },
}

module.exports = withSentryConfig(nextConfig, {
  // Sentry options
  silent: true,
  org: "momsclub",
  project: "javascript-nextjs",
}, {
  // Upload source maps for better error tracking
  widenClientFileUpload: true,
  hideSourceMaps: true,
  disableLogger: true,
});
