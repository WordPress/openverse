<template>
  <VButton
    as="NuxtLink"
    to="/"
    variant="plain"
    size="disabled"
    class="max-w-min hover:bg-yellow"
  >
    <VLogoLoader
      :status="isFetching ? 'loading' : 'idle'"
      :auto-resize="autoResizeLogo"
    />
    <OpenverseLogoText
      v-if="!isHeaderScrolled"
      class="-ml-1 mt-1 me-3"
      :class="{ 'md:hidden': isSearchRoute }"
      width="95"
      height="15"
    />
  </VButton>
</template>
<script>
import { defineComponent } from '@nuxtjs/composition-api'
import OpenverseLogoText from '~/assets/icons/openverse-logo-text.svg?inline'
import VLogoLoader from '~/components/VLogoLoader/VLogoLoader.vue'
import VButton from '~/components/VButton.vue'

const VLogoButton = defineComponent({
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
export default VLogoButton
</script>
