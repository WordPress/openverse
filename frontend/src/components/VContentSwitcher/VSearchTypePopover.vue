<script setup lang="ts">
import { ref } from "vue"

import { SEARCH_TYPES_DIALOG } from "#shared/constants/dialogs"
import useSearchType from "~/composables/use-search-type"

import VPopover from "~/components/VPopover/VPopover.vue"
import VSearchTypeButton from "~/components/VContentSwitcher/VSearchTypeButton.vue"
import VSearchTypes from "~/components/VContentSwitcher/VSearchTypes.vue"

withDefaults(defineProps<{ showLabel?: boolean }>(), { showLabel: false })

const contentMenuPopover = ref<InstanceType<typeof VPopover> | null>(null)

const { activeType: searchType } = useSearchType()

const handleSelect = () => {
  contentMenuPopover.value?.close()
}
</script>

<template>
  <VPopover
    :id="SEARCH_TYPES_DIALOG"
    ref="contentMenuPopover"
    :label="$t('searchType.label')"
    placement="bottom-end"
    :clippable="true"
    :trap-focus="false"
  >
    <template #trigger="{ a11yProps }">
      <VSearchTypeButton
        id="search-type-button"
        v-bind="a11yProps"
        :search-type="searchType"
        :show-label="showLabel"
        aria-controls="content-switcher-popover"
      />
    </template>
    <VSearchTypes
      id="content-switcher-popover"
      size="small"
      :use-links="true"
      @select="handleSelect"
    />
  </VPopover>
</template>
