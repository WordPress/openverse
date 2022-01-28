<template>
  <NuxtLink
    to="/"
    class="rounded-sm ring-offset-1 focus:outline-none focus-visible:ring focus-visible:ring-pink -ms-2 inline-flex items-center hover:bg-yellow mr-auto"
    :class="{
      'pe-3 md:pe-0': isSearchRoute && !isHeaderScrolled,
      'md:pe-3': !isSearchRoute,
    }"
  >
    <VLogoLoader :status="isFetching ? 'loading' : 'idle'" />
    <OpenverseLogoText
      v-if="!isHeaderScrolled"
      class="logo-text -ml-1 mt-1"
      :class="{ 'md:hidden': isSearchRoute }"
      width="95"
      height="15"
    />
  </NuxtLink>
</template>
<script>
import { defineComponent } from '@nuxtjs/composition-api'
import OpenverseLogoText from '~/assets/icons/openverse-logo-text.svg?inline'
import VLogoLoader from '~/components/VLogoLoader/VLogoLoader.vue'

const VLogoButton = defineComponent({
  name: 'VLogoButton',
  components: { OpenverseLogoText, VLogoLoader },
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
      required: true,
    },
  },
})
export default VLogoButton
</script>
<style scoped>
@media (max-width: 370px) {
  .logo-text {
    display: none;
  }
}
</style>
