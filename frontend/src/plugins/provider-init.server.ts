import { defineNuxtPlugin, useProviderStore } from "#imports"

/**
 * This plugin is used to fetch the providers from the API if for whatever reason
 * the providers were not synced during build time.
 */
export default defineNuxtPlugin({
  name: "provider-init",
  hooks: {
    "app:created"() {
      // If the providers weren't already fetched during build, fetch them now.
      const providerStore = useProviderStore()
      console.log(
        "app:created hook:",
        providerStore.needsUpdate
          ? "will sync providers."
          : "providers already synced."
      )
      if (providerStore.needsUpdate) {
        providerStore.fetchMediaProviders().then(() => {
          console.log("app:created hook, providers fetched.")
        })
      }
    },
  },
})
