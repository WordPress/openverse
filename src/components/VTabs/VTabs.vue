<template>
  <div>
    <div role="tablist" class="flex flex-row" v-bind="accessibleLabel">
      <slot name="tabs" />
    </div>
    <slot name="default" />
  </div>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  PropType,
  provide,
  ref,
} from '@nuxtjs/composition-api'

import { tabsContextKey, TabsState } from '~/models/tabs'
import { defineEvent } from '~/types/emits'

/**
 * VTabs is an accessible implementation of tabs component that displays one panel at a time.
 * @see { https://www.w3.org/TR/wai-aria-practices/#tabpanel }
 * Use the default automatic activation of tabs when the tab button receives focus for panels
 * that can be displayed instantly, without fetching any data. For tab panels that fetch data
 * from the internet or require expensive computation, set `manual` to true to activate the tabs
 * by clicking `Enter` or `Space` after focusing on them using `Tab`.
 */
export default defineComponent({
  name: 'VTabs',
  props: {
    /**
     * Accessible name label to use for the tablist.
     *
     * Re-use an existing element as a label by passing its `id` starting with `#`.
     * The tablist's `aria-labelledby` will be set to this element.
     *
     * If there are no existing elements that can be used as a label, pass a translated
     * string to be used as `aria-label`.
     */
    label: {
      type: String,
      required: true,
    },
    /**
     * By default, the tab panels are activated when the corresponding tabs are focused on.
     * If the tabs require expensive calculations or fetch data from the network, set manual
     * to true to only activate the tab panels after user clicks `Enter` or `Space` on the focused
     * tab.
     */
    manual: {
      type: Boolean,
      default: false,
    },
    /**
     * `bordered` tabs have a border around the tab panel, and around the selected tab.
     * `plain` tabs only have a line under the tabs, and a thicker line under the selected tab.
     */
    variant: {
      type: String as PropType<TabsState['variant']['value'][number]>,
      default: 'bordered',
    },
    /**
     * To ensure that a panel is visible on SSR, before we can run `onMounted` hook to register panel.
     */
    selectedId: {
      type: String,
      required: true,
    },
  },
  emits: {
    change: defineEvent<[number]>(),
  },
  setup(props, { emit }) {
    const selectedIndex = ref<TabsState['selectedIndex']['value']>(0)
    const tabs = ref<TabsState['tabs']['value']>([])
    const panels = ref<TabsState['panels']['value']>([])

    const tabGroupContext: TabsState = {
      selectedIndex,
      initiallySelectedId: props.selectedId,
      activation: computed(() => (props.manual ? 'manual' : 'auto')),
      variant: computed(() =>
        props.variant === 'bordered' ? 'bordered' : 'plain'
      ),
      tabs,
      panels,
      setSelectedIndex(index: number) {
        if (selectedIndex.value === index) return
        selectedIndex.value = index
        emit('change', index)
      },
      registerTab(tab: typeof tabs['value'][number]) {
        if (!tabs.value.includes(tab)) tabs.value.push(tab)
      },
      unregisterTab(tab: typeof tabs['value'][number]) {
        let idx = tabs.value.indexOf(tab)
        if (idx !== -1) tabs.value.splice(idx, 1)
      },
      registerPanel(panel: typeof panels['value'][number]) {
        if (!panels.value.includes(panel)) panels.value.push(panel)
      },
      unregisterPanel(panel: typeof panels['value'][number]) {
        let idx = panels.value.indexOf(panel)
        if (idx !== -1) panels.value.splice(idx, 1)
      },
    }
    provide(tabsContextKey, tabGroupContext)

    const accessibleLabel = computed(() =>
      props.label.startsWith('#')
        ? { 'aria-labelledby': props.label.slice(1) }
        : { 'aria-label': props.label }
    )
    return {
      accessibleLabel,
    }
  },
})
</script>
