<template>
  <VTeleport v-if="visible" to="modal">
    <!-- Prevent FocusTrap from trying to focus the first element. We already do that in a more flexible, adaptive way in our Dialog composables. -->
    <FocusTrap :initial-focus="() => false">
      <div
        class="flex justify-center z-40 fixed inset-0 bg-dark-charcoal bg-opacity-75 min-h-screen overflow-y-auto"
      >
        <div
          ref="dialogRef"
          v-bind="$attrs"
          class="w-full md:max-w-[768px] lg:w-[768px] xl:max-w-[1024px] xl:w-[1024px] flex flex-col"
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
              class="w-full flex justify-between md:justify-end bg-white md:bg-tx ps-4 pe-3 md:px-0 py-4 md:py-3 shrink-0"
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
                class="md:text-white text-sr md:text-base"
                @click="hide()"
              >
                {{ $t('modal.close') }}
                <VIcon :icon-path="closeIcon" class="ms-2" :size="5" />
              </VButton>
            </div>
          </slot>

          <div
            class="w-full flex-grow align-bottom bg-white md:rounded-t-md text-left"
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
