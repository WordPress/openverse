<template>
  <div ref="nodeRef">
    <!-- eslint-disable-next-line vuejs-accessibility/click-events-have-key-events -->
    <div ref="triggerContainerRef" class="flex" @click="onTriggerClick">
      <!--
        @slot The trigger. Should be a button 99% of the time. If you need custom event handling on the trigger button, ensure bubbling is not prevented or else the dialog will not open.
          @binding {object} a11yProps Props to v-bind to the trigger element to ensure accessibility
          @binding {boolean} visible Whether the dialog is currently visible (open)
      -->
      <slot
        name="trigger"
        :a11y-props="triggerA11yProps"
        :visible="internalVisibleRef"
      />
    </div>
    <VModalContent
      :visible="internalVisibleRef"
      :trigger-element="triggerRef"
      :hide-on-esc="hideOnEsc"
      :hide-on-click-outside="hideOnClickOutside"
      :auto-focus-on-show="autoFocusOnShow"
      :auto-focus-on-hide="autoFocusOnHide"
      :hide="close"
      :aria-label="label"
      :aria-labelledby="labelledBy"
      :initial-focus-element="initialFocusElement"
      :variant="variant"
      :mode="mode"
      :content-classes="modalContentClasses"
    >
      <template #top-bar>
        <slot name="top-bar" />
      </template>
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
  toRef,
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
    /**
     * The variant of the modal content.
     * The `default` variant is a full-screen modal on mobile widths, and is a smaller mobile
     * on a grayed out backdrop on larger screens.
     *
     * The `full` variant is a full-screen modal on all screen widths. It is currently
     * only used for mobile version of the `VHeaderInternal` component.
     *
     * @default 'default'
     */
    variant: {
      type: /** @type {import('@nuxtjs/composition-api').PropType<'default' | 'full' | 'two-thirds'>} */ (
        String
      ),
      default: 'default',
    },
    /**
     * The color mode of the modal content.
     * The default `light` mode uses dark charcoal content on the white background.
     * The `dark` mode uses white content on the dark charcoal background.
     *
     * @default 'light'
     */
    mode: {
      type: /** @type {import('@nuxtjs/composition-api').PropType<'dark' | 'light'>} */ (
        String
      ),
      default: 'light',
    },
    /**
     * This props allows for the modal to be opened or closed programmatically.
     * The modal handles the visibility internally if this prop is not provided.
     *
     * @default undefined
     */
    visible: {
      type: Boolean,
      default: undefined,
    },
    modalContentClasses: {
      type: String,
      default: '',
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
  setup(props, { emit }) {
    const visibleRef = toRef(props, 'visible')
    const internalVisibleRef =
      /** @type {import('@nuxtjs/composition-api').Ref<boolean>} */ (
        ref(props.visible === undefined ? false : props.visible)
      )
    const nodeRef = ref()

    /** @type {import('@nuxtjs/composition-api').Ref<HTMLElement | undefined>} */
    const triggerContainerRef = ref()

    const triggerA11yProps = reactive({
      'aria-expanded': false,
      'aria-haspopup': 'dialog',
    })

    const triggerRef = computed(
      () =>
        /** @type {HTMLElement | undefined} */ (
          triggerContainerRef.value?.firstChild
        )
    )

    watch(internalVisibleRef, (visible) => {
      triggerA11yProps['aria-expanded'] = !!visible
    })

    /**
     * When the `visible` prop is set to a different value than internalVisibleRef,
     * we update the internalVisibleRef to match the prop.
     */
    watch(visibleRef, (visible) => {
      if (visible === undefined || visible === internalVisibleRef.value) return

      if (visible) {
        open()
      } else {
        close()
      }
    })

    const { lock, unlock } = useBodyScrollLock({ nodeRef })

    const open = () => {
      internalVisibleRef.value = true
      lock()
      if (props.visible !== internalVisibleRef.value) {
        emit('open')
      }
    }

    const close = () => {
      internalVisibleRef.value = false
      unlock()
      emit('close')
    }

    const onTriggerClick = () => {
      if (internalVisibleRef.value === true) {
        close()
      } else {
        open()
      }
    }

    return {
      nodeRef,
      internalVisibleRef,
      triggerContainerRef,
      triggerRef,

      close,
      onTriggerClick,
      triggerA11yProps,
    }
  },
})
</script>
