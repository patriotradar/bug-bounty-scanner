import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "ScopeGuard AI", short_name: "ScopeGuard", description: "Authorised security research workspace",
    start_url: "/dashboard", display: "standalone", background_color: "#f4f7f6", theme_color: "#132b29",
  };
}
