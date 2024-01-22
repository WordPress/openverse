import { defineNuxtPrepareHandler } from "nuxt-prepare/config"
import { $fetch } from "ofetch"

import { sortProviders } from "./src/utils/provider"

export default defineNuxtPrepareHandler(async () => {
  const apiUrl =
    process.env.NUXT_PUBLIC_API_URL || "https://api.openverse.engineering/"
  console.log("Fetching audio providers from ", `${apiUrl}v1/audio/stats/`)
  const audioProviders = (await $fetch(`${apiUrl}v1/audio/stats/`)) ?? []
  console.log("Fetching image providers from ", `${apiUrl}v1/images/stats/`)
  const imageProviders = (await $fetch(`${apiUrl}v1/images/stats/`)) ?? []
  const preparedProviders = {
    audio: sortProviders(audioProviders),
    image: sortProviders(imageProviders),
    lastUpdated: new Date(),
  }

  console.log("Prepared providers", preparedProviders)

  return {
    ok: true,
    state: {
      preparedProviders,
    },
  }
})
