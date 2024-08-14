<script setup lang="ts">
/**
 * The home link for the search header. Shows the Openverse logo and the loading state.
 * When the results are being fetched, the logo is animated.
 */
import VLogoLoader from "~/components/VLogoLoader/VLogoLoader.vue"
import VButton from "~/components/VButton.vue"

withDefaults(defineProps<{ isFetching?: boolean }>(), {
  isFetching: false,
})
</script>

<template>
  <VButton
    as="VLink"
    href="/"
    :aria-label="$t('header.homeLink', { openverse: 'Openverse' })"
    variant="transparent-tx"
    size="large"
    icon-only
    class="text-default hover:bg-complementary"
  >
    <VLogoLoader :status="isFetching ? 'loading' : 'idle'" />
  </VButton>
</template>
