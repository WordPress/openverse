<script setup lang="ts">
/**
 * Renders the inner content of a modal and manages focus.
 */
import { toRefs, ref, computed, useAttrs } from "vue"

import { useDialogContent } from "~/composables/use-dialog-content"

import type { ModalColorMode, ModalVariant } from "~/types/modal"

import VIconButton from "~/components/VIconButton/VIconButton.vue"

defineOptions({
  inheritAttrs: false,
})

const props = withDefaults(
  defineProps<{
    visible: boolean
    hide: () => void
    hideOnEsc?: boolean
    hideOnClickOutside?: boolean
    autoFocusOnShow?: boolean
    autoFocusOnHide?: boolean
    trapFocus?: boolean
    triggerElement?: HTMLElement | null
    initialFocusElement?: HTMLElement | null
    variant?: ModalVariant
    mode?: ModalColorMode
    /**
     * The tailwind classes to apply to the modal backdrop element.
     * Can be used to make the modal hidden on some breakpoint.
     */
    contentClasses?: string
  }>(),
  {
    hideOnEsc: true,
    hideOnClickOutside: false,
    autoFocusOnShow: true,
    autoFocusOnHide: true,
    trapFocus: true,
    triggerElement: null,
    initialFocusElement: null,
    variant: "default",
    mode: "light",
    contentClasses: "",
  }
)

const emit = defineEmits<{
  keydown: [KeyboardEvent]
  focus: [FocusEvent]
  blur: [FocusEvent]
  close: []
  open: []
}>()

const attrs = useAttrs()

const propsRefs = toRefs(props)
const closeButton = ref<InstanceType<typeof VIconButton> | null>(null)
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
  emit: emit as (event: string) => void,
  attrs,
})

const handleClose = (event: MouseEvent) => {
  event.stopPropagation()
  props.hide()
}

defineExpose({
  dialogRef,
  deactivateFocusTrap,
})
</script>

<template>
  <Teleport to="#teleports">
    <div
      v-show="visible"
      class="backdrop h-dyn-screen min-h-dyn-screen fixed inset-0 z-40 flex justify-center overflow-y-auto"
      :class="[
        { 'flex-col items-center': variant === 'centered' },
        variant === 'mobile-input' ? 'bg-tx' : 'bg-modal-layer bg-opacity-75',
        contentClasses,
        variant,
      ]"
    >
      <!-- re: disabled static element interactions rule https://github.com/WordPress/openverse/issues/2906 -->
      <!-- eslint-disable-next-line vuejs-accessibility/no-static-element-interactions -->
      <div
        ref="dialogRef"
        v-bind="$attrs"
        class="flex flex-col"
        :class="[
          mode === 'dark' ? 'bg-black text-default' : 'bg-overlay text-default',
          {
            'w-full md:max-w-[768px] lg:w-[768px] xl:w-[1024px] xl:max-w-[1024px]':
              variant === 'default',
            'w-full': variant === 'full',
            'mt-auto h-2/3 w-full rounded-se-lg rounded-ss-lg bg-overlay':
              variant === 'two-thirds',
            'mt-auto w-full rounded-se-lg rounded-ss-lg bg-overlay':
              variant === 'fit-content',
            'm-6 max-w-90 rounded sm:m-0': variant === 'centered',
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
            class="flex w-full shrink-0 justify-between bg-overlay py-4 pe-3 ps-4 md:justify-end md:bg-tx md:px-0 md:py-3"
          >
            <VIconButton
              ref="closeButton"
              :label="$t('modal.ariaClose')"
              variant="filled-white"
              size="small"
              @click="handleClose"
            />
          </div>
        </slot>

        <div
          class="modal-content flex w-full flex-grow flex-col"
          :class="{
            'text-left align-bottom md:rounded-se-lg md:rounded-ss-lg':
              variant === 'default',
            'w-auto rounded': variant === 'centered',
            'mt-auto w-full rounded-se-lg rounded-ss-lg bg-overlay':
              variant === 'fit-content',
            'flex w-full flex-col justify-between px-6 pb-10':
              variant === 'full',
            'overflow-y-hidden rounded-se-lg rounded-ss-lg':
              variant === 'two-thirds',
            'h-full': variant === 'mobile-input',
            'bg-black text-default': mode === 'dark',
            'bg-overlay text-default': mode === 'light',
            'fallback-padding':
              variant === 'fit-content' ||
              variant === 'two-thirds' ||
              variant === 'mobile-input',
          }"
        >
          <slot />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.backdrop.mobile-input {
  height: calc(100dvh - var(--header-height, 80px));
  top: var(--header-height, 80px);
}
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
