<template>
  <div :id={id} class="overlay" @click.self="$emit('close')">
    <div class="modal relative">
      <button type="button"
        class="close-button has-color-gray"
        @click="$emit('close')"
        aria-label="close">
        <i class="icon cross" />
      </button>
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
  props: ['id'],
};
</script>

<style lang="scss" scoped>
.modal {
  max-width: 80vw;
  max-height: 80vh;
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
  color: rgb(176, 176, 176)
}

.close-button {
  appearance: none;
  border: none;
  background-color: transparent;
  font-size: 30px;
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
