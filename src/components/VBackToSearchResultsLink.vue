<template>
  <!-- @todo: Seperate the absolute container from the link itself. -->
  <NuxtLink
    v-if="show"
    class="px-2 pt-1 md:px-6 md:pt-4 md:pb-2 flex flex-row items-center font-semibold text-dark-charcoal text-xs md:text-sr"
    :to="path"
  >
    <Chevron class="-ms-2" />
    {{ $t('single-result.back') }}
  </NuxtLink>
</template>

<script>
import { defineComponent } from '@vue/composition-api'
import Chevron from '~/assets/icons/chevron-left.svg?inline'

export default defineComponent({
  components: {
    Chevron,
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
