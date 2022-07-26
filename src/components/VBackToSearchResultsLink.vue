<template>
  <!-- @todo: Separate the absolute container from the link itself. -->
  <VLink
    class="flex flex-row items-center px-2 py-3 text-xs font-semibold text-dark-charcoal md:px-6 md:pt-4 md:pb-2 md:text-sr"
    :href="path"
  >
    <VIcon :icon-path="chevronIcon" class="-ms-2" />
    {{ $t('single-result.back') }}
  </VLink>
</template>

<script lang="ts">
import { defineComponent } from '@nuxtjs/composition-api'

import VIcon from '~/components/VIcon/VIcon.vue'
import VLink from '~/components/VLink.vue'

import chevronIcon from '~/assets/icons/chevron-left.svg'

export default defineComponent({
  components: {
    VIcon,
    VLink,
  },
  props: {
    path: {
      type: String,
      required: true,
    },
  },
  setup() {
    return { chevronIcon }
  },
})
</script>
