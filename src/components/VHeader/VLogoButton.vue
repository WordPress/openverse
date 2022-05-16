<template>
  <VButton
    as="VLink"
    href="/"
    variant="plain"
    size="disabled"
    class="max-w-min hover:bg-yellow text-dark-charcoal"
  >
    <VLogoLoader
      :status="isFetching ? 'loading' : 'idle'"
      :auto-resize="autoResizeLogo"
    />
    <OpenverseLogoText
      v-show="!isHeaderScrolled"
      class="-ml-1 mt-1 me-3"
      :class="{
        'hidden sm:block md:hidden': isSearchRoute,
      }"
      width="95"
      height="15"
    />
  </VButton>
</template>
<script>
import { defineComponent } from '@nuxtjs/composition-api'

import VLogoLoader from '~/components/VLogoLoader/VLogoLoader.vue'
import VButton from '~/components/VButton.vue'

import OpenverseLogoText from '~/assets/icons/openverse-logo-text.svg?inline'

export default defineComponent({
  name: 'VLogoButton',
  components: { OpenverseLogoText, VLogoLoader, VButton },
  props: {
    isFetching: {
      type: Boolean,
      default: false,
    },
    isHeaderScrolled: {
      type: Boolean,
      default: false,
    },
    isSearchRoute: {
      type: Boolean,
      default: false,
    },
    autoResizeLogo: {
      type: Boolean,
      default: true,
    },
  },
})
</script>
