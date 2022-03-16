<template>
  <div
    v-show="visible"
    class="w-0 h-0"
    :aria-hidden="!visible"
    v-on="$listeners"
    @keydown="onKeyDown"
  >
    <div
      ref="popoverRef"
      class="bg-white border border-light-gray rounded-sm shadow max-w-max"
      :style="{ zIndex }"
      :tabindex="-1"
      @blur="onBlur"
    >
      <slot />
    </div>
  </div>
</template>

<script>
import { defineComponent, toRefs, ref, provide } from '@nuxtjs/composition-api'

import { usePopoverContent } from '~/composables/use-popover-content'
import { warn } from '~/utils/console'

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
