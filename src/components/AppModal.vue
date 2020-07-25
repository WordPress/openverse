<template>
  <div
    v-if="visible"
    class="overlay"
    @click.self="$emit('close')"
    @keyup="checkKey"
  >
    <div class="modal relative" aria-modal="true" role="dialog">
      <slot default />
    </div>
  </div>
</template>

<script>
/**
 * @todo: This entire component should be moved to vue-vocabulary
 */
export default {
  name: 'app-modal',
  props: {
    visible: Boolean
  },
  watch: {
    visible: {
      handler(to) {
        if (to) document.addEventListener('keyup', this.checkKey)
        else document.removeEventListener('keyup', this.checkKey)
      },
      immediate: true
    }
  },
  destroyed() {
    document.removeEventListener('keyup', this.checkKey)
  },
  methods: {
    checkKey(e) {
      if (e.keyCode === 27) this.$emit('close')
    }
  }
}
</script>

<style lang="scss" scoped>
.modal {
  width: 21.875rem;
  max-height: 37rem;
  margin: 0px auto;
  background-color: #fff;
  border-radius: 2px;
  overflow-x: hidden;
  overflow-y: scroll;
  box-shadow: 0 2px 8px 3px;
  position: relative;
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
  z-index: 100;
  background: #00000094;
}

.has-color-gray {
  color: rgb(176, 176, 176);
}

.close-button {
  appearance: none;
  border: none;
  background-color: transparent;
  padding: 20px;
  line-height: 1;
  height: auto;
  position: absolute;
  top: 0;
  right: 0;
  cursor: pointer;

  .icon {
    height: auto;
  }

  &:hover {
    color: rgb(120, 120, 120);
  }
}
</style>
