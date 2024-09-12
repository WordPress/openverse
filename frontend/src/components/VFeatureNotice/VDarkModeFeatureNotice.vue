<script setup lang="ts">
import { useUiStore } from "~/stores/ui"

import VFeatureNotice from "~/components/VFeatureNotice/VFeatureNotice.vue"

const uiStore = useUiStore()

const handleClick = () => {
  uiStore.setIsDarkModeSeen(true)
}
</script>

<template>
  <!-- TODO: Populate the post permalink. -->
  <VFeatureNotice
    see-more-href="https://make.wordpress.org/openverse/"
    @click="handleClick"
  >
    {{ $t("notification.darkMode.text") }}
  </VFeatureNotice>
</template>
