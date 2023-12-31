import { defineNuxtPlugin } from "#imports"

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.hook("vue:error", (err) => {
    console.log("[vue:error]: ", err)
  })
  nuxtApp.hook("app:error", (err) => {
    console.log("[app:error]: ", err)
  })
})
