<template>
  <PortalTarget name="modal" />
</template>

<script>
import { defineComponent } from "@nuxtjs/composition-api"
import { PortalTarget } from "portal-vue"

export default defineComponent({
  name: "VModalTarget",
  components: { PortalTarget },
})
</script>
