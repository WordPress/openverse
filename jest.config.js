module.exports = {
  rootDir: ".",
  moduleFileExtensions: ["ts", "js", "vue", "json"],
  moduleNameMapper: {
    "^@openverse/(.*)$": "<rootDir>/packages/$1/src",
  },
  transform: {
    "^.+\\.(j|t)s$": "babel-jest",
  },
  testPathIgnorePatterns: [
    // The frontend has its own jest configuration due to vue's peculiarities
    "frontend",
  ],
}
