<template>
  <VButton
    variant="action-menu"
    size="disabled"
    class="w-12 p-2"
    :aria-label="$t('header.aria.menu')"
    data-testid="page-menu-button"
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
