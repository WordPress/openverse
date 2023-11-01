<template>
  <VTeleport v-if="visible" to="modal">
    <div
      class="fixed inset-0 z-40 flex justify-center overflow-y-auto bg-dark-charcoal bg-opacity-75"
      :class="[
        $style['modal-backdrop'],
        $style[`modal-backdrop-${variant}`],
        $style[`modal-backdrop-${mode}`],
        contentClasses,
      ]"
    >
      <!-- re: disabled static element interactions rule https://github.com/WordPress/openverse/issues/2906 -->
      <!-- eslint-disable-next-line vuejs-accessibility/no-static-element-interactions -->
      <div
        ref="dialogRef"
        v-bind="$attrs"
        class="flex flex-col"
        :class="[$style[`modal-${variant}`], $style[`modal-${mode}`]]"
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
            v-if="variant === 'default'"
            class="flex w-full shrink-0 justify-between py-4 pe-3 ps-4 md:justify-end md:bg-tx md:px-0 md:py-3"
            :class="[$style[`top-bar-${variant}`], $style[`top-bar-${mode}`]]"
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
          class="flex w-full flex-grow flex-col"
          :class="[
            $style[`modal-content-${variant}`],
            $style[`modal-content-${mode}`],
          ]"
        >
          <slot />
        </div>
      </div>
    </div>
  </VTeleport>
</template>

<script lang="ts">
import { defineComponent, toRefs, ref, computed, PropType } from "vue"

import { Portal as VTeleport } from "portal-vue"

import { useDialogContent } from "~/composables/use-dialog-content"

import type { ModalColorMode, ModalVariant } from "~/types/modal"

import VIconButton from "~/components/VIconButton/VIconButton.vue"

/**
 * Renders the inner content of a modal and manages focus.
 */
export default defineComponent({
  name: "VModalContent",
  components: { VIconButton, VTeleport },
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

<style module>
.top-bar-default {
  @apply flex w-full shrink-0 justify-between bg-white py-4 pe-3 ps-4 md:justify-end md:bg-tx md:px-0 md:py-3;
}
.top-bar-full {
  @apply flex h-20 w-full shrink-0 justify-between bg-dark-charcoal px-4 py-3 md:items-stretch md:justify-start md:px-7 md:py-4;
}
.top-bar-two-thirds {
  @apply bg-tx;
}
.modal-backdrop {
  @apply h-[100dvh] max-h-[100dvh];
}
.modal-backdrop-fit-content,
.modal-backdrop-two-thirds {
  @apply bg-dark-charcoal bg-opacity-75;
}
.modal-backdrop-centered {
  @apply flex-col items-center;
}

.modal-default {
  @apply w-full md:max-w-[768px] lg:w-[768px] xl:w-[1024px] xl:max-w-[1024px];
}
.modal-full {
  @apply w-full;
}
.modal-two-thirds {
  @apply mt-auto h-2/3 w-full rounded-se-lg rounded-ss-lg bg-white;
}
.modal-centered {
  @apply m-6 rounded sm:m-0;
}

.modal-dark {
  @apply bg-black text-white;
}
.modal-light {
  @apply bg-white text-dark-charcoal;
}

.modal-content-default {
  @apply text-left align-bottom md:rounded-se-lg md:rounded-ss-lg;
}
.modal-content-centered {
  @apply w-auto rounded;
}
.modal-fit-content {
  @apply mt-auto w-full rounded-se-lg rounded-ss-lg bg-white;
}
.modal-content-full {
  @apply flex w-full flex-col justify-between px-6 pb-10;
}
.modal-content-two-thirds {
  @apply overflow-y-hidden rounded-se-lg rounded-ss-lg;
}
.modal-content-fit-content {
  @apply rounded-se-lg rounded-ss-lg;
}
.modal-content-dark {
  @apply bg-black text-white;
}
.modal-content-light {
  @apply bg-white text-dark-charcoal;
}
/*
For mobiles that do not support dvh units, we add a fallback padding
to the modal content to make sure that no clickable elements are hidden
by the address bar.
*/
@supports not (height: 100dvh) {
  .modal-content-fit-content,
  .modal-content-two-thirds {
    @apply pb-10;
  }
}
</style>
