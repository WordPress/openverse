<script setup lang="ts">
/**
 * Display placeholder elements while waiting for the actual elements to be
 * loaded in the results views.
 */
import { computed } from "vue"

import type { SupportedSearchType } from "~/constants/media"

import VAudioTrackSkeleton from "~/components/VSkeleton/VAudioTrackSkeleton.vue"
import VBone from "~/components/VSkeleton/VBone.vue"

const props = withDefaults(
  defineProps<{
    isForTab?: SupportedSearchType
    numElems?: number
    isSidebarVisible?: boolean
  }>(),
  {
    isForTab: "image",
    isSidebarVisible: false,
  }
)

function getRandomSize(max = 300, min = 100) {
  return Math.floor(Math.random() * (max - min) + min)
}

const elementCount = computed(() => {
  // Calculate the default element count based on isForTab
  if (props.numElems) {
    return props.numElems
  }
  if (props.isForTab === "all") {
    return 20
  }
  if (props.isForTab === "image") {
    return 30
  }
  return 8
})
</script>

<template>
  <section>
    <div
      v-if="isForTab === 'all'"
      class="grid grid-cols-2 gap-4"
      :class="
        isSidebarVisible
          ? 'lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5'
          : 'sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6'
      "
    >
      <VBone v-for="idx in elementCount" :key="idx" class="square" />
    </div>

    <div v-if="isForTab === 'image'" class="masonry">
      <VBone
        v-for="idx in elementCount"
        :key="idx"
        class="mb-4"
        :style="{ height: `${getRandomSize()}px` }"
      />
    </div>

    <template v-if="isForTab === 'audio'">
      <VAudioTrackSkeleton v-for="idx in elementCount" :key="idx" />
    </template>
  </section>
</template>

<style scoped>
.square {
  @apply aspect-square;
}

.masonry {
  @apply columns-2 gap-x-4 md:columns-3 lg:columns-5;
}
</style>
