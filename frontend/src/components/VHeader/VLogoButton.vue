<template>
  <VButton
    as="VLink"
    href="/"
    :aria-label="$t('header.homeLink', { openverse: 'Openverse' })"
    variant="transparent-tx"
    size="large"
    icon-only
    class="text-dark-charcoal hover:bg-yellow"
  >
    <VLogoLoader :status="isFetching ? 'loading' : 'idle'" />
  </VButton>
</template>
<script lang="ts">
import { defineComponent } from "vue"

import VLogoLoader from "~/components/VLogoLoader/VLogoLoader.vue"
import VButton from "~/components/VButton.vue"

/**
 * The home link for the search header. Shows the Openverse logo and the loading state.
 * When the results are being fetched, the logo is animated.
 */
export default defineComponent({
  name: "VLogoButton",
  components: { VLogoLoader, VButton },
  props: {
    isFetching: {
      type: Boolean,
      default: false,
    },
  },
})
</script>
