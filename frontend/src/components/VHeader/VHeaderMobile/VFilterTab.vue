<template>
  <VTab id="filters" size="medium" class="label-regular gap-x-2">
    <VIcon :icon-path="filtersIcon" />
    <h2>{{ $t("filters.title") }}</h2>
  </VTab>
</template>
<script lang="ts">
import VIcon from "~/components/VIcon/VIcon.vue"
import VTab from "~/components/VTabs/VTab.vue"

import filtersIcon from "~/assets/icons/filter.svg"

export default {
  name: "VFilterTab",
  components: { VIcon, VTab },
  props: {
    appliedFilterCount: {
      type: Number,
      default: 0,
    },
  },
  setup() {
    return { filtersIcon }
  },
}
</script>
