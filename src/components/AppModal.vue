<template>
  <!-- eslint-disable-next-line vuejs-accessibility/click-events-have-key-events -->
  <div
    ref="modal"
    class="overlay app-modal fixed w-full flex justify-center z-50 bg-dark-charcoal bg-opacity-75"
    @click.self="$emit('close')"
  >
    <FocusTrap :active="true">
      <div
        class="rounded mt-10 mb-80 min-h-min bg-white"
        aria-modal="true"
        role="dialog"
      >
        <slot default />
      </div>
    </FocusTrap>
  </div>
</template>

<script>
import { FocusTrap } from 'focus-trap-vue'

/**
 * @todo: This entire component should be moved to vue-vocabulary
 */
export default {
  name: 'AppModal',
  components: {
    FocusTrap,
  },
  props: {
    /** Required for titlebar AND close button to show */
    title: String,
    subTitle: String,
  },
  mounted() {
    document.addEventListener('keyup', this.closeOnEsc)
  },
  destroyed() {
    document.removeEventListener('keyup', this.closeOnEsc)
  },
  methods: {
    closeOnEsc(e) {
      if (e.keyCode === 27) {
        this.$emit('close')
      }
    },
  },
}
</script>
