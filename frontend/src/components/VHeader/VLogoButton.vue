<template>
  <VButton
    as="VLink"
    href="/"
    :aria-label="$t('header.home-link')"
    variant="plain"
    size="disabled"
    class="text-dark-charcoal hover:bg-yellow"
    :class="fixedSize ? 'h-12 w-12 flex-shrink-0' : 'max-w-min'"
  >
    <VLogoLoader
      :status="isFetching ? 'loading' : 'idle'"
      :auto-resize="autoResizeLogo"
    />
  </VButton>
</template>
<script>
import { defineComponent } from "@nuxtjs/composition-api"

import VLogoLoader from "~/components/VLogoLoader/VLogoLoader.vue"
import VButton from "~/components/VButton.vue"

export default defineComponent({
  name: "VLogoButton",
  components: { VLogoLoader, VButton },
  props: {
    isFetching: {
      type: Boolean,
      default: false,
    },
    autoResizeLogo: {
      type: Boolean,
      default: false,
    },
    fixedSize: {
      type: Boolean,
      default: false,
    },
  },
})
</script>
