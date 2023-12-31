import { defineNuxtPlugin, useCookie, useUiStore } from "#imports"

import type { OpenverseCookieState } from "~/types/cookies"

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.hook("vue:error", (err) => {
    console.log("[vue:error]: ", err)
  })
  nuxtApp.hook("app:error", (err) => {
    console.log("[app:error]: ", err)

    const uiCookies = useCookie<OpenverseCookieState["ui"]>("ui")
    console.log("Will init UI from cookies", uiCookies.value)
    const uiStore = useUiStore()
    uiStore.initFromCookies(uiCookies.value ?? {})
  })
})
