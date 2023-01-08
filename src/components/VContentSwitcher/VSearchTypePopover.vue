<template>
  <VPopover
    ref="contentMenuPopover"
    :label="$t('search-type.label').toString()"
    placement="bottom-end"
    :clippable="true"
  >
    <template #trigger="{ a11yProps }">
      <VSearchTypeButton
        v-bind="{ ...a11yProps, ...searchTypeProps }"
        :show-label="showLabel"
        aria-controls="content-switcher-popover"
      />
    </template>
    <VSearchTypes
      id="content-switcher-popover"
      class="w-[260px] pt-2"
      size="small"
      :use-links="placement === 'header'"
      @select="handleSelect"
    />
  </VPopover>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  PropType,
  ref,
} from "@nuxtjs/composition-api"

import useSearchType from "~/composables/use-search-type"

import type { SearchType } from "~/constants/media"

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
