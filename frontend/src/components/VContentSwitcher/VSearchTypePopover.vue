<template>
  <VPopover
    ref="contentMenuPopover"
    :label="$t('searchType.label').toString()"
    placement="bottom-end"
    :clippable="true"
    :trap-focus="false"
  >
    <template #trigger="{ a11yProps }">
      <VSearchTypeButton
        id="search-type-button"
        v-bind="{ ...a11yProps, ...searchTypeProps }"
        :show-label="showLabel"
        aria-controls="content-switcher-popover"
      />
    </template>
    <VSearchTypes
      id="content-switcher-popover"
      size="small"
      :use-links="placement === 'header'"
      @select="handleSelect"
    />
  </VPopover>
</template>

<script lang="ts">
import { computed, defineComponent, PropType, ref } from "vue"

import useSearchType from "~/composables/use-search-type"

import type { SearchType } from "~/constants/media"

import { defineEvent } from "~/types/emits"

import VPopover from "~/components/VPopover/VPopover.vue"
import VSearchTypeButton from "~/components/VContentSwitcher/VSearchTypeButton.vue"
import VSearchTypes from "~/components/VContentSwitcher/VSearchTypes.vue"

export default defineComponent({
  name: "VSearchTypePopover",
  components: {
    VPopover,
    VSearchTypeButton,
    VSearchTypes,
  },
  props: {
    showLabel: {
      type: Boolean,
      default: false,
    },
    placement: {
      type: String as PropType<"header" | "searchbar">,
      default: "header",
    },
  },
  emits: {
    select: defineEvent<[SearchType]>(),
  },
  setup(_, { emit }) {
    const contentMenuPopover = ref<InstanceType<typeof VPopover> | null>(null)

    const { getSearchTypeProps } = useSearchType()

    const searchTypeProps = computed(() => getSearchTypeProps())

    const handleSelect = (searchType: SearchType) => {
      emit("select", searchType)
      contentMenuPopover.value?.close()
    }

    return {
      handleSelect,
      contentMenuPopover,
      searchTypeProps,
    }
  },
})
</script>
