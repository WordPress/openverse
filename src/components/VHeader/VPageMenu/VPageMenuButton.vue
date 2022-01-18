<template>
  <VButton
    variant="action-menu"
    size="disabled"
    class="font-semibold p-2 w-12 leading-7"
    :aria-label="buttonLabel"
    v-bind="a11yProps"
    @click="$emit('click')"
  >
    <VIcon :icon-path="ellipsisIcon" />
  </VButton>
</template>
<script>
import { computed, useContext } from '@nuxtjs/composition-api'

import ellipsisIcon from '~/assets/icons/ellipsis.svg'

import VIcon from '~/components/VIcon/VIcon.vue'
import VButton from '~/components/VButton.vue'

export default {
  name: 'VPageMenuButton',
  components: { VButton, VIcon },
  props: {
    a11yProps: {},
  },
  setup() {
    const { i18n } = useContext()
    const buttonLabel = computed(() => i18n.t('header.aria.menu'))
    return {
      buttonLabel,
      ellipsisIcon,
    }
  },
}
</script>
