<template>
  <VButton
    :href="`#${skipToContentTargetId}`"
    as="a"
    variant="filled-pink"
    size="medium"
    class="skip-button z-50 focus:fixed focus:absolute focus:ms-2 focus:mt-2"
    >{{ t("skipToContent") }}
  </VButton>
</template>
<script setup lang="ts">
import { useNuxtApp } from "#imports"

import { skipToContentTargetId } from "~/constants/window"

import VButton from "~/components/VButton.vue"

const {
  $i18n: { t },
} = useNuxtApp()
</script>
<style scoped>
.skip-button:not(:focus) {
  @apply sr-only;
}
</style>
