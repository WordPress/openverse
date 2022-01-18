<template>
  <VPopover
    ref="pageMenuPopover"
    class="flex mx-2 items-stretch"
    :label="$t('header.aria.menu')"
  >
    <template #trigger="{ a11yProps }">
      <VPageMenuButton :a11y-props="a11yProps" />
    </template>
    <VPageList layout="vertical" @click="closeMenu" />
  </VPopover>
</template>

<script>
import { ref } from '@nuxtjs/composition-api'

import VPopover from '~/components/VPopover/VPopover.vue'
import VPageMenuButton from '~/components/VHeader/VPageMenu/VPageMenuButton.vue'
import VPageList from '~/components/VHeader/VPageMenu/VPageList.vue'

export default {
  name: 'VDesktopPageMenu',
  components: {
    VPageMenuButton,
    VPageList,
    VPopover,
  },
  setup() {
    const pageMenuPopover = ref(null)

    /**
     * Only the contentMenuPopover needs to be closed programmatically
     */
    const closeMenu = () => {
      if (pageMenuPopover.value) {
        pageMenuPopover.value.close()
      }
    }

    return {
      pageMenuPopover,
      closeMenu,
    }
  },
}
</script>
