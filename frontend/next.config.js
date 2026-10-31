/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Emit a self-contained server bundle for the production Docker image.
  output: "standalone",
  transpilePackages: ["three"],
  // Turbopack is the default bundler in Next.js 16.
  // `canvas` is an optional native dependency of three.js and must stay external.
  turbopack: {
    resolveAlias: {
      canvas: "./src/shims/empty-module.js",
    },
  },
};

module.exports = nextConfig;
