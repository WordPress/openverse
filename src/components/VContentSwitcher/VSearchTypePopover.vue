<template>
  <VPopover
    ref="contentMenuPopover"
    class="flex items-stretch"
    :label="$t('search-type.label')"
    placement="bottom-start"
  >
    <template #trigger="{ a11yProps }">
      <VSearchTypeButton
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
    <VSearchTypes
      id="content-switcher-popover"
      size="medium"
      :active-item="activeItem"
      :use-links="placement === 'header'"
      @select="selectItem"
    />
  </VPopover>
</template>

<script>
import { computed, defineComponent, ref } from '@nuxtjs/composition-api'

import useSearchType from '~/composables/use-search-type'

import VPopover from '~/components/VPopover/VPopover.vue'
import VSearchTypeButton from '~/components/VContentSwitcher/VSearchTypeButton.vue'
import VSearchTypes from '~/components/VContentSwitcher/VSearchTypes.vue'

import checkIcon from '~/assets/icons/checkmark.svg'

export default defineComponent({
  name: 'VSearchTypePopover',
  components: {
    VSearchTypeButton,
    VPopover,
    VSearchTypes,
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
    const content = useSearchType()

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
})
</script>
