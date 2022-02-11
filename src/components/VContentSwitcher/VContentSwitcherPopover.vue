<template>
  <VPopover
    ref="contentMenuPopover"
    class="flex items-stretch"
    :label="$t('search-type.label')"
    placement="bottom-start"
  >
    <template #trigger="{ a11yProps }">
      <VContentSwitcherButton
        :a11y-props="a11yProps"
        aria-controls="content-switcher-popover"
        :active-item="activeItem"
        :class="{
          '!border-tx': isInSearchBar,
          'group-hover:!border-dark-charcoal-20':
            isInSearchBar && !a11yProps['aria-expanded'],
        }"
        :type="placement"
      />
    </template>
    <VContentTypes
      id="content-switcher-popover"
      size="medium"
      :active-item="activeItem"
      @select="selectItem"
    />
  </VPopover>
</template>

<script>
import { computed, ref } from '@nuxtjs/composition-api'
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
    placement: {
      type: String,
      default: 'header',
    },
  },
  setup(props, { emit }) {
    const content = useContentType()

    const contentMenuPopover = ref(null)

    /**
     * When in the searchbar, content switcher button has a border when the
     * search bar group is hovered on.
     * @type {ComputedRef<boolean>}
     */
    const isInSearchBar = computed(() => props.placement === 'searchbar')

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
      isInSearchBar,
      closeMenu,
    }
  },
}
</script>
