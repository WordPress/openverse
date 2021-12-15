<template>
  <div
    class="wrapper px-8 py-2 md:flex md:items-center md:justify-between"
    dir="ltr"
  >
    <p class="text-center md:text-left">
      <slot name="default" />
    </p>
    <div class="flex">
      <slot name="buttons">
        <button
          class="button is-text small dismiss-button"
          type="button"
          aria-label="close notification banner"
          @click="handleDismissClick"
        >
          <CloseIcon aria-hidden="true" />
        </button>
      </slot>
    </div>
  </div>
</template>

<script>
import CloseIcon from '~/assets/icons/close.svg?inline'
export default {
  name: 'NotificationBanner',
  components: {
    CloseIcon,
  },
  methods: {
    handleDismissClick() {
      this.$emit('close')
    },
  },
}
</script>

<style scoped lang="scss">
// Styles from learn.wordpress.org
$bgColor: #fff8e5;
.wrapper {
  background-color: $bgColor;
  border-left: 4px solid #ffb900;
}
</style>
