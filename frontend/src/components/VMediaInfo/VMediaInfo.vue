<script setup lang="ts">
import type { Media } from "~/types/media"

import VByLine from "~/components/VMediaInfo/VByLine/VByLine.vue"

defineProps<{ media: Media }>()
</script>

<template>
  <div class="w-full lg:w-auto">
    <h1 class="heading-6 mb-3 sm:mb-1">{{ media.title }}</h1>
    <VByLine :media="media" />
  </div>
</template>
