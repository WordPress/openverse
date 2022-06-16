<template>
  <VButton
    variant="action-menu"
    size="disabled"
    class="font-semibold p-2 w-12 leading-7 focus-visible:border-tx"
    :aria-label="$t('header.aria.menu')"
    v-bind="a11yProps"
    @click="$emit('click')"
  >
    <VIcon :icon-path="ellipsisIcon" />
  </VButton>
</template>
<script lang="ts">
import { defineComponent } from '@nuxtjs/composition-api'

import { defineEvent } from '~/types/emits'

import VIcon from '~/components/VIcon/VIcon.vue'
import VButton from '~/components/VButton.vue'

import ellipsisIcon from '~/assets/icons/ellipsis.svg'

export default defineComponent({
  name: 'VPageMenuButton',
  components: { VButton, VIcon },
  props: {
    a11yProps: {},
  },
  emits: {
    click: defineEvent(),
  },
  setup() {
    return {
      ellipsisIcon,
    }
  },
})
</script>
