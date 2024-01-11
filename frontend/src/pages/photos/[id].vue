<template><div></div></template>
<script lang="ts">
import { defineComponent, definePageMeta, navigateTo } from "#imports"

export default defineComponent({
  name: "PhotosRedirect",
  setup() {
    definePageMeta({
      middleware: (to) => {
        const localePrefix = to.path.startsWith("/photos/")
          ? ""
          : `/${to.path.split("/")[1]}`
        const redirectUrl = `${localePrefix}/image/${to.params.id}`
        return navigateTo(redirectUrl, { redirectCode: 301 })
      },
    })
  },
})
</script>
