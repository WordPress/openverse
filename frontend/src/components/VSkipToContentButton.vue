<script setup lang="ts">
import { skipToContentTargetId } from "#shared/constants/window"

import VButton from "~/components/VButton.vue"
</script>

<template>
  <VButton
    :href="`#${skipToContentTargetId}`"
    as="a"
    variant="filled-pink-8"
    size="medium"
    class="skip-button top-2 z-50 max-w-max focus:absolute focus:right-2 focus:left-2 focus-visible:absolute focus-visible:right-2 focus-visible:left-2"
    >{{ $t("skipToContent") }}
  </VButton>
</template>

<style scoped>
@reference "~/styles/tailwind.css";
.skip-button:not(:focus-visible) {
  @apply sr-only;
}
</style>
