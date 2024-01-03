<template>
  <VItem
    :selected="selected"
    :is-first="isFirst"
    :as="component"
    class="label-regular"
    :size="size"
    v-bind="{ href }"
    @click="$emit('click', item)"
  >
    <VIcon :name="icon" class="h-6 w-6" />
    <span>{{ itemLabelKey }}</span>
    <VPill v-if="isBeta" class="ms-auto">{{
      $t("searchType.statusBeta")
    }}</VPill>
  </VItem>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import { BETA, contentStatus, SearchType } from "~/constants/media"
import { isSearchTypeSupported, useSearchStore } from "~/stores/search"
import useSearchType from "~/composables/use-search-type"

import { defineEvent } from "~/types/emits"

import VIcon from "~/components/VIcon/VIcon.vue"
import VItem from "~/components/VItemGroup/VItem.vue"
import VPill from "~/components/VPill.vue"

export default defineComponent({
  name: "VSearchTypeItem",
  components: { VIcon, VItem, VPill },
  props: {
    /**
     * The search type to render.
     */
    item: {
      type: String as PropType<SearchType>,
      required: true,
    },
    /**
     * Used for correctly handling keyboard navigation in VItem.
     */
    isFirst: {
      type: Boolean,
      default: false,
    },
    /**
     * Whether the item is selected.
     */
    selected: {
      type: Boolean,
      default: false,
    },
    /**
     * The icon used for the search type.
     */
    icon: {
      type: String,
      required: true,
    },
    /**
     * Whether to use a `/search/image/?<query>` link or a button.
     */
    useLinks: {
      type: Boolean,
      default: true,
    },
    /**
     * 'Small' size for larger screens,
     * 'medium' size for mobile screens.
     */
    size: {
      type: String as PropType<"small" | "medium">,
      default: "small",
    },
  },
  emits: {
    click: defineEvent<[SearchType]>(),
  },
  setup(props) {
    const searchStore = useSearchStore()
    const { getSearchTypeProps } = useSearchType()

    const itemLabelKey = computed(() => getSearchTypeProps(props.item).label)

    /**
     * Currently, there are no Beta search types, so TS raises an error saying
     * that this condition will always return false.
     */
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-expect-error
    const isBeta = computed(() => contentStatus[props.item] === BETA)

    const href = computed(() => {
      if (!props.useLinks || !isSearchTypeSupported(props.item)) {
        return undefined
      }
      return searchStore.getSearchPath({ type: props.item })
    })

    /**
     * The query sets the filters that are applicable for the specific search type.
     */
    const component = computed(() => (props.useLinks ? "VLink" : undefined))
    return {
      component,
      href,
      isBeta,
      itemLabelKey,
    }
  },
})
</script>
