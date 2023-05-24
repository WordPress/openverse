<template>
  <VButton
    as="VLink"
    href="/"
    :aria-label="$t('header.home-link', { openverse: 'Openverse' }).toString()"
    variant="transparent-tx"
    size="disabled"
    :class="
      variant === 'dark'
        ? 'text-dark-charcoal hover:bg-yellow'
        : 'text-white focus-slim-tx-yellow'
    "
    class="h-12 px-4 text-[1.125rem]"
  >
    <OpenverseLogoAndWordmark class="h-[1em] w-auto" />
  </VButton>
</template>

<script lang="ts">
import { type PropType, defineComponent } from "vue"

import VButton from "~/components/VButton.vue"

import OpenverseLogoAndWordmark from "~/assets/logo_and_wordmark.svg?inline"

/**
 * The home link for the internal header. Shows the Openverse logo and wordmark,
 * and does not have a loading state.
 */
export default defineComponent({
  name: "VHomeLink",
  components: {
    OpenverseLogoAndWordmark,
    VButton,
  },
  props: {
    /**
     * In `light` mode, the links are white and the background is dark charcoal.
     * In `dark` mode, the links are dark charcoal and the background is transparent.
     *
     * @default 'light'
     */
    variant: {
      type: String as PropType<"light" | "dark">,
      default: "light",
    },
  },
})
</script>
