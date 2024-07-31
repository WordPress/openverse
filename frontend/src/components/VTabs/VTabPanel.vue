<template>
  <div
    :id="`panel-${id}`"
    ref="internalPanelRef"
    :aria-labelledby="`tab-${id}`"
    role="tabpanel"
    :tabindex="isSelected ? 0 : -1"
    class="border-gray-3 min-h-0 overflow-y-auto p-6"
    :class="[panelVariantStyle, { hidden: !isSelected }]"
  >
    <slot />
  </div>
</template>
<script lang="ts">
import {
  computed,
  defineComponent,
  inject,
  onMounted,
  onUnmounted,
  ref,
} from "vue"

import { tabsContextKey } from "~/types/tabs"

export default defineComponent({
  name: "VTabPanel",
  props: {
    /**
     * Tabpanel id should be the same as the controlling tab id.
     * The id of the HTML element will be `panel-${id}`
     */
    id: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const tabContext = inject(tabsContextKey)
    if (!tabContext) {
      throw new Error(`Could not resolve tabContext in VTabPanel`)
    }
    const internalPanelRef = ref(null)

    onMounted(() => {
      tabContext.registerPanel(internalPanelRef)
    })
    onUnmounted(() => tabContext.unregisterPanel(internalPanelRef))

    const panelIndex = computed(() =>
      tabContext.panels.value.indexOf(internalPanelRef)
    )

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

    return {
      internalPanelRef,
      isSelected,
      panelVariantStyle,
      panelIndex,
    }
  },
})
</script>
