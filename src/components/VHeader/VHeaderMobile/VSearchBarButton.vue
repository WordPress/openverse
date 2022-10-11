<template>
  <VIconButton
    size="search-medium"
    class="border-tx bg-tx"
    :button-props="{ variant: 'plain--avoid' }"
    v-on="$listeners"
  >
    <template #default="{ iconSize }">
      <span
        class="relative flex flex-shrink-0 flex-grow-0 items-center justify-center rounded-sm group-focus-visible:ring group-focus-visible:ring-pink group-active:ring group-active:ring-pink"
        :class="[`h-${innerSize} w-${innerSize}`, innerAreaClasses]"
      >
        <VIcon
          :icon-path="iconPath"
          :rtl-flip="rtlFlip"
          class="pointer-events-none"
          :size="iconSize"
        />
        <slot name="notification" />
      </span>
    </template>
  </VIconButton>
</template>
<script lang="ts">
import { defineComponent, PropType } from '@nuxtjs/composition-api'

import VIcon from '~/components/VIcon/VIcon.vue'
import VIconButton from '~/components/VIconButton/VIconButton.vue'

export default defineComponent({
  name: 'VSearchBarButton',
  components: { VIcon, VIconButton },
  props: {
    iconPath: {
      type: String,
      required: true,
    },
    innerSize: {
      type: Number as PropType<6 | 8>,
      default: 8,
    },
    innerAreaClasses: {
      type: String,
      default: '',
    },
    rtlFlip: {
      type: Boolean,
      default: false,
    },
  },
})
</script>
