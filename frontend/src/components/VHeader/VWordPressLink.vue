<template>
  <VLink
    href="https://wordpress.org"
    :aria-label="
      $t('footer.wordpress-affiliation', { wordpress: 'WordPress' }).toString()
    "
    :class="mode === 'light' ? 'text-dark-charcoal' : 'text-white'"
    class="hover:no-underline focus-visible:rounded-sm focus-visible:outline-none focus-visible:ring focus-visible:ring-pink focus-visible:ring-offset-1 focus-visible:ring-offset-tx"
  >
    <i18n
      tag="p"
      path="footer.wordpress-affiliation"
      class="label-regular flex flex-row items-center gap-1"
    >
      <template #wordpress>
        <WordPress />
      </template>
    </i18n>
  </VLink>
</template>
<script lang="ts">
import { PropType } from "vue"

import VLink from "~/components/VLink.vue"

import WordPress from "~/assets/wordpress.svg?inline"

export default {
  name: "VWordPressLink",
  components: { VLink, WordPress },
  props: {
    mode: {
      type: String as PropType<"dark" | "light">,
      default: "light",
    },
  },
}
</script>
