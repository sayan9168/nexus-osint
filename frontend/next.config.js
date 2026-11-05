/** @type {import('next').NextConfig} */
// Where the FastAPI backend lives for server-side proxying. Override with
// NEXUS_BACKEND_URL when the backend runs somewhere other than the default.
const BACKEND = process.env.NEXUS_BACKEND_URL || "http://127.0.0.1:8000";

const nextConfig = {
  reactStrictMode: true,
  // Emit a self-contained server bundle for the production Docker image.
  output: "standalone",
  transpilePackages: ["three"],
  // Allow the dev server to serve requests coming through a remote preview
  // host / tunnel in addition to localhost.
  allowedDevOrigins: ["*.e2b.app", "localhost:3000", "127.0.0.1:3000"],
  // Turbopack is the default bundler in Next.js 16.
  // `canvas` is an optional native dependency of three.js and must stay external.
  turbopack: {
    resolveAlias: {
      canvas: "./src/shims/empty-module.js",
    },
  },
  // Proxy same-origin `/api/v1/*` calls to the FastAPI backend so the browser
  // never has to reach the backend port directly (works behind tunnels,
  // reverse proxies and remote previews where only the web port is exposed).
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${BACKEND}/api/v1/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
