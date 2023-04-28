<template>
  <VButton
    variant="plain"
    class="report-button font-semibold text-dark-charcoal-70 hover:underline"
  >
    <span class="text-sr md:hidden md:text-base">{{
      $t("media-details.content-report.short")
    }}</span>
    <span class="hidden text-sr md:inline md:text-base">{{
      $t("media-details.content-report.long")
    }}</span>
    <VIcon name="flag" class="ms-2" />
  </VButton>
</template>

<script>
import { defineComponent } from "vue"

import VIcon from "~/components/VIcon/VIcon.vue"
import VButton from "~/components/VButton.vue"

export default defineComponent({
  name: "VContentReportButton",
  components: { VButton, VIcon },
})
</script>

<style scoped>
.report-button {
  @apply px-0;
}
</style>
