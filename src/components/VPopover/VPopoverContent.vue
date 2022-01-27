<template>
  <div
    v-if="visible"
    ref="popoverRef"
    :class="[$style.popover, { [`z-${zIndex}`]: zIndex !== undefined }]"
    :aria-hidden="!visible"
    :tabindex="typeof $props.tabindex !== 'undefined' ? $props.tabindex : -1"
    v-on="$listeners"
    @keydown="onKeyDown"
    @blur="onBlur"
  >
    <slot />
  </div>
</template>

<script>
import { defineComponent, toRefs, ref, provide } from '@nuxtjs/composition-api'
import { usePopoverContent } from '~/composables/use-popover-content'
import { warn } from '~/utils/warn'

import { propTypes } from './VPopoverContent.types'

/**
 * @type {import('@nuxtjs/composition-api').InjectionKey<boolean>}
 */
export const VPopoverContentContextKey = Symbol('VPopoverContentContextKey')

export default defineComponent({
  name: 'VPopover',
  props: propTypes,
  /**
   * This is the only documented emitted event but in reality we pass through `$listeners`
   * to the underlying element so anything and everything is emitted. `@keydown` is the
   * only one this component overrides and controls (but ultimately still emits).
   */
  emits: ['keydown', 'blur'],
  /**
   * @param {import('./VPopoverContent.types').Props} props
   * @param {import('@nuxtjs/composition-api').SetupContext} context
   */
  setup(props, { emit, attrs }) {
    provide(VPopoverContentContextKey, true)
    if (!attrs['aria-label'] && !attrs['aria-labelledby']) {
      warn('You should provide either `aria-label` or `aria-labelledby` props.')
    }

    const propsRefs = toRefs(props)
    const popoverRef = ref()
    const { onKeyDown, onBlur } = usePopoverContent({
      popoverRef,
      popoverPropsRefs: propsRefs,
      emit,
    })

    return { popoverRef, onKeyDown, onBlur }
  },
})
</script>

<style module>
.popover {
  @apply bg-white border border-light-gray rounded-sm max-w-max whitespace-nowrap shadow;
}
</style>
