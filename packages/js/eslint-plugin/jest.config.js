module.exports = {
  transform: {
    // Use `swc` to ease compatibility with typescript eslint dependency
    // and jest's default `ts-node` implementation. `swc` is faster and more reliable
    // https://github.com/typescript-eslint/typescript-eslint/issues/7284#issuecomment-1696101984
    "^.+\\.(t|j)s$": "@swc/jest",
  },
}
