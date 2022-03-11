<template>
  <!-- @todo: Separate the absolute container from the link itself. -->
  <VLink
    v-if="show"
    class="px-2 pt-1 md:px-6 md:pt-4 md:pb-2 flex flex-row items-center font-semibold text-dark-charcoal text-xs md:text-sr"
    :href="path"
  >
    <Chevron class="-ms-2" />
    {{ $t('single-result.back') }}
  </VLink>
</template>

<script>
import { defineComponent } from '@vue/composition-api'

import VLink from '~/components/VLink.vue'

import Chevron from '~/assets/icons/chevron-left.svg?inline'

export default defineComponent({
  components: {
    Chevron,
    VLink,
  },
  data() {
    return {
      /** @type {undefined|string} */
      path: undefined,
      show: false,
    }
  },
  created() {
    if (!this.$nuxt?.context?.from?.fullPath) {
      return
    }

    this.path = this.$nuxt.context.from.fullPath
    if (this.path.startsWith('/search')) {
      this.show = true
    }
  },
})
</script>
