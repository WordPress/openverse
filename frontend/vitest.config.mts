import { fileURLToPath } from "node:url"

import { defineVitestConfig } from "@nuxt/test-utils/config"

export default defineVitestConfig({
  test: {
    environment: "nuxt",
    globals: true,
    dir: "test/unit/specs",
    setupFiles: [
      fileURLToPath(new URL("./test/unit/vitest-setup.ts", import.meta.url)),
    ],

    environmentOptions: {
      nuxt: {
        domEnvironment: "jsdom",
      },
    },
  },
})
