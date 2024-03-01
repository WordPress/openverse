module.exports = {
  trailingComma: "es5",
  tabWidth: 2,
  semi: false,
  singleQuote: false,
  proseWrap: "always",
  overrides: [
    {
      files: ["*.yml", "*.yaml"],
      options: {
        proseWrap: "preserve",
      },
    },
    {
      files: ["frontend/**/*"],
      options: {
        plugins: ["prettier-plugin-tailwindcss"],
        tailwindConfig: "frontend/tailwind.config.ts",
        vueIndentScriptAndStyle: false,
      },
    },
  ],
}
