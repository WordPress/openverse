import { analyticsConfiguration } from "./analytics-configuration"
import { noUnexplainedDisabledTest } from "./no-unexplained-disabled-test"
import { translationStrings } from "./translation-strings"
import { keyNameCasing } from "./key-name-casing"

export default {
  "analytics-configuration": analyticsConfiguration,
  "no-unexplained-disabled-test": noUnexplainedDisabledTest,
  "translation-strings": translationStrings,
  "key-name-casing": keyNameCasing,
} as const
