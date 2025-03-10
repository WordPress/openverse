<script setup lang="ts">
import { computed } from "vue"

import type { SearchType } from "#shared/constants/media"
import useSearchType from "~/composables/use-search-type"

import VItemGroup from "~/components/VItemGroup/VItemGroup.vue"
import VSearchTypeItem from "~/components/VContentSwitcher/VSearchTypeItem.vue"

type ContentTypeGroup = {
  heading: string
  items: SearchType[]
}

const props = withDefaults(
  defineProps<{
    /**
     * 'Small' size is used in the popover,
     * 'medium' size is used in the mobile modal.
     */
    size?: "small" | "medium"
    /**
     * Whether to use buttons for search type selection, or links to the specific search type search pages.
     */
    useLinks?: boolean
  }>(),
  {
    size: "small",
    useLinks: true,
  }
)

const emit = defineEmits<{ select: [SearchType] }>()

const content = useSearchType({ component: "VSearchTypes" })
const bordered = computed(() => props.size === "medium")

const isActive = (item: SearchType) => item === content.activeType.value

const contentTypeGroups = computed<ContentTypeGroup[]>(() => {
  const base: ContentTypeGroup[] = [
    {
      heading: "heading",
      items: content.types,
    },
  ]

  if (content.additionalTypes.value.length) {
    base.push({
      heading: "additional",
      items: [...content.additionalTypes.value],
    })
  }

  return base
})

const selectItem = (item: SearchType) => {
  content.setActiveType(item)
  emit("select", item)
}
</script>

<template>
  <VItemGroup
    direction="vertical"
    :size="size"
    :bordered="bordered"
    type="radiogroup"
  >
    <div
      v-for="(category, index) in contentTypeGroups"
      :key="category.heading"
      class="flex flex-col"
      :class="{
        'border-t border-default bg-surface': index > 0 && !bordered,
        'w-66 gap-1 py-2': size === 'small',
      }"
    >
      <h4
        v-if="index !== 0"
        :class="bordered ? 'ps-0' : 'ps-6'"
        class="category pb-4 pt-6"
      >
        {{ $t(`searchType.${category.heading}`) }}
      </h4>
      <VSearchTypeItem
        v-for="(item, idx) in category.items"
        :key="item"
        :item="item"
        :is-first="index === 0 && idx === 0"
        :icon="content.icons[item]"
        :use-links="useLinks"
        :selected="isActive(item)"
        @click="selectItem(item)"
      />
    </div>
  </VItemGroup>
</template>
