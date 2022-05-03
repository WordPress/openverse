<template>
  <VButton
    :id="`tab-${id}`"
    ref="internalTabRef"
    role="tab"
    :tabindex="isSelected ? 0 : -1"
    size="disabled"
    variant="plain-dangerous"
    v-bind="tabProps"
    class="py-3 px-4 md:px-6 bg-white text-base font-semibold focus-visible:shadow-[0_0_0_1.5px_#c52b9b_inset] border-0 rounded-none"
    :class="[$style[variant], isSelected && $style[`${variant}-selected`]]"
    @click="handleSelection"
    @focus="handleFocus"
    @mousedown="handleMouseDown"
    @keydown="handleKeyDown"
  >
    <slot />
  </VButton>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  inject,
  onMounted,
  onUnmounted,
  ref,
} from '@nuxtjs/composition-api'

import { tabsContextKey } from '~/models/tabs'
import { keycodes } from '~/constants/key-codes'
import { getDomElement } from '~/utils/dom'
import { Focus, focusIn } from '~/utils/focus-management'

import VButton from '~/components/VButton.vue'

export default defineComponent({
  name: 'VTab',
  components: { VButton },
  props: {
    /**
     * Whether the tab is disabled. TODO: do we really need disabled tabs?
     */
    disabled: {
      type: Boolean,
      default: false,
    },
    /**
     * Tab id should be the same as the id of the tabpanel it controls.
     * The id of the HTML element will be `tab-${id}`
     */
    id: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const tabContext = inject(tabsContextKey)
    if (!tabContext) {
      throw new Error(`Could not resolve tabContext in VTab`)
    }

    const internalTabRef = ref<HTMLElement | null>(null)

    onMounted(() => tabContext.registerTab(internalTabRef))
    onUnmounted(() => tabContext.unregisterTab(internalTabRef))

    const tabIndex = computed(() =>
      tabContext.tabs.value.indexOf(internalTabRef)
    )

    const isSelected = computed(
      () => tabIndex.value === tabContext.selectedIndex.value
    )

    const handleFocus = () => {
      if (props.disabled) return
      if (tabContext.activation.value === 'auto') {
        tabContext.setSelectedIndex(tabIndex.value)
      }
      getDomElement(internalTabRef)?.focus()
    }

    const handleSelection = () => {
      if (props.disabled) return
      getDomElement(internalTabRef)?.focus()
      tabContext.setSelectedIndex(tabIndex.value)
    }

    /**
     * On click, you get a `focus` and then a `click` event. We want to only focus
     * _after_ the click event is finished(mouseup), or when the tab gets focus.

     * @param event - we want to preventDefault for this mouse event
     */
    const handleMouseDown = (event: MouseEvent) => {
      event.preventDefault()
    }

    /**
     * Sets the direction where to move focus considering the document direction (ltr or rtl).
     * The directions for LTR are the opposite of RTL directions.
     * @param arrowKeyCode - the code of key pressed, right or left arrow
     * @param documentDir - the dir attribute of the current document.
     */
    const getFocusDirection = (
      arrowKeyCode: typeof keycodes.ArrowRight | typeof keycodes.ArrowLeft,
      documentDir?: string
    ) => {
      let forward = arrowKeyCode === keycodes.ArrowRight
      if (documentDir === 'rtl') {
        forward = !forward
      }
      return forward ? Focus.Next : Focus.Previous
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      let list = tabContext.tabs.value
        .map((tab) => getDomElement(tab))
        .filter(Boolean) as HTMLElement[]
      const tabControlKeys = [
        keycodes.Spacebar,
        keycodes.Enter,
        keycodes.Home,
        keycodes.PageUp,
        keycodes.End,
        keycodes.PageDown,
        keycodes.ArrowLeft,
        keycodes.ArrowRight,
      ] as string[]

      if (!tabControlKeys.includes(event.key)) {
        return
      }
      event.preventDefault()
      event.stopPropagation()

      switch (event.key) {
        case keycodes.Spacebar:
        case keycodes.Enter:
          tabContext.setSelectedIndex(tabIndex.value)
          break
        case keycodes.Home:
        case keycodes.PageUp:
          focusIn(list, Focus.First)
          break

        case keycodes.End:
        case keycodes.PageDown:
          focusIn(list, Focus.Last)
          break
        case keycodes.ArrowLeft:
          focusIn(
            list,
            getFocusDirection(keycodes.ArrowLeft, document.dir) |
              Focus.WrapAround
          )
          break

        case keycodes.ArrowRight:
          focusIn(
            list,
            getFocusDirection(keycodes.ArrowRight, document.dir) |
              Focus.WrapAround
          )
          break
      }
    }
    const controlledPanel = computed(
      () => tabContext.panels.value[tabIndex.value]?.value?.id
    )
    const tabProps = computed(() => ({
      'aria-controls': controlledPanel.value,
      'aria-selected': isSelected.value,
      disabled: props.disabled ? true : undefined,
    }))
    const isManual = computed(() => tabContext.activation.value === 'manual')

    return {
      internalTabRef,
      tabProps,
      isSelected,
      isManual,
      variant: tabContext.variant,

      handleKeyDown,
      handleFocus,
      handleMouseDown,
      handleSelection,
    }
  },
})
</script>

<style module>
.bordered {
  @apply border-t border-x border-tx rounded-t-sm;
}
.plain {
  @apply border-tx border-b-3;
}
.bordered-selected {
  @apply border border-x-dark-charcoal-20 border-t-dark-charcoal-20 border-b-white -mb-[1px] bg-white;
}
.plain-selected {
  @apply border-dark-charcoal rounded-none;
}
</style>
