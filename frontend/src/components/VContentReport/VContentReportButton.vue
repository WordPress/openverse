<template>
  <VButton
    variant="transparent-gray"
    size="medium"
    has-icon-end
    class="label-bold"
  >
    <span class="md:hidden">{{ $t("mediaDetails.contentReport.short") }}</span>
    <span class="hidden md:inline">{{
      $t("mediaDetails.contentReport.long")
    }}</span>
    <VIcon name="flag" />
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
