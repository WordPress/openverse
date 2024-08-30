import { defineConfig } from "rollup"

import typescript from "@rollup/plugin-typescript"

export default defineConfig(
  (["esm", "cjs"] as const).map((format) => ({
    input: "src/index.ts",
    external: ["openapi-fetch"],
    output: {
      format: format,
      dir: `dist/${format}`,
      preserveModules: true,
      preserveModulesRoot: "src",
    },
    plugins: [
      typescript({
        outDir: `dist/${format}`,
        tsconfig: "tsconfig.prod.json",
        noEmitOnError: true,
        declarationDir: `dist/${format}`,
        declaration: true,
        declarationMap: true,
      }),
    ],
  }))
)
