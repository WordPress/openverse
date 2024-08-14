<script setup lang="ts">
import { computed } from "vue"

import VIcon from "~/components/VIcon/VIcon.vue"

const props = withDefaults(
  defineProps<{
    appliedFilterCount?: number
    pressed?: boolean
  }>(),
  {
    appliedFilterCount: 0,
    pressed: false,
  }
)

const showIcon = computed(() => props.appliedFilterCount === 0)
</script>

<template>
  <VIcon v-if="showIcon" name="filter" />
  <p
    v-else
    class="flex h-6 w-6 items-center justify-center rounded-sm"
    :class="pressed ? 'bg-tx' : 'bg-secondary'"
  >
    {{ appliedFilterCount }}
  </p>
</template>
