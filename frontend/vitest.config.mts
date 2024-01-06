import { defineVitestConfig } from "@nuxt/test-utils/config"

export default defineVitestConfig({
  test: {
    environment: "nuxt",
    globals: true,
    dir: "test/unit/specs",
    setupFiles: ["./test/unit/vitest-setup.ts"],

    environmentOptions: {
      nuxt: {},
    },
  },
})
