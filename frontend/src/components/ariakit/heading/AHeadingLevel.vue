<script setup lang="ts" generic="T extends Renderable = never">
import type { Renderable, AsProps } from "~/types/ariakit"

import {
  useHeadingLevel,
  type HeadingLevelOptions,
} from "./AHeadingLevel.composable"

const props = defineProps<HeadingLevelOptions & AsProps<T>>()

useHeadingLevel(props)
</script>

<template>
  <component :is="as" v-if="as" v-bind="asProps ?? {}">
    <slot />
  </component>
  <slot v-else />
</template>
