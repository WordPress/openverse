<template>
  <VButton
    as="VLink"
    href="/"
    :aria-label="$t('header.home-link')"
    variant="plain"
    size="disabled"
    class="max-w-min text-dark-charcoal hover:bg-yellow"
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
      :aria-hidden="true"
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
  name: 'VLogoButtonOld',
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
