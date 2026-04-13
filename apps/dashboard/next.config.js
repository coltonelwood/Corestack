/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ["@abf/core", "@abf/db"],
  output: "standalone",
  poweredByHeader: false,
};

module.exports = nextConfig;
