<script setup lang="ts">
import { skipToContentTargetId } from "~/constants/window"

import VButton from "~/components/VButton.vue"
</script>

<template>
  <VButton
    :href="`#${skipToContentTargetId}`"
    as="a"
    variant="filled-pink-8"
    size="medium"
    class="skip-button top-2 z-50 max-w-max focus:absolute focus:left-2 focus:right-2 focus-visible:absolute focus-visible:left-2 focus-visible:right-2"
    >{{ $t("skipToContent") }}
  </VButton>
</template>

<style scoped>
.skip-button:not(:focus-visible) {
  @apply sr-only;
}
</style>
