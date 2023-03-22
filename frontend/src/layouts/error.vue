<template>
  <VFourOhFour :error="error" />
</template>

<script>
import { defineComponent } from "vue"

import VFourOhFour from "~/components/VFourOhFour.vue"

export default defineComponent({
  name: "ErrorPage",
  components: { VFourOhFour },
  props: ["error"],
})
</script>
