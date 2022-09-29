<template>
  <VItemGroup
    direction="vertical"
    :size="size"
    :bordered="bordered"
    type="radiogroup"
    class="z-10 max-w-full md:w-[260px]"
  >
    <div
      v-for="(category, index) in contentTypeGroups"
      :key="index"
      :class="{
        'mt-2': index > 0,
        'border-t border-dark-charcoal-20 bg-dark-charcoal-06':
          index > 0 && !bordered,
      }"
    >
      <h4
        :class="bordered ? 'ps-0' : 'ps-6'"
        class="pt-6 pb-4 text-sr font-semibold uppercase pe-6"
      >
        {{ $t(`search-type.${category.heading}`) }}
      </h4>
      <VSearchTypeItem
        v-for="(item, idx) in category.items"
        :key="item"
        class="md:mb-1"
        :item="item"
        :item-id="idx"
        :icon="content.icons[item]"
        :use-links="useLinks"
        :selected="isActive(item)"
        @click="selectItem(item)"
      />
    </div>
  </VItemGroup>
</template>
<script lang="ts">
import {
  computed,
  defineComponent,
  type PropType,
} from '@nuxtjs/composition-api'

import useSearchType from '~/composables/use-search-type'
import type { SearchType } from '~/constants/media'
import { defineEvent } from '~/types/emits'

import VItemGroup from '~/components/VItemGroup/VItemGroup.vue'
import VSearchTypeItem from '~/components/VContentSwitcher/VSearchTypeItem.vue'

export default defineComponent({
  name: 'VSearchTypes',
  components: { VItemGroup, VSearchTypeItem },
  props: {
    /**
     * 'Small' size for mobile screens,
     * 'medium' size for larger screens.
     */
    size: {
      type: String as PropType<'small' | 'medium'>,
      default: 'small',
    },
    /**
     * Whether to use buttons for search type selection, or links to the specific search type search for the items.
     */
    useLinks: {
      type: Boolean,
      default: true,
    },
  },
  emits: {
    select: defineEvent<[SearchType]>(),
  },
  setup(props, { emit }) {
    const content = useSearchType()
    const bordered = computed(() => props.size === 'small')

    const isActive = (item: SearchType) => item === content.activeType.value

    const contentTypeGroups = computed(() => {
      const base = [
        {
          heading: 'heading',
          items: content.types,
        },
      ]

      if (content.additionalTypes.value.length && props.useLinks) {
        base.push({
          heading: 'additional',
          items: content.additionalTypes.value,
        })
      }

      return base
    })

    const selectItem = (item: SearchType) => {
      content.setActiveType(item)
      emit('select', item)
    }

    return {
      content,
      contentTypeGroups,
      isActive,
      bordered,
      selectItem,
    }
  },
})
</script>
