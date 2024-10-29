<script setup lang="ts">
/**
 * The home link for the internal header. Shows the Openverse logo and wordmark,
 * and does not have a loading state.
 */
import VButton from "~/components/VButton.vue"
import VSvg from "~/components/VSvg/VSvg.vue"
</script>

<template>
  <VButton
    as="VLink"
    href="/"
    :aria-label="$t('header.homeLink', { openverse: 'Openverse' })"
    variant="transparent-tx"
    size="disabled"
    class="h-12 px-4 text-[1.125rem] text-contrast"
  >
    <VSvg
      name="logo_and_wordmark"
      class="h-[1em] w-auto"
      viewBox="0 0 226 34"
    />
  </VButton>
</template>
