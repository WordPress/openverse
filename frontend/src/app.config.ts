import { defineAppConfig } from "#app/nuxt"

export default defineAppConfig({
  semanticVersion: import.meta.env.SEMANTIC_VERSION as string,
})
