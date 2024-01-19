import { defineNuxtPrepareHandler } from "nuxt-prepare/config"
import { $fetch } from "ofetch"

import { sortProviders } from "./src/utils/provider"

export default defineNuxtPrepareHandler(async () => {
  const apiUrl =
    process.env.NUXT_PUBLIC_API_URL || "https://api.openverse.engineering/"
  const audioProviders = (await $fetch(`${apiUrl}v1/audio/stats/`)) ?? []
  const imageProviders = (await $fetch(`${apiUrl}v1/images/stats/`)) ?? []

  return {
    ok: true,
    state: {
      preparedProviders: {
        audio: sortProviders(audioProviders),
        image: sortProviders(imageProviders),
        lastUpdated: new Date(),
      },
    },
  }
})
