import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  poweredByHeader: false,
  // This app is nested inside a repo that has its own Next.js app at the root.
  // Without pinning the root, Turbopack walks up, finds the parent lockfile and
  // compiles the parent's proxy.ts into this build.
  turbopack: {
    root: path.resolve(import.meta.dirname),
  },
};

export default nextConfig;
