<template>
  <VPopover
    ref="contentMenuPopover"
    class="flex items-stretch"
    :label="$t('search-type.label').toString()"
    placement="bottom-end"
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

<script lang="ts">
import {
  ComponentInstance,
  computed,
  defineComponent,
  PropType,
  ref,
} from '@nuxtjs/composition-api'

import useSearchType from '~/composables/use-search-type'
import type { SearchType } from '~/constants/media'
import { defineEvent } from '~/types/emits'

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
      type: String as PropType<SearchType>,
      required: true,
    },
    placement: {
      type: String as PropType<'header' | 'searchbar'>,
      default: 'header',
    },
  },
  emits: {
    select: defineEvent<SearchType>(),
  },
  setup(props, { emit }) {
    const content = useSearchType()

    const contentMenuPopover = ref<ComponentInstance | null>(null)

    /**
     * When in the searchbar, content switcher button has a border when the
     * search bar group is hovered on.
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

    const selectItem = (item: SearchType) => {
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
