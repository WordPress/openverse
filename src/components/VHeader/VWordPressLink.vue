<template>
  <VLink
    href="https://wordpress.org"
    :class="mode === 'light' ? 'text-dark-charcoal' : 'text-white'"
    class="hover:no-underline focus-visible:rounded-sm focus-visible:outline-none focus-visible:ring focus-visible:ring-pink focus-visible:ring-offset-1 focus-visible:ring-offset-tx"
  >
    <i18n
      tag="p"
      path="footer.wordpress-affiliation"
      class="label-regular flex flex-row items-center gap-2"
    >
      <template #wordpress>
        <WordPress class="aria-hidden" />
        <span class="sr-only">WordPress</span>
      </template>
    </i18n>
  </VLink>
</template>
<script lang="ts">
import { PropType } from '@nuxtjs/composition-api'

import VLink from '~/components/VLink.vue'

import WordPress from '~/assets/wordpress.svg?inline'

export default {
  name: 'VWordPressLink',
  components: { VLink, WordPress },
  props: {
    mode: {
      type: String as PropType<'dark' | 'light'>,
      default: 'light',
    },
  },
}
</script>
