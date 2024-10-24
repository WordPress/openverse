import { fileURLToPath } from "node:url"
import path from "node:path"
import fs from "node:fs"

// eslint-disable-next-line import/no-unresolved
import { config as defineConfig } from "typescript-eslint"
import { convertIgnorePatternToMinimatch } from "@eslint/compat"
import openverse from "@openverse/eslint-plugin"

const __dirname = path.dirname(fileURLToPath(import.meta.url))

const gitignoreFiles = [
  path.resolve(__dirname, ".gitignore"),
  path.resolve(__dirname, "frontend", ".gitignore"),
  path.resolve(__dirname, "automations", "js", ".gitignore"),
  path.resolve(__dirname, "packages", "js", "api-client", ".gitignore"),
]

/**
 * Vendored in from `@eslint/compat` to support multiple ignore files.
 * Reads an ignore file and returns a list of ignore patterns.
 * @param {string[]} ignoreFilePaths The absolute path to the ignore file.
 * @returns {string[]} An array of ignore patterns.
 * @throws {Error} If the ignore file path is not an absolute path.
 */
function mapIgnoreFiles(ignoreFilePaths) {
  for (const ignoreFilePath of ignoreFilePaths) {
    if (!path.isAbsolute(ignoreFilePath)) {
      throw new Error("The ignore file location must be an absolute path.")
    }
  }

  /** @type {string[]} */
  const ignores = []
  for (const ignoreFilePath of ignoreFilePaths) {
    const ignoreFile = fs.readFileSync(ignoreFilePath, "utf8")
    const lines = ignoreFile.split(/\r?\n/u)
    ignores.push(
      ...lines
        .map((line) => line.trim())
        .filter((line) => line && !line.startsWith("#"))
        .map(convertIgnorePatternToMinimatch)
    )
  }

  return ignores
}

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

export default defineConfig(
  {
    name: "openverse:ignore-files",
    ignores: [...mapIgnoreFiles(gitignoreFiles), ...eslintIgnores],
  },
  { files: [".pnpmfile.cjs"] },
  ...openverse.default.configs.project
)
