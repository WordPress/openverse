import { dirname, join } from "path"
import { fileURLToPath } from "url"

const __dirname = dirname(fileURLToPath(import.meta.url))
export const baseDir = join(__dirname, "..", "..")
export const srcDir = join(baseDir, "src")
export const testLocalesDir = join(baseDir, "test", "locales")
export const i18nDir = join(baseDir, "i18n")

export const localesDir = join(i18nDir, "locales")
export const i18nDataDir = join(i18nDir, "data")

export const enJson = /** @type {`${string}.json`} */ (
  join(localesDir, "en.json")
)
export const enJson5 = /** @type {`${string}.json5`} */ (
  join(i18nDataDir, "en.json5")
)
export const validLocales = join(i18nDataDir, "valid-locales.json")
