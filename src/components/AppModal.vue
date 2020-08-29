<template>
  <div
    v-if="visible"
    class="overlay"
    @click.self="$emit('close')"
    @keyup="checkKey"
  >
    <FocusTrap :active="true">
      <div class="modal relative" aria-modal="true" role="dialog">
        <header
          v-if="title"
          class="modal-header padding-top-bigger padding-left-bigger padding-right-normal padding-bottom-small"
        >
          <slot name="header">
            <h3>{{ title }}</h3>
          </slot>
          <button
            type="button"
            class="close-button has-color-gray is-size-6 is-size-4-touch"
            :aria-label="$t('browse-page.aria.close')"
            @click="$emit('close')"
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
/**
 * @todo: This entire component should be moved to vue-vocabulary
 */

import { FocusTrap } from 'focus-trap-vue'

export default {
  name: 'AppModal',
  components: {
    FocusTrap,
  },
  props: {
    visible: Boolean,
    title: String, // required for titlebar AND close button to show
    subTitle: String,
  },
  watch: {
    visible: {
      handler(to) {
        if (typeof document !== 'undefined') {
          if (to) {
            document.addEventListener('keyup', this.checkKey)
          } else {
            document.removeEventListener('keyup', this.checkKey)
          }
        }
      },
      immediate: true,
    },
  },
  destroyed() {
    document.removeEventListener('keyup', this.checkKey)
  },
  methods: {
    checkKey(e) {
      if (e.keyCode === 27) this.$emit('close')
    },
  },
}
</script>

<style lang="scss" scoped>
@import 'bulma/sass/utilities/_all';

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

.has-color-gray {
  color: rgb(176, 176, 176);
}

.modal-header {
  display: flex;
  display: flex;
  justify-content: space-around;
  align-items: flex-start;
  width: 100%;
  box-sizing: border-box;
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
