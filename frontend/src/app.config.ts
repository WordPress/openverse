import { defineAppConfig } from "#imports"

export default defineAppConfig({
  semanticVersion: import.meta.env.SEMANTIC_VERSION as string,
})
