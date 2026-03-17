import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    domains: ["img.danawa.com", "thumbnail6.coupangcdn.com", "compuzone.co.kr"],
  },
  async rewrites() {
    return [
      {
        source: "/api/backend/:path*",
        destination: `${process.env.BACKEND_URL || "http://backend:8000"}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
