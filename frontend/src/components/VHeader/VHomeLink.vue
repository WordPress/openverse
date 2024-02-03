<template>
  <VButton
    as="VLink"
    href="/"
    :aria-label="t('header.homeLink', { openverse: 'Openverse' })"
    variant="transparent-tx"
    size="disabled"
    :class="
      variant === 'dark'
        ? 'text-dark-charcoal hover:bg-yellow'
        : 'text-white focus-slim-tx-yellow'
    "
    class="h-12 px-4 text-[1.125rem]"
  >
    <VSvg
      name="logo_and_wordmark"
      class="h-[1em] w-auto"
      viewBox="0 0 226 34"
    />
  </VButton>
</template>

<script setup lang="ts">
import { useNuxtApp } from "#imports"

import VButton from "~/components/VButton.vue"
import VSvg from "~/components/VSvg/VSvg.vue"

/**
 * The home link for the internal header. Shows the Openverse logo and wordmark,
 * and does not have a loading state.
 */
withDefaults(
  defineProps<{
    /**
     * In `light` mode, the links are white and the background is dark charcoal.
     * In `dark` mode, the links are dark charcoal and the background is transparent.
     *
     * @default 'light'
     */
    variant: "light" | "dark"
  }>(),
  {}
)
const {
  $i18n: { t },
} = useNuxtApp()
</script>
