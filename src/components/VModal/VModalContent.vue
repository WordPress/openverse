<template>
  <VTeleport v-if="visible" to="modal">
    <!-- Prevent FocusTrap from trying to focus the first element. We already do that in a more flexible, adaptive way in our Dialog composables. -->
    <FocusTrap :initial-focus="() => false">
      <div
        class="fixed inset-0 z-40 flex min-h-screen justify-center overflow-y-auto bg-dark-charcoal bg-opacity-75"
      >
        <div
          ref="dialogRef"
          v-bind="$attrs"
          class="flex w-full flex-col md:max-w-[768px] lg:w-[768px] xl:w-[1024px] xl:max-w-[1024px]"
          role="dialog"
          aria-modal="true"
          v-on="$listeners"
          @keydown="onKeyDown"
          @blur="onBlur"
        >
          <slot name="top-bar" :close="hide">
            <!--
              These specific padding and margin values serve to
              visually align the Openverse logo button in the modal
              with the header logo button so that there isn't a
              jarring "shifting" effect when opening the mobile modal.
            -->
            <div
              class="flex w-full shrink-0 justify-between bg-white py-4 pe-3 ps-4 md:justify-end md:bg-tx md:px-0 md:py-3"
            >
              <VLogoButton
                class="md:hidden"
                :is-fetching="false"
                :is-header-scrolled="false"
                :is-search-route="true"
              />
              <VButton
                ref="closeButton"
                size="disabled"
                variant="plain"
                class="text-sr md:text-base md:text-white"
                @click="hide()"
              >
                {{ $t('modal.close') }}
                <VIcon :icon-path="closeIcon" class="ms-2" :size="5" />
              </VButton>
            </div>
          </slot>

          <div
            class="w-full flex-grow bg-white text-left align-bottom md:rounded-t-md"
          >
            <slot />
          </div>
        </div>
      </div>
    </FocusTrap>
  </VTeleport>
</template>

<script>
import { defineComponent, toRefs, ref, computed } from '@nuxtjs/composition-api'
import { FocusTrap } from 'focus-trap-vue'
import { Portal as VTeleport } from 'portal-vue'

import { useDialogContent } from '~/composables/use-dialog-content'
import { warn } from '~/utils/console'

import VButton from '~/components/VButton.vue'
import VIcon from '~/components/VIcon/VIcon.vue'
import VLogoButton from '~/components/VHeader/VLogoButton.vue'

import closeIcon from '~/assets/icons/close.svg'

/**
 * Renders the inner content of a modal and manages focus.
 */
export default defineComponent({
  name: 'VModalContent',
  components: { VTeleport, VButton, VIcon, FocusTrap, VLogoButton },
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
      default: false,
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
    const closeButton = ref()
    const initialFocusElement = computed(
      () => props.initialFocusElement || closeButton.value?.$el
    )
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
      initialFocusElementRef: initialFocusElement,
      emit,
    })

    return {
      dialogRef,
      onKeyDown,
      onBlur,
      closeIcon,
      closeButton,
    }
  },
})
</script>

<style module></style>
