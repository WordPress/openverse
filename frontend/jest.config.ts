import type { Config } from "jest"

const config: Config = {
  globals: {
    "vue-jest": {
      experimentalCSSCompile: false,
      templateCompiler: {
        prettify: false,
      },
    },
  },
  testEnvironment: "jsdom",
  moduleFileExtensions: ["ts", "js", "vue", "json"],
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
    "^~/(.*)$": "<rootDir>/src/$1",
    "^~~/(.*)$": "<rootDir>/$1",
    "^@nuxtjs/composition-api$":
      "<rootDir>/node_modules/@nuxtjs/composition-api/dist/runtime/index.js",
  },
  setupFiles: ["<rootDir>/test/unit/setup.js"],
  setupFilesAfterEnv: ["<rootDir>/test/unit/setup-after-env.js"],
  transform: {
    "^.+\\.(j|t)s$": "babel-jest",
    ".*\\.(vue)$": "@vue/vue2-jest",
    ".+\\.(css|png|jpg|ttf|woff|woff2)$": "jest-transform-stub",
  },
  transformIgnorePatterns: ["/node_modules/(?!@nuxtjs/composition-api)"],
  testPathIgnorePatterns: ["/playwright/", "/storybook/", ".remake"],
  collectCoverage: false,
  coverageDirectory: "<rootDir>/test/unit/coverage",
  collectCoverageFrom: [
    "<rootDir>/src/**/*.vue",
    "<rootDir>/src/**/*.js",
    "<rootDir>/src/**/*.ts",
  ],
}
export default config
