<template>
  <VTeleportTarget name="sidebar" element="aside" />
</template>

<script>
import { defineComponent } from '@nuxtjs/composition-api'
import { PortalTarget as VTeleportTarget } from 'portal-vue'

export default defineComponent({
  name: 'VSidebarTarget',
  components: { VTeleportTarget },
  props: { element: { type: String, default: 'div' } },
})
</script>
