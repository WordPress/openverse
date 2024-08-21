<script setup lang="ts">
import { computed, inject, onMounted, onUnmounted, ref } from "vue"

import { tabsContextKey } from "~/types/tabs"

const props = defineProps<{
  /**
   * Tabpanel id should be the same as the controlling tab id.
   * The id of the HTML element will be `panel-${id}`
   */
  id: string
}>()
const tabContext = inject(tabsContextKey)
if (!tabContext) {
  throw new Error(`Could not resolve tabContext in VTabPanel`)
}
const internalPanelRef = ref(null)

onMounted(() => {
  tabContext.registerPanel(internalPanelRef)
})
onUnmounted(() => tabContext.unregisterPanel(internalPanelRef))

/**
 * On SSR, when internalPanelRef is null, we determine if the Panel is selected
 * by its id. It is selected if it's equal the VTabs' selectedId.
 * After VTabs had mounted, the panels and tabs are registered and `selected`
 * status is managed by the `tabContext`.
 */
const isSelected = computed(() => props.id === tabContext.selectedId.value)

const panelVariantStyle = computed(() =>
  tabContext.variant.value === "bordered"
    ? "border rounded-sm first:rounded-ss-none"
    : "border-t"
)
</script>

<template>
  <div
    :id="`panel-${id}`"
    ref="internalPanelRef"
    :aria-labelledby="`tab-${id}`"
    role="tabpanel"
    :tabindex="isSelected ? 0 : -1"
    class="min-h-0 overflow-y-auto border-default p-6"
    :class="[panelVariantStyle, { hidden: !isSelected }]"
  >
    <slot />
  </div>
</template>
