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
    visible: Boolean,
  },
  watch: {
    visible: {
      handler(to) {
        if (to) document.addEventListener('keyup', this.checkKey)
        else document.removeEventListener('keyup', this.checkKey)
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
.modal {
  margin: 0px auto;
  border-radius: 2px;
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

</style>
