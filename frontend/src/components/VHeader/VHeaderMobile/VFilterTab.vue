<template>
  <VTab id="filters" size="medium" class="gap-x-2" :aria-label="ariaLabel">
    <VFilterIconOrCounter :applied-filter-count="appliedFilterCount" />
    <h2 class="label-regular">{{ $t("filters.title") }}</h2>
  </VTab>
</template>
<script lang="ts">
import { computed, defineComponent } from "vue"

import { useI18n } from "~/composables/use-i18n"

import VFilterIconOrCounter from "~/components/VHeader/VFilterIconOrCounter.vue"
import VTab from "~/components/VTabs/VTab.vue"

export default defineComponent({
  name: "VFilterTab",
  components: { VFilterIconOrCounter, VTab },
  props: {
    appliedFilterCount: {
      type: Number,
      default: 0,
    },
  },
  setup(props) {
    const i18n = useI18n()
    const ariaLabel = computed(() =>
      i18n.tc("header.filterButton.withCount", props.appliedFilterCount)
    )
    return { ariaLabel }
  },
})
</script>
