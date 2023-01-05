<template>
  <VPopover
    ref="contentMenuPopover"
    class="flex items-stretch"
    :label="$t('search-type.label').toString()"
    placement="bottom-end"
    :clippable="true"
  >
    <template #trigger="{ a11yProps }">
      <VSearchTypeButton
        :a11y-props="a11yProps"
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
import { defineComponent, PropType, ref } from "@nuxtjs/composition-api"

import type { SearchType } from "~/constants/media"

import VPopover from "~/components/VPopover/VPopover.vue"
import VSearchTypeButton from "~/components/VContentSwitcher/VSearchTypeButton.vue"
import VSearchTypes from "~/components/VContentSwitcher/VSearchTypes.vue"

import checkIcon from "~/assets/icons/checkmark.svg"

export default defineComponent({
  name: "VSearchTypePopover",
  components: {
    VPopover,
    VSearchTypeButton,
    VSearchTypes,
  },
  props: {
    placement: {
      type: String as PropType<"header" | "searchbar">,
      default: "header",
    },
  },
  setup(_, { emit }) {
    const contentMenuPopover = ref<InstanceType<typeof VPopover> | null>(null)

    const handleSelect = (searchType: SearchType) => {
      emit("select", searchType)
      contentMenuPopover.value?.close()
    }

    return {
      checkIcon,
      handleSelect,
      contentMenuPopover,
    }
  },
})
</script>
