<template>
  <div
    class="wrapper px-4 md:px-7 py-2 md:flex md:items-center md:justify-between"
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
          :aria-label="$t('modal.close')"
          @click="$emit('close')"
        >
          <VIcon :icon-path="closeIcon" />
        </button>
      </slot>
    </div>
  </div>
</template>

<script>
import { defineComponent } from '@nuxtjs/composition-api'

import VIcon from '~/components/VIcon/VIcon.vue'

import closeIcon from '~/assets/icons/close.svg'

const VNotificationBanner = defineComponent({
  name: 'VNotificationBanner',
  components: {
    VIcon,
  },
  setup() {
    return { closeIcon }
  },
})
export default VNotificationBanner
</script>

<style scoped lang="scss">
// Styles from learn.wordpress.org
.wrapper {
  background-color: #fff8e5;
  border-left: 0.25rem solid #ffb900;
}
</style>
