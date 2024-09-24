<script setup lang="ts" generic="T extends Renderable = 'h1'">
import { ref, mergeProps, computed } from "vue"

import type { Renderable, AsProps } from "~/types/ariakit"

import { useHeading } from "./AHeading.composable"

const { as, asProps } = defineProps<AsProps<T>>()
const templateRef = ref<Element | null>(null)
const { Element, attributes } = useHeading({ element: as, templateRef })
const mergedProps = computed(() => mergeProps(asProps ?? {}, attributes.value))
</script>

<template>
  <component :is="Element" v-bind="mergedProps" :ref="templateRef">
    <slot
      v-bind="{
        Element,
        attributes,
        setTemplateRef: (e: Element) => (templateRef = e),
      }"
    />
  </component>
</template>
