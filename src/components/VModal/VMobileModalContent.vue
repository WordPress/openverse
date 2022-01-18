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
          <div class="w-full flex justify-between h-20 px-4 py-6 shrink-0">
            <NuxtLink
              to="/"
              class="rounded-sm ring-offset-1 focus:outline-none focus-visible:ring focus-visible:ring-pink -ms-2 inline-flex items-center hover:bg-yellow"
            >
              <VLogoLoader />
              <OpenverseLogoText class="-ml-1 mt-1" width="95" height="15" />
            </NuxtLink>
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
import { warn } from '~/utils/warn'

import closeIcon from '~/assets/icons/close.svg'
import OpenverseLogoText from '~/assets/icons/openverse-logo-text.svg?inline'

import VTeleport from '~/components/VTeleport/VTeleport.vue'
import VButton from '~/components/VButton.vue'
import VIcon from '~/components/VIcon/VIcon.vue'
import VLogoLoader from '~/components/VLogoLoader/VLogoLoader.vue'

/**
 * Renders the inner content of a modal and manages focus.
 */
const VMobileModalContent = defineComponent({
  name: 'VMobileModalContent',
  components: {
    OpenverseLogoText,
    VLogoLoader,
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
