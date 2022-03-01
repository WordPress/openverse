<template>
  <VTeleport v-if="visible" to="modal">
    <!-- Prevent FocusTrap from trying to focus the first element. We already do that in a more flexible, adaptive way in our Dialog composables. -->
    <FocusTrap :initial-focus="() => false">
      <div :class="$style.overlay">
        <div
          ref="dialogRef"
          v-bind="$attrs"
          class="flex flex-col w-full"
          role="dialog"
          aria-modal="true"
          v-on="$listeners"
          @keydown="onKeyDown"
          @blur="onBlur"
        >
          <div class="w-full flex justify-between px-4 py-3 shrink-0">
            <VLogoButton
              :is-fetching="false"
              :is-header-scrolled="false"
              :is-search-route="true"
            />
            <VButton
              size="disabled"
              variant="plain"
              class="py-2 px-4 font-semibold text-sr"
              @click="hide()"
            >
              {{ $t('modal.close') }}
              <VIcon :icon-path="closeIcon" class="ms-2" />
            </VButton>
          </div>

          <div
            class="w-full flex-grow align-bottom bg-white rounded-t-sm text-left overflow-y-auto"
          >
            <slot />
          </div>
        </div>
      </div>
    </FocusTrap>
  </VTeleport>
</template>

<script>
import { defineComponent, toRefs, ref } from '@nuxtjs/composition-api'
import { FocusTrap } from 'focus-trap-vue'

import { useDialogContent } from '~/composables/use-dialog-content'
import { warn } from '~/utils/console'

import VTeleport from '~/components/VTeleport/VTeleport.vue'
import VButton from '~/components/VButton.vue'
import VIcon from '~/components/VIcon/VIcon.vue'
import VLogoButton from '~/components/VHeader/VLogoButton.vue'

import closeIcon from '~/assets/icons/close.svg'

/**
 * Renders the inner content of a modal and manages focus.
 */
const VMobileModalContent = defineComponent({
  name: 'VMobileModalContent',
  components: {
    VLogoButton,
    VTeleport,
    VButton,
    VIcon,
    FocusTrap,
  },
  props: {
    visible: {
      type: Boolean,
      required: true,
    },
    hide: {
      type: /** @type {import('@nuxtjs/composition-api').PropType<() => void>} */ (
        Function
      ),
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
      type: /** @type {import('@nuxtjs/composition-api').PropType<HTMLElement>} */ (
        process.server ? Object : HTMLElement
      ),
    },
    initialFocusElement: {
      type: /** @type {import('@nuxtjs/composition-api').PropType<HTMLElement>} */ (
        process.server ? Object : HTMLElement
      ),
      required: false,
    },
  },
  setup(props, { emit, attrs }) {
    if (!attrs['aria-label'] && !attrs['aria-labelledby']) {
      warn('You should provide either `aria-label` or `aria-labelledby` props.')
    }

    const propsRefs = toRefs(props)
    const dialogRef = ref()
    const { onKeyDown, onBlur } = useDialogContent({
      dialogRef,
      visibleRef: propsRefs.visible,
      autoFocusOnShowRef: propsRefs.autoFocusOnShow,
      autoFocusOnHideRef: propsRefs.autoFocusOnHide,
      triggerElementRef: propsRefs.triggerElement,
      hideOnClickOutsideRef: propsRefs.hideOnClickOutside,
      hideRef: propsRefs.hide,
      hideOnEscRef: propsRefs.hideOnEsc,
      initialFocusElementRef: propsRefs.initialFocusElement,
      emit,
    })

    return { dialogRef, onKeyDown, onBlur, closeIcon }
  },
})

export default VMobileModalContent
</script>

<style module>
.overlay {
  @apply flex justify-center z-50 fixed inset-0 min-h-screen bg-white;
}
</style>
