<template>
  <PortalTarget name="modal" />
</template>

<script>
import { defineComponent } from "vue"

import { PortalTarget } from "portal-vue"

export default defineComponent({
  name: "VModalTarget",
  components: { PortalTarget },
})
</script>
