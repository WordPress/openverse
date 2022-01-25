<template>
  <VPopover
    ref="contentMenuPopover"
    class="flex mx-4 items-stretch"
    :label="$t('search-type.label')"
    placement="bottom-start"
  >
    <template #trigger="{ a11yProps }">
      <VContentSwitcherButton
        :a11y-props="a11yProps"
        :active-item="activeItem"
      />
    </template>
    <VContentTypes
      size="medium"
      :active-item="activeItem"
      @select="selectItem"
    />
  </VPopover>
</template>

<script>
import { ref } from '@nuxtjs/composition-api'
import useContentType from '~/composables/use-content-type'
import checkIcon from '~/assets/icons/checkmark.svg'

import VPopover from '~/components/VPopover/VPopover.vue'
import VContentSwitcherButton from '~/components/VContentSwitcher/VContentSwitcherButton.vue'
import VContentTypes from '~/components/VContentSwitcher/VContentTypes.vue'

export default {
  name: 'VContentSwitcherPopover',
  components: {
    VContentSwitcherButton,
    VPopover,
    VContentTypes,
  },
  model: {
    prop: 'activeItem',
    event: 'select',
  },
  props: {
    activeItem: {
      type: String,
      required: true,
    },
  },
  setup(props, { emit }) {
    const content = useContentType()

    const contentMenuPopover = ref(null)

    /**
     * Only the contentMenuPopover needs to be closed programmatically
     */
    const closeMenu = () => {
      if (contentMenuPopover.value) {
        contentMenuPopover.value.close()
      }
    }

    const selectItem = (item) => {
      emit('select', item)
    }

    return {
      content,
      checkIcon,
      selectItem,
      contentMenuPopover,
      closeMenu,
    }
  },
}
</script>
