import { fileURLToPath } from "node:url"

import path from "node:path"

// eslint-disable-next-line import/no-unresolved
import { config as defineConfig } from "typescript-eslint"
import { includeIgnoreFile } from "@eslint/compat"
import openverse from "@openverse/eslint-plugin"

// @ts-ignore
const __dirname = path.dirname(fileURLToPath(import.meta.url))

const gitignoreFiles = [
  path.resolve(__dirname, ".gitignore"),
  path.resolve(__dirname, "frontend", ".gitignore"),
  path.resolve(__dirname, "automations", "js", ".gitignore"),
  path.resolve(__dirname, "packages", "js", "api-client", ".gitignore"),
]

// List of files from old .eslintignore
const eslintIgnores = [
  "**/dist/**",
  "frontend/.pnpm-store/**",
  "frontend/.nuxt/**",
  "frontend/.output/**",
  "frontend/.remake/**",
  "frontend/src/locales/*.json",
  // Vendored module. See explanation in file
  "frontend/test/unit/test-utils/render-suspended.ts",
  "**/coverage/**",
  "frontend/test/tapes/**",
  "frontend/storybook-static/**",
  "packages/**/dist/**",
]

let ignoreConfigs = gitignoreFiles
  .map((gitignoreFile) => includeIgnoreFile(gitignoreFile))
  .reduce(
    (acc, gitignoreFile, index) => {
      return { ...acc, ignores: acc.ignores.concat(gitignoreFile.ignores) }
    },
    { name: "openverse:ignore-files", ignores: eslintIgnores }
  )

export default defineConfig(
  ignoreConfigs,
  { files: [".pnpmfile.cjs"] },
  ...openverse.default.configs.project
)
