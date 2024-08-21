<script setup lang="ts">
import { useI18n } from "#imports"

import { computed } from "vue"

import VIconButton from "~/components/VIconButton/VIconButton.vue"

const props = defineProps<{ direction: "forward" | "back" }>()

defineEmits<{ click: [] }>()

const { t } = useI18n({ useScope: "global" })

const iconName = computed(() =>
  props.direction === "forward" ? "chevron-forward" : "chevron-back"
)

const label = computed(() =>
  t(
    props.direction === "forward"
      ? "mediaDetails.scroll.forward"
      : "mediaDetails.scroll.back"
  )
)
</script>

<template>
  <div class="absolute z-10 h-8 w-8 flex-none">
    <VIconButton
      :icon-props="{ name: iconName, rtlFlip: true }"
      :label="label"
      variant="transparent-gray"
      size="small"
      @click="$emit('click')"
    />
  </div>
</template>
