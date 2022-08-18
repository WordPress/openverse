<template>
  <div role="alert" :class="[$style.snackbar, $style[size]]">
    <!-- @slot Your message or subcomponent goes passed here. -->
    <slot />
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from '@nuxtjs/composition-api'

export default defineComponent({
  name: 'VSnackbar',
  props: {
    size: {
      type: String as PropType<'small' | 'large'>,
      default: 'small',
    },
  },
})
</script>

<style module>
.snackbar {
  box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.3);
  @apply fixed bottom-4 rounded-sm bg-black text-white ltr:left-4 rtl:right-4;
}

.large {
  @apply w-max max-w-full flex-row items-center py-4 px-8 text-sm;
}

.small {
  @apply w-2/3 flex-col items-start py-3 px-4 text-sr sm:w-2/5;
}
</style>
