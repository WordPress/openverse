<script setup lang="ts">
import { computed, inject, onMounted, onUnmounted, ref } from "vue"

import { tabsContextKey, type TabsState } from "~/types/tabs"
import { keycodes } from "~/constants/key-codes"
import { getDomElement } from "~/utils/dom"
import { Focus, focusIn } from "~/utils/focus-management"

import VButton from "~/components/VButton.vue"

const props = withDefaults(
  defineProps<{
    /**
     * Tab id should be the same as the id of the tabpanel it controls.
     * The id of the HTML element will be `tab-${id}`
     */
    id: string
    /**
     * Whether the tab is disabled. TODO: do we really need disabled tabs?
     */
    disabled?: boolean
    size?: "default" | "large" | "medium"
  }>(),
  {
    disabled: false,
    size: "default",
  }
)

const injectedTabContext = inject(tabsContextKey)
if (!injectedTabContext) {
  throw new Error(`Could not resolve tabContext in VTab`)
}
const tabContext = injectedTabContext as TabsState

const internalTabRef = ref<HTMLElement | null>(null)

onMounted(() => tabContext.registerTab(internalTabRef))
onUnmounted(() => tabContext.unregisterTab(internalTabRef))

const isSelected = computed(() => tabContext.selectedId.value === props.id)

const handleFocus = () => {
  if (props.disabled) {
    return
  }
  if (tabContext.activation.value === "auto") {
    tabContext.setSelectedId(props.id)
  }
  getDomElement(internalTabRef)?.focus()
}

const handleSelection = () => {
  if (props.disabled) {
    return
  }
  getDomElement(internalTabRef)?.focus()
  tabContext.setSelectedId(props.id)
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
  if (documentDir === "rtl") {
    forward = !forward
  }
  return forward ? Focus.Next : Focus.Previous
}

const handleKeyDown = (event: KeyboardEvent) => {
  const list = tabContext.tabs.value
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
    case keycodes.Enter: {
      tabContext.setSelectedId(props.id)
      break
    }
    case keycodes.Home:
    case keycodes.PageUp: {
      focusIn(list, Focus.First)
      break
    }

    case keycodes.End:
    case keycodes.PageDown: {
      focusIn(list, Focus.Last)
      break
    }
    case keycodes.ArrowLeft: {
      focusIn(
        list,
        getFocusDirection(keycodes.ArrowLeft, document.dir) | Focus.WrapAround
      )
      break
    }

    case keycodes.ArrowRight: {
      focusIn(
        list,
        getFocusDirection(keycodes.ArrowRight, document.dir) | Focus.WrapAround
      )
      break
    }
  }
}

const tabProps = computed(() => ({
  "aria-controls": `panel-${props.id}`,
  "aria-selected": isSelected.value,
  disabled: props.disabled ? true : undefined,
}))

const variant = computed(() => tabContext.variant.value)
</script>

<template>
  <VButton
    :id="`tab-${id}`"
    ref="internalTabRef"
    role="tab"
    :tabindex="isSelected ? 0 : -1"
    size="disabled"
    variant="plain--avoid"
    v-bind="tabProps"
    class="rounded-none bg-default focus-slim-tx focus:z-10"
    :class="[variant, `size-${size}`, { [`${variant}-selected`]: isSelected }]"
    @click="handleSelection"
    @focus="handleFocus"
    @mousedown="handleMouseDown"
    @keydown="handleKeyDown"
  >
    <slot />
  </VButton>
</template>

<style scoped>
.bordered {
  @apply rounded-se-sm rounded-ss-sm border-x border-t border-tx text-sm font-semibold md:text-base md:font-semibold md:leading-snug;
}
.plain {
  @apply rounded-sm border-tx bg-tx text-sm hover:bg-secondary;
}
.bordered-selected {
  @apply -mb-[1px] border border-x-default border-b-tx border-t-default bg-default;
}
.plain-selected {
  @apply relative after:absolute after:right-1/2 after:h-0.5 after:w-full after:translate-x-1/2 after:translate-y-[-50%] after:bg-tertiary after:transition-all after:duration-200;
}
.plain-selected.size-default {
  @apply after:bottom-[-0.125rem];
}
.size-default {
  @apply px-4 py-3 md:px-6;
}
.size-large {
  @apply h-16;
}
.size-medium {
  @apply h-12 px-2;
}
.plain.size-medium {
  @apply my-2 border-tx;
}
.plain-selected.size-medium {
  @apply after:bottom-[-0.625rem];
}
</style>
