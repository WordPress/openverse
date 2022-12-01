<template>
  <div
    class="flex items-center justify-between px-4 py-2 md:px-7"
    :class="$style[variant]"
    :data-testid="`banner-${id}`"
  >
    <p class="caption-regular md:description-regular text-left">
      <slot name="default" />
    </p>
    <div class="flex">
      <slot name="buttons">
        <VIconButton
          :class="{ 'text-white': variant === 'announcement' }"
          size="small"
          :aria-label="$t('modal.close')"
          :icon-props="{
            iconPath: closeIcon,
          }"
          @click="handleClose"
        />
      </slot>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from '@nuxtjs/composition-api'

import { defineEvent } from '~/types/emits'

import type { BannerId } from '~/types/banners'

import VIconButton from '~/components/VIconButton/VIconButton.vue'

import closeIcon from '~/assets/icons/close.svg'

export default defineComponent({
  name: 'VNotificationBanner',
  components: {
    VIconButton,
  },
  props: {
    variant: {
      type: String as PropType<'announcement' | 'informational'>,
      required: true,
    },
    id: {
      type: String as PropType<BannerId>,
      required: true,
    },
  },
  emits: {
    close: defineEvent(),
  },
  setup(_, { emit }) {
    const handleClose = () => {
      emit('close')
    }

    return {
      closeIcon,
      handleClose,
    }
  },
})
</script>

<style module>
/* Styles from learn.wordpress.org */
.informational {
  background-color: #fff8e5;
  border-left: 0.25rem solid #ffb900;
}

.announcement {
  @apply bg-trans-blue text-white;
  border-left: 0.25rem solid transparent;
}
</style>
