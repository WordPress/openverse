<script setup lang="ts" generic="TIs extends Renderable = 'hr'">
import { computed, mergeProps } from "vue"

import type { Renderable, AsProps } from "~/types/ariakit"

import { useSeparator, type SeparatorOptions } from "./ASeparator.composable"

const {
  as = "hr",
  asProps,
  orientation,
} = defineProps<SeparatorOptions & AsProps<TIs>>()

const { attributes } = useSeparator({ orientation })
const mergedProps = computed(() => mergeProps(attributes.value, asProps ?? {}))
</script>

<template>
  <component :is="as" v-if="as" v-bind="mergedProps" />
</template>
