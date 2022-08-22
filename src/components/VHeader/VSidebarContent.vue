<template>
  <VTeleport v-if="visible" :to="to">
    <VSearchGridFilter @close="$emit('close')" />
  </VTeleport>
</template>

<script>
import { defineComponent } from '@nuxtjs/composition-api'
import { Portal as VTeleport } from 'portal-vue'

import VSearchGridFilter from '~/components/VFilters/VSearchGridFilter.vue'

/**
 * Renders the inner content of the sidebar and manages focus.
 */
export default defineComponent({
  name: 'VSidebarContent',
  components: { VTeleport, VSearchGridFilter },
  props: {
    visible: {
      type: Boolean,
      required: true,
    },
    to: {
      type: String,
      required: true,
    },
  },
})
</script>
