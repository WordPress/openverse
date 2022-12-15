<template>
  <div>
    <VBanners />
    <Nuxt />
  </div>
</template>

<script>
import { defineComponent } from "@nuxtjs/composition-api"

import VBanners from "~/components/VBanner/VBanners.vue"

export default defineComponent({
  name: "BlankLayout",
  components: { VBanners },
  head() {
    return this.$nuxtI18nHead({ addSeoAttributes: true, addDirAttribute: true })
  },
})
</script>
