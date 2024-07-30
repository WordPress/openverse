import { defineNitroPlugin } from "nitropack/runtime"

import { PRODUCTION } from "~/constants/deploy-env"

export default defineNitroPlugin(async (nitroApp) => {
  nitroApp.hooks.hook("site-config:init", ({ siteConfig }) => {
    siteConfig.push({
      indexable: import.meta.env.DEPLOYMENT_ENV === PRODUCTION,
    })
  })
})
