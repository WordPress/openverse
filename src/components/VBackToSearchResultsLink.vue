<template>
  <!-- @todo: Separate the absolute container from the link itself. -->
  <VLink
    class="px-2 py-3 md:px-6 md:pt-4 md:pb-2 flex flex-row items-center font-semibold text-dark-charcoal text-xs md:text-sr"
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
