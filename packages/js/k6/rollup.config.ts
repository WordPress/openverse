/**
 * Adapted from Apache Licensed k6 template repositories
 * https://github.com/grafana/k6-rollup-example
 * https://github.com/grafana/k6-template-typescript
 */
import { defineConfig } from "rollup"
import { glob } from "glob"

import typescript from "@rollup/plugin-typescript"
import { nodeResolve } from "@rollup/plugin-node-resolve"
import commonjs from "@rollup/plugin-commonjs"

function getConfig(testFile: string) {
  return defineConfig({
    input: testFile,
    external: [new RegExp(/^(k6|https?:\/\/)(\/.*)?/)],
    output: {
      format: "es",
      dir: "dist",
      preserveModules: true,
      preserveModulesRoot: "src",
    },
    plugins: [typescript(), nodeResolve(), commonjs()],
  })
}

export default defineConfig((commandLineArgs) => {
  if (commandLineArgs.input) {
    // --input flag passed
    return getConfig(commandLineArgs.input)
  }

  const tests = glob.sync("./src/**/*.test.ts")
  return tests.map(getConfig)
})
