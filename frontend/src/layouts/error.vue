<template>
  <VFourOhFour :error="error" />
</template>

<script>
import { defineComponent } from "vue"

import { useDarkMode } from "~/composables/use-dark-mode"

import VFourOhFour from "~/components/VFourOhFour.vue"

export default defineComponent({
  name: "ErrorPage",
  components: { VFourOhFour },
  props: ["error"],
  head() {
    const darkMode = useDarkMode()
    return {
      bodyAttrs: { class: darkMode.cssClass },
    }
  },
})
</script>
