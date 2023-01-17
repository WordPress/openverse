<template>
  <VItemGroup
    direction="vertical"
    :size="size"
    :bordered="bordered"
    type="radiogroup"
    :class="{ 'w-66 pt-2': size === 'small' }"
  >
    <div
      v-for="(category, index) in contentTypeGroups"
      :key="index"
      :class="{
        'mt-2': index > 0,
        'border-t border-dark-charcoal-20 bg-dark-charcoal-06':
          index > 0 && !bordered,
        'w-66': size === 'small',
      }"
    >
      <h4
        :class="bordered ? 'ps-0' : 'ps-6'"
        class="category pt-6 pb-4 text-sr"
      >
        {{ $t(`search-type.${category.heading}`) }}
      </h4>
      <VSearchTypeItemOld
        v-for="(item, idx) in category.items"
        :key="item"
        :class="{ 'mb-1': size === 'small' }"
        :item="item"
        :item-id="idx"
        :icon="content.icons[item]"
        :use-links="useLinks"
        :selected="item === activeItem"
        @click="handleClick(item)"
      />
    </div>
  </VItemGroup>
</template>
<script lang="ts">
import { computed, defineComponent, PropType } from "@nuxtjs/composition-api"

import type { SearchType } from "~/constants/media"
import useSearchType from "~/composables/use-search-type"
import { defineEvent } from "~/types/emits"

import VItemGroup from "~/components/VItemGroup/VItemGroup.vue"
import VSearchTypeItemOld from "~/components/VContentSwitcherOld/VSearchTypeItemOld.vue"

export default defineComponent({
  name: "VSearchTypesOld",
  components: { VItemGroup, VSearchTypeItemOld },
  props: {
    /**
     * 'Small' size for popovers on larger screens,
     * 'medium' size for modals on mobile screens.
     */
    size: {
      type: String as PropType<"small" | "medium">,
      default: "small",
    },
    activeItem: {
      type: String as PropType<SearchType>,
      required: true,
    },
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

    const contentTypeGroups = computed(() => {
      const base = [
        {
          heading: "heading",
          items: content.types,
        },
      ]

      if (content.additionalTypes.value.length && props.useLinks) {
        base.push({
          heading: "additional",
          items: content.additionalTypes.value,
        })
      }

      return base
    })

    const bordered = computed(() => props.size === "medium")
    const handleClick = (item) => {
      emit("select", item)
    }
    return {
      content,
      contentTypeGroups,
      bordered,
      handleClick,
    }
  },
})
</script>
