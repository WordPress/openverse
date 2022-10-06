<template>
  <div
    v-show="visible"
    class="h-0 w-0"
    :aria-hidden="!visible"
    v-on="$listeners"
    @keydown="onKeyDown"
  >
    <div
      ref="popoverRef"
      class="popover-content max-w-max overflow-y-auto overflow-x-hidden rounded-sm border border-light-gray bg-white shadow"
      :class="`z-${zIndex}`"
      :style="heightProperties"
      :tabindex="-1"
      @blur="onBlur"
    >
      <slot />
    </div>
  </div>
</template>

<script lang="ts">
import {
  defineComponent,
  toRefs,
  ref,
  provide,
  InjectionKey,
  PropType,
  computed,
} from '@nuxtjs/composition-api'

import {
  Placement,
  placements as popoverPlacements,
  PositioningStrategy,
} from '@popperjs/core'

import { usePopoverContent } from '~/composables/use-popover-content'
import { warn } from '~/utils/console'
import { defineEvent } from '~/types/emits'

import type { CSSProperties } from '@vue/runtime-dom'
import type { SetupContext } from 'vue'

export const VPopoverContentContextKey = Symbol(
  'VPopoverContentContextKey'
) as InjectionKey<boolean>

export default defineComponent({
  name: 'VPopoverContent',
  props: {
    visible: {
      type: Boolean,
      required: true,
    },
    hide: {
      type: Function as PropType<() => void>,
      required: true,
    },
    hideOnEsc: {
      type: Boolean,
      default: true,
    },
    hideOnClickOutside: {
      type: Boolean,
      default: true,
    },
    autoFocusOnShow: {
      type: Boolean,
      default: true,
    },
    autoFocusOnHide: {
      type: Boolean,
      default: true,
    },
    triggerElement: {
      type: (process.server
        ? Object
        : HTMLElement) as PropType<HTMLElement | null>,
      default: null,
    },
    placement: {
      type: String as PropType<Placement>,
      default: 'bottom-end',
      validate: (v: string) =>
        (popoverPlacements as unknown as string[]).includes(v),
    },
    strategy: {
      type: String as PropType<PositioningStrategy>,
      default: 'absolute',
      validate: (v: string) => ['absolute', 'fixed'].includes(v),
    },
    zIndex: {
      type: Number,
      required: true,
      // TODO: extract valid z-indexes (these are from the tailwind config)
      validator: (v: number | 'auto') =>
        [0, 10, 20, 30, 40, 50, 'auto'].includes(v),
    },
    clippable: {
      type: Boolean,
      default: false,
    },
  },
  /**
   * This is the only documented emitted event but in reality we pass through `$listeners`
   * to the underlying element so anything and everything is emitted. `@keydown` is the
   * only one this component overrides and controls (but ultimately still emits).
   */
  emits: { keydown: defineEvent(), blur: defineEvent() },
  setup(props, { emit, attrs }) {
    provide(VPopoverContentContextKey, true)
    if (!attrs['aria-label'] && !attrs['aria-labelledby']) {
      warn('You should provide either `aria-label` or `aria-labelledby` props.')
    }

    const propsRefs = toRefs(props)
    const popoverRef = ref<HTMLElement | null>(null)

    const { onKeyDown, onBlur, maxHeightRef } = usePopoverContent({
      popoverRef,
      popoverPropsRefs: propsRefs,
      emit: emit as SetupContext['emit'],
    })

    const heightProperties = computed(() => {
      // extracting this to ensure that computed is updated when the value changes
      const maxHeight = maxHeightRef.value

      return maxHeight && props.clippable
        ? ({ '--popover-height': `${maxHeight}px` } as CSSProperties)
        : ({} as CSSProperties)
    })

    return { popoverRef, onKeyDown, onBlur, heightProperties }
  },
})
</script>
<style>
.popover-content {
  height: var(--popover-height, auto);
  scrollbar-gutter: stable;
  overflow-x: hidden;
}
</style>
