import { analyticsConfiguration } from "./analytics-configuration"
import { noUnexplainedDisabledTest } from "./no-unexplained-disabled-test"
import { translationStrings } from "./translation-strings"

export default {
  "analytics-configuration": analyticsConfiguration,
  "no-unexplained-disabled-test": noUnexplainedDisabledTest,
  "translation-strings": translationStrings,
} as const
