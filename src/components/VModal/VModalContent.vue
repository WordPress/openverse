<template>
  <VTeleport v-if="visible" to="modal">
    <div
      class="fixed inset-0 z-40 flex min-h-screen justify-center overflow-y-auto bg-dark-charcoal bg-opacity-75"
      :class="[
        $style[`modal-backdrop-${variant}`],
        $style[`modal-backdrop-${mode}`],
        contentClasses,
      ]"
    >
      <div
        ref="dialogRef"
        v-bind="$attrs"
        class="flex w-full flex-col"
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
            class="md:justify-end md:bg-tx md:px-0 md:py-3 flex w-full shrink-0 justify-between py-4 pe-3 ps-4"
            :class="[$style[`top-bar-${variant}`], $style[`top-bar-${mode}`]]"
          >
            <VLogoButtonOld
              class="md:hidden"
              :is-fetching="false"
              :is-header-scrolled="false"
              :is-search-route="true"
            />
            <VButton
              ref="closeButton"
              size="disabled"
              variant="plain"
              class="md:text-base md:text-white text-sr"
              @click="hide()"
            >
              {{ $t('modal.close') }}
              <VIcon :icon-path="closeIcon" class="ms-2" :size="5" />
            </VButton>
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
import {
  defineComponent,
  toRefs,
  ref,
  computed,
  PropType,
} from '@nuxtjs/composition-api'

import { Portal as VTeleport } from 'portal-vue'

import { useDialogContent } from '~/composables/use-dialog-content'
import { warn } from '~/utils/console'

import type { ModalColorMode, ModalVariant } from '~/types/modal'

import VButton from '~/components/VButton.vue'
import VIcon from '~/components/VIcon/VIcon.vue'
import VLogoButtonOld from '~/components/VHeaderOld/VLogoButtonOld.vue'

import closeIcon from '~/assets/icons/close.svg'

/**
 * Renders the inner content of a modal and manages focus.
 */
export default defineComponent({
  name: 'VModalContent',
  components: { VTeleport, VButton, VIcon, VLogoButtonOld },
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
      default: 'default',
    },
    mode: {
      type: String as PropType<ModalColorMode>,
      default: 'light',
    },
    /**
     * The tailwind classes to apply to the modal backdrop element.
     * Can be used to make the modal hidden on some breakpoint.
     */
    contentClasses: {
      type: String,
      default: '',
    },
  },
  setup(props, { emit, attrs }) {
    if (!attrs['aria-label'] && !attrs['aria-labelledby']) {
      warn('You should provide either `aria-label` or `aria-labelledby` props.')
    }

    const propsRefs = toRefs(props)
    const closeButton = ref<InstanceType<typeof VButton> | null>(null)
    const initialFocusElement = computed(
      () => props.initialFocusElement || closeButton.value?.$el
    )
    const dialogRef = ref<HTMLElement | null>(null)
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

<style module>
.top-bar-default {
  @apply md:justify-end md:bg-tx md:px-0 md:py-3 flex w-full shrink-0 justify-between bg-white py-4 pe-3 ps-4;
}
.top-bar-full {
  @apply md:items-stretch md:justify-start md:py-4 md:px-7 flex h-20 w-full shrink-0 justify-between bg-dark-charcoal px-4 py-3;
}
.top-bar-two-thirds {
  @apply bg-tx;
}
.modal-backdrop-two-thirds {
  @apply bg-dark-charcoal bg-opacity-75;
}
.modal-default {
  @apply md:max-w-[768px] lg:w-[768px] xl:w-[1024px] xl:max-w-[1024px];
}

.modal-dark {
  @apply bg-dark-charcoal text-white;
}
.modal-light {
  @apply bg-white text-dark-charcoal;
}
.modal-content-default {
  @apply md:rounded-t-md text-left align-bottom;
}
.modal-content-full {
  @apply flex w-full flex-col justify-between px-6 pb-10;
}
.modal-two-thirds {
  @apply mt-auto h-2/3 w-full rounded-t-lg bg-white;
}
.modal-content-two-thirds {
  @apply overflow-y-hidden rounded-t-md;
}
.modal-content-dark {
  @apply bg-dark-charcoal text-white;
}
.modal-content-light {
  @apply bg-white text-dark-charcoal;
}
</style>
