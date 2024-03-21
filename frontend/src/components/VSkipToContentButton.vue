<template>
  <VButton
    :href="`#${skipToContentTargetId}`"
    as="a"
    variant="filled-pink"
    size="medium"
    class="skip-button z-50 focus:fixed focus:absolute focus:ms-2 focus:mt-2"
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
.skip-button:not(:focus) {
  @apply sr-only;
}
</style>
