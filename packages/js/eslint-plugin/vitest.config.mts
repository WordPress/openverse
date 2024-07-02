import { defineConfig, configDefaults } from "vitest/config"

export default defineConfig({
  test: {
    globals: true,
    include: ["test/**/*.spec.ts"],
    exclude: [...configDefaults.exclude],
  },
})
