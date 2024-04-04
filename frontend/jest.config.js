module.exports = {
  globals: {
    "vue-jest": {
      experimentalCSSCompile: false,
    },
  },
  moduleFileExtensions: ["ts", "js", "cjs", "vue", "json"],
  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
    "^~/(.*.svg)\\?inline$": "<rootDir>/src/$1",
    "^~/(.*)$": "<rootDir>/src/$1",
    "^~~/(.*)$": "<rootDir>/$1",
    "^vue$": "vue/dist/vue.common.js",
    "(.*svg)(\\?inline)$": "<rootDir>/test/unit/test-utils/svgTransform.js",
    "^axios$": "axios/dist/node/axios.cjs",
  },
  setupFiles: ["<rootDir>/test/unit/setup.js"],
  setupFilesAfterEnv: ["<rootDir>/test/unit/setup-after-env.js"],
  transform: {
    "^.+\\.(j|t)s$": "babel-jest",
    ".*\\.(vue)$": "vue-jest",
    ".+\\.(css|png|jpg|ttf|woff|woff2)$": "jest-transform-stub",
    "^.+\\.svg$": "<rootDir>/test/unit/svg-transform.js",
  },
  testPathIgnorePatterns: ["/playwright/", "/storybook/", ".remake"],
  collectCoverage: false,
  coverageDirectory: "<rootDir>/test/unit/coverage",
  collectCoverageFrom: [
    "<rootDir>/src/**/*.vue",
    "<rootDir>/src/**/*.js",
    "<rootDir>/src/**/*.ts",
    "!<rootDir>/src/**/*.stories.js",
  ],
}
