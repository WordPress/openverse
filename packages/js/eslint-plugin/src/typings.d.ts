declare module "@intlify/eslint-plugin-vue-i18n" {
  import { FlatConfig } from "@typescript-eslint/utils/ts-eslint"

  export const configs: {
    "flat/recommended": FlatConfig.Config[]
  }
}

declare module "eslint-plugin-import" {
  import { FlatConfig } from "@typescript-eslint/utils/ts-eslint"

  export const flatConfigs: {
    recommended: FlatConfig.Config
    typescript: FlatConfig.Config
  }
}

declare module "@eslint-community/eslint-plugin-eslint-comments/configs" {
  import { FlatConfig } from "@typescript-eslint/utils/ts-eslint"

  export const recommended: FlatConfig.Config
}
