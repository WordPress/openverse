<template>
  <!-- eslint-disable-next-line vuejs-accessibility/click-events-have-key-events -->
  <div ref="modal" class="overlay app-modal" @click.self="$emit('close')">
    <FocusTrap :active="true">
      <div class="modal relative" aria-modal="true" role="dialog">
        <header v-if="title" class="modal-header pt-8 ps-8 pe-4 pb-2">
          <slot name="header">
            <h3>{{ title }}</h3>
          </slot>
          <button
            type="button"
            class="close-button text-gray text-lgr desk:text-base"
            :aria-label="$t('browse-page.aria.close')"
            @click="$emit('close')"
            @keypress.enter="$emit('close')"
          >
            <i class="icon cross" />
          </button>
        </header>
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

<style lang="scss" scoped>
.modal {
  position: relative;
  margin: 0px auto;
  max-width: 85vw;
  max-height: 85vh;
  overflow-x: hidden;
  overflow-y: auto;
  border-radius: 2px;
  box-shadow: 0 2px 8px 3px;
  background-color: #fff;
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  z-index: 600;
  background: #00000094;
}

.modal-header {
  display: flex;
  justify-content: space-around;
  align-items: flex-start;
  width: 100%;
}

.close-button {
  appearance: none;
  border: none;
  height: auto;
  margin: -20px -20px -20px auto;
  padding: 20px;
  background-color: transparent;
  line-height: 1;
  cursor: pointer;
  .icon {
    height: auto;
  }
  &:hover {
    color: rgb(120, 120, 120);
  }
}
</style>
