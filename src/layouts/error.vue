<template>
  <VFourOhFour :error="error" />
</template>

<script>
import { defineComponent } from "@nuxtjs/composition-api"

import { useFeatureFlagStore } from "~/stores/feature-flag"

import VFourOhFour from "~/components/VFourOhFour.vue"

export default defineComponent({
  name: "ErrorPage",
  components: { VFourOhFour },
  layout: () => {
    return useFeatureFlagStore().isOn("new_header") ? "default" : "blank"
  },
  props: ["error"],
})
</script>
