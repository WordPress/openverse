module.exports = {
  presets: [
    ["@babel/preset-env", { modules: "auto" }],
    "@babel/preset-typescript",
  ],
  plugins: ["babel-plugin-add-module-exports"],
}
