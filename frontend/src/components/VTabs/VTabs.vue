<script setup lang="ts">
import { computed, provide, ref } from "vue"

import { tabsContextKey } from "~/types/tabs"
import type { TabsState, TabVariant } from "~/types/tabs"

/**
 * VTabs is an accessible implementation of tabs component that displays one panel at a time.
 * @see { https://www.w3.org/TR/wai-aria-practices/#tabpanel }
 * Use the default automatic activation of tabs when the tab button receives focus for panels
 * that can be displayed instantly, without fetching any data. For tab panels that fetch data
 * from the internet or require expensive computation, set `manual` to true to activate the tabs
 * by clicking `Enter` or `Space` after focusing on them using `Tab`.
 *
 * To link the VTab to VTabPanel, make sure to pass the same `id` to both.
 */
const props = withDefaults(
  defineProps<{
    /**
     * Accessible name label to use for the tablist.
     *
     * Reuse an existing element as a label by passing its `id` starting with `#`.
     * The tablist's `aria-labelledby` will be set to this element.
     *
     * If there are no existing elements that can be used as a label, pass a translated
     * string to be used as `aria-label`.
     */
    label: string
    /**
     * By default, the tab panels are activated when the corresponding tabs are focused on.
     * If the tabs require expensive calculations or fetch data from the network, set manual
     * to true to only activate the tab panels after user clicks `Enter` or `Space` on the focused
     * tab.
     */
    manual?: boolean
    /**
     * `bordered` tabs have a border around the tab panel, and around the selected tab.
     * `plain` tabs only have a line under the tabs, and a thicker line under the selected tab.
     */
    variant?: TabVariant
    /**
     * To ensure that a panel is visible on SSR, before we can run `onMounted` hook to register panel.
     */
    selectedId: string
    /**
     * The classes to pass to the div wrapping VTabs.
     */
    tablistStyle?: string
  }>(),
  {
    manual: false,
    variant: "bordered",
    tabListStyle: "",
  }
)
const emit = defineEmits<{
  change: [string]
  close: []
}>()

const selectedId = ref<TabsState["selectedId"]["value"]>(props.selectedId)
const tabs = ref<TabsState["tabs"]["value"]>([])
const panels = ref<TabsState["panels"]["value"]>([])

const tabGroupContext: TabsState = {
  selectedId,
  activation: computed(() => (props.manual ? "manual" : "auto")),
  variant: computed(() => props.variant),
  tabs,
  panels,
  setSelectedId(id: string) {
    if (selectedId.value === id) {
      return
    }
    selectedId.value = id
    emit("change", id)
  },
  registerTab(tab: (typeof tabs)["value"][number]) {
    if (!tabs.value.includes(tab)) {
      tabs.value.push(tab)
    }
  },
  unregisterTab(tab: (typeof tabs)["value"][number]) {
    const idx = tabs.value.indexOf(tab)
    if (idx !== -1) {
      tabs.value.splice(idx, 1)
    }
  },
  registerPanel(panel: (typeof panels)["value"][number]) {
    if (!panels.value.includes(panel)) {
      panels.value.push(panel)
    }
  },
  unregisterPanel(panel: (typeof panels)["value"][number]) {
    const idx = panels.value.indexOf(panel)
    if (idx !== -1) {
      panels.value.splice(idx, 1)
    }
  },
}
provide(tabsContextKey, tabGroupContext)

const accessibleLabel = computed(() =>
  props.label.startsWith("#")
    ? { "aria-labelledby": props.label.slice(1) }
    : { "aria-label": props.label }
)
</script>

<template>
  <div>
    <div
      role="tablist"
      class="flex flex-row items-stretch"
      :class="tablistStyle"
      v-bind="accessibleLabel"
    >
      <slot name="tabs" />
    </div>
    <slot name="default" />
  </div>
</template>
