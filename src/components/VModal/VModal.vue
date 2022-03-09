<template>
  <div ref="nodeRef">
    <!-- eslint-disable-next-line vuejs-accessibility/click-events-have-key-events -->
    <div ref="triggerContainerRef" @click="onTriggerClick">
      <!--
        @slot The trigger. Should be a button 99% of the time. If you need custom event handling on the trigger button, ensure bubbling is not prevented or else the dialog will not open.
          @binding {object} a11yProps Props to v-bind to the trigger element to ensure accessibility
          @binding {boolean} visible Whether the dialog is currently visible (open)
      -->
      <slot
        name="trigger"
        :a11y-props="triggerA11yProps"
        :visible="visibleRef"
      />
    </div>
    <VModalContent
      :visible="visibleRef"
      :trigger-element="triggerRef"
      :hide-on-esc="hideOnEsc"
      :hide-on-click-outside="hideOnClickOutside"
      :auto-focus-on-show="autoFocusOnShow"
      :auto-focus-on-hide="autoFocusOnHide"
      :hide="close"
      :aria-label="label"
      :aria-labelledby="labelledBy"
      :initial-focus-element="initialFocusElement"
    >
      <slot name="default" />
    </VModalContent>
  </div>
</template>

<script>
import {
  defineComponent,
  ref,
  watch,
  reactive,
  computed,
} from '@nuxtjs/composition-api'

import { useBodyScrollLock } from '~/composables/use-body-scroll-lock'

import VModalContent from '~/components/VModal/VModalContent.vue'

export default defineComponent({
  name: 'VModal',
  components: { VModalContent },
  /**
   * NB: Most of these technically default to `undefined` so that the underlying `VPopoverContent`
   * default for each of them can take over.
   */
  props: {
    /**
     * Whether the popover should hide when the <kbd>Escape</kbd> key is pressed.
     *
     * @default true
     */
    hideOnEsc: { type: Boolean, default: undefined },
    /**
     * Whether the popover should hide when a click happens outside the popover content,
     * excluding the trigger. When the trigger is clicked and the popover is open, nothing
     * will happen.
     *
     * @default true
     */
    hideOnClickOutside: { type: Boolean, default: undefined },
    /**
     * Whether the popover content should automatically receive focus when the popover
     * opens.
     *
     * @default true
     */
    autoFocusOnShow: { type: Boolean, default: undefined },
    /**
     * Whether the trigger should automatically receive focus when the popover closes.
     *
     * @default true
     */
    autoFocusOnHide: { type: Boolean, default: undefined },
    /**
     * The label of the popover content. Must be provided if `labelledBy` is empty.
     *
     * @default undefined
     */
    label: { type: String },
    /**
     * The id of the element labelling the popover content. Must be provided if `label` is empty.
     *
     * @default undefined
     */
    labelledBy: { type: String },
    /**
     * The element to focus when the modal is opened. If nothing is
     * passed, then the first tabbable element in the modal content
     * will be focused. If no tabbable element is found in the modal
     * content, then the entire modal content itself will be focused.
     *
     * @default undefined
     */
    initialFocusElement: {
      type: /** @type {import('@nuxtjs/composition-api').PropType<HTMLElement>} */ (
        process.server ? Object : HTMLElement
      ),
      default: undefined,
    },
  },
  emits: [
    /**
     * Fires when the popover opens, regardless of reason. There are no extra parameters.
     */
    'open',
    /**
     * Fires when the popover closes, regardless of reason. There are no extra parameters.
     */
    'close',
  ],
  setup(_, { emit }) {
    const visibleRef = ref(false)
    const nodeRef = ref()

    /** @type {import('@nuxtjs/composition-api').Ref<HTMLElement | undefined>} */
    const triggerContainerRef = ref()

    const triggerA11yProps = reactive({
      'aria-expanded': false,
      'aria-haspopup': 'dialog',
    })

    const triggerRef = computed(() => triggerContainerRef.value?.firstChild)

    watch([visibleRef], ([visible]) => {
      if (visible) {
        triggerA11yProps['aria-expanded'] = true
      } else {
        triggerA11yProps['aria-expanded'] = false
      }
    })

    const { lock, unlock } = useBodyScrollLock({ nodeRef })

    const open = () => {
      visibleRef.value = true
      emit('open')
      lock()
    }

    const close = () => {
      visibleRef.value = false
      emit('close')
      unlock()
    }

    const onTriggerClick = () => {
      if (visibleRef.value === true) {
        close()
      } else {
        open()
      }
    }

    return {
      nodeRef,
      visibleRef,
      close,
      triggerContainerRef,
      triggerRef,
      onTriggerClick,
      triggerA11yProps,
    }
  },
})
</script>
