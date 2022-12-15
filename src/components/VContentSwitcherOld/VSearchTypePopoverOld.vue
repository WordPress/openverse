<template>
  <VPopover
    ref="contentMenuPopover"
    class="flex items-stretch"
    :label="$t('search-type.label').toString()"
    placement="bottom-end"
    :clippable="true"
  >
    <template #trigger="{ a11yProps }">
      <VSearchTypeButtonOld
        :a11y-props="a11yProps"
        aria-controls="content-switcher-popover"
        :active-item="activeItem"
        :type="placement"
      />
    </template>
    <VSearchTypesOld
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
  computed,
  defineComponent,
  PropType,
  ref,
} from "@nuxtjs/composition-api"

import type { SearchType } from "~/constants/media"
import { defineEvent } from "~/types/emits"

import VPopover from "~/components/VPopover/VPopover.vue"
import VSearchTypeButtonOld from "~/components/VContentSwitcherOld/VSearchTypeButtonOld.vue"
import VSearchTypesOld from "~/components/VContentSwitcherOld/VSearchTypesOld.vue"

import checkIcon from "~/assets/icons/checkmark.svg"

export default defineComponent({
  name: "VSearchTypePopoverOld",
  components: {
    VSearchTypeButtonOld,
    VPopover,
    VSearchTypesOld,
  },
  model: {
    prop: "activeItem",
    event: "select",
  },
  props: {
    activeItem: {
      type: String as PropType<SearchType>,
      required: true,
    },
    placement: {
      type: String as PropType<"header" | "searchbar">,
      default: "header",
    },
  },
  emits: {
    select: defineEvent<SearchType>(),
  },
  setup(props, { emit }) {
    const contentMenuPopover = ref<InstanceType<typeof VPopover> | null>(null)

    /**
     * When in the searchbar, content switcher button has a border when the
     * search bar group is hovered on.
     */
    const isInSearchBar = computed(() => props.placement === "searchbar")

    /**
     * Only the contentMenuPopover needs to be closed programmatically
     */
    const closeMenu = () => {
      contentMenuPopover.value?.close()
    }

    const selectItem = (item: SearchType) => {
      emit("select", item)
    }

    return {
      checkIcon,
      selectItem,
      contentMenuPopover,
      isInSearchBar,
      closeMenu,
    }
  },
})
</script>
