import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://ossianravn.github.io",
  base: "/orderly/",
  output: "static",
  trailingSlash: "ignore",
  devToolbar: { enabled: false },
  server: { port: 4811 },
  build: { inlineStylesheets: "always" },
});
