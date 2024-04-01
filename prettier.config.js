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
        // Do not include tailwind plugin in test environment, as it breaks jest
        plugins: global.test ? [] : ["prettier-plugin-tailwindcss"],
        tailwindConfig: "frontend/tailwind.config.ts",
        vueIndentScriptAndStyle: false,
      },
    },
  ],
}
