<template>
  <VLink
    href="https://wordpress.org"
    :aria-label="
      $t('footer.wordpressAffiliation', { wordpress: 'WordPress' }).toString()
    "
    :class="mode === 'light' ? 'text-dark-charcoal' : 'text-white'"
    class="hover:no-underline focus-visible:rounded-sm focus-visible:outline-none focus-visible:ring focus-visible:ring-pink focus-visible:ring-offset-1 focus-visible:ring-offset-tx"
  >
    <i18n-t
      tag="p"
      keypath="footer.wordpressAffiliation"
      class="label-regular flex flex-row items-center gap-1"
    >
      <template #wordpress>
        <VSvg name="wordpress" class="h-6 w-6" width="24" height="24" />
      </template>
    </i18n-t>
  </VLink>
</template>
<script lang="ts">
import VLink from "~/components/VLink.vue"
import VSvg from "~/components/VSvg/VSvg.vue"

import type { PropType } from "vue"

export default {
  name: "VWordPressLink",
  components: { VLink, VSvg },
  props: {
    mode: {
      type: String as PropType<"dark" | "light">,
      default: "light",
    },
  },
}
</script>
