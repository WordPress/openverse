<template>
  <VButton
    :href="`#${skipToContentTargetId}`"
    as="a"
    variant="filled-pink"
    size="medium"
    class="skip-button top-2 z-50 max-w-max focus:absolute focus:left-2 focus:right-2 focus-visible:absolute focus-visible:left-2 focus-visible:right-2"
    >{{ $t("skipToContent") }}
  </VButton>
</template>

<script lang="ts">
import { skipToContentTargetId } from "~/constants/window"

import VButton from "~/components/VButton.vue"

export default {
  name: "VSkipToContentButton",
  components: { VButton },
  setup() {
    return {
      skipToContentTargetId,
    }
  },
}
</script>

<style scoped>
.skip-button:not(:focus-visible) {
  @apply sr-only;
}
</style>
