<template>
  <VPopover
    ref="pageMenuPopover"
    class="flex items-stretch"
    :clippable="true"
    :label="$t('header.aria.menu')"
  >
    <template #trigger="{ a11yProps }">
      <VPageMenuButton :a11y-props="a11yProps" />
    </template>
    <template #default="{ close }">
      <VPageList layout="vertical" @click="close" />
    </template>
  </VPopover>
</template>

<script>
import { defineComponent } from '@nuxtjs/composition-api'

import VPopover from '~/components/VPopover/VPopover.vue'
import VPageMenuButton from '~/components/VHeaderOld/VPageMenu/VPageMenuButton.vue'
import VPageList from '~/components/VHeaderOld/VPageMenu/VPageList.vue'

export default defineComponent({
  name: 'VDesktopPageMenu',
  components: {
    VPageMenuButton,
    VPageList,
    VPopover,
  },
})
</script>
