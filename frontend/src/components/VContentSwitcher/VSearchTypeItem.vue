<template>
  <VItem
    :selected="selected"
    :is-first="isFirst"
    :as="component"
    class="label-regular"
    v-bind="{ href }"
    @click="emit('click', item)"
  >
    <VIcon :name="icon" class="h-6 w-6" />
    <span>{{ itemLabelKey }}</span>
    <VPill v-if="isBeta" class="ms-auto">{{
      t("searchType.statusBeta")
    }}</VPill>
  </VItem>
</template>

<script setup lang="ts">
import { useNuxtApp } from "#imports"

import { computed } from "vue"

import { BETA, contentStatus, SearchType } from "~/constants/media"
import { isSearchTypeSupported, useSearchStore } from "~/stores/search"
import useSearchType from "~/composables/use-search-type"

import VIcon from "~/components/VIcon/VIcon.vue"
import VItem from "~/components/VItemGroup/VItem.vue"
import VPill from "~/components/VPill.vue"

const {
  $i18n: { t },
} = useNuxtApp()

const props = withDefaults(
  defineProps<{
    /**
     * The search type to render.
     */
    item: SearchType
    /**
     * Used for correctly handling keyboard navigation in VItem.
     */
    isFirst?: boolean
    /**
     * Whether the item is selected.
     */
    selected?: boolean
    /**
     * The icon used for the search type.
     */
    icon: string
    /**
     * Whether to use a `/search/image/?<query>` link or a button.
     */
    useLinks?: boolean
  }>(),
  {
    isFirst: false,
    selected: false,
    useLinks: true,
  }
)

const emit = defineEmits<{
  click: [SearchType]
}>()

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
</script>
