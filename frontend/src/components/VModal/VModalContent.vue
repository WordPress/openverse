<template>
  <div>
    <ClientOnly>
      <Teleport to="#modal">
        <div
          v-show="visible"
          class="fixed inset-0 z-40 flex h-[100dvh] max-h-[100dvh] justify-center overflow-y-auto bg-dark-charcoal bg-opacity-75"
          :class="[
            {
              'bg-dark-charcoal bg-opacity-75':
                variant === 'fit-content' || variant === 'two-thirds',
              'flex-col items-center': variant === 'centered',
            },
            contentClasses,
          ]"
        >
          <!-- re: disabled static element interactions rule https://github.com/WordPress/openverse/issues/2906 -->
          <!-- eslint-disable-next-line vuejs-accessibility/no-static-element-interactions -->
          <div
            ref="dialogRef"
            v-bind="$attrs"
            class="flex flex-col"
            :class="[
              mode === 'dark'
                ? 'bg-black text-white'
                : 'bg-white text-dark-charcoal',
              {
                'w-full md:max-w-[768px] lg:w-[768px] xl:w-[1024px] xl:max-w-[1024px]':
                  variant === 'default',
                'w-full': variant === 'full',
                'mt-auto h-2/3 w-full rounded-se-lg rounded-ss-lg bg-white':
                  variant === 'two-thirds',
                'mt-auto w-full rounded-se-lg rounded-ss-lg bg-white':
                  variant === 'fit-content',
                'm-6 rounded sm:m-0': variant === 'centered',
              },
            ]"
            role="dialog"
            aria-modal="true"
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
                v-if="variant === 'default'"
                class="flex w-full shrink-0 justify-between bg-white py-4 pe-3 ps-4 md:justify-end md:bg-tx md:px-0 md:py-3"
              >
                <VIconButton
                  ref="closeButton"
                  :label="$t('modal.ariaClose')"
                  variant="filled-white"
                  size="small"
                  @click="hide()"
                />
              </div>
            </slot>

            <div
              class="modal-content flex w-full flex-grow flex-col"
              :class="{
                'text-left align-bottom md:rounded-se-lg md:rounded-ss-lg':
                  variant === 'default',
                'w-auto rounded': variant === 'centered',
                'mt-auto w-full rounded-se-lg rounded-ss-lg bg-white':
                  variant === 'fit-content',
                'flex w-full flex-col justify-between px-6 pb-10':
                  variant === 'full',
                'overflow-y-hidden rounded-se-lg rounded-ss-lg':
                  variant === 'two-thirds',
                'bg-black text-white': mode === 'dark',
                'bg-white text-dark-charcoal': mode === 'light',
                'fallback-padding':
                  variant === 'fit-content' || variant === 'two-thirds',
              }"
            >
              <slot />
            </div>
          </div>
        </div>
      </Teleport>
    </ClientOnly>
  </div>
</template>

<script lang="ts">
import { defineComponent, toRefs, ref, computed, PropType } from "vue"

import { useDialogContent } from "~/composables/use-dialog-content"

import type { ModalColorMode, ModalVariant } from "~/types/modal"

import VIconButton from "~/components/VIconButton/VIconButton.vue"

/**
 * Renders the inner content of a modal and manages focus.
 */
export default defineComponent({
  name: "VModalContent",
  components: { VIconButton },
  inheritAttrs: false,
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
    trapFocus: {
      type: Boolean,
      default: true,
    },
    triggerElement: {
      type: (process.server ? Object : HTMLElement) as PropType<HTMLElement>,
      default: null,
    },
    initialFocusElement: {
      type: (process.server ? Object : HTMLElement) as PropType<HTMLElement>,
      default: null,
    },
    variant: {
      type: String as PropType<ModalVariant>,
      default: "default",
    },
    mode: {
      type: String as PropType<ModalColorMode>,
      default: "light",
    },
    /**
     * The tailwind classes to apply to the modal backdrop element.
     * Can be used to make the modal hidden on some breakpoint.
     */
    contentClasses: {
      type: String,
      default: "",
    },
  },
  setup(props, { emit, attrs }) {
    const propsRefs = toRefs(props)
    const closeButton = ref<{ $el: HTMLElement } | null>(null)
    const initialFocusElement = computed(
      () => props.initialFocusElement || closeButton.value?.$el
    )
    const dialogRef = ref<HTMLElement | null>(null)
    const { onKeyDown, onBlur, deactivateFocusTrap } = useDialogContent({
      dialogElements: {
        dialogRef,
        initialFocusElementRef: initialFocusElement,
        triggerElementRef: propsRefs.triggerElement,
      },
      visibleRef: propsRefs.visible,
      dialogOptions: {
        hideOnEscRef: propsRefs.hideOnEsc,
        hideOnClickOutsideRef: propsRefs.hideOnClickOutside,
        autoFocusOnShowRef: propsRefs.autoFocusOnShow,
        autoFocusOnHideRef: propsRefs.autoFocusOnHide,
        trapFocusRef: propsRefs.trapFocus,
      },
      hideRef: propsRefs.hide,
      emit,
      attrs,
    })

    return {
      dialogRef,
      onKeyDown,
      onBlur,
      closeButton,
      deactivateFocusTrap,
    }
  },
})
</script>

<style scoped>
/*
For mobiles that do not support dvh units, we add a fallback padding
to the modal content to make sure that no clickable elements are hidden
by the address bar.
*/
@supports not (height: 100dvh) {
  .modal-content.fallback-padding {
    @apply pb-10;
  }
}
</style>
